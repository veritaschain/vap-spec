# Handling external results — operating note

This note concerns kit `b1af0dc` and subject `c8ccf97`. It adds no protocol
requirements and changes no test expectations. The experimental extension remains
unadopted. Independent third-party reproduction has not been established by the
internal CI records distributed with the kit.

| Observation | Record and next action | Permitted conclusion |
| --- | --- | --- |
| Environment differs or execution cannot start | Preserve actual versions, errors, attempted commands and support received. Classify as unable to execute or incomplete. Agree any environment repair, then record a separate attempt. | The documented procedure did not complete in that environment; do not relax fixed inputs or expected results to claim success. |
| False acceptance or undetected missing evidence | Preserve the triggering input, original output and failed criterion. Register a defect against the exact version. Publish a correction/advisory linked to that version; develop any repair separately. | The affected version failed that evaluation. Do not count the affected evaluation as a successful reproduction. |
| Results match expectations | Review complete outputs, fresh-execution provenance, support and relationships, then obtain the separate publication permissions. | Reproduction of the stated observations in the named environment, versions and test scope, subject to the separately assessed independence. |
| VSO performs or materially assists execution | Record exactly who ran which steps and who controlled the host, plus all assistance. Preserve useful results. | Assisted external execution, unless a separate, evidenced independence assessment supports a narrower independent claim. |

Never overwrite a previously distributed ZIP or quietly replace historical
results. New code, environments or reruns receive separate version/attempt
identifiers, hashes and evidence. Retain failed runs and describe corrections in
separate notes. Do not modify a checksummed output directory to insert reports,
consent notes or a revised independence label.

Matching tests do not imply specification adoption, production suitability,
capture of every real-world action, regulator endorsement or certification.
Keep VAP v1.2, the existing verifier, gate, OS experiment and K3 conditions separate.
Use the existing [evaluator report and evidence-retention procedure](https://github.com/veritaschain/vap-spec/blob/b1af0dc9d368b466bf74e7c1b2a6808fb41949ae/reproduction/os-isolation/REPORTING.md)
and the [separate proposed consent terms](EVALUATION-TERMS.md).
