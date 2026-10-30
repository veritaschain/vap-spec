"""Fresh-key, synthetic-only fixture support; never imported by runtime code.

Private signing keys live only in each in-memory fixture. ``inputs()`` returns
JSON-compatible public evidence and separate evaluator trust, never those keys.
"""

from copy import deepcopy
from pathlib import Path
import hashlib
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

LEGACY_ROOT = Path(__file__).resolve().parent.parent / "incident-evidence-assessor"
if str(LEGACY_ROOT) not in sys.path:
    sys.path.insert(1, str(LEGACY_ROOT))

from incident_assessor.evidence import digest, signing_bytes as legacy_signing_bytes
from retention_adapter import signing_bytes


REQUESTED_AT = "2026-10-01T00:00:00Z"
STATEMENT_AT = "2026-10-01T01:00:00Z"
DEADLINE = "2026-10-31T00:00:00Z"
NOW = "2026-10-31T12:00:00Z"
BEFORE_DEADLINE = "2026-10-30T23:59:59.999999Z"
AFTER_DEADLINE = "2026-10-31T00:00:00.000001Z"


class FreshFixture:
    """Build signed examples independently of case IDs or expected verdicts."""

    def __init__(self, *, as_of=NOW, add_request=True):
        roles = ("responder", "provider", "collector", "reviewer")
        self._private_keys = {role: Ed25519PrivateKey.generate() for role in roles}
        authorities = {role: role + "-synthetic" for role in roles}
        subject = {
            "request_id": "retention-request-synthetic",
            "provider_id": "provider-synthetic",
            "tenant_id": "tenant-synthetic-a",
            "account_id": "account-synthetic-a",
            "object_ids": ["object-synthetic-v1"],
            "payload_sha256": hashlib.sha256(b"SYNTHETIC RETENTION TEST OBJECT").hexdigest(),
        }
        legacy = {
            "format": "incident-evidence-input/0.1",
            "evaluation_id": "retention-evaluation-synthetic",
            "workflow": "erasure",
            "as_of": as_of,
            "target": {
                "subject": subject,
                "operation_at": REQUESTED_AT,
                "coverage_requested": "managed_route",
                "authorities": authorities,
            },
            "records": [],
        }
        keys = {}
        for role, key in self._private_keys.items():
            keys[role + "-fresh-key"] = {
                "public_key": key.public_key().public_bytes_raw().hex(),
                "issuer": authorities[role],
                "organization": "requester-organization" if role in {"responder", "collector"} else role + "-organization",
                "roles": [role],
                "not_before": "2026-01-01T00:00:00Z",
                "not_after": "2027-01-01T00:00:00Z",
            }
        legacy_trust = {
            "format": "incident-evidence-trust/0.1",
            "evaluation_id": legacy["evaluation_id"],
            "workflow": "erasure",
            "as_of": as_of,
            "target_sha256": digest(legacy["target"]),
            "mode": "synthetic-test-only",
            "keys": keys,
        }
        self.package = {
            "format": "retention-evidence-input/0.1",
            "erasure": legacy,
            "retention_records": [],
        }
        self.trust = {"format": "retention-evidence-trust/0.1", "erasure_trust": legacy_trust}
        self.request_id = "request-record-synthetic"
        if add_request:
            self.add_legacy("erasure.request", {
                "requested_at": REQUESTED_AT,
                "requested_locations": ["active", "provider-log", "backup"],
            }, role="responder", recorded_at=REQUESTED_AT, record_id=self.request_id)

    def _record(self, kind, data, *, role, recorded_at, record_id=None, binding=None, legacy=False):
        records = self.package["erasure"]["records"] if legacy else self.package["retention_records"]
        body = {
            "record_id": record_id or kind + "-" + str(len(records) + 1),
            "evaluation_id": self.package["erasure"]["evaluation_id"],
            "kind": kind,
            "issuer": role + "-synthetic",
            "recorded_at": recorded_at,
            "binding": deepcopy(self.package["erasure"]["target"]["subject"] if binding is None else binding),
            "data": deepcopy(data),
        }
        record = {"algorithm": "Ed25519", "key_id": role + "-fresh-key", "body": body, "signature": "00" * 64}
        self.resign(record, role, legacy=legacy)
        records.append(record)
        return record

    def resign(self, record, role="provider", *, legacy=False):
        """Sign a deliberately modified record; do not silently alter its body."""
        message = legacy_signing_bytes(record) if legacy else signing_bytes(record)
        record["signature"] = self._private_keys[role].sign(message).hex()
        return record

    def add_legacy(self, kind, data, *, role, recorded_at=REQUESTED_AT, record_id=None, binding=None):
        return self._record(kind, data, role=role, recorded_at=recorded_at,
                            record_id=record_id, binding=binding, legacy=True)

    def statement(self, *, deadline=DEADLINE, schedule=None, training_use="reported-disabled",
                  processing_locations=None, locations=None, exceptions=None,
                  request_record_id=None, recorded_at=STATEMENT_AT, record_id=None, binding=None):
        return self._record("retention.statement", {
            "request_record_id": self.request_id if request_record_id is None else request_record_id,
            "terms_ref": "https://provider.example.invalid/terms/synthetic-v1",
            "terms_sha256": digest({"document": "synthetic-provider-terms", "version": 1}),
            "processing_locations": ["JP"] if processing_locations is None else processing_locations,
            "training_use": training_use,
            "locations": ["active", "provider-log"] if locations is None else locations,
            "schedule": {"kind": "stated-deadline", "deadline": deadline} if schedule is None else schedule,
            "exceptions": [] if exceptions is None else exceptions,
        }, role="provider", recorded_at=recorded_at, record_id=record_id, binding=binding)

    def presence(self, *, observed_at="2026-10-31T01:00:00Z", recorded_at="2026-10-31T02:00:00Z",
                 location="active", request_record_id=None, record_id=None, binding=None):
        return self._record("retention.presence", {
            "request_record_id": self.request_id if request_record_id is None else request_record_id,
            "observed_at": observed_at,
            "location": location,
            "method": "Synthetic presence statement; no external storage was queried.",
            "limitations": ["Fixture claim only; no continuity or independent storage inspection is established."],
        }, role="collector", recorded_at=recorded_at, record_id=record_id, binding=binding)

    def attestation(self, *, completed_at="2026-10-31T00:30:00Z",
                    recorded_at="2026-10-31T00:45:00Z", record_id="completion-record-synthetic"):
        return self.add_legacy("erasure.provider_attestation", {
            "request_record_id": self.request_id,
            "completed_at": completed_at,
            "locations": ["active"],
            "exclusions": ["provider-log", "backup"],
        }, role="provider", recorded_at=recorded_at, record_id=record_id)

    def review(self, *, attestation_record_id="completion-record-synthetic", conclusion="deletion-observed"):
        return self.add_legacy("erasure.review", {
            "request_record_id": self.request_id,
            "attestation_record_id": attestation_record_id,
            "method": "Synthetic scoped review statement; no actual storage assessment is claimed.",
            "evidence_record_ids": [self.request_id, attestation_record_id],
            "window_start": "2026-10-31T00:00:00Z",
            "window_end": "2026-10-31T01:00:00Z",
            "locations": ["active"],
            "limitations": ["Synthetic input; review covers only its stated active-object scope."],
            "conclusion": conclusion,
        }, role="reviewer", recorded_at="2026-10-31T01:00:00Z", record_id="review-record-synthetic")

    def inputs(self, *, as_of=None):
        """Return detached public input/trust snapshots with explicit pins."""
        package, trust = deepcopy(self.package), deepcopy(self.trust)
        if as_of is not None:
            package["erasure"]["as_of"] = as_of
        trust["erasure_trust"]["as_of"] = package["erasure"]["as_of"]
        trust["erasure_trust"]["target_sha256"] = digest(package["erasure"]["target"])
        return package, trust
