# PR #12 final review — unadopted research implementation

Review scope: the new Linux lab, HTTP transport wrapper, synthetic key setup,
probe acceptance conditions, cleanup, output/provenance handling, recorded
results and CI. This review concerns merging research implementation only; it
neither adopts an extension nor assigns a formal number or applicable release.

## Corrections made before merge

1. **Incomplete permission evidence could pass.** Removing all foreign-role
   canary observations still satisfied the old `all(...)` expression. The new
   predicate requires the exact five-role inventory and all five observations
   per role, including the expected kernel error for each of twenty foreign-role
   reads. Missing/extra entries, incorrect errors and non-boolean permissions
   cannot pass. Mount verification now requires the exact private config/data
   volumes and shared non-secret canary volume, with their correct access modes;
   the separately reported Docker tmpfs configuration is also checked.
2. **Failed cleanup inspection could look like successful deletion.** A failed
   image-removal command followed by an inspection error previously returned
   success. Cleanup now requires successful removal for a built image and a
   successful, empty image-list query. An unavailable daemon or failed query
   leaves absence unconfirmed and prevents a passing run. The temporary seed
   directory is still cleaned in the error path.
3. **Reruns could retain stale evidence.** An early failure in a reused output
   directory left the previous run's evidence alongside a new failure summary.
   Provisioning now requires a new directory, rejects existing directories and
   symlinks before creating a lab, and preserves previous results. Use a fresh
   `--output` path for each repeat run.
4. **Provenance omitted imported code from the local dirty check.** The snapshot
   now covers the imported gate/verifier code, requirements and dedicated
   workflow, with separate content digests. Source/commit changes during a run
   invalidate completion. No imported source file was modified to add this check.

The previous complete CI observation record is not alleged to be false: it had
the full inventory and successful cleanup. The counterexamples exposed ways that
future incomplete or failed executions could have been misreported. New regression
tests exercise those paths. The refreshed Linux execution record is linked from
[results/README.md](results/README.md).

## Preserved boundary

Only `experiments/os-isolated-gate/` and its dedicated workflow are changed from
base `2d4fda80b9e26cbaa51112fb2a65fdfb51d2bd1f`. VAP v1.2, the existing verifier,
the existing gate, proposal text, DOC-SYNC and K3 remain unchanged. Both verifier
modes are rechecked using the existing implementation.

The deliberate negative control must still produce a direct effect at the
unauthenticated API when the controller adds a route. Its bypass guarantee remains
false. Host/kernel/controller compromise, IPv6, host services and other real API
routes are outside this experiment; no production or independent-reproduction
claim is added. Saved cryptographic evidence covers only the first authorized
operation, not the OS observations or blocked second operation.

## Validation

Corrected source `1e8e497f2082cb11b7d2f7da1278205f1449a774` passed
[Linux CI run 40058076259](https://github.com/veritaschain/vap-spec/actions/runs/40058076259):
28 new regression tests, all 16 OS experiment expectations, the unchanged gate's
46 regressions / 15 scenarios / 11 exported bundles, and the unchanged verifier's
64 regressions / 14 acceptance cases. The downloaded evidence was also rechecked
locally with the unchanged validator; this was not a local Linux OS execution.
The refreshed record includes a successful image-list query and confirmed
absence after cleanup. No unresolved blocking finding remains in this review;
listed experimental limitations remain in force.
