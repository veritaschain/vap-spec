"""Informative synthetic evidence-boundary experiment; NOT a VAP conformance verifier."""
from dataclasses import dataclass
from enum import Enum
import unittest

class Verdict(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    INDETERMINATE = "INDETERMINATE"

@dataclass(frozen=True)
class Observation:
    system: str
    trace: str | None
    authenticated: bool | None = None
    authorized: bool | None = None
    records: int | None = None
    observed: bool = True

def authorization(o: Observation) -> Verdict:
    if o.authorized is False:
        return Verdict.INVALID
    if o.authorized is True and o.authenticated is True:
        return Verdict.VALID
    return Verdict.INDETERMINATE

def correlation(a: Observation, b: Observation) -> Verdict:
    if not a.trace or not b.trace:
        return Verdict.INDETERMINATE
    return Verdict.VALID if a.trace == b.trace else Verdict.INVALID

def confirmed_count(o: Observation) -> int | None:
    return o.records if o.observed and o.records is not None else None

def exfiltration(outbound: Observation | None) -> Verdict:
    if outbound is None or not outbound.observed:
        return Verdict.INDETERMINATE
    if outbound.records is None:
        return Verdict.INDETERMINATE
    return Verdict.VALID if outbound.records > 0 else Verdict.INDETERMINATE

def credential_use(revoked_at: int | None, used_at: int | None) -> Verdict:
    if revoked_at is None or used_at is None:
        return Verdict.INDETERMINATE
    return Verdict.INVALID if used_at >= revoked_at else Verdict.INDETERMINATE

def integrity(signature_ok: bool | None, merkle_ok: bool | None) -> Verdict:
    if signature_ok is False or merkle_ok is False:
        return Verdict.INVALID
    if signature_ok is True and merkle_ok is True:
        return Verdict.VALID
    return Verdict.INDETERMINATE

def causal_binding(shared_trace: bool, trusted_parent_receipt: bool, verified_time_order: bool) -> Verdict:
    """A shared trace identifier alone is insufficient to prove causation."""
    if not shared_trace:
        return Verdict.INDETERMINATE
    return Verdict.VALID if trusted_parent_receipt and verified_time_order else Verdict.INDETERMINATE

def exposure_bounds(possible: int | None, observed_read: int | None, observed_egress: int | None) -> tuple[int | None, int | None, int | None]:
    """Keep maximum exposure, observed reads and observed outbound transfer distinct."""
    values = (possible, observed_read, observed_egress)
    if any(v is not None and (type(v) is not int or v < 0) for v in values):
        raise ValueError("counts must be nonnegative integers or unknown")
    if possible is not None and observed_read is not None and observed_read > possible:
        raise ValueError("observed read exceeds declared possible population")
    return values

def independent_gap(local_present: bool, independent_receipt: bool) -> Verdict:
    if independent_receipt and not local_present:
        return Verdict.INVALID
    return Verdict.INDETERMINATE

class EvidenceBoundaryTests(unittest.TestCase):
    def test_t01_authentication_not_authorization(self):
        self.assertEqual(authorization(Observation("db", "x", True, False)), Verdict.INVALID)
    def test_t02_missing_cross_system_id(self):
        self.assertEqual(correlation(Observation("gitlab", None), Observation("db", "x")), Verdict.INDETERMINATE)
    def test_t03_query_does_not_prove_results(self):
        self.assertIsNone(confirmed_count(Observation("db", "x", records=1000, observed=False)))
    def test_t04_no_egress_log_not_no_exfiltration(self):
        self.assertEqual(exfiltration(None), Verdict.INDETERMINATE)
    def test_t05_revoked_credential_use(self):
        self.assertEqual(credential_use(100, 101), Verdict.INVALID)
    def test_t06_local_log_deleted_independent_receipt(self):
        self.assertEqual(independent_gap(False, True), Verdict.INVALID)
    def test_t07_valid_integrity_not_authorization(self):
        self.assertEqual(integrity(True, True), Verdict.VALID)
        self.assertEqual(authorization(Observation("db", "x", True, False)), Verdict.INVALID)
    def test_t08_collection_outage(self):
        self.assertIsNone(confirmed_count(Observation("db", "x", records=100, observed=False)))
    def test_t09_shared_trace_not_causation(self):
        self.assertEqual(causal_binding(True, False, True), Verdict.INDETERMINATE)
        self.assertEqual(causal_binding(True, True, True), Verdict.VALID)
    def test_t10_exposure_scopes_not_conflated(self):
        self.assertEqual(exposure_bounds(4798255, None, None), (4798255, None, None))
        self.assertEqual(exposure_bounds(4798255, 12, None), (4798255, 12, None))
    def test_t11_invalid_exposure_counts(self):
        with self.assertRaises(ValueError):
            exposure_bounds(10, 11, None)
        with self.assertRaises(ValueError):
            exposure_bounds(True, None, None)
    def test_no_claim_without_receipt(self):
        self.assertEqual(independent_gap(False, False), Verdict.INDETERMINATE)
    def test_unverified_signature(self):
        self.assertEqual(integrity(None, True), Verdict.INDETERMINATE)

if __name__ == "__main__":
    unittest.main()
