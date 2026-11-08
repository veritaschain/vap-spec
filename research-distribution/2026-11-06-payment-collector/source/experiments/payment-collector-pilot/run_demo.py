"""Native synthetic collector failures and evidence-only recovery; no real funds.

Only summary.json and evidence-bundle.json are exported. Private service keys,
credentials, configuration and SQLite stores remain in temporary directories.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import importlib.util
import json
import os
from pathlib import Path
import secrets
import selectors
import subprocess
import sys
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "payment-authorization-pilot"))
import authorization_gate as admission
import payment_collector as collection

runtime = admission.runtime
_SPEC = importlib.util.spec_from_file_location(
    "_vso_collector_demo_authority", ROOT.parent / "payment-authorization-pilot" / "run_demo.py")
if _SPEC is None or _SPEC.loader is None:
    raise ImportError("local_demo_authority_unavailable")
authority = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = authority
_SPEC.loader.exec_module(authority)


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise RuntimeError("collector_demo_expectation_failed:" + reason)


def encoded(value):
    """Preserve bytes explicitly, without rewriting signed JSON envelopes."""
    if type(value) is bytes:
        return {"encoding": "hex", "bytes": value.hex()}
    if type(value) is dict:
        return {key: encoded(item) for key, item in value.items()}
    if type(value) in (list, tuple):
        return [encoded(item) for item in value]
    return value


def artifact_json(value) -> bytes:
    # A multi-scenario artifact is not a wire request. Preserve the component
    # bytes without applying the runtime's per-message 64 KiB input limit.
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def compact(value):
    """Keep states/counts in the summary; original bytes live in the bundle."""
    if type(value) is bytes:
        return {"original_bytes_digest": runtime.bytes_digest(value), "byte_length": len(value)}
    if type(value) is str and len(value) > 512:
        return {"summary_text_digest": runtime.bytes_digest(value.encode("utf-8")),
                "character_length": len(value), "full_value_in_evidence_bundle": True}
    if type(value) is dict:
        return {key: compact(item) for key, item in value.items()}
    if type(value) in (list, tuple):
        return [compact(item) for item in value]
    return value


class Service:
    def __init__(self, command: list[str]):
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(self.process.stdout, selectors.EVENT_READ)
                if not selector.select(timeout=10):
                    raise RuntimeError("native_demo_service_startup_timeout")
                line = self.process.stdout.readline()
            ready = json.loads(line) if line else {}
            if ready.get("event") != "ready":
                raise RuntimeError("native_demo_service_startup_failed")
            self.endpoint = ready["endpoint"]
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        for stream in (self.process.stdout, self.process.stderr):
            if stream is not None and not stream.closed:
                stream.close()


class Scenario:
    def __init__(self, name: str, *, provider_response_loss=False, collector_ack_loss=False):
        self.name = name
        self.temporary = tempfile.TemporaryDirectory(prefix="synthetic-payment-collector-")
        self.root = Path(self.temporary.name)
        self.root.chmod(0o700)
        self.services: list[Service] = []
        self.index = 0
        self.context = {
            "tenant": "synthetic-tenant-A", "environment": "synthetic-lab",
            "api_audience": "synthetic-loopback-api", "idempotency_domain": "synthetic-domain-A",
            "currency": "USD", "minor_unit_scale": 2,
        }
        self.configuration = runtime.digest({"synthetic_configuration": "payment-collector-demo-v0"})
        self.provider_key = Ed25519PrivateKey.generate()
        self.collector_key = Ed25519PrivateKey.generate()
        self.provider_credential = secrets.token_hex(32)
        self.collector_credential = secrets.token_hex(32)
        self.provider_db = self.root / "provider.sqlite"
        self.collector_db = self.root / "collector.sqlite"
        self.journal = self.root / "journal.sqlite"
        self.collector_id = "synthetic-payment-collector-v0"
        self.collector_epoch = 1
        self.request = runtime.make_request(self.context,
            operation_id="synthetic-operation-" + name, idempotency_key="synthetic-idempotency-" + name,
            configuration_digest=self.configuration, recovery_epoch=1,
            source_account="synthetic-source", beneficiary="synthetic-beneficiary", amount_minor="12500")
        self.gate_config, self.approval_keys = authority.demo_authority(self.context, self.configuration)
        self.steps = []
        self.observations = []
        self.latest_custody = None
        try:
            self.provider = self.start(runtime.__file__, "provider", {
                "db_path": str(self.provider_db), "context": self.context,
                "private_key_hex": self.provider_key.private_bytes_raw().hex(),
                "credential": self.provider_credential, "configuration_digest": self.configuration,
                "recovery_epoch": 1,
                "initial_balances": {"synthetic-source": "1000000", "synthetic-beneficiary": "0"},
                "drop_after_commit": provider_response_loss,
            })
            self.start_collector(drop_ack_after_commit=collector_ack_loss)
            self.native = runtime.Adapter(self.journal, self.provider.endpoint, self.context,
                self.provider_key.public_key().public_bytes_raw(), self.provider_credential,
                self.configuration, 1)
            self.authorized = admission.AuthorizedAdapter(self.native, self.gate_config)
            self.adapter = self.collected()
        except BaseException:
            self.close()
            raise

    def start(self, script: str, command: str, config: dict) -> Service:
        self.index += 1
        config_file = self.root / f"private-service-{self.index}.json"
        descriptor = os.open(config_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(runtime.canonical_json(config))
        executable = [sys.executable] + (["-O"] if sys.flags.optimize else [])
        service = Service([*executable, str(script), command, "--config", str(config_file)])
        self.services.append(service)
        return service

    def start_collector(self, *, drop_ack_after_commit=False):
        self.collector = self.start(collection.__file__, "collector", {
            "db_path": str(self.collector_db), "context": self.context,
            "private_key_hex": self.collector_key.private_bytes_raw().hex(),
            "credential": self.collector_credential, "collector_id": self.collector_id,
            "recovery_epoch": self.collector_epoch, "drop_ack_after_commit": drop_ack_after_commit,
        })

    def collected(self):
        client = collection.CollectorClient(self.collector.endpoint, self.context,
            self.collector_key.public_key().public_bytes_raw(), self.collector_credential,
            collector_id=self.collector_id, recovery_epoch=self.collector_epoch)
        return collection.CollectedAdapter(self.authorized, client)

    def restart_collector(self):
        self.collector.close()
        self.start_collector()
        self.adapter = self.collected()

    def submit(self):
        return self.adapter.submit(self.request,
            authority.demo_evidence(self.request, self.gate_config, self.approval_keys))

    def capture(self, stage: str, result: dict):
        provider = runtime.provider_snapshot(self.provider_db)
        collector = collection.collector_snapshot(self.collector_db)
        local = self.adapter.read_custody(self.request)
        self.latest_custody = local
        self.steps.append({
            "stage": stage, "state": result.get("state"),
            "reason": result.get("reason"), "request_digest": runtime.bytes_digest(runtime.request_bytes(self.request)),
            "payment_posts": provider["post_attempts"], "payment_effects": provider["effects"],
            "provider_lookups": provider["lookup_attempts"],
            "collector": {key: collector[key] for key in (
                "collect_attempts", "query_attempts", "records", "kind_counts")},
            "custody": compact(local),
        })
        self.observations.append({"stage": stage, "returned": compact(result),
                                  "local_custody": compact(local)})
        return provider

    def expect_payment(self, state: str, posts: int, effects: int, lookups: int):
        step = self.steps[-1]
        require((step["state"], step["payment_posts"], step["payment_effects"], step["provider_lookups"])
                == (state, posts, effects, lookups), self.name + ":" + step["stage"])
        provider = runtime.provider_snapshot(self.provider_db)
        require(provider["balances"]["synthetic-source"] == str(1000000 - 12500 * effects)
                and provider["balances"]["synthetic-beneficiary"] == str(12500 * effects),
                self.name + ":actual_toy_balance_effects")
        require(self.native.snapshot()["claims"] == 1, self.name + ":original_claim_retained")

    def expect_custody(self, pre_dispatch: str, admission_state: str, receipt_state: str, records: int):
        custody = self.latest_custody
        require((custody["pre_dispatch"]["state"], custody["admission_record"]["state"],
                 custody["provider_receipt"]["state"], self.steps[-1]["collector"]["records"])
                == (pre_dispatch, admission_state, receipt_state, records),
                self.name + ":custody:" + self.steps[-1]["stage"])
        require(custody["present_retention"] == "NOT_CHECKED", "local_history_is_not_a_current_lookup")
        require(custody["unverifiable_observations"] == 0, "demo_history_reverification")
        expected = "ACKNOWLEDGED" if admission_state == receipt_state == "ACKNOWLEDGED" else "UNKNOWN"
        require(custody["state"] == expected, "both_evidence_phases_required_for_overall_custody")
        if pre_dispatch == "VERIFIED_PREREQUISITE":
            require(custody["pre_dispatch"]["proves_payment_post_occurred"] is False,
                    "prerequisite_does_not_prove_dispatch")

    def original_ack_in_collector(self, kind: str) -> bytes:
        # Trusted demo-controller inspection, separate from what the client
        # could learn after a lost ACK. This is not independent observation.
        with closing(runtime._readonly(self.collector_db)) as connection:
            row = connection.execute("SELECT ack_bytes FROM collection_records WHERE request_digest=? AND kind=?",
                (runtime.bytes_digest(runtime.request_bytes(self.request)), kind)).fetchone()
            require(row is not None, "controller_expected_original_collector_record")
            return bytes(row["ack_bytes"])

    def expect_original_ack(self, kind: str, expected: bytes):
        observed = [item["ack_bytes"] for item in self.latest_custody["observations"] if item["kind"] == kind]
        require(bool(observed) and all(value == expected for value in observed), "original_ack_bytes_preserved")

    def export(self):
        original = self.authorized.read_authorization(self.request)
        status = self.authorized.read_status(self.request)
        bundle = {
            "scenario": self.name,
            "request": encoded(runtime.request_bytes(self.request)),
            "admission_record": encoded(original.get("record_bytes")),
            "provider_receipt": encoded(status.get("receipt_bytes")),
            "configured_public_pins": {
                "provider_id": self.native.provider_id,
                "provider_public_key_hex": self.provider_key.public_key().public_bytes_raw().hex(),
                "collector_id": self.collector_id, "collector_epoch": self.collector_epoch,
                "collector_public_key_hex": self.collector_key.public_key().public_bytes_raw().hex(),
                "context": self.context,
                "independent_trust_established": False,
            },
            "observations": self.observations,
            "original_custody_records": [{"observation_digest": item["observation_digest"],
                "record_bytes": encoded(item["record_bytes"])}
                for item in self.latest_custody["observations"]],
        }
        # Deliberately check the selected export, without printing private material.
        raw = artifact_json(bundle)
        private_values = [self.provider_credential, self.collector_credential,
            self.provider_key.private_bytes_raw().hex(), self.collector_key.private_bytes_raw().hex(),
            *(key.private_bytes_raw().hex() for key in self.approval_keys.values()), str(self.root)]
        require(not any(value.encode() in raw for value in private_values), "private_material_in_public_export")
        return {"scenario": self.name, "steps": self.steps}, bundle

    def close(self):
        for service in reversed(self.services):
            service.close()
        self.temporary.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def run_demo():
    summaries, bundles = [], []

    def finish(case):
        summary, bundle = case.export()
        summaries.append(summary)
        bundles.append(bundle)

    with Scenario("healthy") as case:
        case.capture("original_collection_and_payment", case.submit())
        case.expect_payment("SETTLED", 1, 1, 0)
        case.expect_custody("VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "ACKNOWLEDGED", 2)
        original_collector_counts = case.steps[-1]["collector"]
        case.capture("repeat_returns_original_result", case.adapter.submit(case.request))
        case.expect_payment("SETTLED", 1, 1, 0)
        case.expect_custody("VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "ACKNOWLEDGED", 2)
        require(case.steps[-1]["collector"] == original_collector_counts, "repeat_must_not_recollect")
        finish(case)

    with Scenario("collector_stopped") as case:
        case.collector.close()
        case.capture("collector_unreachable_before_payment", case.submit())
        case.expect_payment("UNKNOWN", 0, 0, 0)
        case.expect_custody("NOT_RECORDED", "UNKNOWN", "UNKNOWN", 0)
        case.restart_collector()
        case.capture("later_evidence_recovery", case.adapter.recover_evidence(case.request))
        case.expect_payment("UNKNOWN", 0, 0, 0)
        case.expect_custody("NOT_RECORDED", "ACKNOWLEDGED", "UNKNOWN", 1)
        case.capture("repeat_does_not_resume_payment", case.submit())
        case.expect_payment("UNKNOWN", 0, 0, 0)
        case.expect_custody("NOT_RECORDED", "ACKNOWLEDGED", "UNKNOWN", 1)
        finish(case)

    with Scenario("collector_ack_lost", collector_ack_loss=True) as case:
        case.capture("collector_committed_ack_lost", case.submit())
        case.expect_payment("UNKNOWN", 0, 0, 0)
        case.expect_custody("NOT_RECORDED", "UNKNOWN", "UNKNOWN", 1)
        original_ack = case.original_ack_in_collector("admission_record")
        case.restart_collector()
        case.capture("recover_original_collection_ack", case.adapter.recover_evidence(case.request))
        case.expect_payment("UNKNOWN", 0, 0, 0)
        case.expect_custody("NOT_RECORDED", "ACKNOWLEDGED", "UNKNOWN", 1)
        case.expect_original_ack("admission_record", original_ack)
        case.capture("repeat_still_consumed", case.submit())
        case.expect_payment("UNKNOWN", 0, 0, 0)
        case.expect_custody("NOT_RECORDED", "ACKNOWLEDGED", "UNKNOWN", 1)
        finish(case)

    with Scenario("provider_response_lost", provider_response_loss=True) as case:
        case.capture("provider_committed_response_lost", case.submit())
        case.expect_payment("UNKNOWN", 1, 1, 0)
        case.expect_custody("VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "UNKNOWN", 1)
        original_collector_counts = case.steps[-1]["collector"]
        reconciled = case.adapter.reconcile(case.request)
        case.capture("provider_get_only_reconciliation", reconciled)
        case.expect_payment("SETTLED", 1, 1, 1)
        case.expect_custody("VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "UNKNOWN", 1)
        require(case.steps[-1]["collector"] == original_collector_counts, "provider_reconciliation_is_not_collection")
        recovered = case.adapter.recover_evidence(case.request)
        require(recovered["receipt_bytes"] == reconciled["receipt_bytes"], "provider_original_receipt_preserved")
        case.capture("collect_original_provider_receipt", recovered)
        case.expect_payment("SETTLED", 1, 1, 1)
        case.expect_custody("VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "ACKNOWLEDGED", 2)
        finish(case)

    with Scenario("outcome_collection_stopped") as case:
        def stop_after_provider_response(stage, _details):
            if stage == "after_response":
                case.collector.close()

        case.native.fault_hook = stop_after_provider_response
        settled = case.submit()
        case.capture("financial_settled_outcome_custody_unresolved", settled)
        case.expect_payment("SETTLED", 1, 1, 0)
        case.expect_custody("VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "UNKNOWN", 1)
        case.native.fault_hook = None
        case.restart_collector()
        recovered = case.adapter.recover_evidence(case.request)
        require(recovered["receipt_bytes"] == settled["receipt_bytes"], "settled_receipt_retained_during_custody_outage")
        case.capture("recover_outcome_evidence_only", recovered)
        case.expect_payment("SETTLED", 1, 1, 0)
        case.expect_custody("VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "ACKNOWLEDGED", 2)
        finish(case)

    summary = {
        "schema": "synthetic-payment-collector-demo-summary-v0",
        "synthetic": True, "scenario_count": len(summaries),
        "stage_count": sum(len(case["steps"]) for case in summaries),
        "business_authorization_verified": False, "production_gate": False,
        "independent_custody_established": False, "complete_collection_asserted": False,
        "automatic_payment_retry": False, "scenarios": summaries,
        "limits": [
            "all_roles_keys_processes_and_toy_balances_belong_to_one_operator_and_host_user",
            "collection_ack_is_historical_fresh_readback_is_point_in_time_only",
            "later_collection_never_establishes_original_pre_dispatch_coverage",
            "mock_admission_remains_at_claim_time_not_live_authority_or_continuous_revocation",
            "raw_runtime_or_provider_with_bearer_can_bypass_wrappers",
            "no_independent_anchor_complete_log_storage_rollback_or_power_loss_guarantee",
            "no_VAP_conformance_complete_payment_acceptance_or_production_readiness_claim",
        ],
    }
    bundle = {"schema": "synthetic-payment-collector-demo-evidence-v0",
              "byte_encoding": "Original custody records, requests, admission records and provider receipts use encoding=hex objects. Stage observations reference their original digests. Each custody record retains original package, ACK and readback bytes as hex.",
              "public_keys_are_same_operator_declarations": True, "scenarios": bundles}
    return summary, bundle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Directory for two explicitly public demo files")
    args = parser.parse_args()
    summary, bundle = run_demo()
    if args.output is not None:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "summary.json").write_bytes(artifact_json(summary) + b"\n")
        (args.output / "evidence-bundle.json").write_bytes(artifact_json(bundle) + b"\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
