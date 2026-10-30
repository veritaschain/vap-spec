"""Real signature checks under separately supplied evaluator trust assumptions."""

import hashlib
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from . import ADAPTER
from .model import InputError, canonical, timestamp


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def signing_bytes(envelope):
    return (ADAPTER + "\0").encode("utf-8") + canonical({
        "algorithm": envelope["algorithm"], "key_id": envelope["key_id"], "body": envelope["body"],
    })


@dataclass(frozen=True)
class VerifiedRecord:
    record_id: str
    kind: str
    issuer: str
    recorded_at: object
    binding: dict
    data: dict
    organization: str


class Context:
    def __init__(self, package, trust, roles):
        self.package, self.trust = package, trust
        self.target, self.subject = package["target"], package["target"]["subject"]
        self.as_of = timestamp(package["as_of"])
        self.operation_at = timestamp(self.target["operation_at"])
        self.checks, self.findings, self._eligible = [], [], []
        if package["evaluation_id"] != trust["evaluation_id"]:
            raise InputError("Trust configuration is for a different evaluation")
        if package["workflow"] != trust["workflow"]:
            raise InputError("Workflow differs from the evaluator-pinned workflow")
        if self.as_of != timestamp(trust["as_of"]):
            raise InputError("Observation cutoff differs from the evaluator-pinned cutoff")
        if self.operation_at > self.as_of:
            raise InputError("Target operation time is after the observation cutoff")
        if digest(self.target) != trust["target_sha256"]:
            raise InputError("Target differs from the evaluator-pinned target digest")
        for envelope in package["records"]:
            body, key = envelope["body"], trust["keys"].get(envelope["key_id"])
            required_role = roles[body["kind"]]
            recorded = timestamp(body["recorded_at"])
            check = {
                "record_id": body["record_id"], "kind": body["kind"],
                "signature": "UNTRUSTED_KEY", "identity": "UNKNOWN", "role": "UNKNOWN",
                "time": "FUTURE_RECORD" if recorded > self.as_of else "WITHIN_DECLARED_WINDOW",
                "evaluation": "MATCH" if body["evaluation_id"] == package["evaluation_id"] else "MISMATCH",
                "binding_differences": [k for k in self.subject if canonical(body["binding"][k]) != canonical(self.subject[k])],
                "eligibility": "INELIGIBLE",
            }
            if key is not None:
                try:
                    Ed25519PublicKey.from_public_bytes(bytes.fromhex(key["public_key"])).verify(
                        bytes.fromhex(envelope["signature"]), signing_bytes(envelope))
                    check["signature"] = "VERIFIED"
                except InvalidSignature:
                    check["signature"] = "FAILED"
                expected_issuer = self.target["authorities"].get(required_role)
                check["identity"] = "EXPECTED_ISSUER" if body["issuer"] == key["issuer"] == expected_issuer else "MISMATCH"
                check["role"] = "AUTHORIZED" if required_role in key["roles"] else "UNAUTHORIZED"
                if not timestamp(key["not_before"]) <= recorded < timestamp(key["not_after"]):
                    check["time"] = "OUTSIDE_KEY_VALIDITY"
                if (check["signature"] == "VERIFIED" and check["identity"] == "EXPECTED_ISSUER"
                        and check["role"] == "AUTHORIZED" and check["time"] == "WITHIN_DECLARED_WINDOW"
                        and check["evaluation"] == "MATCH"):
                    check["eligibility"] = "ELIGIBLE"
                    self._eligible.append(VerifiedRecord(body["record_id"], body["kind"], body["issuer"], recorded,
                                                         body["binding"], body["data"], key["organization"]))
            self.checks.append(check)
        self.integrity_established = bool(self.checks) and all(c["eligibility"] == "ELIGIBLE" for c in self.checks)

    def records(self, kind):
        return [r for r in self._eligible if r.kind == kind]

    def differences(self, record, fields=None):
        fields = self.subject.keys() if fields is None else fields
        return [k for k in fields if k not in self.subject or k not in record.binding
                or canonical(record.binding[k]) != canonical(self.subject[k])]

    def matches(self, record, fields=None):
        return not self.differences(record, fields)

    def bound(self, kind, fields=None):
        return [r for r in self.records(kind) if self.matches(r, fields)]

    def finding(self, code, *records):
        entry = {"code": code, "record_ids": sorted({r.record_id for r in records})}
        if entry not in self.findings:
            self.findings.append(entry)

    def organization_for(self, role):
        issuer = self.target["authorities"].get(role)
        organizations = {key["organization"] for key in self.trust["keys"].values()
                         if key["issuer"] == issuer and role in key["roles"]}
        return next(iter(organizations)) if len(organizations) == 1 else None
