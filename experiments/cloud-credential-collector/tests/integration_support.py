"""Synthetic caller policy/context around genuinely collected native envelopes.

The collector does not manufacture these policy, operation or collection
statements. Public fixture keys belong to this same test operator. The existing
offline verifier is unchanged and receives caller-pinned trust separately.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

from collector_support import (
    KEY_ID, KEYVAULT_ADAPTER, PRINCIPAL, PUBLIC_TEST_KEY, RESOURCE_IDENTITY,
    RESOURCE_PRINCIPAL, ROOT, SECRET_URI, SIGNIN_ADAPTER, TENANT, VAULT,
    canonical, context, digest, private_write, raw_record,
)


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT.parent / "cloud-credential-evidence" / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError("synthetic integration dependency unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def bridge_scenario(h, *, resource_request_id="request-1"):
    """Collect/export native records and evaluate a separately signed caller bundle."""
    evidence = _load("_local_collector_test_evidence", "cloud_evidence.py")
    fixture = _load("_local_collector_test_evidence_fixtures", "fixtures.py")
    signin_file = private_write(h.root / "signin-source.raw", raw_record(SIGNIN_ADAPTER, at=h.source_at - 10))
    signin_receipt = h.collect("signin-1", path=signin_file, source_context=context(SIGNIN_ADAPTER))
    with h.open() as store:
        resource_receipt = store.get_receipt(resource_request_id)
        resource_path = h.root / "collected-resource-native.json"
        signin_path = h.root / "collected-signin-native.json"
        resource_summary = store.export_native(resource_request_id, resource_path)
        signin_summary = store.export_native("signin-1", signin_path)
    resource_envelope = json.loads(resource_path.read_text(encoding="utf-8"))
    signin_envelope = json.loads(signin_path.read_text(encoding="utf-8"))
    last_receipt = max(resource_receipt["payload"]["received_time"], signin_receipt["payload"]["received_time"])
    action_time = h.source_at
    operation_id, attempt_id = "synthetic-collected-operation", "synthetic-collected-attempt"
    audience = "https://vault.azure.net"
    permission = fixture.make_record("permission", "policy_authority", "synthetic-policy", {
        "operation_id": operation_id, "attempt_id": attempt_id, "principal_id": PRINCIPAL,
        "audience": audience, "action": "SecretGet", "request_uri": SECRET_URI,
        "decision": "allow", "valid_from": action_time - 100, "valid_until": last_receipt + 100,
    }, action_time - 5, available=action_time - 5, received=action_time - 4)
    permission_envelope = fixture.sign_payload(permission["payload"], "policy_authority")
    binding = fixture.make_record("binding", "operation_observer", "synthetic-binding", {
        "operation_id": operation_id, "attempt_id": attempt_id, "principal_id": PRINCIPAL,
        "audience": audience, "action": "SecretGet", "request_uri": SECRET_URI,
        "method": "GET", "api_version": "7.4", "api_plane": "data",
        "sign_in_ref": digest(canonical(signin_envelope)),
        "resource_ref": digest(canonical(resource_envelope)),
    }, last_receipt + 1, available=last_receipt + 1, received=last_receipt + 1)
    binding_envelope = fixture.sign_payload(binding["payload"], "operation_observer")
    declared = [signin_envelope, permission_envelope, resource_envelope, binding_envelope]
    expected = [item["payload"]["record_id"] for item in declared]
    interval_start, interval_end = action_time - 20, last_receipt + 2
    collection = fixture.make_record("collection", "collector", "synthetic-collection-statement", {
        "interval_start": interval_start, "interval_end": interval_end,
        "record_refs": {item["payload"]["record_id"]: digest(canonical(item)) for item in declared},
        "closed": True, "gaps": [],
    }, last_receipt + 3, available=last_receipt + 3, received=last_receipt + 3)
    collection_envelope = fixture.sign_payload(collection["payload"], "collector")
    scope = {
        "operation_id": operation_id, "attempt_id": attempt_id, "tenant_id": TENANT,
        "principal_id": PRINCIPAL, "resource_id": VAULT, "audience": audience,
        "action": "SecretGet", "request_uri": SECRET_URI,
        "sign_in_resource": {"resource_identity": RESOURCE_IDENTITY, "resource_tenant_id": TENANT,
                             "resource_principal_id": RESOURCE_PRINCIPAL},
        "action_time": action_time, "interval_start": interval_start, "interval_end": interval_end,
        "expected_record_ids": expected,
        "prerequisite_record_ids": [signin_envelope["payload"]["record_id"], "synthetic-policy"],
    }
    trust = fixture.trust_config()
    for configuration in trust["keys"].values():
        for grant in configuration["grants"]:
            grant.update(valid_from=action_time - 1000, valid_until=last_receipt + 1000)
    trust["keys"][KEY_ID] = {"public_key": PUBLIC_TEST_KEY.hex(), "grants": [{
        "issuer": context()["issuer"], "role": "collector", "tenant_id": TENANT, "resource_id": VAULT,
        "valid_from": action_time - 1000, "valid_until": last_receipt + 1000,
    }]}
    bundle = {"schema": "experimental-cloud-evidence-bundle-v0", "synthetic": True,
              "records": [*declared, collection_envelope]}
    horizon = last_receipt + 4
    report = evidence.verify_bundle(bundle, trust, scope=scope, evaluation_time=horizon)
    return {"report": report, "scope": scope, "trust": trust,
            "native_envelopes": {"signin": signin_envelope, "resource": resource_envelope},
            "receipts": {"signin": signin_receipt, "resource": resource_receipt},
            "export_summaries": {"signin": signin_summary, "resource": resource_summary}}
