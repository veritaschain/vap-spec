# MAP medical-advice evidence bindings: change-control candidate

**Status:** Proposed / NOT ADOPTED. **Date:** 2026-10-31 JST.
**Scope:** Future Medical / Healthcare AI Profile (MAP) review; not a VAP v1.2 amendment.

## Candidate requirements (non-normative)

- **MAP-EV-01:** Bind the exact observed request and effective assembled context separately; disclose inaccessible provider context.
- **MAP-EV-02:** Attribute model/configuration, prompt, safety policy and clinical reference versions only when actually observed or source-attested.
- **MAP-EV-03:** Represent safety checks as passed, warned, failed, not-run, timeout, or unknown. Never treat missing observations as passed.
- **MAP-EV-04:** Bind user-visible output independently of raw model output; preserve transformation lineage.
- **MAP-EV-05:** Preserve declared collection scope, outage windows and limitations; anchored-batch completeness does not prove capture of every real-world interaction.
- **MAP-EV-06:** Link clinician intervention and approval to actor authority, exact content and scope; mere presence of a human event does not prove authorization.
- **MAP-EV-07:** Support privacy-preserving patient-data commitments, access control, retention and selective disclosure.
- **MAP-EV-08:** Keep clinical validity, cryptographic validity, attribution, and legal/causal conclusions as separate assessment dimensions.

## Acceptance gates

1. Source claims checked against complaint, benchmark publication and current legal texts.
2. A healthcare domain expert reviews terminology, risk and safety-check taxonomy.
3. Synthetic positive and negative fixtures exercise every candidate binding.
4. A real VAP verifier is run with valid and deliberately tampered manifests, Merkle proofs and externally anchored roots.
5. Independent reviewer reproduces results, and evidence is retained with its exact scope.
6. A formal governance change proposal maps the candidate to MAP's canonical versioned specification and normative registry.

## Current evidence

The companion nine-case Python unittest suite is a **synthetic classification smoke test**. It does not perform cryptographic verification, validate drug doses, integrate a healthcare provider, or satisfy the above acceptance gates. Its outcome cannot be described as independent reproduction or MAP conformance.

Related: [case note](README.md), [test fixtures](tests/README.md), [VAP normative baseline](../../spec/v1.2/README.md).
