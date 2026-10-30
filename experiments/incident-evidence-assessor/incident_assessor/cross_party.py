"""Authenticate a scoped imported statement without inventing XREF verification."""

from .model import InputError, digest_hex, exact_keys, strings, text, timestamp

KINDS = {"cross_provider_receipt": "provider", "cross_anchor_claim": "collector"}
TARGET_FIELDS = {"request_id", "provider_id", "tenant_id", "object_ids"}


def validate_data(kind, data):
    if kind == "cross_provider_receipt":
        exact_keys(data, {"received_at", "statement", "statement_scope"})
        timestamp(data["received_at"])
        text(data["statement"])
        strings(data["statement_scope"])
        if not data["statement_scope"]:
            raise InputError("Provider statement must name its scope")
    elif kind == "cross_anchor_claim":
        exact_keys(data, {"anchor_time", "format", "material_sha256", "record_ids", "party_ids"})
        timestamp(data["anchor_time"])
        text(data["format"])
        digest_hex(data["material_sha256"])
        strings(data["record_ids"])
        strings(data["party_ids"])
        if not data["record_ids"] or not data["party_ids"]:
            raise InputError("Anchor claims require explicit records and parties")
    else:
        raise InputError("Unsupported cross-party record kind")


def evaluate(ctx):
    result = {"receipt_attribution": "NOT_ESTABLISHED", "evidence_basis": "UNKNOWN",
              "xref_assessment": "NOT_ESTABLISHED", "anchor_verification": "NOT_SUPPORTED"}
    if not TARGET_FIELDS <= ctx.subject.keys():
        ctx.finding("cross_party_target_incomplete")
        return result
    receipts = []
    for record in ctx.bound("cross_provider_receipt"):
        received = timestamp(record.data["received_at"])
        if received > record.recorded_at or received > ctx.as_of or received < ctx.operation_at:
            ctx.finding("cross_receipt_time_inapplicable", record)
        else:
            receipts.append(record)
    if receipts:
        result["receipt_attribution"] = "ESTABLISHED_UNDER_GIVEN_ASSUMPTIONS"
        result["evidence_basis"] = "AUTHENTICATED_IMPORTED_PROVIDER_STATEMENT"
        ctx.finding("cross_receipt_authenticity_is_not_statement_truth_or_xref", *receipts)
    else:
        ctx.finding("cross_matching_authenticated_receipt_not_established")
    for record in ctx.bound("cross_anchor_claim"):
        # No supported external timestamp/anchor verifier exists in this adapter.
        # A signed claim about one never establishes a positive XREF result.
        ctx.finding("cross_external_anchor_material_not_verified", record)
    ctx.finding("cross_independent_anchored_matching_not_established")
    return result
