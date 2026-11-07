#!/usr/bin/env python3
"""Public, synthetic cloud-evidence fixtures; never use these keys for real data.

The keys below are reproducible PUBLIC TEST MATERIAL, not provider keys.  Every
role is controlled by this same fixture author.  No network or Azure operation is
performed.  Fixture construction deliberately does not import the implementation
under test: canonicalization, byte commitments and signatures are made here.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


BUNDLE_SCHEMA = "experimental-cloud-evidence-bundle-v0"
RECORD_SCHEMA = "experimental-cloud-evidence-record-v0"
SIGNING_DOMAIN = b"VSO experimental cloud evidence v0\x00"
SIGNIN_ADAPTER = "azure-service-principal-signin-subset-v0"
KEYVAULT_ADAPTER = "azure-key-vault-audit-subset-v0"

# Fixed synthetic time and reserved .invalid/TEST-NET names are not incident data.
BASE = 1_794_000_000
TENANT_A = "11111111-1111-4111-8111-111111111111"
TENANT_B = "22222222-2222-4222-8222-222222222222"
HOME_TENANT = "33333333-3333-4333-8333-333333333333"
WORKSPACE = "44444444-4444-4444-8444-444444444444"
PRINCIPAL_A = "55555555-5555-4555-8555-555555555555"
PRINCIPAL_B = "66666666-6666-4666-8666-666666666666"
APP_ID = "77777777-7777-4777-8777-777777777777"
RESOURCE_PRINCIPAL = "88888888-8888-4888-8888-888888888888"
RESOURCE_IDENTITY = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
CREDENTIAL_ID = "99999999-9999-4999-8999-999999999999"
VAULT_A = "/subscriptions/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa/resourceGroups/synthetic/providers/Microsoft.KeyVault/vaults/fixture-a"
VAULT_B = "/subscriptions/bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb/resourceGroups/synthetic/providers/Microsoft.KeyVault/vaults/fixture-b"
SECRET_URI = "https://fixture-a.invalid/secrets/synthetic-secret/version-1?api-version=7.4"
OTHER_SECRET_URI = "https://fixture-a.invalid/secrets/another-synthetic-secret/version-2?api-version=7.4"
AUDIENCE = "https://vault.azure.net"
OPERATION_ID = "synthetic-operation-A"
ATTEMPT_ID = "synthetic-attempt-1"

ROLES = (
    "collector", "policy_authority", "operation_observer",
    "control_observer", "source_reviewer",
)
KEY_IDS = {role: "PUBLIC-SYNTHETIC-KEY-" + role for role in ROLES}
ISSUERS = {role: "synthetic-fixture/" + role for role in ROLES}
PUBLIC_TEST_SEEDS = {
    role: hashlib.sha256(("PUBLIC SYNTHETIC CLOUD EVIDENCE TEST KEY / " + role).encode()).digest()
    for role in ROLES
}


def canonical(value):
    """Independent encoding of the experiment's documented JSON subset."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def bytes_hash(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def object_hash(value):
    return bytes_hash(canonical(value))


def public_key(role):
    return Ed25519PrivateKey.from_private_bytes(PUBLIC_TEST_SEEDS[role]).public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()


def sign_payload(payload, role, *, key_id=None):
    key_id = KEY_IDS[role] if key_id is None else key_id
    signed = {"key_id": key_id, "payload": copy.deepcopy(payload)}
    key = Ed25519PrivateKey.from_private_bytes(PUBLIC_TEST_SEEDS[role])
    return {**signed, "signature": key.sign(SIGNING_DOMAIN + canonical(signed)).hex()}


