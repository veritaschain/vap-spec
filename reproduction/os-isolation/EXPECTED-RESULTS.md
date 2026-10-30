# Expected observations and interpretation

Machine-readable comparisons are in `expected-results.json`; executable source,
acceptance policies and tests are fixed by `source-lock.json`. No expectation
update is performed during a run. All data, authority keys, trust keys and
receipts are synthetic. Mock receipt verification does not establish external
time attestation. The synthetic evaluation time is supplied by the frozen suites,
not substituted with wall-clock time.

| OS case | Required observation |
| --- | --- |
| 01 | Five distinct non-root UIDs/GIDs; no supplementary root group; zero effective/permitted/bounding capabilities; no-new-privileges; seccomp; setuid(0) denied; distinct mount/PID/network namespaces. |
| 02 | Each role reads its own configuration/canary; all four foreign canaries deny access. Complete role/canary inventories required. |
| 03 | Code and role configuration writes denied by permission/read-only errors; root filesystem read-only; exact own config/data and shared canary mounts; restricted tmpfs; no Docker socket or seed visible. |
| 04 | Only declared internal networks, exact role membership, no published ports or privileged services. |
| 05 | Authorized gate request confirms success; backend requests/effects go from 0/0 to 1/1. |
| 06 | Direct connection from agent to healthy protected backend denied; counts remain 1/1. |
| 07 | Direct connection from agent to healthy audit service denied; backend counts remain 1/1. |
| 08 | Direct connection to healthy unauthenticated mock backend denied; its counts remain 0/0. |
| 09 | Unauthorized target denied; gate proxy path returns 404; counts remain 1/1. |
| 10 | CONNECT returns 501 and does not forward a backend request. |
| 11 | Agent log deletion succeeds; separate signed audit evidence remains intact and cryptographically verifiable in both modes. |
| 12 | Audit outage blocks a new request before any backend attempt; counts remain 1/1. |
| 13 | Audit restart preserves evidence and previously confirmed success without another backend request. |
| 14 | **Negative control:** adding a route allows connection, protected API returns 403. Network isolation is false; no unauthorized effect. |
| 15 | **Negative control:** added route plus unauthenticated API allows a direct write (200, 1 request / 1 effect). Bypass-prevention guarantee is false. |
| 16 | Removing the added route restores connection denial; negative-control counts remain 1/1. |

The package also requires a successful original cleanup record, including a
successful image-absence query. It checks source fingerprints and independent
copies of saved runtime observations. It cannot prove historical OS facts from
JSON alone; a trusted evaluator must execute and observe the run.

The unchanged gate suite must match all 15 entries in its pinned `acceptance.json`
and revalidate 11 exported evidence bundles. Its same-UID loopback test is not an
OS-isolation proof. The unchanged verifier suite must match all 14 entries in its
pinned `acceptance.json`, including each required reason and requirement outcome.
Both modes are recomputed from the saved evidence and evaluator trust fixtures.

`vap-v1.2` remains a limited current-spec verification mode with
`scope_fulfillment: null` and `proposal_status: not_applied`. The distinct
`experimental-scope` mode evaluates unadopted semantics. Integrity and scope
fulfillment are separate axes: cases intentionally produce failed/indeterminate
integrity or not-met/unknown scope. Matching those expected negatives is a
successful experiment, not a declaration that the evidence itself passed.

## Comparison contract

Require complete case inventories, typed values (JSON `true` is not `1`), exact
expected outcomes, regression counts 28/46/64, actual evidence verification and
complete output hashes. Missing evidence, unknown counts, skipped tests/steps, expected failures, source
changes, execution errors and cleanup failures cannot produce `matched`. The
recorded runtime versions must agree across preflight and per-case reports;
recorded dependencies must match the lock.

Do **not** byte-compare separate runs' random keys/signatures, evidence digests,
container/project IDs, IP addresses, namespace IDs, wall-clock times or latency
samples. Check their internal bindings and role relationships instead. The
package does not set a performance threshold or generalize the ten synthetic
latency samples into a production benchmark. Dependency versions must match;
host/Docker version deviations are recorded for evaluator interpretation.

All successful reports still say `experimental_unadopted`,
`independence: not_assessed`, `overall_vap_pass: null`. They do not establish
IPv6/host-service isolation, resistance to a privileged host or Docker operator,
kernel exploit resistance, VM isolation, power-loss durability, real external
anchors, production suitability or compliance with an entire VAP version.
