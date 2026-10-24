# Final implementation review — 2026-10-24 JST

Reviewed the implementation introduced through PR #10 head `c13cac3239d2d88bb96763b805f23220801425ee`.
The review found issues not covered by the original 14 scenarios or 49 regression tests. The following
repairs are part of implementation 0.1.1, and the regression suite now contains 63 tests.

| Finding | Repair and regression coverage |
| --- | --- |
| A known inventory suppressed additional individually required obligations, allowing an incorrect `met`. | Always reconcile their union; deduplicate identical obligations and reject conflicting definitions. |
| An unsupported derivation rule returned early and hid independently provable violations. | Preserve unresolved-set diagnostics while continuing checks supported by separately approved individual obligations. |
| Python equality treated JSON booleans and numbers as equal, allowing a false relationship match. | Compare canonical JSON values, including nested types. |
| Malformed role/source lists could use substring membership; null gaps could act as an empty list; a non-object extension raised an unhandled exception. | Validate the relevant objects, bounded arrays and string identifiers before interpreting them. |
| INT-006 inherited unrelated event-signature failures when its own anchor evidence was merely unresolved. | Aggregate only anchor, receipt, policy-binding and Merkle-proof dependencies. |
| A derived inventory could be reported with a complete count while source closure or gaps remained unresolved. | Leave the full derived set/count unresolved until closure is supported, available and free of reported gaps. |

Additional tests cover identical individual obligations, incomplete source inventories and unsupported clock
semantics. Unknown time units/intervals cannot establish deadline violations. The 14 original acceptance
outcomes remain unchanged, including mode separation and the distinction between cryptographic integrity,
INT-008 completeness and experimental fulfillment. Actual executions and source provenance are recorded in
[results](results/README.md); the snapshot recording commit follows the tested code commit.

The merge scope is **research code, synthetic evidence, tests and discussion documents only**:

- `vap-v1.2` does not require experimental sidecars and does not produce a scope-fulfillment result.
- `experimental-scope` continues to label the extension `experimental_unadopted`.
- Normative files under `spec/`, DOC-SYNC, K3/program materials and scorecards are unchanged.
- Formal proposal number and target release remain unassigned/undecided. Repository integration is not adoption.
- Production external anchoring, complete VAP conformance and organizationally independent reproduction remain unestablished.

This is an internal code review and synthetic test record, not an external independent audit or an adoption decision.
