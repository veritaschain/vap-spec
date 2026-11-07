"""Offline, synthetic cloud evidence checks; no Azure connection or control.

This deliberately restricted experiment is neither an Azure export parser nor a
VAP conformance verifier. Collector signatures cover supplied statements, not
Microsoft's origin, honest collection, independent custody or universal scope.
The caller supplies every trust grant, review boundary and evaluation horizon.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey,
)


BUNDLE_SCHEMA = "experimental-cloud-evidence-bundle-v0"
RECORD_SCHEMA = "experimental-cloud-evidence-record-v0"
RESULT_SCHEMA = "experimental-cloud-evidence-result-v0"
SIGNIN_ADAPTER = "azure-service-principal-signin-subset-v0"
KEYVAULT_ADAPTER = "azure-key-vault-audit-subset-v0"
SIGNING_DOMAIN = b"VSO experimental cloud evidence v0\x00"
MAX_INTEGER = 9007199254740991
MAX_DOCUMENT = 1048576
TICKS = 10000000
HASH_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")
TIME_RE = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,7}))?Z\Z")
ROLES = {
    "native": "collector", "permission": "policy_authority",
    "binding": "operation_observer", "collection": "collector",
    "control": "control_observer", "assessment": "source_reviewer",
}
CLAIMS = (
    "integrity", "provenance", "authentication", "authority", "operation",
    "association", "timing", "coverage", "assessment",
    "temporal_consistency",
    "external_exfiltration", "global_containment", "ai_orchestration",
)


def _json_value(value: Any, depth: int = 0) -> None:
    if depth > 32:
        raise ValueError("json_nesting_limit")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > MAX_INTEGER:
            raise ValueError("unsafe_json_integer")
        return
    if type(value) is str:
        if len(value) > 65536:
            raise ValueError("json_string_limit")
        if unicodedata.normalize("NFC", value) != value:
            raise ValueError("non_nfc_string")
        value.encode("utf-8", errors="strict")
        return
    if type(value) is list:
        if len(value) > 256:
            raise ValueError("json_array_limit")
        for item in value:
            _json_value(item, depth + 1)
        return
    if type(value) is dict:
        if len(value) > 256:
            raise ValueError("json_object_limit")
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("non_string_json_key")
            _json_value(key, depth + 1)
            _json_value(item, depth + 1)
        return
    raise ValueError("unsupported_json_type")


def canonical_json(value: Any) -> bytes:
    """Bounded experiment encoding, not RFC 8785 or Azure's original bytes."""
    _json_value(value)
    result = json.dumps(value, ensure_ascii=False, sort_keys=True,
                        separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(result) > MAX_DOCUMENT:
        raise ValueError("json_document_limit")
    return result


def _pairs(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def _integer_token(value: str) -> int:
    if value == "-0":
        raise ValueError("ambiguous_json_integer")
    number = int(value)
    if abs(number) > MAX_INTEGER:
        raise ValueError("unsafe_json_integer")
    return number


def _no_float(_: str) -> None:
    raise ValueError("non_integer_json_number")


def load_json(raw: str | bytes) -> Any:
    if type(raw) not in (str, bytes) or len(raw) > MAX_DOCUMENT:
        raise ValueError("json_input_type_or_size")
    try:
        if type(raw) is bytes:
            raw = raw.decode("utf-8", errors="strict")
        value = json.loads(raw, object_pairs_hook=_pairs, parse_int=_integer_token,
                           parse_float=_no_float, parse_constant=_no_float)
        canonical_json(value)
        return value
    except RecursionError as exc:
        raise ValueError("json_nesting_limit") from exc


def bytes_digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest(value: Any) -> str:
    return bytes_digest(canonical_json(value))


def sign_envelope(payload: dict, key_id: str, private_key: Ed25519PrivateKey) -> dict:
    """Convenience for PUBLIC synthetic fixtures, never a provider attestation."""
    signed = {"key_id": key_id, "payload": load_json(canonical_json(payload))}
    return {**signed, "signature": private_key.sign(
        SIGNING_DOMAIN + canonical_json(signed)).hex()}


def _text(value: Any) -> bool:
    return type(value) is str and 0 < len(value) <= 4096


def _integer(value: Any) -> bool:
    return type(value) is int and 0 <= value <= MAX_INTEGER


def _hash(value: Any) -> bool:
    return type(value) is str and HASH_RE.fullmatch(value) is not None


def _optional(check):
    return lambda value: value is None or check(value)


def _strings(value: Any) -> bool:
    return (type(value) is list and len(value) <= 128
            and all(_text(item) for item in value) and len(value) == len(set(value)))


def _shape(value: Any, schema: dict) -> bool:
    return (type(value) is dict and set(value) == set(schema)
            and all(check(value[key]) for key, check in schema.items()))


def _require_shape(value: Any, schema: dict, code: str) -> None:
    if not _shape(value, schema):
        raise ValueError(code)


def _ticks(value: str) -> int:
    """UTC source precision is retained through seven fractional digits."""
    match = TIME_RE.fullmatch(value)
    if match is None:
        raise ValueError("unsupported_source_timestamp")
    try:
        instant = datetime.strptime(match[1], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        delta = instant - datetime(1970, 1, 1, tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError("invalid_source_timestamp") from exc
    seconds = delta.days * 86400 + delta.seconds
    if seconds < 0:
        raise ValueError("unsupported_source_timestamp")
    return seconds * TICKS + int((match[2] or "").ljust(7, "0"))


def _native_text(raw: dict, key: str) -> str | None:
    value = raw.get(key)
    if value == "":
        return None
    if value is not None and not _text(value):
        raise ValueError("native_text_field_type")
    return value


def _native_time(raw: dict, key: str) -> str | None:
    value = _native_text(raw, key)
    if value is not None:
        _ticks(value)
    return value


def _http_code(value: Any) -> int | None:
    if value is None:
        return None
    if type(value) is int and 100 <= value <= 599:
        return value
    if type(value) is str and re.fullmatch(r"[1-5][0-9]{2}", value):
        return int(value)
    if type(value) is str:
        label = re.sub(r"[ _-]", "", value).casefold()
        for status in HTTPStatus:
            if label in (status.name.replace("_", "").casefold(),
                         status.phrase.replace(" ", "").casefold()):
                return int(status)
    return None


def _claim_alias(claim: dict, short: str, long: str) -> tuple[str | None, bool]:
    a, b = _native_text(claim, short), _native_text(claim, long)
    return a if a is not None else b, a is not None and b is not None and a != b


def _uri_versions(uri: str | None) -> list[str]:
    if uri is None:
        return []
    try:
        return [value for key, value in parse_qsl(urlsplit(uri).query, keep_blank_values=True)
                if key == "api-version"]
    except ValueError as exc:
        raise ValueError("native_request_uri_shape") from exc


def normalize_record(adapter: str, raw_text: str) -> dict:
    """Map a documented subset, preserving missingness and the source vocabulary.

    This function does not authenticate its input. verify_bundle checks the exact
    raw byte commitment before calling it and gates subsequent semantic use.
    Caller/request context is never used to fill a missing native field.
    """
    raw = load_json(raw_text)
    if type(raw) is not dict:
        raise ValueError("native_record_shape")
    if adapter not in (SIGNIN_ADAPTER, KEYVAULT_ADAPTER):
        raise ValueError("unknown_native_adapter")
    result = {key: None for key in (
        "native_id", "source_time", "generated_time", "tenant_id", "workspace_id",
        "app_id", "app_owner_tenant_id", "resource_tenant_id", "principal_id",
        "resource_principal_id", "resource_identity", "resource_id", "request_uri", "credential_id",
        "token_id", "correlation_id", "operation", "operation_version", "result_type",
        "result_signature", "http_status", "method", "api_plane",
        "source_table", "source_operation_name", "source_category",
    )}
    result.update(adapter=adapter, result="unknown", status_conflict=False,
                  identity_conflict=False, agent_field_present="Agent" in raw,
                  user_agent_field_present="UserAgent" in raw, source_kind_conflict=False,
                  request_version_conflict=False)
    if adapter == SIGNIN_ADAPTER:
        fields = {
            "native_id": "Id", "tenant_id": "AADTenantId", "workspace_id": "TenantId",
            "app_id": "AppId", "app_owner_tenant_id": "AppOwnerTenantId",
            "resource_tenant_id": "ResourceOwnerTenantId", "principal_id": "ServicePrincipalId",
            "resource_principal_id": "ResourceServicePrincipalId",
            "resource_identity": "ResourceIdentity",
            "credential_id": "ServicePrincipalCredentialKeyId", "token_id": "UniqueTokenIdentifier",
            "correlation_id": "CorrelationId", "operation_version": "OperationVersion",
            "result_type": "ResultType", "result_signature": "ResultSignature",
        }
        result.update({target: _native_text(raw, source) for target, source in fields.items()})
        result["source_time"] = _native_time(raw, "CreatedDateTime")
        result["generated_time"] = _native_time(raw, "TimeGenerated")
        result["operation"] = "sign_in"
        result["source_table"] = _native_text(raw, "Type")
        result["source_operation_name"] = _native_text(raw, "OperationName")
        result["source_kind_conflict"] = result["source_table"] not in (None, "AADServicePrincipalSignInLogs") \
            or result["source_operation_name"] not in (None, "Sign-in activity")
        known = {"Success": "success", "Failure": "failure"}
        result["result"] = known.get(result["result_type"], "unknown")
        code = result["result_signature"]
        if code is not None and re.fullmatch(r"[0-9]+", code):
            code_result = "success" if int(code) == 0 else "failure"
            if result["result"] != "unknown" and result["result"] != code_result:
                result["status_conflict"] = True
    else:
        identity = raw.get("identity", {})
        properties = raw.get("properties", {})
        if type(identity) is not dict or type(properties) is not dict:
            raise ValueError("native_object_field_type")
        claim = identity.get("claim", {})
        if type(claim) is not dict:
            raise ValueError("native_claim_shape")
        prefix = "http://schemas.microsoft.com/identity/claims/"
        principal, pc = _claim_alias(claim, "oid", prefix + "objectidentifier")
        tenant, tc = _claim_alias(claim, "tid", prefix + "tenantid")
        result.update(
            source_time=_native_time(raw, "time"), tenant_id=tenant,
            principal_id=principal, app_id=_native_text(claim, "appid"),
            resource_id=_native_text(raw, "resourceId"),
            request_uri=_native_text(properties, "requestUri"),
            correlation_id=_native_text(raw, "correlationId"),
            operation=_native_text(raw, "operationName"),
            operation_version=_native_text(raw, "operationVersion"),
            result_type=_native_text(raw, "resultType"),
            result_signature=_native_text(raw, "resultSignature"), identity_conflict=pc or tc,
            source_category=_native_text(raw, "category"),
        )
        result["source_kind_conflict"] = result["source_category"] not in (None, "AuditEvent")
        versions = _uri_versions(result["request_uri"])
        result["request_version_conflict"] = len(versions) > 1 or bool(versions) and (
            not versions[0] or result["operation_version"] is not None
            and versions[0] != result["operation_version"])
        property_code = properties.get("httpStatusCode")
        if property_code is not None and _http_code(property_code) is None:
            raise ValueError("native_http_status_type")
        signature_code = _http_code(result["result_signature"])
        result["http_status"] = _http_code(property_code)
        if property_code is None:
            result["http_status"] = signature_code
        status = {"Success": "success", "Failure": "failure"}.get(result["result_type"], "unknown")
        channels = [status] if status != "unknown" else []
        for code in (signature_code, _http_code(property_code)):
            if code is not None and (200 <= code < 300 or code >= 400):
                channels.append("success" if code < 300 else "failure")
        result["status_conflict"] = len(set(channels)) > 1 or (
            signature_code is not None and property_code is not None
            and signature_code != _http_code(property_code))
        unknown_signature = result["result_signature"] is not None and signature_code is None
        result["result"] = channels[0] if channels and not unknown_signature else "unknown"
    if result["status_conflict"]:
        result["result"] = "unknown"
    return result


SIGNIN_RESOURCE_SCHEMA = {
    key: _text for key in ("resource_identity", "resource_tenant_id", "resource_principal_id")
}
SCOPE_SCHEMA = {
    **{key: _text for key in ("operation_id", "attempt_id", "tenant_id", "principal_id",
                              "resource_id", "audience", "action", "request_uri")},
    **{key: _integer for key in ("action_time", "interval_start", "interval_end")},
    "expected_record_ids": _strings, "prerequisite_record_ids": _strings,
    "sign_in_resource": lambda x: x is None or _shape(x, SIGNIN_RESOURCE_SCHEMA),
}
GRANT_SCHEMA = {
    **{key: _text for key in ("issuer", "role", "tenant_id", "resource_id")},
    "valid_from": _integer, "valid_until": _integer,
}
NATIVE_SCHEMA = {
    "adapter": lambda x: x in (SIGNIN_ADAPTER, KEYVAULT_ADAPTER),
    "raw": lambda x: type(x) is str and 0 < len(x) <= 65536,
    "raw_sha256": _hash, "claimed_normalized": lambda x: x is None or type(x) is dict,
}
PERMISSION_SCHEMA = {
    **{key: _text for key in ("operation_id", "attempt_id", "principal_id", "audience",
                              "action", "request_uri")},
    "decision": lambda x: x in ("allow", "deny"), "valid_from": _integer, "valid_until": _integer,
}
BINDING_SCHEMA = {
    **{key: _text for key in ("operation_id", "attempt_id", "principal_id", "audience",
                              "action", "request_uri")},
    "method": _optional(_text), "api_version": _optional(_text),
    "api_plane": lambda x: x in (None, "control", "data"),
    "sign_in_ref": _optional(_hash), "resource_ref": _optional(_hash),
}
COLLECTION_SCHEMA = {
    "interval_start": _integer, "interval_end": _integer,
    "record_refs": lambda x: type(x) is dict and all(_text(k) and _hash(v) for k, v in x.items()),
    "closed": lambda x: type(x) is bool, "gaps": _strings,
}
CONTROL_SCHEMA = {
    "action": lambda x: x in ("rotate", "alert", "enforce"),
    "credential_id": _optional(_text), "related_ref": _optional(_hash),
}
ASSESSMENT_SCHEMA = {
    **{key: _text for key in ("publisher", "source_url", "version", "basis")},
    "published_at": _integer, "updated_at": _integer,
    "assessment": lambda x: x in ("uncertain", "agentic"), "supersedes": _optional(_hash),
}
BODY_SCHEMAS = {
    "native": NATIVE_SCHEMA, "permission": PERMISSION_SCHEMA, "binding": BINDING_SCHEMA,
    "collection": COLLECTION_SCHEMA, "control": CONTROL_SCHEMA, "assessment": ASSESSMENT_SCHEMA,
}
PAYLOAD_SCHEMA = {
    "schema": lambda x: x == RECORD_SCHEMA,
    **{key: _text for key in ("record_id", "issuer", "role", "tenant_id", "resource_id")},
    **{key: _optional(_integer) for key in ("event_time", "available_time", "received_time")},
    "kind": lambda x: type(x) is str and x in ROLES, "body": lambda x: type(x) is dict,
}


class Claim:
    def __init__(self) -> None:
        self.good: list[str] = []
        self.bad: list[str] = []
        self.missing: list[str] = []

    def add(self, status: str, reason: str) -> None:
        target = {"supported": self.good, "contradicted": self.bad, "unresolved": self.missing}[status]
        if reason not in target:
            target.append(reason)

    def report(self) -> dict:
        status = "contradicted" if self.bad else "unresolved" if self.missing or not self.good else "supported"
        return {"status": status, "reasons": self.bad + self.missing + self.good}


def _validate_inputs(bundle: Any, trust: Any, scope: Any, evaluation_time: Any) -> tuple:
    bundle, trust, scope = (load_json(canonical_json(x)) for x in (bundle, trust, scope))
    _require_shape(scope, SCOPE_SCHEMA, "scope_shape")
    if not _integer(evaluation_time) or scope["interval_start"] > scope["interval_end"]:
        raise ValueError("evaluation_time_or_scope_interval")
    if not scope["expected_record_ids"]:
        raise ValueError("empty_declared_record_set")
    if not set(scope["prerequisite_record_ids"]) <= set(scope["expected_record_ids"]):
        raise ValueError("prerequisite_outside_declared_record_set")
    _require_shape(bundle, {"schema": lambda x: x == BUNDLE_SCHEMA, "synthetic": lambda x: x is True,
                           "records": lambda x: type(x) is list and len(x) <= 128}, "bundle_shape")
    _require_shape(trust, {"keys": lambda x: type(x) is dict}, "trust_shape")
    keys = {}
    for key_id, config in trust["keys"].items():
        if not _text(key_id):
            raise ValueError("trust_key_id")
        _require_shape(config, {
            "public_key": lambda x: type(x) is str and re.fullmatch(r"[0-9a-f]{64}", x) is not None,
            "grants": lambda x: type(x) is list and len(x) <= 128,
        }, "trust_key_shape")
        for grant in config["grants"]:
            _require_shape(grant, GRANT_SCHEMA, "trust_grant_shape")
            if grant["valid_from"] > grant["valid_until"]:
                raise ValueError("trust_grant_interval")
        keys[key_id] = Ed25519PublicKey.from_public_bytes(bytes.fromhex(config["public_key"]))
    for envelope in bundle["records"]:
        _require_shape(envelope, {
            "key_id": _text, "payload": lambda x: type(x) is dict,
            "signature": lambda x: type(x) is str and re.fullmatch(r"[0-9a-f]{128}", x) is not None,
        }, "envelope_shape")
        payload = envelope["payload"]
        _require_shape(payload, PAYLOAD_SCHEMA, "payload_shape")
        _require_shape(payload["body"], BODY_SCHEMAS[payload["kind"]], "body_shape")
        if payload["kind"] != "native" and payload["event_time"] is None:
            raise ValueError("missing_statement_event_time")
    return bundle, trust, scope, keys


def _public_normalized(normalized: dict | None) -> dict | None:
    if normalized is None:
        return None
    result = dict(normalized)
    uri = result.pop("request_uri")
    result["request_uri_commitment"] = bytes_digest(uri.encode("utf-8")) if uri is not None else None
    # No raw body, retrieved contents, token bytes, query string or arbitrary Agent object is emitted.
    return result


def _record(envelope: dict, trust: dict, keys: dict, horizon: int) -> dict:
    payload, key_id = envelope["payload"], envelope["key_id"]
    state = {"envelope": envelope, "payload": payload, "ref": digest(envelope),
             "signature_status": "unresolved", "authority_status": "unresolved",
             "commitment_status": "supported", "temporal_status": "unresolved", "normalized": None,
             "reasons": [], "eligible": False, "scope_conflict": False}
    key = keys.get(key_id)
    if key is None:
        state["reasons"].append("unknown_key_material")
    else:
        signed = {"key_id": key_id, "payload": payload}
        try:
            key.verify(bytes.fromhex(envelope["signature"]), SIGNING_DOMAIN + canonical_json(signed))
            state["signature_status"] = "supported"
        except InvalidSignature:
            state["signature_status"] = "contradicted"
            state["reasons"].append("signature_mismatch")
    if payload["kind"] == "native":
        body = payload["body"]
        if bytes_digest(body["raw"].encode("utf-8")) != body["raw_sha256"]:
            state["commitment_status"] = "contradicted"
            state["reasons"].append("original_bytes_commitment_mismatch")
        else:
            normalized = normalize_record(body["adapter"], body["raw"])
            state["normalized"] = normalized
            if body["claimed_normalized"] is not None and body["claimed_normalized"] != normalized:
                state["commitment_status"] = "contradicted"
                state["reasons"].append("normalized_view_mismatch")
    received = payload["received_time"]
    if state["signature_status"] == "supported":
        grants = trust["keys"][key_id]["grants"]
        matching = [grant for grant in grants if all(grant[k] == payload[k]
                    for k in ("issuer", "role", "tenant_id", "resource_id"))]
        if payload["role"] != ROLES[payload["kind"]]:
            state["authority_status"] = "contradicted"
            state["reasons"].append("role_kind_mismatch")
        elif received is None:
            state["reasons"].append("grant_receipt_time_unknown")
        elif any(grant["valid_from"] <= received <= grant["valid_until"] for grant in matching):
            state["authority_status"] = "supported"
        else:
            state["reasons"].append("no_applicable_key_authority_grant")
    normalized = state["normalized"]
    if normalized is not None and state["signature_status"] == state["authority_status"] == "supported":
        for native_field, scope_field in (("tenant_id", "tenant_id"), ("resource_id", "resource_id")):
            if normalized[native_field] is not None and normalized[native_field] != payload[scope_field]:
                state["scope_conflict"] = True
                state["reasons"].append("native_" + native_field + "_scope_mismatch")
        if normalized["identity_conflict"]:
            state["scope_conflict"] = True
            state["reasons"].append("conflicting_native_identity_aliases")
        if normalized["source_kind_conflict"]:
            state["scope_conflict"] = True
            state["reasons"].append("native_adapter_discriminator_conflict")
    event, available = payload["event_time"], payload["available_time"]
    source_ticks = _event_ticks(state)
    generated_ticks = (_ticks(normalized["generated_time"]) if normalized is not None
                       and normalized["generated_time"] is not None else None)
    bad_order = (received is not None and (
        available is not None and available > received or
        event is not None and event > received or
        source_ticks is not None and source_ticks > received * TICKS or
        generated_ticks is not None and generated_ticks > received * TICKS)) or (
        source_ticks is not None and available is not None and source_ticks > available * TICKS)
    if bad_order:
        state["temporal_status"] = "contradicted"
        state["reasons"].append("inconsistent_observation_clock_order")
    elif source_ticks is not None and available is not None and received is not None:
        state["temporal_status"] = "supported"
    else:
        state["reasons"].append("source_availability_or_clock_unknown")
    future_source = normalized is not None and normalized["source_time"] is not None and _ticks(
        normalized["source_time"]) > horizon * TICKS
    if received is None:
        state["reasons"].append("receipt_time_unknown")
    elif (received > horizon or event is not None and event > horizon or future_source
          or available is not None and available > horizon):
        state["reasons"].append("after_evaluation_horizon")
        if state["temporal_status"] != "contradicted":
            state["temporal_status"] = "unresolved"
    else:
        state["eligible"] = (state["signature_status"] == state["authority_status"]
                             == state["commitment_status"] == "supported"
                             and not state["scope_conflict"] and not bad_order)
    return state


def _same_scope(state: dict, scope: dict) -> bool:
    return all(state["payload"][key] == scope[key] for key in ("tenant_id", "resource_id"))


def _event_ticks(state: dict) -> int | None:
    normalized = state["normalized"]
    if normalized is not None:
        return _ticks(normalized["source_time"]) if normalized["source_time"] is not None else None
    event = state["payload"]["event_time"]
    return event * TICKS if event is not None else None


def _seconds(ticks: int) -> str:
    sign = "-" if ticks < 0 else ""
    whole, fraction = divmod(abs(ticks), TICKS)
    return sign + str(whole) + ("." + f"{fraction:07d}".rstrip("0") if fraction else "")


def _reference_chronology(states: list[dict], scope: dict, claims: dict[str, Claim]) -> None:
    """Check exact supplied-envelope receipt order under the common-clock assumption.

    These are collector receipt assertions, not proof of source publication or
    provider event times. A contradictory reference does not erase its target.
    """
    refs = {state["ref"]: state for state in states}
    for state in states:
        state["individually_eligible"] = state["eligible"]
    for state in states:
        payload, body = state["payload"], state["payload"]["body"]
        if state["signature_status"] != "supported" or state["authority_status"] != "supported" \
                or state["commitment_status"] != "supported":
            continue
        if payload["kind"] == "binding":
            referenced, claim_name = (body["sign_in_ref"], body["resource_ref"]), "association"
        elif payload["kind"] == "collection":
            referenced, claim_name = body["record_refs"].values(), "coverage"
        elif payload["kind"] == "assessment":
            referenced, claim_name = (body["supersedes"],), "assessment"
        else:
            continue
        for ref in referenced:
            target = refs.get(ref)
            if target is None or target["signature_status"] != "supported" \
                    or target["authority_status"] != "supported" or target["commitment_status"] != "supported":
                continue
            target_receipt = target["payload"]["received_time"]
            referring_receipt = payload["received_time"]
            if target_receipt is not None and referring_receipt is not None and target_receipt > referring_receipt:
                state["temporal_status"] = "contradicted"
                state["eligible"] = False
                if "referenced_envelope_received_later" not in state["reasons"]:
                    state["reasons"].append("referenced_envelope_received_later")
                relevant = _same_scope(state, scope) and (payload["kind"] != "binding" or (
                    body["operation_id"] == scope["operation_id"] and body["attempt_id"] == scope["attempt_id"]))
                if relevant:
                    claims[claim_name].add("contradicted", "referenced_envelope_received_later")
                claims["temporal_consistency"].add("contradicted", "referenced_envelope_received_later")


def _identity(state: dict, scope: dict) -> tuple[str, str]:
    normalized = state["normalized"]
    if normalized is None:
        return "unresolved", "native_mapping_missing"
    if normalized["identity_conflict"]:
        return "contradicted", "conflicting_native_identity_aliases"
    for field in ("tenant_id", "principal_id"):
        if normalized[field] is not None and normalized[field] != scope[field]:
            return "contradicted", "native_identity_does_not_match_review_scope"
    if any(normalized[field] is None for field in ("tenant_id", "principal_id")):
        return "unresolved", "native_identity_missing"
    return "supported", "tenant_local_identity_matches"


def _operation_claim(state: dict, scope: dict, claim: Claim, binding: dict | None = None) -> None:
    normalized = state["normalized"]
    if normalized is None or normalized["adapter"] != KEYVAULT_ADAPTER:
        claim.add("unresolved", "resource_observation_missing")
        return
    identity_status, reason = _identity(state, scope)
    if identity_status != "supported":
        claim.add(identity_status, reason)
    bindings_complete = identity_status == "supported"
    for field in ("resource_id", "request_uri"):
        if normalized[field] is None:
            claim.add("unresolved", "native_exact_resource_binding_missing")
            bindings_complete = False
        elif normalized[field] != scope[field]:
            claim.add("contradicted", "native_exact_resource_binding_mismatch")
            bindings_complete = False
    observed = _event_ticks(state)
    if observed is None:
        claim.add("unresolved", "native_operation_time_unknown")
        bindings_complete = False
    elif not scope["interval_start"] * TICKS <= observed <= scope["interval_end"] * TICKS:
        claim.add("contradicted", "native_operation_outside_review_interval")
        bindings_complete = False
    if normalized["operation"] is None:
        claim.add("unresolved", "native_operation_unknown")
    elif normalized["operation"] != scope["action"]:
        claim.add("contradicted", "different_native_operation")
    elif normalized["status_conflict"]:
        claim.add("contradicted", "conflicting_native_result_channels")
    elif normalized["result"] == "failure":
        claim.add("contradicted", "source_reports_operation_failure")
    elif normalized["result"] == "unknown":
        claim.add("unresolved", "native_result_unknown")
    elif scope["action"] == "SecretGet" and normalized["http_status"] != 200:
        claim.add("unresolved", "secret_get_success_status_not_established")
    elif bindings_complete:
        claim.add("supported", "source_reports_exact_operation_success")
    if normalized["request_version_conflict"]:
        claim.add("contradicted", "request_uri_version_conflicts_with_native_version")
    if binding is not None:
        if normalized["operation_version"] is not None and binding["api_version"] is not None \
                and normalized["operation_version"] != binding["api_version"]:
            claim.add("contradicted", "observed_api_version_mismatch")
        if scope["action"] == "SecretGet" and binding["api_plane"] == "control":
            claim.add("contradicted", "control_plane_context_is_not_secret_read")
        if scope["action"] == "SecretGet" and binding["method"] not in (None, "GET"):
            claim.add("contradicted", "collector_method_contradicts_secret_get")


def _association_mapping(state: dict, body: dict, scope: dict, claim: Claim) -> None:
    normalized = state["normalized"]
    if normalized["adapter"] == SIGNIN_ADAPTER:
        expected = scope["sign_in_resource"]
        if expected is None:
            claim.add("unresolved", "caller_sign_in_resource_mapping_missing")
            return
        for field, value in expected.items():
            if normalized[field] is None:
                claim.add("unresolved", "native_sign_in_resource_binding_missing")
            elif normalized[field] != value:
                claim.add("contradicted", "native_sign_in_resource_mapping_mismatch")
        return
    for field, expected in (("resource_id", scope["resource_id"]),
                            ("request_uri", body["request_uri"]), ("operation", body["action"])):
        if normalized[field] is None:
            claim.add("unresolved", "native_request_correspondence_missing")
        elif normalized[field] != expected:
            claim.add("contradicted", "native_request_correspondence_mismatch")
    if normalized["operation_version"] is not None and body["api_version"] is not None \
            and normalized["operation_version"] != body["api_version"]:
        claim.add("contradicted", "observed_api_version_mismatch")
    if normalized["request_version_conflict"]:
        claim.add("contradicted", "request_uri_version_conflicts_with_native_version")
    if body["action"] == "SecretGet" and (
            body["method"] not in (None, "GET") or body["api_plane"] == "control"):
        claim.add("contradicted", "collector_context_contradicts_secret_get")


def _permission_observation(state: dict, observations: list[tuple[dict, dict]],
                            scope: dict, claim: Claim) -> None:
    payload, body = state["payload"], state["payload"]["body"]
    if not _same_scope(state, scope) or any(body[key] != scope[key] for key in (
            "principal_id", "audience", "action", "request_uri")):
        claim.add("contradicted", "permission_binding_mismatch")
        return
    if not observations:
        if (body["decision"] == "deny" and body["valid_from"] <= scope["action_time"] <= body["valid_until"]
                and payload["event_time"] <= scope["action_time"]):
            claim.add("contradicted", "explicit_operation_denial")
        else:
            claim.add("unresolved", "observed_operation_for_authority_missing")
        return
    for observed, binding in observations:
        status, reason = _identity(observed, scope)
        issues = Claim()
        if status != "supported":
            issues.add(status, reason)
        _association_mapping(observed, binding, scope, issues)
        if issues.bad:
            claim.add("contradicted", "observed_operation_does_not_match_permission")
            continue
        if issues.missing:
            claim.add("unresolved", "observed_operation_binding_for_authority_missing")
            continue
        event = _event_ticks(observed)
        if event is None:
            claim.add("unresolved", "observed_operation_time_for_authority_unknown")
        elif not scope["interval_start"] * TICKS <= event <= scope["interval_end"] * TICKS:
            claim.add("contradicted", "observed_operation_outside_review_interval")
        elif not body["valid_from"] * TICKS <= event <= body["valid_until"] * TICKS:
            claim.add("contradicted", "permission_not_valid_at_observed_operation")
        elif payload["event_time"] * TICKS > event:
            claim.add("contradicted", "permission_observed_after_operation")
        elif body["decision"] == "deny":
            claim.add("contradicted", "explicit_operation_denial")
        else:
            claim.add("supported", "scoped_permission_covers_observed_operation")


def _semantics(states: list[dict], scope: dict, claims: dict[str, Claim]) -> None:
    eligible = [state for state in states if state["eligible"]]
    refs = {state["ref"]: state for state in states}
    native = [state for state in eligible if state["payload"]["kind"] == "native"]
    bindings = [state for state in eligible if state["payload"]["kind"] == "binding"
                and state["payload"]["body"]["operation_id"] == scope["operation_id"]
                and state["payload"]["body"]["attempt_id"] == scope["attempt_id"]]
    linked_signins: list[dict] = []
    linked_resources: list[tuple[dict, dict]] = []
    binding_pairs = set()
    for state in bindings:
        body = state["payload"]["body"]
        if not _same_scope(state, scope) or any(body[key] != scope[key] for key in (
                "principal_id", "audience", "action", "request_uri")):
            claims["association"].add("contradicted", "collector_request_context_mismatch")
            continue
        binding_pairs.add((body["sign_in_ref"], body["resource_ref"]))
        pair = []
        for field, adapter in (("sign_in_ref", SIGNIN_ADAPTER), ("resource_ref", KEYVAULT_ADAPTER)):
            target = refs.get(body[field])
            if target is None or not target["eligible"] or target["normalized"] is None:
                claims["association"].add("unresolved", "bound_native_record_unavailable_or_untrusted")
                continue
            if target["normalized"]["adapter"] != adapter:
                claims["association"].add("contradicted", "bound_native_adapter_mismatch")
                continue
            if field == "sign_in_ref":
                linked_signins.append(target)
            else:
                linked_resources.append((target, body))
            status, reason = _identity(target, scope)
            if status != "supported" or not _same_scope(target, scope):
                claims["association"].add(status if status != "supported" else "contradicted", reason)
                continue
            pair.append(target)
            _association_mapping(target, body, scope, claims["association"])
        if len(pair) == 2:
            app_ids = [item["normalized"]["app_id"] for item in pair]
            if all(value is not None for value in app_ids) and app_ids[0] != app_ids[1]:
                claims["association"].add("contradicted", "observed_application_ids_disagree")
            source_times = [_event_ticks(item) for item in pair]
            if all(value is not None for value in source_times) and source_times[0] > source_times[1]:
                claims["association"].add("contradicted", "sign_in_follows_bound_resource_operation")
            claims["association"].add("supported", "explicit_scoped_collector_binding")
    if len(binding_pairs) > 1:
        claims["association"].add("contradicted", "conflicting_attempt_bindings")
    if not bindings:
        claims["association"].add("unresolved", "no_explicit_scoped_binding")
    signins = linked_signins if bindings else [state for state in native if _same_scope(state, scope)
                                             and state["normalized"]["adapter"] == SIGNIN_ADAPTER]
    if not signins:
        claims["authentication"].add("unresolved", "trusted_sign_in_observation_missing")
    for state in signins:
        status, reason = _identity(state, scope)
        normalized = state["normalized"]
        if status != "supported":
            claims["authentication"].add(status, reason)
        elif normalized["status_conflict"]:
            claims["authentication"].add("contradicted", "conflicting_sign_in_result_channels")
        elif normalized["result"] == "success":
            claims["authentication"].add("supported", "source_reports_sign_in_success")
        elif normalized["result"] == "failure":
            claims["authentication"].add("contradicted", "source_reports_sign_in_failure")
        else:
            claims["authentication"].add("unresolved", "sign_in_result_unknown")
    if not linked_resources:
        claims["operation"].add("unresolved", "exact_attempt_resource_binding_missing")
    for state, binding in linked_resources:
        _operation_claim(state, scope, claims["operation"], binding)
    permissions = [state for state in eligible if state["payload"]["kind"] == "permission"
                   and state["payload"]["body"]["operation_id"] == scope["operation_id"]
                   and state["payload"]["body"]["attempt_id"] == scope["attempt_id"]]
    if not permissions:
        claims["authority"].add("unresolved", "operation_permission_missing")
    for state in permissions:
        _permission_observation(state, linked_resources, scope, claims["authority"])
    # Exclusion cannot erase a separately checkable contradiction in a signed
    # candidate reference. Only negative findings survive this path; it never
    # supplies a positive operation, association or authority judgment.
    for state in states:
        payload, body = state["payload"], state["payload"]["body"]
        if (payload["kind"] != "binding" or state["eligible"] or not state["individually_eligible"]
                or not _same_scope(state, scope) or body["operation_id"] != scope["operation_id"]
                or body["attempt_id"] != scope["attempt_id"]):
            continue
        target = refs.get(body["resource_ref"])
        if target is None or not target["eligible"] or target["normalized"] is None:
            continue
        candidate = Claim()
        _operation_claim(target, scope, candidate, body)
        for reason in candidate.bad:
            claims["operation"].add("contradicted", "excluded_reference_" + reason)
        for permission in permissions:
            candidate = Claim()
            _permission_observation(permission, [(target, body)], scope, candidate)
            for reason in candidate.bad:
                claims["authority"].add("contradicted", "excluded_reference_" + reason)
    for state in states:
        if state["scope_conflict"] and state["signature_status"] == state["authority_status"] == "supported":
            target = "authentication" if state["normalized"]["adapter"] == SIGNIN_ADAPTER else "operation"
            claims[target].add("contradicted", "signed_native_scope_conflict")


def _timing(states: list[dict], scope: dict, claim: Claim) -> list[dict]:
    timings = []
    required = set(scope["prerequisite_record_ids"])
    seen = set()
    if not required:
        claim.add("unresolved", "no_declared_prerequisite_records")
    for state in states:
        payload = state["payload"]
        if payload["record_id"] not in required:
            continue
        seen.add(payload["record_id"])
        if payload["kind"] not in ("native", "permission") or (
                payload["kind"] == "native" and state["normalized"] is not None
                and state["normalized"]["adapter"] != SIGNIN_ADAPTER):
            claim.add("contradicted", "outcome_is_not_a_pre_action_prerequisite")
            continue
        if state["signature_status"] != "supported" or state["authority_status"] != "supported" \
                or state["commitment_status"] != "supported":
            claim.add("unresolved", "required_timing_record_untrusted")
            continue
        event = _event_ticks(state)
        available, received = payload["available_time"], payload["received_time"]
        item = {"record_ref": state["ref"], "source_event_time": (
            state["normalized"]["source_time"] if state["normalized"] is not None else payload["event_time"]),
            "available_time": available, "received_time": received,
            "event_to_available_seconds": None, "available_to_received_seconds": None}
        if event is None or available is None or received is None:
            claim.add("unresolved", "source_availability_or_clock_unknown")
        if event is not None and available is not None:
            item["event_to_available_seconds"] = _seconds(available * TICKS - event)
        if available is not None and received is not None:
            item["available_to_received_seconds"] = str(received - available)
        if state["temporal_status"] == "contradicted":
            claim.add("contradicted", "inconsistent_observation_clock_order")
        if (available is not None and available > scope["action_time"]
                or received is not None and received > scope["action_time"]):
            claim.add("contradicted", "evidence_not_available_to_collector_by_action")
        if not state["eligible"]:
            claim.add("unresolved", "timing_record_outside_evaluation_scope")
        elif event is not None and available is not None and received is not None \
                and state["temporal_status"] == "supported" \
                and available <= scope["action_time"] and received <= scope["action_time"]:
            claim.add("supported", "declared_evidence_available_by_action")
        timings.append(item)
    if required - seen:
        claim.add("unresolved", "required_timing_record_missing")
    return timings


def _coverage(states: list[dict], scope: dict, claim: Claim, horizon: int) -> None:
    refs = {state["ref"]: state for state in states}
    collections = [state for state in states if state["eligible"] and _same_scope(state, scope)
                   and state["payload"]["kind"] == "collection"]
    if not collections:
        claim.add("unresolved", "scoped_collection_statement_missing")
    for state in collections:
        body = state["payload"]["body"]
        if any(body[key] != scope[key] for key in ("interval_start", "interval_end")):
            claim.add("contradicted", "collection_window_mismatch")
            continue
        end = body["interval_end"]
        payload = state["payload"]
        if body["closed"] and (end > horizon or payload["event_time"] < end
                or payload["received_time"] < end
                or payload["available_time"] is not None and payload["available_time"] < end):
            claim.add("contradicted", "collection_window_not_closed_at_observed_time")
        if not body["closed"] or body["gaps"]:
            claim.add("unresolved", "collection_open_or_declared_gaps")
        for record_id in scope["expected_record_ids"]:
            target = refs.get(body["record_refs"].get(record_id))
            if record_id not in body["record_refs"]:
                claim.add("unresolved", "required_record_not_declared_collected")
            elif target is None or target["payload"]["record_id"] != record_id:
                claim.add("contradicted", "collection_reference_mismatch")
            elif not target["eligible"] or not _same_scope(target, scope):
                claim.add("unresolved", "collected_record_untrusted_or_outside_scope")
            else:
                event = _event_ticks(target)
                if event is None:
                    claim.add("unresolved", "collected_record_time_unknown")
                elif not scope["interval_start"] * TICKS <= event <= scope["interval_end"] * TICKS:
                    claim.add("contradicted", "collected_record_outside_declared_window")
                else:
                    claim.add("supported", "declared_record_reference_present")


def _assessments(states: list[dict], scope: dict, claim: Claim) -> list[dict]:
    selected = [state for state in states if state["eligible"] and _same_scope(state, scope)
                and state["payload"]["kind"] == "assessment"]
    refs = {state["ref"]: state for state in selected}
    history = []
    versions = set()
    if not selected:
        claim.add("unresolved", "dated_source_assessment_missing")
    for state in selected:
        payload, body = state["payload"], state["payload"]["body"]
        version = (body["publisher"], body["source_url"], body["version"])
        if version in versions:
            claim.add("contradicted", "duplicate_source_version")
        versions.add(version)
        if body["published_at"] > body["updated_at"] or body["updated_at"] > payload["received_time"]:
            claim.add("contradicted", "source_assessment_date_conflict")
        else:
            claim.add("supported", "dated_source_judgment_preserved")
        previous = body["supersedes"]
        if previous is not None:
            older = refs.get(previous)
            if older is None:
                claim.add("unresolved", "earlier_source_version_missing")
            else:
                earlier = older["payload"]["body"]
                if any(body[k] != earlier[k] for k in ("publisher", "source_url")) \
                        or earlier["updated_at"] >= body["updated_at"]:
                    claim.add("contradicted", "source_revision_binding_conflict")
    for state in states:
        if state["payload"]["kind"] != "assessment":
            continue
        body = state["payload"]["body"]
        history.append({"record_ref": state["ref"], "publisher": body["publisher"],
                        "source_url_commitment": bytes_digest(body["source_url"].encode("utf-8")),
                        "version": body["version"], "published_at": body["published_at"],
                        "updated_at": body["updated_at"], "assessment": body["assessment"],
                        "supersedes": body["supersedes"], "eligible": state["eligible"],
                        "classification": "supplied_source_assessment_not_model_telemetry"})
    return sorted(history, key=lambda item: (item["updated_at"], item["record_ref"]))


def verify_bundle(bundle: dict, trust: dict, *, scope: dict, evaluation_time: int) -> dict:
    """Assess only supplied synthetic statements under caller-pinned authority.

    Trust grant intervals apply to the statement's asserted collector receipt
    time. They do not prove key lifecycle, signing time or trusted clocks.
    scope.action_time is the claimed action/checkpoint under review. Only caller
    identified prerequisite_record_ids are checked for availability before it;
    later outcome evidence supports retrospective claims, never prevention.
    """
    bundle, trust, scope, keys = _validate_inputs(bundle, trust, scope, evaluation_time)
    states = [_record(env, trust, keys, evaluation_time) for env in bundle["records"]]
    claims = {name: Claim() for name in CLAIMS}
    counts = Counter(state["payload"]["record_id"] for state in states)
    for state in states:
        if counts[state["payload"]["record_id"]] > 1:
            state["eligible"] = False
            state["reasons"].append("duplicate_record_id")
            claims["integrity"].add("contradicted", "duplicate_record_id")
        claims["integrity"].add(state["signature_status"], "envelope_signature_" + state["signature_status"])
        claims["integrity"].add(state["commitment_status"], "original_or_mapping_" + state["commitment_status"])
        claims["provenance"].add(state["authority_status"], "key_authority_" + state["authority_status"])
        if state["signature_status"] == state["authority_status"] == state["commitment_status"] == "supported":
            claims["temporal_consistency"].add(state["temporal_status"], "record_clock_" + state["temporal_status"])
        else:
            claims["temporal_consistency"].add("unresolved", "untrusted_record_clock")
        if state["commitment_status"] == "contradicted":
            claims["provenance"].add("contradicted", "original_or_normalized_view_conflict")
        if state["scope_conflict"]:
            claims["provenance"].add("contradicted", "native_scope_conflict")
    if not states:
        claims["integrity"].add("unresolved", "no_supplied_records")
        claims["provenance"].add("unresolved", "no_supplied_records")
    _reference_chronology(states, scope, claims)
    _semantics(states, scope, claims)
    timings = _timing(states, scope, claims["timing"])
    _coverage(states, scope, claims["coverage"], evaluation_time)
    history = _assessments(states, scope, claims["assessment"])
    claims["external_exfiltration"].add("unresolved", "no_onward_transfer_or_payload_evidence_adapter")
    claims["global_containment"].add("unresolved", "declared_collection_and_rotation_do_not_prove_containment")
    claims["ai_orchestration"].add("unresolved", "no_direct_attacker_model_telemetry")
    records, attempts, controls = [], [], []
    for state in states:
        payload, body = state["payload"], state["payload"]["body"]
        normalized_view = _public_normalized(state["normalized"])
        original = None
        if payload["kind"] == "native":
            original_bytes = body["raw"].encode("utf-8")
            original = {"claimed_sha256": body["raw_sha256"],
                        "computed_sha256": bytes_digest(original_bytes), "byte_count": len(original_bytes)}
        records.append({"record_id": payload["record_id"], "record_ref": state["ref"],
                        "kind": payload["kind"], "signature_status": state["signature_status"],
                        "event_time": payload["event_time"], "available_time": payload["available_time"],
                        "received_time": payload["received_time"],
                        "authority_status": state["authority_status"],
                        "temporal_status": state["temporal_status"],
                        "commitment_status": state["commitment_status"], "eligible": state["eligible"],
                        "reasons": state["reasons"], "original": original, "normalized": normalized_view,
                        "normalized_sha256": digest(normalized_view) if normalized_view is not None else None})
        if payload["kind"] == "binding":
            attempts.append({"record_ref": state["ref"], "operation_id": body["operation_id"],
                             "attempt_id": body["attempt_id"], "eligible": state["eligible"],
                             "sign_in_ref": body["sign_in_ref"], "resource_ref": body["resource_ref"],
                             "request_context": {"origin": "collector_statement", "method": body["method"],
                                                 "api_version": body["api_version"], "api_plane": body["api_plane"],
                                                 "request_uri_commitment": bytes_digest(
                                                     body["request_uri"].encode("utf-8"))}})
        if payload["kind"] == "control":
            controls.append({"record_ref": state["ref"], "action": body["action"],
                             "event_time": payload["event_time"], "available_time": payload["available_time"],
                             "received_time": payload["received_time"], "eligible": state["eligible"],
                             "related_ref": body["related_ref"]})
    report = {"schema": RESULT_SCHEMA, "experimental": True, "synthetic": True,
              "read_only": True, "automatic_retry": False, "evaluation_time": evaluation_time,
              "scope_commitment": digest(scope), "claims": {name: claim.report() for name, claim in claims.items()},
              "records": records, "attempts": attempts, "timing_observations": timings,
              "controls": controls, "assessment_history": history,
              "limits": ["collector_statements_not_provider_signatures", "no_independent_custody_proof",
                         "no_universal_completeness", "no_live_cloud_access", "no_vap_conformance_result"]}
    canonical_json(report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--trust", required=True, type=Path)
    parser.add_argument("--scope", required=True, type=Path)
    parser.add_argument("--at", required=True, type=int)
    args = parser.parse_args(argv)
    try:
        def read(path: Path) -> Any:
            with path.open("rb") as source:
                raw = source.read(MAX_DOCUMENT + 1)
            return load_json(raw)
        report = verify_bundle(read(args.bundle), read(args.trust), scope=read(args.scope), evaluation_time=args.at)
        sys.stdout.buffer.write(canonical_json(report) + b"\n")
        return 0  # A report was produced; this is deliberately not an evidence or safety pass.
    except (ValueError, OSError, TypeError, OverflowError):
        # Do not echo input data, raw source text, filenames or secret-bearing parse diagnostics.
        sys.stderr.write("invalid offline synthetic evidence input\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
