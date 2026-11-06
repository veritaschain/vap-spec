"""Synthetic live admission around the existing loopback payment runtime.

Configured identities and supplied signed status snapshots are synthetic. This
does not establish real people, actual business approval, latest authority state,
continuous revocation, VAP conformance or a production authorization boundary.
The underlying runtime/bearer remains callable by its trusted harness.
"""
from __future__ import annotations

import importlib.util
import re
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


# A named, explicit repository dependency. Existing source is neither copied
# nor imported from an unmerged experiment. An Adapter supplied by the caller
# can come from its normal payment_runtime import; no class identity test is used.
_RUNTIME_PATH = Path(__file__).resolve().parents[1] / "payment-runtime-pilot" / "payment_runtime.py"
_SPEC = importlib.util.spec_from_file_location("_vso_payment_authorization_runtime", _RUNTIME_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError("local_payment_runtime_dependency_unavailable")
runtime = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = runtime
_SPEC.loader.exec_module(runtime)

canonical_json = runtime.canonical_json
load_json = runtime.load_json
bytes_digest = runtime.bytes_digest
digest = runtime.digest

POLICY_SCHEMA = "synthetic-payment-admission-policy-v0"
APPROVAL_SCHEMA = "synthetic-payment-admission-approval-v0"
STATUS_SCHEMA = "synthetic-payment-admission-status-v0"
DECISION_SCHEMA = "synthetic-payment-admission-decision-v0"
PROOF_SCHEMA = "synthetic-payment-admission-proof-v0"
SIGNING_DOMAIN = b"VSO synthetic payment admission evidence v0\x00"
SLOTS = ("maker_approval", "checker_approval", "final_status")
APPROVALS = SLOTS[:2]
ROLES = {"maker_approval": "approver", "checker_approval": "approver", "final_status": "status_authority"}
POLICY_FIELDS = {"schema", "policy_id", "version", "context", "principal_id", "credential_id",
                 "configuration_digest", "recovery_epoch", "allowed_sources", "allowed_beneficiaries",
                 "max_amount_minor", "valid_from_ms", "valid_until_ms"}
APPROVAL_FIELDS = {"schema", "kind", "approval_id", "request_digest", "policy_digest",
                   "issued_at_ms", "expires_at_ms"}
STATUS_FIELDS = {"schema", "kind", "status_id", "request_digest", "policy_digest", "approval_digests",
                 "principal_id", "credential_id", "configuration_digest", "recovery_epoch",
                 "observed_at_ms", "valid_until_ms", "state", "revoked_at_ms"}
IDENTITY_FIELDS = {"person_id", "roles", *runtime.SCOPE_FIELDS, "valid_from_ms", "valid_until_ms"}


def now_ms() -> int:
    return time.time_ns() // 1000000


def _text(value: Any) -> bool:
    return runtime._text(value)


def _int(value: Any) -> bool:
    return runtime._integer(value)


def _hash(value: Any) -> bool:
    return runtime._hash(value)


def _texts(value: Any) -> bool:
    return (type(value) is list and len(value) <= 64 and all(_text(x) for x in value)
            and len(value) == len(set(value)))


def _exact(value: Any, fields: set[str]) -> bool:
    return type(value) is dict and set(value) == fields


def _policy(value: Any) -> dict:
    value = load_json(canonical_json(value))
    if (not _exact(value, POLICY_FIELDS) or value["schema"] != POLICY_SCHEMA
            or not all(_text(value[name]) for name in ("policy_id", "version", "principal_id", "credential_id"))
            or not _hash(value["configuration_digest"]) or not _int(value["recovery_epoch"])
            or not _texts(value["allowed_sources"]) or not _texts(value["allowed_beneficiaries"])
            or not runtime._decimal(value["max_amount_minor"])
            or not _int(value["valid_from_ms"]) or not _int(value["valid_until_ms"])
            or value["valid_from_ms"] >= value["valid_until_ms"]):
        raise ValueError("configured_policy_shape")
    runtime.validate_context(value["context"])
    return value


def policy_digest(policy: dict) -> str:
    return digest(_policy(policy))


def sign_evidence(payload: dict, key_id: str, private_key: Ed25519PrivateKey) -> bytes:
    """Return the original canonical envelope bytes for synthetic approval/status."""
    if not _text(key_id):
        raise ValueError("evidence_key_id_shape")
    signed = {"key_id": key_id, "payload": load_json(canonical_json(payload))}
    return canonical_json({**signed, "signature": private_key.sign(
        SIGNING_DOMAIN + canonical_json(signed)).hex()})


@dataclass
class GateConfig:
    policy: dict
    trusted_keys: dict[str, dict[str, bytes]]
    identities: dict[str, dict]
    max_status_age_ms: int = 30000


def _trust_manifest(trust: Any) -> dict:
    if type(trust) is not dict or set(trust) - set(ROLES.values()):
        raise ValueError("configured_trust_roles")
    result = {}
    for role, keys in trust.items():
        if type(keys) is not dict:
            raise ValueError("configured_role_keys")
        result[role] = {}
        for key_id, public in keys.items():
            if not _text(key_id) or type(public) is not bytes or len(public) != 32:
                raise ValueError("configured_role_key_shape")
            Ed25519PublicKey.from_public_bytes(public)
            result[role][key_id] = public.hex()
    return load_json(canonical_json(result))


def _identity_manifest(identities: Any) -> dict:
    result = load_json(canonical_json(identities))
    if type(result) is not dict:
        raise ValueError("configured_identity_mapping")
    for public_hex, value in result.items():
        if (re.fullmatch(r"[0-9a-f]{64}", public_hex) is None
                or not _exact(value, IDENTITY_FIELDS) or not _text(value["person_id"])
                or not _texts(value["roles"]) or not value["roles"]
                or set(value["roles"]) - {"maker", "checker"}
                or not all(_text(value[field]) for field in runtime.SCOPE_FIELDS)
                or not _int(value["valid_from_ms"]) or not _int(value["valid_until_ms"])
                or value["valid_from_ms"] >= value["valid_until_ms"]):
            raise ValueError("configured_identity_shape")
    return result


class _Decision:
    def __init__(self, request_digest: str, at_ms: int) -> None:
        self.request_digest = request_digest
        self.at_ms = at_ms
        self.denied: list[str] = []
        self.unknown: list[str] = []

    def require(self, condition: bool, reason: str) -> None:
        if not condition:
            self.denied.append(reason)

    def available(self, condition: bool, reason: str) -> None:
        if not condition:
            self.unknown.append(reason)

    def result(self) -> dict:
        verdict = "DENIED" if self.denied else "UNKNOWN" if self.unknown else "AUTHORIZED"
        return {"schema": DECISION_SCHEMA, "verdict": verdict,
                "request_digest": self.request_digest, "evaluated_at_ms": self.at_ms,
                "admitted_at_ms": self.at_ms if verdict == "AUTHORIZED" else None,
                "reasons": sorted(set(self.denied + self.unknown or ["configured_mock_admission_supported_at_claim_time"]))}


class AdmissionBlocked(Exception):
    def __init__(self, decision: dict) -> None:
        super().__init__("mock_admission_blocked")
        self.decision = decision


def _freeze_evidence(evidence: Any) -> tuple[dict[str, bytes], list[str]]:
    """Own original immutable bytes without trusting names, assertions or keys."""
    if evidence is None:
        return {}, []
    if type(evidence) is not dict or set(evidence) - set(SLOTS):
        return {}, ["evidence_slots_unusable"]
    result = {}
    problems = []
    for name, raw in evidence.items():
        if type(raw) is not bytes or not 0 < len(raw) <= 16384:
            problems.append(name + ":original_canonical_envelope_bytes_required")
        else:
            result[name] = bytes(raw)
    return result, problems


def _approval_shape(body: Any, slot: str) -> bool:
    return (_exact(body, APPROVAL_FIELDS) and body["schema"] == APPROVAL_SCHEMA
            and body["kind"] == slot and _text(body["approval_id"])
            and _hash(body["request_digest"]) and _hash(body["policy_digest"])
            and _int(body["issued_at_ms"]) and _int(body["expires_at_ms"]))


def _status_shape(body: Any) -> bool:
    if (not _exact(body, STATUS_FIELDS) or body["schema"] != STATUS_SCHEMA or body["kind"] != "final_status"
            or not all(_text(body[name]) for name in ("status_id", "principal_id", "credential_id"))
            or not all(_hash(body[name]) for name in ("request_digest", "policy_digest", "configuration_digest"))
            or not all(_int(body[name]) for name in ("recovery_epoch", "observed_at_ms", "valid_until_ms"))
            or type(body["state"]) is not str or body["state"] not in ("active", "revoked", "unknown")
            or body["revoked_at_ms"] is not None and not _int(body["revoked_at_ms"])
            or not _exact(body["approval_digests"], set(APPROVALS))
            or not all(_hash(ref) for ref in body["approval_digests"].values())):
        return False
    return True


def _verified(slot: str, evidence: dict[str, bytes], trust: dict,
              decision: _Decision) -> tuple[dict | None, str | None]:
    raw = evidence.get(slot)
    if raw is None:
        decision.unknown.append(slot + ":missing_envelope")
        return None, None
    try:
        envelope = load_json(raw)
        if (not _exact(envelope, {"key_id", "payload", "signature"})
                or canonical_json(envelope) != raw or not _text(envelope["key_id"])
                or type(envelope["signature"]) is not str
                or re.fullmatch(r"[0-9a-f]{128}", envelope["signature"]) is None):
            raise ValueError("envelope_shape_or_encoding")
        public = trust.get(ROLES[slot], {}).get(envelope["key_id"])
        if public is None:
            decision.unknown.append(slot + ":no_configured_role_key")
            return None, None
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(public)).verify(
            bytes.fromhex(envelope["signature"]), SIGNING_DOMAIN + canonical_json({
                "key_id": envelope["key_id"], "payload": envelope["payload"]}))
        body = envelope["payload"]
        shape = _approval_shape(body, slot) if slot in APPROVALS else _status_shape(body)
        if not shape:
            decision.unknown.append(slot + ":signed_statement_shape_unusable")
            return None, None
        observed = body["issued_at_ms"] if slot in APPROVALS else body["observed_at_ms"]
        if observed > decision.at_ms:
            decision.unknown.append(slot + ":statement_after_admission_time")
            return None, None
        return body, public
    except (ValueError, TypeError, UnicodeError, InvalidSignature):
        decision.unknown.append(slot + ":signature_or_canonical_envelope_unverifiable")
        return None, None


