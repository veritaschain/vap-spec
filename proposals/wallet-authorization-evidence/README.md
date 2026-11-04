# Wallet authorization evidence — informative proposal

**Status: unadopted proposal and experiment; no normative change.** This work does not adopt DAP, create a new generic profile, alter VAP v1.2, or claim that VAP/VCP alone would prevent an incident. [日本語](README-ja.md)

## Problem and scope

A reported compromise path can connect developer tooling, an internal AI tool, deployment credentials and a wallet signer. In that situation, valid credentials or a valid cryptographic signature do not establish that a particular wallet operation was authorized. Application shutdown also does not establish that an existing on-chain delegation has been removed.

The [Binance report supplied as motivation](https://www.binance.bh/en/blog/community/3229153443759566763) and [WIRED coverage](https://www.wired.com/story/binance-says-hackers-used-well-known-tricks-to-carry-out-a-dollar634-billion-heist/) motivate this bounded evidence question. The experiment contains **no forensic evidence from that incident** and makes no claim to reproduce the intrusions, quantify losses, establish attribution, or show autonomous AI planning. Every test credential, approval, workload and evidence record is labelled synthetic.

The purpose is to test whether an evidence consumer keeps four propositions separate: supplied-record integrity, exact-operation authorization, execution matching, and observed delegation state. This addresses a wallet-specific case within the existing delegated-agent/tool-action direction, without changing the status of any registered draft.

## Existing coverage and additive work

| Existing source | Already present | This proposal adds |
| --- | --- | --- |
| [VAP v1.2 draft, §4.6](../../spec/v1.2/VAP_Framework_Specification.md) | Registry direction for DAP / VAP-AGENT and delegated tool actions | An informative wallet case; no DAP adoption or new requirements |
| [Pre-record gate](../../experiments/pre-record-gate/README.md) | Verified authorization, exact operation/approval binding, revocation refresh, durable dispatch intent and no automatic resend | Wallet-specific intent fields and a separately signed final revocation observation bound into execution evidence |
| [OS-isolated gate](../../experiments/os-isolated-gate/README.md) | Reachability checks and privileged-controller negative controls | A deployment-to-signer bypass evidence case and an explicitly unobserved-route case |
| [Control-state evidence](../../experiments/control-state-evidence/README.md) | Integrity/control separation and an advisory preflight boundary | Explicit check/approval/execution time ordering, while retaining the enforcement and race limitations |
| [PR #44](https://github.com/veritaschain/vap-spec/pull/44) | Proposed synthetic integrity-versus-authorization and observation-boundary tests | A separate wallet result schema; no dependency on unmerged code and no change to its five-claim v0 contract |

[PR #43](https://github.com/veritaschain/vap-spec/pull/43) remains an independent incident-review contribution. This proposal uses a new directory and does not rewrite its incident index or fixed evidence. All previous experiments and result artifacts remain reproducible.

## Concrete artifact and acceptance criteria

The implementation is [experiments/wallet-authorization-evidence](../../experiments/wallet-authorization-evidence/README.md). It verifies actual Ed25519 evidence signatures with externally supplied role-specific trust keys. It has no network, public-chain transaction, production wallet key or automatic recovery path.

1. An approval binds the complete declared identity/workload and wallet intent: chain, wallet, action, asset, amount, destination, calldata, delegation target, nonce, exact signing-payload digest and policy digest. Changing a bound field leaves the original approval insufficient.
2. Policy and approval are signed. The final signed revocation snapshot identifies the exact approval and operation. Approval issuance precedes the snapshot; the snapshot and scoped control observation precede execution and meet freshness checks. A revoked credential is invalid; an unavailable or stale observation is indeterminate.
3. Execution evidence binds the actual operation, exact payload bytes, policy, approval and final check digests. A valid signature on a different execution cannot establish a match.
4. A separately trusted chain observer supplies block, run and operation context, receipt information and actual account code. Receipt success does not establish delegation removal; a reverted outer execution does not negate an observed applied delegation or clear. Local EVM tests exercise these behaviors using actual EIP-7702 authorization processing.
5. An observed deployment-mediated bypass can coexist with valid cryptographic evidence and an invalid control/authorization claim. An unobserved path stays indeterminate. The model does not pretend to contain a malicious privileged controller.
6. A read-only report presents `integrity`, `authorization`, `execution_match` and `delegation_state` separately. Missing evidence never becomes proof of absence. Evidence admission may fail closed while retaining indeterminate retrospective claims.

## Trust and interpretation limits

The caller establishes trusted keys and evaluation time. The experiment cannot discover that a signer is an authorized employee, that an observer is honest, or that separate keys belong to independent organizations. Synthetic fixture keys are public and generated in one process. Real deployment would require independently governed trust anchors and collectors.

The control observations cover named routes at their recorded observation time; freshness bounds do not prove uninterrupted control. There is no atomic link from the final check to a real signer, no prevention of subsequent privileged configuration change, and no continuous revocation guarantee. The verifier's `ALLOW` means acceptance of evidence under these assumptions; it is not live permission to execute, a transaction success verdict, or replay prevention. The verifier has no consumption ledger and can evaluate the same bundle repeatedly.

The signing-payload digest binds bytes. Generic code does not decode arbitrary Ethereum payloads or prove the semantic safety of delegate code. The EVM adapter checks the specific authorization bytes it creates. Nonzero observed chain IDs are distinct from chain ID zero in EIP-7702 authorization tuples.

Version 0 requires chain-state observation and transaction inclusion at the same block and hash. Later blocks remain indeterminate without ancestry evidence. There is no consensus-finality proof, reorganization handling or independently verified chain state. A configured observer's signed statement is the trust boundary, not a replacement for a light client.

## Review and adoption

The signed-evidence tests and separately required local-EVM tests run in a focused CI workflow. They validate an experiment, not conformance or production readiness. Potential future adoption requires review of the threat model, semantic transaction adapters, trust/key lifecycle, protected deployment enforcement, atomic execution binding, replay/consumption storage, chain canonicality/finality, privacy and independently reproduced results. Any normative DAP/VAP change needs its own proposal and decision.

Primary Ethereum behavior source: [EIP-7702 — Behavior](https://eips.ethereum.org/EIPS/eip-7702#behavior). The EIP's code-state semantics, not incident headlines or receipt status, define the local EVM assertions.
