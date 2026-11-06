# 91APP-inspired cross-system evidence boundary experiment

**Status:** Informative experimental proposal, not adopted normative text. **Incident data:** synthetic only. **No claim:** 91APP infrastructure was accessed, incident reconstructed, or VAP conformance demonstrated.

## Scope and security boundaries

This experiment defines eight original negative checks plus three additional boundary checks for an evidence consumer. It is deliberately not a production verifier. Run with `python -m unittest discover -s experiments/incident-evidence-bindings -p 'test_*.py' -v` from repository root (Python 3.10+). No network or external packages.

| Case | Evidence question | Required behavior |
| --- | --- | --- |
| T01 | Authenticated but unauthorized database request | Authorization INVALID; authentication is separate |
| T02 | Missing cross-system correlation identifier | INDETERMINATE |
| T03 | Query claims 1,000 rows but no observed result set | Confirmed count unavailable |
| T04 | No outbound telemetry | Exfiltration INDETERMINATE, never absence proven |
| T05 | Credential used after known effective revocation | INVALID under a trusted timestamp premise |
| T06 | Local event missing but independent receipt exists | Contradiction INVALID |
| T07 | Signature and Merkle proof valid; action unauthorized | Integrity VALID and authorization INVALID coexist |
| T08 | Collector outage | Confirmed count unavailable |
| T09 | Matching trace ID without trusted parent receipt | Causation INDETERMINATE |
| T10 | Maximum potential exposure but no observed read/egress | Keep all three values separate |
| T11 | Invalid or contradictory exposure counts | Reject invalid input |

## Proposed bindings (non-normative)

A future Evidence Pack may bind `system_id`, `operation_id`, `trace_id`, `actor_ref`, `credential_ref`, `policy_ref`, `policy_version`, `authorization_decision`, `observation_boundary`, `collection_status`, `result_scope_ref`, `egress_ref`, `clock_evidence_ref`, and `receipt_ref`. References must not embed raw credentials, customer PII or reversible unsalted identifiers. Each claim must identify its collector, trust boundary, timestamp uncertainty and independent witness status.

## Known limits

- Test results are properties of these synthetic functions only. They do not test SDK, EVIDECT, DB, GitLab, Appsmith or network collectors.
- The VALID enum means only that the *specified local proposition* was established by synthetic inputs, never that an incident or whole evidence pack is valid.
- Positive authorization requires actual policy/ownership validation and trusted decision-time evidence; this stub merely models the distinction.
- A valid Merkle proof does not prove complete capture, lawful operation, actor identity or recipient receipt.
- A missing correlation ID cannot be recovered cryptographically. A common ID alone is not causal proof.
- Unknown data extraction must not be rounded up to maximum potential exposure or rounded down to zero.
- Independent collection and key custody must be demonstrated rather than assumed.

## Adoption gates

1. Threat model and event semantics reviewed separately from this incident note.
2. Signed evidence schema, policy binding, privacy analysis and source trust model agreed.
3. Independent implementations with negative tests, clock and replay adversarial tests.
4. External verifier reproduction, documented gaps, versioned change control.
5. Only then consider a normative VAP extension through a separate proposal.