def _assess(request: dict, raw: bytes, evidence: dict[str, bytes], evidence_problems: list[str],
            policy: dict, trust: dict, identities: dict, *, at_ms: int,
            max_status_age_ms: int) -> dict:
    result = _Decision(bytes_digest(raw), at_ms)
    result.unknown.extend(evidence_problems)
    configured_policy_digest = digest(policy)
    result.require(policy["valid_from_ms"] <= at_ms < policy["valid_until_ms"], "policy:outside_validity_window")
    for field in runtime.CONTEXT_FIELDS:
        result.require(request[field] == policy["context"][field], "policy:" + field + "_mismatch")
    for field in ("configuration_digest", "recovery_epoch"):
        result.require(request[field] == policy[field], "policy:" + field + "_mismatch")
    result.require(request["source_account"] in policy["allowed_sources"], "policy:source_not_allowed")
    result.require(request["beneficiary"] in policy["allowed_beneficiaries"], "policy:beneficiary_not_allowed")
    result.require(int(request["amount_minor"]) <= int(policy["max_amount_minor"]), "policy:amount_limit_exceeded")
    records, publics = {}, {}
    for slot in SLOTS:
        records[slot], publics[slot] = _verified(slot, evidence, trust, result)
    people = []
    approval_ids = []
    for slot, role in zip(APPROVALS, ("maker", "checker")):
        approval = records[slot]
        if approval is None:
            continue
        approval_ids.append(approval["approval_id"])
        result.require(approval["request_digest"] == bytes_digest(raw), slot + ":request_digest_mismatch")
        result.require(approval["policy_digest"] == configured_policy_digest, slot + ":policy_digest_mismatch")
        result.require(approval["issued_at_ms"] < approval["expires_at_ms"], slot + ":invalid_window")
        result.require(approval["issued_at_ms"] <= at_ms < approval["expires_at_ms"], slot + ":outside_validity_window")
        identity = identities.get(publics[slot])
        result.available(identity is not None, slot + ":configured_identity_missing")
        if identity is not None:
            people.append(identity["person_id"])
            result.require(role in identity["roles"], slot + ":role_ineligible")
            for field in runtime.SCOPE_FIELDS:
                result.require(identity[field] == request[field], slot + ":identity_" + field + "_mismatch")
            result.require(identity["valid_from_ms"] <= approval["issued_at_ms"] < identity["valid_until_ms"],
                           slot + ":identity_not_eligible_at_issuance")
            result.require(identity["valid_from_ms"] <= at_ms < identity["valid_until_ms"],
                           slot + ":identity_not_eligible_at_admission")
    if len(people) == 2:
        result.require(people[0] != people[1], "approvals:same_configured_person")
    if len(approval_ids) == 2:
        result.require(approval_ids[0] != approval_ids[1], "approvals:duplicate_approval_id")
    status = records["final_status"]
    if status is not None:
        result.require(status["request_digest"] == bytes_digest(raw), "final_status:request_digest_mismatch")
        result.require(status["policy_digest"] == configured_policy_digest, "final_status:policy_digest_mismatch")
        for field in ("principal_id", "credential_id", "configuration_digest", "recovery_epoch"):
            result.require(status[field] == policy[field], "final_status:" + field + "_mismatch")
        for slot in APPROVALS:
            if records[slot] is not None:
                result.require(status["approval_digests"][slot] == bytes_digest(evidence[slot]),
                               "final_status:" + slot + "_digest_mismatch")
                result.require(records[slot]["issued_at_ms"] <= status["observed_at_ms"],
                               "final_status:precedes_" + slot)
            else:
                # An unauthenticated replacement does not establish a signed
                # contradiction about the authentic approval it replaced.
                result.unknown.append("final_status:" + slot + "_referent_unverifiable")
        result.require(status["observed_at_ms"] < status["valid_until_ms"], "final_status:invalid_window")
        fresh = (status["observed_at_ms"] <= at_ms < status["valid_until_ms"]
                 and at_ms - status["observed_at_ms"] <= max_status_age_ms)
        result.available(fresh, "final_status:missing_current_freshness")
        if fresh:
            if status["state"] == "revoked":
                revoked = status["revoked_at_ms"]
                result.available(revoked is not None, "final_status:revocation_time_missing")
                if revoked is not None:
                    result.require(revoked <= status["observed_at_ms"], "final_status:revocation_after_observation")
                    result.require(revoked > at_ms, "final_status:credential_revoked")
            else:
                result.require(status["revoked_at_ms"] is None, "final_status:contradictory_revocation_time")
                result.available(status["state"] == "active", "final_status:active_state_not_supplied")
    decision = result.result()
    decision.update(policy_digest=configured_policy_digest,
                    trust_manifest_digest=digest(trust), identity_manifest_digest=digest(identities),
                    evidence_digests={slot: bytes_digest(value) for slot, value in evidence.items()})
    return decision


