# Final review record — PR #11

Status: **experimental, unadopted**. This review supports merging the bounded research implementation;
it is not normative adoption, production approval or independent third-party reproduction.
No formal proposal number or target release is assigned.

Reviewed initial PR head: `9343953e9754e15da409f5cffcbe0d7e4a7f7bd5`.
Corrected implementation and test source: `f34c2f51ab2afb4c28fce06db77953dd56cd54e1`.

## Findings corrected before integration

1. **Acknowledgment semantics:** a signed acknowledgment was checked for operation binding but not the
   requested durable state. A signed dispatch-intent acknowledgment could be mistaken for a saved result,
   and a contradictory claim acknowledgment could reach the backend. State/receipt shape and action-specific
   state transitions now fail closed. Malformed acknowledgments do not escape as an uncaught gate error.
2. **Known outcomes:** reconciliation could return unknown when a valid success receipt was already durable
   but the backend was offline. Concurrent confirmation could also be reported as a newly persisted unknown
   event or a failed claim. Valid durable confirmation now remains success, without an extra write or lookup.
3. **Mutable caller input:** replacing the caller's request after pre-recording could change the request
   being authorized at the final check while leaving the original dispatch intent in use. The gate now owns
   a canonical request snapshot and checks that the refreshed authorization binds the same intent.
4. **Export completeness and bindings:** the offline recheck could exit successfully on an empty case list
   or silently skip absent bundles. It now requires the exact case inventory, no duplicates/path escapes,
   all expected primary/recovery bundles, matching expectations/reports, scope/operation binding, and a
   confirmed recovered result. Impossible unknown-after-confirmed event order is rejected by the adapter.

The first seven focused regression reproductions failed or errored on the reviewed head before repair.
The final review added fifteen regression tests in `tests/test_review.py`, covering these failures and
related missing-evidence, state-concurrency and binding cases. All are passing in the recorded local run.

## Validation and separation

The corrected source was tested with a clean experiment working tree on Python 3.14.3/macOS:

- 46 gate regression tests passed; all 15 gate scenarios matched their declared expectations.
- 11 public evidence bundles rechecked offline, with actual Ed25519 signatures and both verifier modes.
- Existing verifier: 64 regression tests passed; all 14 synthetic declared-scope cases matched.
- Signed evidence, public synthetic trust, raw test logs, source digests and local latency samples are in `results/`.

The dedicated CI repeats both experiments on Python 3.12 and 3.14. The actual checks attached to the final
PR head determine CI completion; local execution and project CI are not independent reproduction.
The older evidence remains available in Git history; `results/` now records the corrected source above.

The full PR diff is limited to `experiments/pre-record-gate/` and `.github/workflows/pre-record-gate.yml`.
VAP v1.2, the existing verifier and its test artifacts, the declared-scope proposal, DOC-SYNC and K3 remain unchanged.
The verifier evaluates evidence; the execution gate remains a separate product-side experiment.

## Remaining claim boundaries

The trusted roles share one OS user. Only the mock application credential boundary is exercised; hostile
same-user/administrator access, production egress isolation, real identity integration, independently
operated anchors, accurate external time, production readiness and buyer demand remain unestablished.
The intentionally insecure backend test exposes a successful bypass and labels that guarantee false.
All authority/receipt keys and clocks are synthetic and controlled by the test harness.
The exported authorization snapshot represents the pre-record check; the final refresh is a gate check,
not a separately signed authorization decision. Continuous revocation assurance is not claimed.

A matching negative-control test is not a deployment endorsement. Integration of this code does not alter
the adoption status of the experimental scope extension or turn it into a VAP v1.2 execution requirement.