def iso(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def reference(record_id):
    # This marker exists only in fixture construction; no marker reaches the core.
    return {"$fixture_ref": record_id}


def native_body(adapter, raw):
    text = json.dumps(raw, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    return {"adapter": adapter, "raw": text, "raw_sha256": bytes_hash(text.encode()),
            "claimed_normalized": None}


def make_record(kind, role, record_id, body, at, *, tenant=TENANT_A, resource=VAULT_A,
                available=None, received=None):
    return {"signing_role": role, "payload": {
        "schema": RECORD_SCHEMA, "record_id": record_id, "issuer": ISSUERS[role],
        "role": role, "tenant_id": tenant, "resource_id": resource,
        "event_time": at, "available_time": at + 1 if available is None else available,
        "received_time": at + 2 if received is None else received,
        "kind": kind, "body": copy.deepcopy(body),
    }}


def trust_config():
    return {"keys": {KEY_IDS[role]: {
        "public_key": public_key(role),
        "grants": [{"issuer": ISSUERS[role], "role": role,
                    "tenant_id": TENANT_A, "resource_id": VAULT_A,
                    "valid_from": BASE - 100, "valid_until": BASE + 1000}],
    } for role in ROLES}}


def signin_raw():
    return {
        "Id": "synthetic-signin-event-1", "AADTenantId": TENANT_A,
        "TenantId": WORKSPACE, "AppId": APP_ID, "AppOwnerTenantId": HOME_TENANT,
        "ResourceOwnerTenantId": TENANT_A, "ServicePrincipalId": PRINCIPAL_A,
        "ResourceIdentity": RESOURCE_IDENTITY,
        "ResourceServicePrincipalId": RESOURCE_PRINCIPAL,
        "ServicePrincipalCredentialKeyId": CREDENTIAL_ID,
        "UniqueTokenIdentifier": "synthetic-nonsecret-token-identifier-1",
        "ResultType": "Success", "ResultSignature": "0",
        "CreatedDateTime": iso(BASE + 10), "TimeGenerated": iso(BASE + 10),
        "OperationVersion": "synthetic-signin-schema-version",
        "CorrelationId": "synthetic-client-correlation-1", "IPAddress": "192.0.2.10",
        "UserAgent": "synthetic-fixture-client/1.0",
    }


def resource_raw():
    return {
        "time": iso(BASE + 20), "resourceId": VAULT_A,
        "operationName": "SecretGet", "operationVersion": "7.4",
        "resultType": "Success", "resultSignature": "OK",
        "correlationId": "synthetic-client-correlation-1",
        "callerIpAddress": "192.0.2.10",
        "identity": {"claim": {"appid": APP_ID, "oid": PRINCIPAL_A, "tid": TENANT_A}},
        "properties": {"requestUri": SECRET_URI, "httpStatusCode": 200},
    }


def positive_case():
    """Timely prerequisites and a later retrospective resource observation."""
    scope = {
        "operation_id": OPERATION_ID, "attempt_id": ATTEMPT_ID,
        "tenant_id": TENANT_A, "principal_id": PRINCIPAL_A, "resource_id": VAULT_A,
        "audience": AUDIENCE, "action": "SecretGet", "request_uri": SECRET_URI,
        "sign_in_resource": {"resource_identity": RESOURCE_IDENTITY,
                             "resource_tenant_id": TENANT_A,
                             "resource_principal_id": RESOURCE_PRINCIPAL},
        "action_time": BASE + 20, "interval_start": BASE, "interval_end": BASE + 60,
        "expected_record_ids": ["signin-1", "permission-1", "resource-1", "binding-1"],
        "prerequisite_record_ids": ["signin-1", "permission-1"],
    }
    permission = {
        "operation_id": OPERATION_ID, "attempt_id": ATTEMPT_ID,
        "principal_id": PRINCIPAL_A, "audience": AUDIENCE,
        "action": "SecretGet", "request_uri": SECRET_URI,
        "decision": "allow", "valid_from": BASE, "valid_until": BASE + 120,
    }
    binding = {
        "operation_id": OPERATION_ID, "attempt_id": ATTEMPT_ID,
        "principal_id": PRINCIPAL_A, "audience": AUDIENCE,
        "action": "SecretGet", "request_uri": SECRET_URI,
        "method": "GET", "api_version": "7.4", "api_plane": "data",
        "sign_in_ref": reference("signin-1"), "resource_ref": reference("resource-1"),
    }
    collection = {
        "interval_start": BASE, "interval_end": BASE + 60,
        "record_refs": {name: reference(name) for name in scope["expected_record_ids"]},
        "closed": True, "gaps": [],
    }
    records = [
        make_record("native", "collector", "signin-1", native_body(SIGNIN_ADAPTER, signin_raw()), BASE + 10),
        make_record("permission", "policy_authority", "permission-1", permission, BASE + 15,
                    available=BASE + 15, received=BASE + 16),
        make_record("native", "collector", "resource-1", native_body(KEYVAULT_ADAPTER, resource_raw()), BASE + 20),
        make_record("binding", "operation_observer", "binding-1", binding, BASE + 21),
        make_record("collection", "collector", "collection-1", collection, BASE + 70),
    ]
    return {"case_id": "CE-01", "description": "Exact scoped operation with timely prerequisites and later resource evidence",
            "records": records, "trust": trust_config(), "scope": scope,
            "evaluation_time": BASE + 100,
            "expected": {name: "supported" for name in (
                "integrity", "provenance", "authentication", "authority", "operation",
                "association", "timing", "coverage")}}


def payload(case, record_id):
    return next(record["payload"] for record in case["records"]
                if record["payload"]["record_id"] == record_id)


def change_native(case, record_id, change, *, refresh_commitment=True):
    body = payload(case, record_id)["body"]
    value = json.loads(body["raw"])
    change(value)
    body["raw"] = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if refresh_commitment:
        body["raw_sha256"] = bytes_hash(body["raw"].encode())


def drop_record(case, record_id):
    """Keep declared requirements, remove only the supplied record and its references."""
    case["records"] = [record for record in case["records"]
                       if record["payload"]["record_id"] != record_id]
    for record in case["records"]:
        item = record["payload"]
        if item["kind"] == "collection":
            item["body"]["record_refs"].pop(record_id, None)
        if item["kind"] == "binding":
            for name in ("sign_in_ref", "resource_ref"):
                if item["body"][name] == reference(record_id):
                    item["body"][name] = None


def seal_bundle(case):
    """Resolve fixture-only refs, then sign with public test keys independently."""
    records = {item["payload"]["record_id"]: item for item in case["records"]}
    if len(records) != len(case["records"]):
        raise ValueError("fixture builder requires unique record IDs")
    sealed, visiting = {}, set()

    def resolve(value):
        if isinstance(value, dict):
            if set(value) == {"$fixture_ref"}:
                return object_hash(seal(value["$fixture_ref"]))
            return {name: resolve(item) for name, item in value.items()}
        if isinstance(value, list):
            return [resolve(item) for item in value]
        return copy.deepcopy(value)

    def seal(record_id):
        if record_id in sealed:
            return sealed[record_id]
        if record_id in visiting:
            raise ValueError("cyclic fixture references")
        visiting.add(record_id)
        record = records[record_id]
        sealed[record_id] = sign_payload(resolve(record["payload"]), record["signing_role"])
        visiting.remove(record_id)
        return sealed[record_id]

    return {"schema": BUNDLE_SCHEMA, "synthetic": True,
            "records": [seal(item["payload"]["record_id"]) for item in case["records"]]}


def acceptance_cases():
    """One representative fixture for each independently specified CE distinction."""
    cases = [positive_case()]

    c = positive_case()
    c.update(case_id="CE-02", description="Token/sign-in success without resource or policy evidence")
    for record_id in ("permission-1", "resource-1", "binding-1"):
        drop_record(c, record_id)
    c["expected"] = {"authentication": "supported", "authority": "unresolved",
                     "operation": "unresolved", "association": "unresolved", "coverage": "unresolved"}
    cases.append(c)

    c = positive_case()
    c.update(case_id="CE-03", description="Same AppId in a different tenant cannot support the requested principal link")
    p = payload(c, "signin-1")
    p.update(tenant_id=TENANT_B, resource_id=VAULT_B)
    change_native(c, "signin-1", lambda raw: raw.update(
        AADTenantId=TENANT_B, ResourceOwnerTenantId=TENANT_B,
        ServicePrincipalId=PRINCIPAL_B))
    c["trust"]["keys"][KEY_IDS["collector"]]["grants"].append({
        "issuer": ISSUERS["collector"], "role": "collector", "tenant_id": TENANT_B,
        "resource_id": VAULT_B, "valid_from": BASE - 100, "valid_until": BASE + 1000,
    })
    c["expected"] = {"integrity": "supported", "association": "contradicted"}
    cases.append(c)

    c = positive_case()
    c.update(case_id="CE-04", description="Valid signature under a key lacking this tenant's authority")
    c["trust"]["keys"][KEY_IDS["policy_authority"]]["grants"][0]["tenant_id"] = TENANT_B
    c["expected"] = {"integrity": "supported", "provenance": "unresolved", "authority": "unresolved"}
    cases.append(c)

    c = positive_case()
    c.update(case_id="CE-05", description="Matching client correlation, IP and times without a supported binding")
    drop_record(c, "binding-1")
    c["expected"] = {"integrity": "supported", "association": "unresolved", "coverage": "unresolved"}
    cases.append(c)

    c = positive_case()
    c.update(case_id="CE-06", description="Successful control-plane vault metadata is not the requested SecretGet")
    change_native(c, "resource-1", lambda raw: raw.update(
        operationName="VaultGet", operationVersion="2023-07-01",
        properties={"requestUri": "https://management.invalid" + VAULT_A + "?api-version=2023-07-01",
                    "httpStatusCode": 200}))
    c["expected"] = {"integrity": "supported", "operation": "contradicted", "association": "contradicted"}
    cases.append(c)

    c = positive_case()
    c.update(case_id="CE-07", description="Earlier policy event with late availability and collection")
    payload(c, "permission-1").update(available_time=BASE + 35, received_time=BASE + 40)
    c["expected"] = {"integrity": "supported", "operation": "supported", "timing": "contradicted"}
    cases.append(c)

    c = positive_case()
    c.update(case_id="CE-08", description="Failed original request remains separate from an altered successful retry")
    c["scope"].update(attempt_id="synthetic-attempt-2", action_time=BASE + 40)
    payload(c, "permission-1")["body"]["attempt_id"] = "synthetic-attempt-2"
    payload(c, "resource-1").update(event_time=BASE + 40, available_time=BASE + 41, received_time=BASE + 42)
    change_native(c, "resource-1", lambda raw: raw.update(time=iso(BASE + 40)))
    payload(c, "binding-1").update(event_time=BASE + 41, available_time=BASE + 42, received_time=BASE + 43)
    payload(c, "binding-1")["body"]["attempt_id"] = "synthetic-attempt-2"
    old_uri = SECRET_URI.replace("api-version=7.4", "api-version=7.3")
    failed_raw = resource_raw()
    failed_raw.update(operationVersion="7.3", resultType="Failure", resultSignature="400",
                      properties={"requestUri": old_uri, "httpStatusCode": 400})
    old_binding = copy.deepcopy(payload(c, "binding-1")["body"])
    old_binding.update(attempt_id=ATTEMPT_ID, request_uri=old_uri, method="POST", api_version="7.3",
                       resource_ref=reference("resource-failed"))
    c["records"].extend([
        make_record("native", "collector", "resource-failed", native_body(KEYVAULT_ADAPTER, failed_raw), BASE + 20),
        make_record("binding", "operation_observer", "binding-failed", old_binding, BASE + 21),
    ])
    for name in ("resource-failed", "binding-failed"):
        c["scope"]["expected_record_ids"].append(name)
        payload(c, "collection-1")["body"]["record_refs"][name] = reference(name)
    c["expected"] = {"integrity": "supported", "operation": "supported", "association": "supported"}
    cases.append(c)

    c = positive_case()
    c.update(case_id="CE-09", description="Rotation and an incomplete observation window cannot establish containment")
    payload(c, "collection-1")["body"].update(closed=False, gaps=[
        "synthetic-token-lineage-not-collected", "synthetic-other-tenant-not-collected"])
    c["records"].append(make_record("control", "control_observer", "rotation-1", {
        "action": "rotate", "credential_id": CREDENTIAL_ID, "related_ref": reference("signin-1"),
    }, BASE + 50))
    c["expected"] = {"integrity": "supported", "operation": "supported", "coverage": "unresolved",
                     "global_containment": "unresolved"}
    cases.append(c)

    c = positive_case()
    c.update(case_id="CE-10", description="Dated source assessment revision preserves history without model telemetry")
    for name, at, label, previous in (
        ("assessment-v1", BASE + 30, "uncertain", None),
        ("assessment-v2", BASE + 50, "agentic", reference("assessment-v1")),
    ):
        c["records"].append(make_record("assessment", "source_reviewer", name, {
            "publisher": "Synthetic research publisher", "source_url": "https://research.invalid/fixture",
            "version": name, "published_at": BASE + 5, "updated_at": at,
            "assessment": label, "basis": "Synthetic source judgment; no direct attacker-model telemetry",
            "supersedes": previous,
        }, at))
    c["expected"] = {"integrity": "supported", "assessment": "supported"}
    cases.append(c)
    return cases


def run_cases(verify):
    results = []
    for case in acceptance_cases():
        report = verify(seal_bundle(case), copy.deepcopy(case["trust"]),
                        scope=copy.deepcopy(case["scope"]), evaluation_time=case["evaluation_time"])
        expected = {"external_exfiltration": "unresolved", "global_containment": "unresolved",
                    "ai_orchestration": "unresolved",
                    **case["expected"]}
        mismatches = []
        for name, wanted in expected.items():
            got = report.get("claims", {}).get(name, {}).get("status")
            if got != wanted:
                mismatches.append({"claim": name, "expected": wanted, "actual": got})
        results.append({"case_id": case["case_id"], "description": case["description"],
                        "expected_claims": expected, "expectation_mismatches": mismatches,
                        "actual_report": report})
    return {"schema": "experimental-cloud-evidence-fixture-results-v0", "synthetic": True,
            "public_test_keys": True, "same_operator": True, "live_cloud_calls": 0,
            "independent_reproduction_established": False, "prevention_established": False,
            "acceptance_cases_executed": len(results),
            "expectation_mismatch_count": sum(len(item["expectation_mismatches"]) for item in results),
            "results": results}


def main():
    # The implementation is used only at execution time, not to build expected data.
    from cloud_evidence import verify_bundle
    report = run_cases(verify_bundle)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))
    return 1 if report["expectation_mismatch_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
