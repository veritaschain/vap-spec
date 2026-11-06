"""Run a temporary loopback lost-acknowledgment demonstration; no real funds.

Only public results and the provider's signed mock receipt can be exported.
Temporary databases, ephemeral credentials and private keys are never exported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import selectors
import subprocess
import sys
import tempfile

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from payment_runtime import Adapter, canonical_json, digest, make_request, provider_snapshot


def public_result(result: dict) -> dict:
    receipt = result["receipt_bytes"]
    return {
        "state": result["state"], "request_digest": result["request_digest"],
        "business_authorization_verified": result["business_authorization_verified"],
        "automatic_retry": result["automatic_retry"],
        "receipt_sha256": hashlib.sha256(receipt).hexdigest() if receipt else None,
    }


def run_demo() -> tuple[dict, bytes]:
    with tempfile.TemporaryDirectory(prefix="synthetic-payment-runtime-") as directory:
        root = Path(directory)
        context = {
            "tenant": "synthetic-tenant-A", "environment": "synthetic-lab",
            "api_audience": "synthetic-loopback-api",
            "idempotency_domain": "synthetic-payment-domain-A",
            "currency": "USD", "minor_unit_scale": 2,
        }
        configuration = digest({"synthetic_configuration": "runtime-demo-v0"})
        private = Ed25519PrivateKey.generate()
        private_bytes = private.private_bytes(
            serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
            serialization.NoEncryption())
        public = private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        credential = secrets.token_urlsafe(32)
        provider_db = root / "provider.sqlite"
        config = {
            "db_path": str(provider_db), "context": context,
            "private_key_hex": private_bytes.hex(), "credential": credential,
            "configuration_digest": configuration, "recovery_epoch": 1,
            "initial_balances": {"synthetic-source": "1000000", "synthetic-beneficiary": "0"},
            "drop_after_commit": True,
        }
        config_path = root / "provider-config.json"
        descriptor = os.open(config_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(canonical_json(config))
        command = [sys.executable, str(Path(__file__).with_name("payment_runtime.py")),
                   "provider", "--config", str(config_path)]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                if not selector.select(timeout=10):
                    raise RuntimeError("mock_provider_startup_timeout")
                line = process.stdout.readline()
            if not line:
                raise RuntimeError("mock_provider_startup_failed")
            ready = json.loads(line)
            if ready.get("event") != "ready":
                raise RuntimeError("mock_provider_ready_message")
            adapter = Adapter(root / "client.sqlite", ready["endpoint"], context,
                              public, credential, configuration, 1)
            request = make_request(context, operation_id="synthetic-operation-A",
                idempotency_key="synthetic-idempotency-A", configuration_digest=configuration,
                recovery_epoch=1, source_account="synthetic-source",
                beneficiary="synthetic-beneficiary", amount_minor="12500")
            first = adapter.submit(request)
            after_first = provider_snapshot(provider_db)
            repeated = adapter.submit(request)
            after_repeat = provider_snapshot(provider_db)
            reconciled = adapter.reconcile(request)
            after_reconcile = provider_snapshot(provider_db)
            stable = adapter.submit(request)
            final = provider_snapshot(provider_db)
            valid = (
                first["state"] == repeated["state"] == "UNKNOWN"
                and reconciled["state"] == stable["state"] == "SETTLED"
                and all(x["post_attempts"] == 1 and x["effects"] == 1
                        for x in (after_first, after_repeat, after_reconcile, final))
                and after_first["lookup_attempts"] == after_repeat["lookup_attempts"] == 0
                and after_reconcile["lookup_attempts"] == final["lookup_attempts"] == 1
                and final["balances"] == {"synthetic-source": "987500", "synthetic-beneficiary": "12500"}
                and reconciled["receipt_bytes"] == stable["receipt_bytes"]
                and reconciled["receipt_bytes"] is not None
            )
            if not valid:
                raise RuntimeError("mock_runtime_demonstration_failed")
            summary = {
                "schema": "synthetic-payment-runtime-demo-v0", "synthetic": True,
                "request": request, "provider_public_key_hex": public.hex(),
                "key_provenance": "ephemeral_key_from_this_trusted_demo_controller_not_independent_provenance",
                "business_authorization_verified": False, "automatic_retry": False,
                "steps": [
                    {"stage": "provider_committed_response_lost", "result": public_result(first),
                     "provider": after_first},
                    {"stage": "same_request_repeated_no_resend", "result": public_result(repeated),
                     "provider": after_repeat},
                    {"stage": "read_only_reconciliation", "result": public_result(reconciled),
                     "provider": after_reconcile},
                    {"stage": "stored_result_no_provider_call", "result": public_result(stable),
                     "provider": final},
                ],
                "limitations": [
                    "local_mock_balances_only_no_real_funds_or_bank",
                    "caller_business_authorization_not_implemented",
                    "no_independent_collector_or_external_anchor",
                    "same_operator_and_uid_not_security_isolation",
                    "no_storage_rollback_or_power_loss_guarantee",
                    "not_VAP_conformance_or_generic_exactly_once",
                ],
            }
            return summary, reconciled["receipt_bytes"]
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Directory for public summary and original signed receipt")
    args = parser.parse_args()
    summary, receipt = run_demo()
    if args.output is not None:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "summary.json").write_bytes(canonical_json(summary) + b"\n")
        (args.output / "provider-receipt.json").write_bytes(receipt)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
