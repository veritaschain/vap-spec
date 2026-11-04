# Control-state evidence companion (experimental, unadopted)

This is a separate research experiment, not a VAP v1.2 requirement, conformance
verifier, production admission controller or independent reproduction. It leaves
all normative specifications, prior experiments, fixed evidence and K3 unchanged.

## What is added

The runner imports the existing `os-isolated-gate` lab without editing it. A
trusted-controller adapter records declared network memberships separately from
Docker-observed runtime state before/after agent operations and topology changes.
It captures probe results, monotonic observation times and wall-clock labels,
including the blocked second attempt and the deliberately induced bypass.

The new envelope includes those observations and the exact UTF-8 text plus SHA-256
of **all five** listed original-run artifacts: summary, runtime, environment,
cleanup and first-operation evidence. It is sealed after capture with a fresh
in-memory Ed25519 test key. Verification requires an explicitly supplied key and
run ID, checks ordering/bindings and raw artifact hashes, and returns separate
integrity, case-inventory, isolation, action and external-anchor judgments.
The original first-operation bundle keeps its original scope; it is not relabelled
as covering every action or every network path. The unchanged existing verifier
must still verify that inner bundle separately.

A valid signature on a report with case 15's bypass yields `VERIFIED` integrity
and `VIOLATED_IN_NEGATIVE_CONTROL` isolation, not a universal PASS. A full case
inventory means the expected records are present, not that the world outside the
observation boundary is complete or the controller's assertions are true.

`preflight()` is a separate, non-enforcing policy evaluator. It invalidates
observations from another run/configuration, stale/future times, empty/duplicate
scope, missing or unhealthy targets and unobserved paths. A reachable required
path is a violation even when `isolation_enabled` says true. The live adapter uses
it to expose configuration invalidation and unknown path coverage, but **does not
wire it into action admission**. Eliminating time-of-check/time-of-use races would
require a separately enforced, atomic binding to execution.

## Reproduce

Use a disposable Linux Docker Engine, Compose v2 and Python 3.12+, as required by
the original OS experiment. From the repository root:

```sh
python -m pip install -r experiments/os-isolated-gate/requirements.txt
python -m unittest discover -s experiments/control-state-evidence/tests -v
python -O -m unittest discover -s experiments/control-state-evidence/tests -v
python experiments/control-state-evidence/run.py run \
  --output experiments/control-state-evidence/generated/run-001
python experiments/control-state-evidence/run.py verify \
  experiments/control-state-evidence/generated/run-001/bundle.json \
  --trusted-key experiments/control-state-evidence/generated/run-001/test-public-key.hex \
  --run-id "$(cat experiments/control-state-evidence/generated/run-001/run-id.txt)"
(cd experiments/os-isolated-gate && python -m isolation_lab verify-evidence \
  ../control-state-evidence/generated/run-001/legacy/evidence.json)
```

Choose a new output path for every run. Existing paths and symlinks are refused.
A failed/incomplete run keeps its diagnostics and does not count as a successful
experiment. The private signing key is not written. The public key alongside a
bundle is only a reproducibility aid: obtain/pin the expected key fingerprint and
run ID through a separately trusted channel before treating a downloaded bundle
as authentic. CI logs the test fingerprint and run ID, not an independent anchor.

## Test and evidence boundary

The unit tests use synthetic inputs. They cover IPv4/IPv6/DNS/proxy labels, config
drift and missing coverage, but they do **not** establish actual network isolation.
The live run reruns the existing sixteen Linux cases and adds controller snapshots,
known internal gate-name resolution, IPv6-interface inventory and proxy-environment
presence observations. These contextual observations are not egress tests.

Arbitrary IPv6 routes, DNS tunnels, general proxy egress and host-service access
remain **NOT_ESTABLISHED**. Do not count them as blocked or silently skipped tests.
No public endpoint, host port or real target is probed by the companion. The same
controlled IPv4 topology, mock services and trusted host/controller assumptions as
the original lab apply. Additional protocol-specific live labs need their own
healthy positive controls and explicit reviewed scope before being claimed.

Sealing occurs **after** capture. There is no independent external anchor or trusted
UTC, no prevention of pre-seal omission, and no guarantee against a malicious
controller/signing key or privileged Docker operator. The code intentionally does
not claim remote attestation, per-event independent witnesses, a VAP-compliant wire
format, or proof that every real-world action was observed. JSON encoding is the
experiment's restricted deterministic encoding, not RFC 8785. Safety, factual truth
and causal correctness are not proved by a hash or signature.

The companion's Actions workflow stores fresh output as a versioned run artifact.
A successful job means expected test outcomes matched, including the intended
bypass. It does not adopt the extension, change a release, or establish commercial
or third-party deployment. No execution result is claimed by this README alone;
inspect the commit-bound CI run and its generated verification report.