def _decoded_hex(value: Any) -> bytes:
    if type(value) is not str or re.fullmatch(r"(?:[0-9a-f]{2})+", value) is None:
        raise ValueError("record_hex_encoding")
    return bytes.fromhex(value)


def recheck_record(record_bytes: bytes) -> dict:
    """Reproduce a historical decision under its recorded input snapshots only.

    Embedded public keys/identities are not independently trusted merely because
    they are in this record. This check does not authenticate the record's own
    custody or adoption history, and never establishes current authorization.
    """
    response = {"verdict": "UNVERIFIABLE", "decision": None,
                "record_digest": None, "recorded_inputs_only": True,
                "independent_trust_established": False, "current_authorization_asserted": False}
    try:
        if type(record_bytes) is not bytes:
            return response
        response["record_digest"] = bytes_digest(record_bytes)
        record = load_json(record_bytes)
        fields = {"schema", "request_bytes", "policy_bytes", "trust_manifest_bytes",
                  "identity_manifest_bytes", "max_status_age_ms", "evidence", "decision"}
        if (not _exact(record, fields) or record["schema"] != PROOF_SCHEMA
                or canonical_json(record) != record_bytes
                or not _int(record["max_status_age_ms"]) or record["max_status_age_ms"] == 0
                or not _exact(record["evidence"], set(SLOTS))
                or type(record["decision"]) is not dict):
            return response
        raw_request = _decoded_hex(record["request_bytes"])
        request = load_json(raw_request)
        if runtime.request_bytes(request) != raw_request:
            return response
        policy_raw = _decoded_hex(record["policy_bytes"])
        policy = _policy(load_json(policy_raw))
        if canonical_json(policy) != policy_raw:
            return response
        trust_raw = _decoded_hex(record["trust_manifest_bytes"])
        original_trust = load_json(trust_raw)
        if type(original_trust) is not dict:
            return response
        decoded_trust = {role: {key_id: _decoded_hex(public) for key_id, public in keys.items()}
                         for role, keys in original_trust.items()}
        trust = _trust_manifest(decoded_trust)
        if canonical_json(trust) != trust_raw:
            return response
        identity_raw = _decoded_hex(record["identity_manifest_bytes"])
        identities = _identity_manifest(load_json(identity_raw))
        if canonical_json(identities) != identity_raw:
            return response
        original = record["decision"]
        at_ms = original.get("admitted_at_ms")
        if not _int(at_ms) or original.get("evaluated_at_ms") != at_ms:
            return response
        evidence = {slot: _decoded_hex(raw) for slot, raw in record["evidence"].items()}
        frozen, problems = _freeze_evidence(evidence)
        reconstructed = _assess(request, raw_request, frozen, problems, policy, trust, identities,
                                at_ms=at_ms, max_status_age_ms=record["max_status_age_ms"])
        if reconstructed["verdict"] != "AUTHORIZED" or reconstructed != original:
            return response
        return {**response, "verdict": "SUPPORTED", "decision": reconstructed}
    except (ValueError, TypeError, UnicodeError, AttributeError):
        return response


