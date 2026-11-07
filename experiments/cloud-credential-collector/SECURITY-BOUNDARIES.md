# Authorization and confidentiality boundaries

**Informative, unadopted deployment guidance — 2026-11-08.**
[日本語](SECURITY-BOUNDARIES-ja.md) · [Collector](README.md) · [Portable snapshot](PACK.md)

This guide changes no normative VAP/VCP requirement, CHANGE-001, schema, implementation or test.

## Motivation and attribution

WorkOS's 6 November update attributes October access to a researcher's ARTEX evaluation agent and reports exposed APIs, weak development credentials and delayed detection [S1]. This records WorkOS's account; the escape mechanism and intent are not independently established here. Claude Code documents persistent approval rules and user-global Git exclusions for local settings [S2, S3]. Apiiro incident totals remain withheld pending primary review [S4].

## Proposed execution boundary

Deployment enforcement would establish trusted actor and delegator identities, tenant, environment, exact destination and action, policy version, expiry, nonce/replay state and current revocation status before execution. These are proposed deployment inputs, not new normative fields.

That separate enforcement layer would check the actual resolved endpoint and every redirect or delegated operation against authorized scope, binding the approved destination to the connection. Working credentials do not extend sandbox authorization to production. Keep declared intent, authorization decisions and observed actions/results distinct. Missing observations remain unresolved. A deployment may deny execution because evidence is unavailable, but it cannot invent evidence that an earlier action was denied or never happened.

## Proposed confidentiality boundary

Keep raw credentials out of shareable approval records, command logs and results. Use opaque credential and key-version identifiers. Bare hashes of low-entropy secrets permit candidate guessing; base64, ordinary hashing and signatures provide no confidentiality. Even an original artifact digest can expose a guessable secret when the remaining content is predictable.

Minimize shareable records before signing. Preserve necessary raw originals separately under restricted custody and retention/access policies. Identify and sign any sanitized projection separately, describing its transformation and relationship to the original. Keep sensitive linkage restricted, including original digests when publication enables guessing. Never mutate originals or reuse their signatures for changed bytes. A projection's signature authenticates that projection's statement; it does not recover omitted evidence.

## Current implementation limits

The collector preserves exact original bytes. PACK exports originals and signed custody metadata with private local file permissions. Neither provides **secret scanning, redaction, encryption, recipient authorization, release decisions or an execution gate**. Local permissions do not govern a recipient's later copies. Custody verification does not authorize distribution.

A sanitized disclosure view is not an existing PACK option. Withhold a pack when its originals or commitments cannot be shared; do not silently edit it. Distribution requires separate review and authorization.

The separate [pre-record gate](../pre-record-gate/README.md) already compares exact approved operations and restricts its synthetic transport, including redirects. The [OS isolation experiment](../os-isolated-gate/README.md) exercises bounded routes. The [consumer-agent proposal](../../proposals/consumer-agent-evidence/README.md) already addresses actor, delegation and target scope. The cloud collector also binds tenant/resource context and checks custody integrity.

Those component checks do not establish their end-to-end composition into a deployed authorization or confidential-release boundary. **The six deployment/shareable-view cases below are not established by this collector/PACK experiment and are not newly tested here.** This does not mean every underlying component check is absent.

## Checks for a future deployment or shareable view

| Case | Behavior to demonstrate | Status |
| --- | --- | --- |
| Sandbox approval, production target | Reject the environment/scope mismatch before execution. | Not established by this pilot |
| Redirect or outbound target change | Recheck resolved destinations and delegated operations; bind each connection to approved scope. | Not established by this pilot |
| Missing observations | Retain unresolved evidence; distinguish policy denial from an observed historical outcome. | Not established by this pilot |
| Secrets in argv, headers, approvals or results | Keep each secret fixture out of shared records and error output; restrict necessary originals separately. | Not established by this pilot |
| Insufficient recipient rights | Deny release even when custody verification succeeds. | Not established by this pilot |
| Altered original versus signed projection | Reject altered committed bytes; verify a labelled, separately signed projection under its own context and trust. | Not established by this pilot |

These proposals do not establish VAP/VCP prevention, deployment, conformance or production readiness.

## Sources

- [S1: WorkOS, attribution update, 2026-11-06](https://workos.com/security/bulletins/update-for-october-30th-2026-data-security-incident).
- [S2: Claude Code permissions](https://code.claude.com/docs/en/permissions).
- [S3: Claude Code settings](https://code.claude.com/docs/en/settings).
- [S4: Apiiro HOLD review in vcp-site #205](https://github.com/veritaschain/vcp-site/blob/579e9715489272ead53182f4d4910f7fe852f9e5/incidents/reviews/2026-11-08-claude-code-secrets.md). Retrieval failure does not disprove the report.
