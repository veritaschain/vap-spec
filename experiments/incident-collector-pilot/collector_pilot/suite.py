"""Actual loopback collection, outage and observational-recovery scenarios."""

import hashlib
import json
import platform
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from importlib.metadata import version
from pathlib import Path

from . import ROOT, VERSION
from .client import CollectorClient
from .collector import CollectorProcess
from .gateway import CollectorGateway
from .harness import COLLECTOR_ID, SYNTHETIC_BYTES, make_case, make_keys
from .protocol import InputError, digest, utc_now
from upload_pilot.journal import Journal
from upload_pilot.receiver import ReceiverProcess
from upload_pilot.transport import HttpTransport


class ClaimFailure(Journal):
    """Trusted pre-commit fault, not a physical storage failure measurement."""
    def claim(self, *args, **kwargs):
        raise OSError("injected before local claim")


class ClaimAckLost(Journal):
    """The real SQLite claim commits; its caller loses the acknowledgement."""
    def claim(self, *args, **kwargs):
        super().claim(*args, **kwargs)
        raise OSError("injected after committed local claim")


class ResultFailure(Journal):
    def finish(self, *args, **kwargs):
        raise OSError("injected local outcome persistence failure")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def run_case(case_id, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    keys = make_keys()
    collector_mode = {"CP-03": "drop_before_commit", "CP-04": "drop_after_commit",
                      "CP-08": "wrong_receipt", "CP-09": "wrong_status_nonce"}.get(case_id, "normal")
    receiver = ReceiverProcess(directory / "receiver", gateway_public=keys["gateway"]["public"],
                               gateway_key_id=keys["gateway"]["key_id"], receiver_secret=keys["receiver"]["secret"],
                               receiver_key_id=keys["receiver"]["key_id"],
                               mode="drop_after_commit" if case_id == "CP-15" else "normal")
    collector = CollectorProcess(directory / "collector", collector_id=COLLECTOR_ID,
                                 gateway_public=keys["gateway"]["public"], gateway_key_id=keys["gateway"]["key_id"],
                                 collector_secret=keys["collector"]["secret"], collector_key_id=keys["collector"]["key_id"],
                                 mode=collector_mode)
    reports, reconciliations = [], []
    payload = SYNTHETIC_BYTES
    with receiver, collector:
        options = {"keys": keys}
        if case_id == "CP-07":
            options["expires_in"] = 2
        if case_id == "CP-11":
            options["grant_changes"] = {"tenant_id": "a-different-approved-tenant"}
        package, trust, config, _ = make_case(payload, receiver.endpoint, **options)
        journal_class = {"CP-10": ClaimFailure, "CP-17": ClaimAckLost, "CP-18": ResultFailure}.get(case_id, Journal)
        journal_path = directory / "journal.sqlite3"
        journal = journal_class(journal_path)
        client = CollectorClient(collector.endpoint, keys["collector"]["public"], keys["collector"]["key_id"])
        def gate(journal_instance=journal):
            return CollectorGateway(config, journal_instance, HttpTransport(receiver.endpoint), client,
                                    collector_id=COLLECTOR_ID, collector_public=keys["collector"]["public"],
                                    collector_key_id=keys["collector"]["key_id"])
        gateway = gate()
        hook = None
        if case_id in {"CP-02", "CP-05"}:
            collector.stop()
        if case_id == "CP-06":
            hook = collector.stop
        elif case_id == "CP-07":
            hook = lambda: time.sleep(2.1)
        elif case_id == "CP-16":
            payload = bytearray(SYNTHETIC_BYTES)
            def mutate_caller_owned_inputs():
                payload[:] = b"changed caller buffer after capture"
                package["records"].clear()
                trust["keys"].clear()
            hook = mutate_caller_owned_inputs
        if case_id == "CP-14":
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(gateway.execute, deepcopy(package), deepcopy(trust), payload) for _ in range(2)]
                reports = [future.result() for future in futures]
            reports.sort(key=lambda report: report["state"])
        else:
            reports.append(gateway.execute(package, trust, payload, before_final_check=hook))
        if case_id == "CP-04":
            collector.stop()
            collector.restart(mode="normal")
            reconciliations.append(gateway.reconcile(package["target"]["subject"]["request_id"]))
            reports.append(gateway.execute(package, trust, payload))
        elif case_id == "CP-05":
            collector.restart(mode="normal")
            reports.append(gateway.execute(package, trust, payload))
            fresh_package, fresh_trust, _, _ = make_case(payload, receiver.endpoint, keys=keys)
            reports.append(gateway.execute(fresh_package, fresh_trust, payload))
        elif case_id in {"CP-12", "CP-15", "CP-18"}:
            reports.append(gateway.execute(package, trust, payload))
        elif case_id == "CP-13":
            changed = SYNTHETIC_BYTES + b"different explicitly permitted bytes"
            conflict_package, conflict_trust, _, _ = make_case(
                changed, receiver.endpoint, keys=keys, request_id=package["target"]["subject"]["request_id"])
            reports.append(gateway.execute(conflict_package, conflict_trust, changed))
        elif case_id == "CP-17":
            reports.append(gate(Journal(journal_path)).execute(package, trust, payload))
        collector_snapshot, receiver_snapshot = collector.snapshot(), receiver.snapshot()
    record = {
        "format": "collector-pilot-case/0.1", "case_id": case_id, "recorded_at": utc_now(),
        "collector_id": COLLECTOR_ID, "collector_endpoint": collector.endpoint,
        "keys": {role: {key: value for key, value in item.items() if key != "secret"} for role, item in keys.items()},
        "payload_sha256": hashlib.sha256(SYNTHETIC_BYTES).hexdigest(), "byte_length": len(SYNTHETIC_BYTES),
        "reports": reports, "reconciliations": reconciliations,
        "collector_snapshot": collector_snapshot, "receiver_snapshot": receiver_snapshot,
        "cleanup": {"collector": deepcopy(collector.cleanup_result), "receiver": deepcopy(receiver.cleanup_result)},
    }
    from .exports import derive_actual
    record["actual"] = derive_actual(record)
    serialized = json.dumps(record, ensure_ascii=False)
    if any(item["secret"] in serialized for item in keys.values()) or "SYNTHETIC COLLECTOR PILOT ONLY" in serialized:
        raise InputError("Private key or payload plaintext was present in a public capture")
    return record


