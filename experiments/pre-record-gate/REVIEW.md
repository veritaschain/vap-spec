# Implementation review record

Status: experimental, unadopted; intended for a separate Draft PR. No normative adoption is requested.
Source reviewed and exercised: `56a98eec87339193831f4c78607de5b259745edc`.

The review checked the gate's fail-closed ordering, exact request/authorization binding, concurrency,
response loss, unresolved-state retention, read-only recovery, native signature verification and
claims in both languages. Follow-up corrections before that commit included:

- Prevent reusing a prepared operation ID with a different authorization envelope, even for identical intent.
- Recheck identity/delegation/approval and signed status in the evidence adapter; do not accept only an audit assertion.
- Check actual dispatch intent and original request binding, event ordering and nested native backend receipts.
- Keep storage failure after an external commit as unknown, with the earlier dispatch intent retained.
- Close HTTP error responses and SQLite connections explicitly; regression execution treats resource warnings as errors.

The positive boundary is narrow: an honest trusted gate/audit/backend and a keyless or agent-key-only caller.
The agent and service roles use separate directories, keys, processes and databases, but the same OS user.
The intentionally insecure backend test demonstrates that leaving a direct accepted path defeats the guarantee.
No successful-bypass result is converted into a positive deployment claim.

The unchanged verifier evaluates submitted evidence, not network enforcement. Scope mode remains unadopted;
current-spec mode has no scope result. Pending result evidence is indeterminate; a final submission with
missing required result evidence is not met, without inferring nonoccurrence. Synthetic receipt signatures
are checked, but no independent timestamp, externally operated anchor or real-world identity assurance is claimed.

Validation records are under `results/`: 31 new regressions, 15 gate scenarios, 11 offline evidence-bundle
rechecks, plus the existing 64 regressions and 14 declared-scope cases. CI separately repeats these checks on
Python 3.12 and 3.14; the PR's actual check status is the authority for whether those CI runs have completed.

Diff boundary: only `experiments/pre-record-gate/` and its new CI workflow are added.
The v1.2 specification, DOC-SYNC, K3, existing proposal and existing verifier source/test artifacts remain unchanged.
Remaining limitations and operational recovery costs are explicit in the README; this is not a production release.
