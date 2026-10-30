"""Evaluate supplied evidence without a catalogue, fixture keys, or network IO."""

from . import ADAPTER, VERSION
from . import transfer, erasure, publication, incident_response, cross_party
from .evidence import Context, digest
from .model import InputError, validate_package, validate_trust

WORKFLOWS = {
    "transfer": transfer, "erasure": erasure, "publication": publication,
    "incident_response": incident_response, "cross_party": cross_party,
}
MODULES, ROLES = {}, {}
for module in WORKFLOWS.values():
    for kind, role in module.KINDS.items():
        if kind in MODULES:
            raise RuntimeError("Duplicate implementation record kind: " + kind)
        MODULES[kind], ROLES[kind] = module, role

LIMITATIONS = [
    "Application-layer experimental assessment; no normative VAP or CAP conformance determination.",
    "Evaluator trust configuration and issuer/organization assignments are explicit external assumptions.",
    "Valid signatures attribute records; they do not independently prove claim truth or event time.",
    "Missing records cannot establish absence of activity outside the declared observation scope.",
    "Block and hold outputs are recommendations; this offline program controls no live gateway or publisher.",
    "Provider statements and limited reviews cannot establish universal external deletion.",
    "External anchoring, positive XREF, key revocation, production identity onboarding and legal compliance are not assessed.",
]


def assess(package, trust, *, allow_synthetic=False):
    if type(allow_synthetic) is not bool:
        raise InputError("allow_synthetic must be a boolean")
    validate_trust(trust)
    validate_package(package, MODULES)
    if trust["mode"] == "synthetic-test-only" and not allow_synthetic:
        raise InputError("Synthetic public test keys require explicit --allow-synthetic")
    ctx = Context(package, trust, ROLES)
    assessments = WORKFLOWS[package["workflow"]].evaluate(ctx)
    integrity = ("VERIFIED_UNDER_EVALUATOR_TRUST" if ctx.integrity_established
                 else "FAILED" if any(c["signature"] == "FAILED" for c in ctx.checks) else "INDETERMINATE")
    return {
        "format": "incident-evidence-report/0.1", "adapter": ADAPTER, "implementation_version": VERSION,
        "evaluation_id": package["evaluation_id"], "workflow": package["workflow"], "as_of": package["as_of"],
        "synthetic": trust["mode"] == "synthetic-test-only", "input_sha256": digest(package),
        "trust_sha256": digest(trust), "target_sha256": digest(package["target"]),
        "evidence_integrity": integrity, "assessments": assessments, "findings": ctx.findings,
        "evidence_checks": ctx.checks, "external_anchor_verification": "NOT_IMPLEMENTED",
        "full_vap_conformance": "NOT_ASSESSED", "full_cap_conformance": "NOT_ASSESSED",
        "legal_compliance": "NOT_ASSESSED", "limitations": LIMITATIONS.copy(),
    }
