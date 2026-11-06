"""Experimental evidence result envelope. Not a signed VAP Evidence Pack."""
from dataclasses import dataclass, asdict
from typing import Literal
import json

Verdict = Literal["VALID", "INVALID", "INDETERMINATE"]
PROPOSITIONS = ("integrity", "authorization", "causality", "observed_read", "observed_egress")

@dataclass(frozen=True)
class Claim:
    verdict: Verdict
    evidence_refs: tuple[str, ...] = ()
    reason: str = ""

def make_result(claims: dict[str, Claim], *, case_id: str, synthetic: bool = True) -> dict:
    if not synthetic:
        raise ValueError("experimental results may only be synthetic")
    if not case_id or not isinstance(case_id, str):
        raise ValueError("case_id required")
    if set(claims) != set(PROPOSITIONS):
        raise ValueError("all five independent propositions required")
    output = {}
    for name, claim in claims.items():
        if claim.verdict not in ("VALID", "INVALID", "INDETERMINATE"):
            raise ValueError("unsupported verdict")
        if claim.verdict == "VALID" and not claim.evidence_refs:
            raise ValueError("VALID requires an evidence reference")
        if any(not isinstance(ref, str) or not ref or "://" in ref for ref in claim.evidence_refs):
            raise ValueError("evidence references must be nonempty opaque local IDs")
        output[name] = asdict(claim)
    return {"schema": "experimental-evidence-result-v0", "synthetic": True,
            "case_id": case_id, "claims": output,
            "disclaimer": "Not a signed Evidence Pack or VAP conformance result"}

def encode_result(result: dict) -> bytes:
    return json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