def run_suite(output, *, print_summary=False):
    from .exports import check_case, read_json, scope, source_manifest, verify_exports
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise InputError("Output already exists; choose a fresh path")
    expected_cases = read_json(ROOT / "acceptance.json")["cases"]
    source = source_manifest()
    output.mkdir(parents=True)
    public = output / "public"
    results = []
    for case in expected_cases:
        record = run_case(case["id"], output / "runtime" / case["id"])
        check_case(record)
        differences = {key: {"expected": value, "actual": record["actual"].get(key)}
                       for key, value in case["expected"].items() if record["actual"].get(key) != value}
        write_json(public / "cases" / (case["id"] + ".json"), record)
        results.append({"case_id": case["id"], "title": case["title"], "expected": case["expected"],
                        "actual": record["actual"], "matched": not differences, "differences": differences,
                        "file_sha256": hashlib.sha256((public / "cases" / (case["id"] + ".json")).read_bytes()).hexdigest()})
        print(case["id"] + (" MATCH" if not differences else " MISMATCH " + json.dumps(differences)), flush=True)
    if source != source_manifest():
        raise InputError("Implementation or frozen inputs changed during execution")
    summary = {"format": "collector-pilot-summary/0.1", "implementation_version": VERSION,
               "recorded_at": utc_now(), "scope": scope(), "source_sha256": digest(source), "source_files": source,
               "toolchain": {"python": sys.version, "platform": platform.platform(),
                             "dependencies": {name: version(name) for name in ("cryptography", "rfc8785", "cffi", "pycparser")}},
               "total": len(results), "matched": sum(item["matched"] for item in results), "results": results}
    write_json(public / "summary.json", summary)
    summary_hash = hashlib.sha256((public / "summary.json").read_bytes()).hexdigest()
    (output / "summary.sha256").write_text(summary_hash + "\n", encoding="ascii")
    print("COLLECTOR_SUMMARY_SHA256=" + summary_hash, flush=True)
    if summary["matched"] != summary["total"]:
        return 1
    checked = verify_exports(public, expected_summary_sha256=summary_hash)
    print(json.dumps(checked, ensure_ascii=False), flush=True)
    if print_summary:
        print("COLLECTOR_PILOT_SUMMARY_JSON=" + json.dumps(summary, ensure_ascii=False, separators=(",", ":")), flush=True)
    return 0
