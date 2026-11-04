# Probe result serialization correction, 2026-11-04

Status: experimental and unadopted, as in README.md. This is not a VAP wire-format change.

The first Linux companion run (Actions run 41747377856, source d7ebf3bce46c136d9542675c70c34547532df0bb) completed all sixteen expected case observations but failed while sealing the companion envelope. Actual probe results contained fractional `before_send_ms` and `total_ms`; the restricted outer canonicalizer rejects floats. That run is not a successful companion execution and its artifacts are not replaced or relabelled.

`probe-result` observations now retain role and arguments alongside `result_json`, consisting of UTF-8 JSON text and its SHA-256. This text is a serialization of the already parsed probe result, not an assertion that original HTTP or process-output bytes were retained. Finite timing values are retained without integer rounding or omission. The outer canonical encoding still rejects floats. Verification checks the embedded digest and JSON object shape, rejects duplicate keys and non-finite numbers (including numeric overflow), and verifies the enclosing signature.

Fourteen new synthetic regression tests exercise this boundary. They do not establish operating-system isolation. Check the new commit-bound Linux workflow for runtime evidence; a valid signature remains separate from isolation and safety. Case 15 must remain a detected intentional bypass, and external anchoring and unmeasured alternative paths remain not established.
