# Recorded Linux execution — 2026-10-24

**Experimental, unadopted.** This is an internally run synthetic experiment on a
GitHub-hosted Linux runner. It is not independent reproduction, a production
security assessment or adoption of a VAP requirement.

The retained run is [40058076259](https://github.com/veritaschain/vap-spec/actions/runs/40058076259),
at source commit `1e8e497f2082cb11b7d2f7da1278205f1449a774` (clean checkout), based
on merged PR #11 commit `2d4fda80b9e26cbaa51112fb2a65fdfb51d2bd1f`.
The experiment source digest is
`bfeac73d4b4dec705afa2f75ad767329198adac8de2520499f3c2cc561623322`.
This supersedes the initial record; the original run remains available in
[commit 11c7e3b](https://github.com/veritaschain/vap-spec/blob/11c7e3b/experiments/os-isolated-gate/results/README.md).
See [the final review](../FINAL-REVIEW.md) for the corrected failure paths.
Later documentation/artifact commits do not retroactively change that provenance.
Separate fingerprints for the imported gate/verifier and workflow are now included.

The job ran on `ubuntu-24.04`: Linux `6.17.0-1022-azure`, Docker Engine `28.0.4`,
Compose `2.38.2`, controller Python `3.12.15`. The runtime image's exact base digest
is pinned in the Dockerfile; the built image ID is in the inspection record.

| Verification | Actual result |
| --- | --- |
| New controller/transport/reporting regression tests | 28 passed |
| Actual Linux isolation experiment | 16/16 expected outcomes matched |
| Unchanged gate regression tests | 46 passed |
| Unchanged gate scenarios | 15/15 matched |
| Unchanged gate exported-evidence recheck | 11 bundles verified |
| Unchanged verifier regression tests | 64 passed |
| Unchanged verifier synthetic acceptance cases | 14/14 matched |
| New lab's saved evidence bundle | Native signatures/bindings and both reports rechecked |
| Scoped cleanup | Containers/volumes/networks and temporary image removed; exit codes 0 |

## What the observations show

- Five runtime UIDs/GIDs were 10001–10005. All had zero effective/permitted/bounding
  capabilities, `NoNewPrivs=1`, `Seccomp=2`, and distinct mount/PID/network namespace
  IDs. Each attempted `setuid(0)` received `EPERM`.
- Each role could read its own test canary; all twenty foreign-role combinations
  received `EACCES`. Config writes were denied; code writes received `EROFS`.
  Inspection found role-private, read-only config mounts and no seed/engine socket.
- The authorized path reached the backend once and created one effect. Direct
  agent connections to literal IPv4 addresses of the authenticated API, audit and
  unauthenticated comparison API failed with `ENETUNREACH` (errno 101), while each
  target remained healthy. API handler/effect counters did not change.
- The unsupported target, proxy path and CONNECT attempts made no extra effect.
  Removing the agent's disposable log did not alter the signed audit evidence.
- With audit stopped, a second separately authorized operation returned `blocked`
  with no backend attempt. Restart preserved the first result; retry made no
  additional backend request or effect.
- **Negative control:** after the trusted controller added the backend network to
  the agent, the normal API became reachable but returned 403. Its request counter
  increased to 2 while effects stayed at 1. The unauthenticated comparison API
  accepted a direct call (200) and created one effect. Case 15 explicitly records
  `bypass_guarantee_established: false`.
- Removing that added route restored `ENETUNREACH`, with the comparison API still
  healthy and no further effect. Expected negative-control success must not be
  described as universal bypass prevention.

The evidence bundle covers **only the first authorized operation**: request,
dispatch intent, result. Both verifier modes reported integrity `verified`;
`vap-v1.2` left scope fulfillment null, and the unadopted `experimental-scope` mode
reported `met` for those three obligations. It does not cover the second blocked
attempt or cryptographically attest all OS observations. The scope receipt uses
a test key and provides no independent time attestation.

## Retained artifacts and recheck

`linux-2026-10-24/` contains the unmodified downloaded JSON observations, sanitized
runtime inspection, environment and cleanup records, the actual signed evidence,
and the old suites' summary files. `validation.log` retains the relevant CI step
lines (terminal color sequences removed). `sha256.json` records byte hashes for
these files; it is an integrity inventory, not an external attestation. No seed
or private key is retained.

From `experiments/os-isolated-gate/`, after installing requirements:

```sh
.venv/bin/python -m isolation_lab verify-evidence results/linux-2026-10-24/evidence.json
.venv/bin/python -m isolation_lab run-suite
```

The first command rechecks saved cryptographic evidence under its explicitly
synthetic trust configuration. It was also run locally on macOS with Python 3.14;
that is an offline cryptographic recheck, **not another Linux execution**. The
second command requires Linux Docker and runs fresh probes with fresh keys.
Hashes, UIDs' namespace IDs, IP assignments, image IDs and timings can differ.

VAP v1.2, the existing verifier/gate, the proposal text, DOC-SYNC and K3 are not
modified by this PR. The trusted host, controller and kernel remain outside the
adversarial scope. IPv6, host services, alternate real API routes and privileged
host/kernel attacks remain untested. Full trust boundaries are in the parent
README; nothing in this record establishes production readiness.