class AuthorizedAdapter:
    """A mock admission prerequisite, not an unbypassable payment authority."""

    def __init__(self, adapter: Any, config: GateConfig, *,
                 fault_hook: Callable[[str, dict], None] | None = None) -> None:
        self._adapter = adapter
        self._policy_bytes = canonical_json(_policy(config.policy))
        self._trust_bytes = canonical_json(_trust_manifest(config.trusted_keys))
        self._identities_bytes = canonical_json(_identity_manifest(config.identities))
        if not _int(config.max_status_age_ms) or config.max_status_age_ms == 0:
            raise ValueError("configured_status_freshness")
        if fault_hook is not None and not callable(fault_hook):
            raise ValueError("trusted_fault_hook_type")
        self._max_status_age_ms = config.max_status_age_ms
        self._fault_hook = fault_hook
        self._initialize_proofs()

    def _initialize_proofs(self) -> None:
        connection = runtime._connect(self._adapter.journal_path, self._adapter.sqlite_timeout)
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("""CREATE TABLE IF NOT EXISTS authorization_proofs (
                request_digest TEXT PRIMARY KEY,
                record_bytes BLOB NOT NULL, record_digest TEXT NOT NULL,
                admitted_at_ms INTEGER NOT NULL,
                FOREIGN KEY(request_digest) REFERENCES dispatches(request_digest)
                  DEFERRABLE INITIALLY DEFERRED)""")
            for action in ("UPDATE", "DELETE"):
                connection.execute(f"""CREATE TRIGGER IF NOT EXISTS immutable_authorization_proof_{action.lower()}
                    BEFORE {action} ON authorization_proofs BEGIN
                    SELECT RAISE(ABORT, 'original_authorization_proof_retained'); END""")
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _unavailable_admission(request_digest: str | None, reason: str) -> dict:
        return {"verdict": "UNKNOWN", "request_digest": request_digest,
                "reasons": [reason], "proof_digest": None}

    def _admission_callback(self, evidence: dict[str, bytes], problems: list[str]) -> Callable:
        # Every call owns these snapshots. No pending approval is stored in a
        # mutable instance field shared by concurrent submissions.
        policy_bytes = bytes(self._policy_bytes)
        trust_bytes = bytes(self._trust_bytes)
        identities_bytes = bytes(self._identities_bytes)
        policy, trust, identities = map(load_json, (policy_bytes, trust_bytes, identities_bytes))
        maximum_age = self._max_status_age_ms
        fault_hook = self._fault_hook

        def admit(connection: sqlite3.Connection, request: dict, raw: bytes, at_ms: int) -> None:
            decision = _assess(request, raw, evidence, problems, policy, trust, identities,
                               at_ms=at_ms, max_status_age_ms=maximum_age)
            if decision["verdict"] != "AUTHORIZED":
                raise AdmissionBlocked(decision)
            record = canonical_json({"schema": PROOF_SCHEMA, "request_bytes": raw.hex(),
                "policy_bytes": policy_bytes.hex(), "trust_manifest_bytes": trust_bytes.hex(),
                "identity_manifest_bytes": identities_bytes.hex(),
                "max_status_age_ms": maximum_age,
                "evidence": {name: value.hex() for name, value in evidence.items()}, "decision": decision})
            connection.execute("INSERT INTO authorization_proofs VALUES (?,?,?,?)", (
                bytes_digest(raw), record, bytes_digest(record), at_ms))
            if fault_hook is not None:
                try:
                    fault_hook("after_authorization_proof", {
                        "request_digest": bytes_digest(raw), "record_digest": bytes_digest(record)})
                except Exception as exc:
                    # The callback is only a harness fault point. A failure
                    # cannot be mistaken for successful committed admission.
                    raise AdmissionBlocked(self._unavailable_admission(
                        bytes_digest(raw), "authorization_transaction_fault_no_post")) from exc
        return admit

    def _attach(self, result: dict, request: dict) -> dict:
        original = self.read_authorization(request)
        if (original["status"] == "FOUND"
                and original["request_digest"] == result.get("request_digest")):
            admission = {**original["decision"], "proof_digest": original["record_digest"],
                         "historical_original_decision": True}
        else:
            admission = self._unavailable_admission(result.get("request_digest"),
                "original_authorization_proof_" + original["status"].lower())
        return {**result, "mock_admission": admission}

    def submit(self, request: dict, evidence: Any = None) -> dict:
        try:
            snapshot, raw = self._adapter._prepare(request)
        except (ValueError, TypeError, UnicodeError):
            result = self._adapter._result("REJECTED", None, "request_schema_or_scope_rejected")
            return {**result, "mock_admission": self._unavailable_admission(None, "native_request_unusable")}
        return self._submit_prepared(snapshot, raw, evidence)

    def _submit_prepared(self, snapshot: dict, raw: bytes, evidence: Any = None, *,
                         before_dispatch: Callable[[dict, bytes], None] | None = None,
                         after_terminal_receipt: Callable[[dict, bytes, bytes], None] | None = None) -> dict:
        """Code-owned per-call extensions; no callbacks enter from evidence."""
        original, problems = _freeze_evidence(evidence)
        try:
            result = self._adapter._submit_prepared(snapshot, raw,
                admit_new_claim=self._admission_callback(original, problems),
                before_dispatch=before_dispatch, after_terminal_receipt=after_terminal_receipt)
        except AdmissionBlocked as exc:
            result = self._adapter._result("REJECTED", bytes_digest(raw), "mock_admission_not_committed_no_post")
            return {**result, "mock_admission": {**exc.decision, "proof_digest": None}}
        return self._attach(result, snapshot)

    def reconcile(self, request: dict) -> dict:
        # No new admission or authorization evidence is accepted here. The
        # original CLAIMED row and proof are retained after expiry/revocation.
        try:
            snapshot, _ = self._adapter._prepare(request)
        except (ValueError, TypeError, UnicodeError):
            result = self._adapter._result("REJECTED", None, "request_schema_or_scope_rejected")
            return {**result, "mock_admission": self._unavailable_admission(None, "native_request_unusable")}
        return self._attach(self._adapter.reconcile(snapshot), snapshot)

    def read_status(self, request: dict) -> dict:
        try:
            snapshot, _ = self._adapter._prepare(request)
        except (ValueError, TypeError, UnicodeError):
            result = self._adapter._result("REJECTED", None, "request_schema_or_scope_rejected")
            return {**result, "mock_admission": self._unavailable_admission(None, "native_request_unusable")}
        return self._attach(self._adapter.read_status(snapshot), snapshot)

    def read_authorization(self, request: dict) -> dict:
        result = {"status": "UNAVAILABLE", "request_digest": None, "record_bytes": None,
                  "record_digest": None, "decision": None}
        try:
            snapshot, raw = self._adapter._prepare(request)
            result["request_digest"] = bytes_digest(raw)
            connection = runtime._readonly(self._adapter.journal_path)
            try:
                connection.execute("BEGIN")
                claim = runtime._find(connection, "dispatches", self._adapter.scope, snapshot, raw)
                if claim is None:
                    return {**result, "status": "MISSING"}
                proof = connection.execute("SELECT * FROM authorization_proofs WHERE request_digest=?",
                                           (bytes_digest(raw),)).fetchone()
                if proof is None:
                    return {**result, "status": "MISSING"}
                record = bytes(proof["record_bytes"])
                checked = recheck_record(record)
                packed = load_json(record)
                if (checked["verdict"] != "SUPPORTED" or bytes_digest(record) != proof["record_digest"]
                        or packed["request_bytes"] != raw.hex()
                        or checked["decision"]["request_digest"] != bytes_digest(raw)
                        or checked["decision"]["admitted_at_ms"] != proof["admitted_at_ms"]
                        or proof["admitted_at_ms"] != claim["claimed_at_ms"]):
                    return result
                return {**result, "status": "FOUND", "record_bytes": record,
                        "record_digest": proof["record_digest"], "decision": checked["decision"],
                        "historical_recheck": "SUPPORTED_UNDER_RECORDED_INPUTS"}
            finally:
                connection.close()
        except ValueError as exc:
            if str(exc) == "immutable_request_identity_conflict":
                result["status"] = "CONFLICT"
            return result
        except (sqlite3.Error, OSError, TypeError, UnicodeError):
            return result
