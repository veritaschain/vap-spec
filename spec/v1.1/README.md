# VAP Framework Specification v1.1

**Document ID:** VSO-VAP-SPEC-001  
**Version:** 1.1.0  
**Status:** Draft Specification  
**Release Date:** 2025-12-11

---

## Version Status

| Status | Meaning |
|--------|---------|
| **Draft** | Under development, subject to change |
| **Candidate** | Feature-complete, public review period |
| **Stable** | Released, backward-compatible changes only |
| **Superseded** | Replaced by newer version |

**Current Status: Draft**

---

## What's in v1.1

This version introduces:

- High-Risk AI Domain definitions (Section 2)
- VAP/VSO/VCP hierarchy clarification
- Four-layer architecture formalization
- Crypto-shredding requirements for GDPR compliance
- Conformance level definitions (Core/Standard/Full)

---

## Backward Compatibility Policy

| Change Type | Policy |
|-------------|--------|
| New optional fields | ✅ Allowed in minor versions |
| New required fields | ⚠️ Requires major version |
| Field removal | ❌ Not allowed (deprecate first) |
| Semantic changes | ⚠️ Requires major version |

**v1.1 is backward-compatible with v1.0.**

---

## For Profile Implementers

When implementing a VAP profile (VCP, CAP, DVP, etc.), reference these sections:

| Requirement | Section |
|-------------|---------|
| Core layers | Section 4 |
| Data model | Section 7 |
| Cryptographic requirements | Section 6 |
| Conformance levels | Section 8 |

---

## Files in This Directory

| File | Description |
|------|-------------|
| `VAP_Framework_Specification.md` | Full specification document |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-11 | Initial Release |
| 1.1.0 | 2025-12-11 | High-Risk AI Domains, hierarchy clarification |

---

## Related Documents

- [VCP Specification v1.1](https://github.com/veritaschain/vcp-spec/tree/main/spec/v1.1)
- [CAP Specification v0.2](https://github.com/veritaschain/cap-spec)

---

<p align="center">
  <strong>VeritasChain Standards Organization</strong>
</p>
