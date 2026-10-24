# Independent reproduction kit: OS-isolated mock gate

**Research only. Experimental extension remains unadopted.** This package makes
another evaluator's execution possible; publishing it or passing its CI does not
establish independent reproduction, VAP conformance, adoption, or production readiness.
**Independent third-party reproduction has not been established.**

The subject is the merged PR #12 implementation at
[`c8ccf972196a16d11429a478f4918a08fe27bb73`](https://github.com/veritaschain/vap-spec/commit/c8ccf972196a16d11429a478f4918a08fe27bb73).
The package is a separate orchestrator, expected-observation comparator and report
format. It changes **neither VAP v1.2 / DOC-SYNC / K3 nor the existing verifier,
pre-record gate, OS-isolation lab or their tests**. It imports their frozen code to
recheck actual signatures, hashes and bindings. It does not add a new verifier.

[日本語の実行手順](RUN-ja.md) · [Expected results](EXPECTED-RESULTS.md) ·
[Evidence and evaluator reporting](REPORTING.md)

## Environment and trust boundary

Use a disposable **native Linux host or Linux VM**, with Git, Python 3.12+, venv,
pip, rootful Linux Docker Engine and Compose v2 already installed. The operator
must be able to use that daemon. Do not run against production workloads. The
host, operator, Docker daemon and controller are trusted; containers are not a
boundary against a privileged host. macOS/Windows controllers, rootless Docker
and daemon user-namespace remapping are outside this kit's supported setup.

The recorded reference environment is Ubuntu 24.04 x86_64, Python 3.12.15,
Docker 28.0.4, Compose 2.38.2 and kernel 6.17.0-1022-azure. These describe the prior
internal run, not a byte-identical VM image. The kit records actual versions and
flags deviations, rather than silently claiming equivalence. Python dependencies
are exact: cryptography 50.0.2, rfc8785 0.1.4, cffi 2.1.1, pycparser 3.12. The existing
Dockerfile pins the runtime base by digest in `source-lock.json`. The host kernel,
Docker, Python installation and package indexes are not supplied or attested by
this kit. This is **not an air-gapped or fully hermetic distribution**: first-time
setup needs GitHub, the configured Python package index and container registry.

Only the lab controller creates/deletes its uniquely named containers, networks,
volumes and temporary image. The negative controls intentionally add a route and
call an unauthenticated **mock** API. No external service or real credential is
used. The setup role temporarily runs as root to initialize per-role volumes;
the five tested service roles run as separate non-root UIDs.

## Obtain and check the kit

Check out the package revision you intend to review, then package it:

```sh
python3 reproduction/os-isolation/reproduce.py pack --output /absolute/path/kit.zip
```

Alternatively download the kit ZIP from this PR's `Independent reproduction kit`
CI artifact. Record its workflow URL, package commit and SHA-256. Extract it to a
fresh directory. From inside `vap-os-isolation-kit/`:

```sh
sha256sum -c SHA256SUMS
KIT_DIR="$PWD"
```

The per-file checksums detect corruption relative to the supplied manifest;
they **do not authenticate its author**. Obtain the package revision and ZIP
checksum through the evaluator's chosen trusted channel. The ZIP contains only
this kit, not the implementation, prior successful outputs, private keys or venv.

## Fetch the frozen subject independently

Choose a new working directory outside the kit. All paths below are absolute;
replace `/absolute/path/reproduction-work` once with your chosen empty location.

```sh
WORK_DIR=/absolute/path/reproduction-work
mkdir "$WORK_DIR"
git clone --no-checkout https://github.com/veritaschain/vap-spec.git "$WORK_DIR/source"
git -C "$WORK_DIR/source" checkout --detach c8ccf972196a16d11429a478f4918a08fe27bb73
python3 "$KIT_DIR/reproduce.py" verify-source --source "$WORK_DIR/source"
python3.12 -m venv "$WORK_DIR/venv"
"$WORK_DIR/venv/bin/python" -m pip install -r "$WORK_DIR/source/experiments/os-isolated-gate/requirements.txt"
"$WORK_DIR/venv/bin/python" "$KIT_DIR/reproduce.py" preflight --source "$WORK_DIR/source"
```

`verify-source` uses only the standard library. It requires the exact commit,
a clean checkout, no ignored execution inputs, and matching SHA-256 values for
all tracked files in the three experiment directories and the lab workflow.
Do not create the venv or outputs inside the source checkout. Child executions
suppress bytecode generation. Do not edit expectations to turn a failed run green.

## Execute and recheck

One command runs all three existing regression suites, all three scenario suites,
and saved-evidence rechecks. `results-001` **must not already exist**.

```sh
"$WORK_DIR/venv/bin/python" "$KIT_DIR/reproduce.py" run --source "$WORK_DIR/source" --output "$WORK_DIR/results-001"
"$WORK_DIR/venv/bin/python" "$KIT_DIR/reproduce.py" check --source "$WORK_DIR/source" --output "$WORK_DIR/results-001"
```

The `run` command makes fresh mock keys and evidence and exercises actual Linux
permissions/network probes through the original lab. It records each step's log,
return code and unit-test count. A regression step requires the exact count and
a plain successful unittest conclusion: skipped tests and expected failures do
not count as a complete passing run. Each child has a ten-minute execution limit;
interruptions or timeouts are incomplete runs, never evidence of isolation.
`check` requires the same kit revision and frozen source and rechecks the output
inventory, hashes, counts, stable observations and cryptographic evidence. Recorded
Python and dependency versions in each gate/verifier report must agree with
preflight, and recorded dependencies must match the lock. It does
**not** rerun the OS probes or authenticate the operator's account of execution.

Expected totals: **28 + 46 + 64 regression tests; 16 OS cases; 15 gate scenarios
with 11 evidence bundles; 14 verifier cases in both modes**. See the explicit
negative-control interpretation in [EXPECTED-RESULTS.md](EXPECTED-RESULTS.md).
`run-report.json` reports `matched` only after all steps and final source checks.
The report always keeps `independence: not_assessed`,
`independent_reproduction: not_established`,
`proposal_status: experimental_unadopted`, and `overall_vap_pass: null`.

Exit codes: 0 = requested operation completed (for `run`/`check`, expected results
matched); 1 = `run` started but was incomplete or mismatched; 2 = invalid input,
preflight/check failure or other command error. A zero code never means overall
VAP conformance or guaranteed bypass prevention.

Finally retain the complete output directory and complete the separate
[evaluator report](templates/evaluator-report.json). Never insert that report into
an already checksummed result directory. Report failures and deviations as well
as successes. Independent reproduction requires a separate evaluator's actual
execution and evidence; the package cannot award that status automatically.
