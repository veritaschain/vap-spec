# Recorded execution evidence

The local erasure pilot executes real synthetic file creation, namespace unlink,
directory synchronization, SQLite transactions and bounded readback. It uses no
real provider or personal data. Public case exports retain original signed
evidence and public pins, with no private keys or object plaintext.

CI records will be retained here after execution at a concrete commit. A
configured workflow is not evidence that an execution succeeded. The workflow
requires Python 3.12 and 3.14, zero skipped tests, strict resource/finalizer error
handling, all 18 scenario expectations, an offline export recheck and unchanged
core-assessor checks.

Full case exports are GitHub Actions artifacts with 30-day retention. This
directory retains summary records and CI identifiers; summaries alone cannot
reconstruct original signed case evidence or satisfy `verify-exports`.

Rechecking requires the matching tested source manifest. It validates captured
statements under the recorded controller pins and does not perform new deletion,
prove honest execution, establish independent verification or assert universal
erasure. The runtime directory and SQLite files are not uploaded.
