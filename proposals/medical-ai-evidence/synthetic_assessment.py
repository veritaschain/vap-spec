"""Illustrative evidence classifications, not a clinical or VAP verifier.

Only supplied evidence enters this function. Scenario IDs and expected results
belong to the tests. Labels describe declarations and comparisons; none
authenticates a record, an anchor, or a clinical decision.
"""

import re

_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
DIMENSIONS = (
    "check_execution", "display", "patient_context", "submitted_batch",
    "collection", "translation", "provider_state", "replay",
)


def _compare_digests(first, second, *, different, equal):
    if not all(isinstance(value, str) and _DIGEST.fullmatch(value)
               for value in (first, second)):
        return "UNKNOWN"
    return equal if first == second else different


def assess(evidence):
    """Classify supported dimensions without reading test expectations.

    Missing, malformed, or unsupported evidence remains UNKNOWN. A simulated
    manifest-bound flag is a fixture declaration, not an authenticated binding.
    """
    if not isinstance(evidence, dict):
        raise TypeError("Evidence must be an object")
    result = {dimension: "UNKNOWN" for dimension in DIMENSIONS}

    check = evidence.get("check_status")
    if isinstance(check, str):
        result["check_execution"] = {
            "not_run": "NOT_RUN", "timeout": "UNKNOWN", "unknown": "UNKNOWN",
            "passed": "REPORTED_PASSED", "warning": "REPORTED_WARNING",
            "failed": "REPORTED_FAILED",
        }.get(check, "UNKNOWN")

    result["display"] = _compare_digests(
        evidence.get("draft_digest"), evidence.get("display_digest"),
        different="DIVERGENCE", equal="SAME_COMMITMENT",
    )

    fields = evidence.get("patient_fields")
    if isinstance(fields, list) and all(isinstance(item, str) and item.strip()
                                       for item in fields):
        # This example checks declared field presence, never clinical necessity
        # or the adequacy/correctness of a field's value.
        result["patient_context"] = (
            "PRESENT" if "renal_function" in fields else "MISSING"
        )

    anchored = evidence.get("anchored_count")
    submitted = evidence.get("submitted_count")
    if (evidence.get("manifest_bound") is True
            and type(anchored) is int and anchored >= 0
            and type(submitted) is int and submitted >= 0):
        result["submitted_batch"] = (
            "INCOMPLETE_SUBMISSION" if submitted < anchored else
            "COUNT_CONFLICT" if submitted > anchored else "COUNTS_MATCH"
        )

    coverage = evidence.get("collector_coverage")
    if isinstance(coverage, str):
        result["collection"] = {
            "partial": "UNOBSERVED", "full": "DECLARED_FULL",
        }.get(coverage, "UNKNOWN")

    parent = evidence.get("parent_ref")
    if isinstance(parent, str) and parent.strip():
        result["translation"] = _compare_digests(
            evidence.get("original_digest"), evidence.get("translated_digest"),
            different="DERIVATIVE", equal="SAME_COMMITMENT",
        )

    provider = evidence.get("provider_filter_state")
    if isinstance(provider, str):
        result["provider_state"] = {
            "passed": "REPORTED_PASSED", "warning": "REPORTED_WARNING",
            "failed": "REPORTED_FAILED", "not_run": "REPORTED_NOT_RUN",
        }.get(provider, "UNKNOWN")

    result["replay"] = _compare_digests(
        evidence.get("original_digest"), evidence.get("replay_digest"),
        different="REPLAY_DIFFERS", equal="SAME_COMMITMENT",
    )
    return result
