# 91APP: evidence questions after credential compromise

**Status:** Informative / unadopted design note. **Source review:** 2026-11-01.
**Language:** English · [日本語](91APP-EVIDENCE-REVIEW-ja.md).

This note relates public reporting to the existing [incident-evidence proposal](README.md).
It introduces no normative events, fields, profiles or conformance claims. No incident logs,
customer records or forensic evidence package were accessed, and no experiment described here
reconstructs the attack. Future review questions below have not been executed as acceptance tests.

## 1. Attributed facts and limits

91APP says it found ARTEX traces in its systems. The company's route reconstruction describes
Appsmith, GitLab-held credentials and an orders database.[A1] Its October 29 scope estimate is a
maximum potentially affected population, not a confirmed exfiltration count.[A2] Taiwan's authority
confirmed unauthorized acquisition of some data in its October 20 notice; exact types were then still
under investigation. That notice does not establish ARTEX attribution or that maximum count.[A3]

The [claim ledger](INCIDENTS.md#91app) retains the dates, figures, notification plans, financial
reporting distinction and unresolved attribution, each with its source. In particular, tool traces
do not establish fully autonomous execution or continuity with another attacker group. The reviewed
material does not establish a specific CVE; exact versions and raw forensic evidence were not examined.[A1][A2][A3]
Notification plans must be read as dated, conditional company statements.[A5]

The following analysis proposes review questions. It does not describe controls known to have
been deployed by 91APP or claim that VAP would have prevented the intrusion.

## 2. What VAP and VCP can contribute

The [repository overview](../../README.md) defines VAP as a cross-domain framework and VCP as its
finance and algorithmic-trading profile. A multi-system commerce incident is relevant to generic
evidence bindings; it does not automatically become a VCP financial-trading use case. Reusing a
record-integrity mechanism would require an explicit application mapping and verification policy.

Defender-side collection cannot assume that an attacker participates in VAP, signs actions or
discloses prompts and model decisions. Appsmith, GitLab, database and egress collectors describe
only their scoped observations; correlating those records does not recover attacker intent,
hidden agent reasoning or full autonomy.

Integrity verification can help establish whether supplied records match trusted commitments and
signatures. It cannot, by itself, establish the truth of a collector's account, authorize an operation,
close a software vulnerability, or prevent a direct database connection outside the controlled route.
Those enforcement and observation dependencies remain explicit in [proposal §2](README.md#2-enforcement-and-evidence-have-separate-responsibilities).

## 3. Bindings that a future integration would need

These are application design considerations, not new schema requirements or incident findings.

| Review question | Evidence to distinguish | Limit to retain |
| --- | --- | --- |
| Was a credential accepted, and was the operation authorized? | Database authentication and permissions; authenticated session; executing principal; intended purpose, resource and separate approval; policy version at dispatch | Accepted database credentials are not proof of the owner's intent. A valid evidence signature is a separate cryptographic check, not database authorization. |
| Which credential or signing key was valid, and when? | Protected credential reference and version; issuer; grants; compromise uncertainty; revocation decision, effective time and enforcement observation; active sessions and cached decisions | Database secrets and evidence-signing keys have different trust roles. Rotation alone does not establish when compromise began or whether every existing session stopped. |
| What data actually moved? | Query execution, returned object set, client receipt, export creation, network egress and destination acknowledgment, each with its own scope and time | Successful authentication does not establish a read; a read does not establish export; export does not establish delivery. A receipt does not establish all subsequent processing. |
| How are systems related? | Source identities, protected session/object references, correlation rules, clock uncertainty, disagreement and competing explanations | Matching identifiers and chronology support a trace hypothesis, not automatic proof of causality, attacker identity or autonomous execution. |
| What did collectors cover? | Route, account, tenant and interval; collection outages, retention gaps and paths that bypass the gateway | Missing records leave uncovered activity unresolved. Positive evidence of an unauthorized read or egress must remain recorded even when other coverage is missing. |
| Who can alter the evidence or trust state? | Collector, signer, key administrator, trust-store and witness control boundaries; independently protected checkpoints where available | Multiple services or keys under the same compromised administrator are not independent observers. Correlation alone is not TRC-005 XREF. |
| What changed during containment? | Authorized action, actual result, new configuration generation, credential revocation and subsequent scoped checks; available preservation and explicit gaps | A recorded remediation request is not proof of completion. An old assessment cannot validate changed controls; a later anchor cannot recover missing earlier evidence. |

### Authorization and time

A future verifier should evaluate a signature using the declared trust and compromise policy while
separately evaluating the operation's authorization. An authentic record may accurately document an
unauthorized action. Conversely, possession of a signing key or a database credential must not be
treated as proof that an uncompromised human approved the action.

An incident review needs the difference between when revocation was decided, when it was intended
to become effective, and when each enforcement point actually applied it. Record observation time
and uncertainty separately from claimed event time; a self-reported timestamp does not establish historical
key validity. Where a compromise interval cannot be determined,
retain that uncertainty rather than silently accepting every earlier signature or invalidating every
historical record without a stated policy. A check performed before a long-running query does not
establish continuous authorization throughout later reads and exports.

### Observation and independent checking

The proposal's [common bindings](README.md#3-common-binding-information) and
[transfer discussion](README.md#4-transfer-authorization-and-observed-egress) distinguish decisions
from observed effects. Record a confirmed contradiction even if another collector is unavailable.
Where no observation resolves a bypass, report the gap without asserting that a transfer occurred.

An independent witness requires a defensible administration and trust boundary, not just another
process name. An authenticated imported statement may be useful without satisfying the independently
anchored corresponding records and reconciliation rules required for XREF. A reviewer should identify
which conclusions come from source statements, measured observations or inference.

### Privacy and preservation

Apply [proposal §8](README.md#8-privacy-and-investigation-packaging) to evidence itself. Public proof
material should contain neither raw customer data nor API keys, tokens or database connection strings.
Use opaque credential/object references with protected mappings and authorized, minimal disclosure.
A public hash of a predictable identifier is not anonymization. Record access, retention and the
procedure for opening a sensitive commitment when verification requires it.

Preserve the minimum relevant evidence where feasible without delaying justified urgent containment.
Record unavailable material and its source/time boundary. Do not reconstruct missing historical
observations by signing a new narrative, and retain later corrections as new dated records.

## 4. Existing experiments and their boundaries

Reviewed source: `vap-spec` main `a2a9f6a25906db4be23e6ecd3796eab144d9ac99` and
`evidect-site` main `eeeacf7effc8103276106dcf606b2bafb7349081`. These references identify existing
first-party experiments, not new test results produced for this note.

| Existing material | Relevant behavior | What it does not establish |
| --- | --- | --- |
| [Offline assessor](../../experiments/incident-evidence-assessor/README.md): `UP-05`, `UP-07`, `UP-08`, `IR-02`, `XR-01` | Separates denial from observed transmission, uncovered routes, collector availability, preservation gaps and imported statements | It evaluates structured synthetic inputs; it does not inspect production network traffic, database activity or the 91APP incident. |
| [Collector pilot](../../experiments/incident-collector-pilot/README.md) | Uses a real local collector/receiver, current gate checks and measured payload delivery on one route | Same operator and loopback scope; no production key-revocation service or all-route control. Final-gate approval and later dispatch are not one atomic observation. |
| [EVIDECT execution gate][gate] | Rechecks current task/subject/approver revocation, policy, scope and approval before its in-memory marker tool | Identity, time and revocation are trusted synthetic inputs. No production authentication adapter or proof that a direct database route passes through this gate. |
| [EVIDECT control revalidation][revalidation] | Requires renewed assessment after configuration/generation changes while retaining historical signatures | Control observations are synthetic values, not executed authentication, access or detection tests. |
| [EVIDECT receiver witness][witness] | Uses fresh challenges to compare receiver state with a separately stored signed state | Both stores share an operator. Rolling both back can remain undetected; this is not an independent operational witness or trusted timestamp service. |

The existing test entrypoints are documented by those READMEs: assessor `python -m unittest discover
-s tests -v`; collector `python -W error::ResourceWarning run_tests.py`; EVIDECT `node --test
examples/execution-authorization/gate.test.mjs`, `node --test examples/control-revalidation/demo.test.mjs`,
and the two `examples/receiver-witness/test_*.py` entrypoints. Use each documented working directory
and environment. Passing a negative case means its expected rejection or uncertainty was observed;
it does not turn a denial, unknown result or incident into an overall successful authorization.

The [23-case catalogue](acceptance-cases.json), original 53-scenario evidence and later frozen
captures remain separate and unchanged. This note adds no experiment, alters no signed record,
and does not promote a proposal or first-party demonstration to an adopted standard.

## 5. Questions before a separately authorized future pilot

1. Which real service enforces operation-specific approval, and can the database be reached without it?
2. Which sources independently observe a query's returned data and external delivery, with what gaps?
3. How will credential compromise, revocation propagation, cached authorization and live sessions be observed?
4. Who protects the collector, signing keys, current policy and witness when the application administrator is compromised?
5. How will the review preserve confirmed unauthorized activity alongside unknown coverage, without publishing secrets or personal data?
6. What separately authorized measurements and independent review would be needed before claiming any deployment result?

These are review questions, not an implemented acceptance suite or a request to test a third party's systems.

## Sources

- [A1 — 91APP incident account](https://91app.com/91app-202610-security-incident/)
- [A2 — 91APP October 29 scope update](https://91app.com/blog/91app-202610-security-incident-2/)
- [A3 — Taiwan Administration for Digital Industries notice](https://moda.gov.tw/ADI/news/latest-news/21118)
- [A5 — 91APP notification and compensation information](https://91app.com/91app-202610-security-incident-compensation/)

[A1]: https://91app.com/91app-202610-security-incident/
[A2]: https://91app.com/blog/91app-202610-security-incident-2/
[A3]: https://moda.gov.tw/ADI/news/latest-news/21118
[A5]: https://91app.com/91app-202610-security-incident-compensation/
[gate]: https://github.com/veritaschain/evidect-site/blob/eeeacf7effc8103276106dcf606b2bafb7349081/examples/execution-authorization/README.md
[revalidation]: https://github.com/veritaschain/evidect-site/blob/eeeacf7effc8103276106dcf606b2bafb7349081/examples/control-revalidation/README.md
[witness]: https://github.com/veritaschain/evidect-site/blob/eeeacf7effc8103276106dcf606b2bafb7349081/examples/receiver-witness/README.md
