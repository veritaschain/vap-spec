# Reproducing pinned incident experiments after implementation changes

Updated 15 November 2026. The current incident assessor and retention adapter
reject weak configured Ed25519 keys. Three older experiments deliberately pin
the earlier assessor and related files. Their hashes identify historical inputs
and are not rewritten to accept newer implementation bytes.

| Experiment | Declared source commit | Pin source |
| --- | --- | --- |
| Incident recheck kit | `b72bbf05c912f5b87560f4c809298c7bbcaf05e4` | `incident-recheck-kit/source-lock.json` (`source_commit`) |
| Incident review report | `1553ff9729ceb30f3ff03513cead45c5b7abd1d9` | `incident-review-report/toolchain-lock.json` (`kit_commit`), 136 fixed files |
| Incident collector pilot | `433f019513d991982fc6fb08bd4529808cc9f6a1` | `incident-collector-pilot/dependency-lock.json` (`upstream_commit`), 154 fixed files |

Each affected CI workflow checks out the current candidate and its recorded
source commit separately. It copies only its own experiment directory and own
workflow into the historical source checkout, then runs the existing checks.
Sibling pinned implementations, source locks, captured evidence and original
results retain their original bytes. The current assessor/retention workflows
test the hardened current code separately.

A successful historical recheck establishes only the declared historical
experiment's result. It does not test the hardened assessor, upgrade the old
archives, establish a production key policy or provide independent verification.
New candidate output is captured as a new result. Do not relabel old results
or change expected dependency digests just to make a mixed checkout pass.

## Local reproduction

Choose the experiment and corresponding source commit from the table. From
the repository root, with the experiment's pinned dependencies installed:

```sh
experiment_name=incident-collector-pilot
source_commit=433f019513d991982fc6fb08bd4529808cc9f6a1
git fetch --no-tags origin "$source_commit"
snapshot_dir="$(mktemp -d)"
git archive "$source_commit" | tar -x -C "$snapshot_dir"
cp -R "experiments/$experiment_name" "$snapshot_dir/experiments/"
cp ".github/workflows/$experiment_name.yml" "$snapshot_dir/.github/workflows/"
cd "$snapshot_dir/experiments/$experiment_name"
python -W error::ResourceWarning run_tests.py
```

Use the same staging steps for the other rows. Their existing entry points are:

```sh
# In the staged incident-recheck-kit directory; choose a new output path:
python -W error::ResourceWarning record_run.py --output generated

# In the separately staged incident-review-report directory:
python -W error::ResourceWarning record_run.py --output generated

# In the staged incident-collector-pilot directory after its tests:
python -m collector_pilot run-suite --output generated --print-summary
python -m collector_pilot verify-exports generated/public --expected-summary-sha256 "$(cat generated/summary.sha256)"
```

Installation and fetching missing source commits may require network access.
The collector tests use controlled local processes and loopback HTTP; rechecking
the saved records does not repeat upload, publication or erasure operations.
