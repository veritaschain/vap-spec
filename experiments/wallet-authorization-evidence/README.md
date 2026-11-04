# Wallet authorization evidence experiment

**Status: unadopted, informative experiment.** This directory does not change a VAP requirement, adopt DAP, certify a wallet, or implement a production signing gate. It is additive: existing experiments and their fixed evidence remain unchanged.

The experiment separates four questions that a signed log entry cannot answer by itself:

| Claim | What `VALID` establishes within the stated trust assumptions |
| --- | --- |
| `integrity` | All supplied evidence envelopes verify under the caller's keys for their respective roles. This does not establish completeness. |
| `authorization` | The exact declared operation is covered by a signed policy, approval, final revocation snapshot and observations of the named control routes, at the caller's evaluation time. |
| `execution_match` | The signed execution observation binds the approved operation, exact payload bytes, policy, approval, final revocation and control observations, with the required time ordering. |
| `delegation_state` | A separately trusted observer reports the requested delegation code at the same block and hash as the referenced transaction inclusion, with the policy's required finality statement. |

`INVALID` means a checked signature/structure failure or a contradiction in a verified statement relevant to that claim. `INDETERMINATE` means necessary evidence, trusted provenance, freshness, coverage or context is missing. A missing approval does not prove that approval never existed. A valid signature on an approval for another operation is a verifiable authorization contradiction.

Each claim is evaluated separately. `integrity=VALID`, `authorization=INVALID`, `execution_match=VALID`, `delegation_state=VALID` is possible: an unauthorized operation can be faithfully recorded and have an observed effect.

## Run locally

Python 3.12 is used by CI. Evidence tests use `unittest` and `cryptography`; they require no Ethereum dependencies and make no network calls.

```sh
python -m pip install -r experiments/wallet-authorization-evidence/requirements.txt
python -m unittest discover -s experiments/wallet-authorization-evidence/tests -p 'test_wallet_evidence.py' -v
```

The second suite runs real authorization processing and bytecode in an in-memory Prague EVM. Its development accounts and funds have no public-chain value. Missing dependencies are an error, not a skipped check.

```sh
python -m pip install -r experiments/wallet-authorization-evidence/requirements-evm.txt
python -m unittest discover -s experiments/wallet-authorization-evidence/tests -p 'test_evm_delegation.py' -v
```

The focused workflow [wallet-authorization-evidence.yml](../../.github/workflows/wallet-authorization-evidence.yml) runs both suites in separate jobs. Neither suite contacts a public chain. Dependency installation is separate from test execution.

## Read-only API and report

From this directory:

```python
from fixtures import make_fixture
from wallet_evidence import canonical_json, verify_bundle

bundle, caller_trust, at = make_fixture("stop_with_delegation")
report = verify_bundle(bundle, caller_trust, evaluation_time=at)
print(canonical_json(report).decode("utf-8"))
```

`verify_bundle(bundle, trusted_keys, *, evaluation_time, max_snapshot_age=300)` returns deterministic JSON-compatible data. It snapshots its input, does not mutate the bundle, and does not read a clock, access a network, sign a transaction, dispatch an operation, retry, or write a report file. The fixture helper uses explicitly public synthetic Ed25519 seeds to sign **evidence statements**. The verifier never treats those seeds as real trust anchors.

The CLI reads caller-provided JSON files and writes the report to stdout:

```sh
python wallet_evidence.py --bundle bundle.json --trust trust.json --at 1804723200
```

It exits with `0` when all four claims are `VALID`, `2` otherwise. The output schema is `experimental-wallet-authorization-evidence-v0`; claims are under `report["claims"]`, each with `verdict`, `evidence_refs` and a list of string `reasons`.

**`admission_decision(report)` is an illustration of accepting a verified evidence report, not live authorization or enforcement.** It assumes the caller has just obtained the report by calling `verify_bundle` with its own trust anchors and time. A forged dictionary is not an authenticated report. `ALLOW` does not mean a transaction succeeded, an attacker was blocked, a nonce was consumed, or a new transaction may safely be sent. The same bundle can be checked repeatedly and return `ALLOW`: this stateless verifier has no consumption ledger or replay suppression. Nonce binding detects substitution; it does not prevent replay.

## Input and trust contract

The top-level bundle has exactly `schema`, `synthetic: true`, `run_id`, `operation` and `evidence`. The schema is `experimental-wallet-authorization-bundle-v0`. Evidence entries are optional; their absence produces an indeterminate affected claim. Each supplied envelope has exactly:

```json
{"key_id":"caller-pinned-key-id","payload":{},"signature":"128 lowercase hex characters"}
```

An Ed25519 signature covers the domain `VSO experimental wallet evidence v0\0` followed by canonical JSON of `key_id` and `payload`. Including `key_id` prevents a key alias being substituted without re-signing. The signature does not contain a trust anchor.

The API's caller-owned trust dictionary maps role to key ID to raw 32-byte Ed25519 public key. The CLI uses the same structure with lowercase hex public keys. Roles are `policy_authority`, `approval_authority`, `revocation_authority`, `control_observer`, `execution_observer` and `chain_observer`. Keys cannot grant themselves another role through a bundle. Unknown role keys leave provenance indeterminate. The chain observer's key must differ from all keys configured for the other roles.

**Different keys do not prove different organizations, independent collection, trustworthy clocks or honest statements.** The fixture producer runs in one process and all its keys are public. In an actual deployment, the caller must establish these trust properties outside this artifact. The verifier checks statements by configured observers; it does not query an authoritative chain or discover an organizational trust hierarchy.

The JSON representation is intentionally restricted and is not an RFC 8785 implementation. It uses UTF-8 NFC strings, sorted object keys, no insignificant whitespace, no floats, no duplicate object keys, no unpaired surrogates, a nesting limit of 64, and safe JSON integers. Large amounts, nonces, chain IDs and block numbers use canonical unsigned decimal strings. Hex encodings use lowercase and exact lengths where applicable. Unknown operation fields are rejected.

### Exact operation binding

The signed approval covers a digest of the complete operation, including:

| Group | Fields |
| --- | --- |
| Identity and workload | `operation_id`, `actor_id`, `credential_id`, `workload_id`, `deployment_digest` |
| Wallet intent | `chain_id`, `wallet`, `action`, `asset`, `amount`, `destination`, `calldata`, `delegation_target`, `nonce` |
| Protected context | `signing_payload_digest`, `policy_digest` |

The policy body contains its ID and version, allowed chains/wallets/actions/assets/destinations/delegation targets, amount limit, actor/credential/workload/deployment binding, validity interval, required control routes and required finality. Its digest is in the operation and approval. The execution observer supplies the actual operation and exact signing payload bytes; both must match the approved digests.

`signing_payload_digest` uses SHA-256 as an evidence binding. It is not an Ethereum authorization hash. The basic fixtures use synthetic JSON intent bytes. The EVM integration separately supplies actual `0x05 || RLP([chain_id, address, nonce])` authorization signing bytes and checks the corresponding Ethereum Keccak hash. The general verifier does not decode arbitrary Ethereum transactions or prove that every declared semantic field follows from opaque signing bytes. A trusted execution observer and a format-specific adapter are still needed. It also does not validate delegate contract safety.

### Final authorization and observed execution

The final revocation snapshot is signed and binds the operation, policy and approval digests. It names revoked credentials and approvals, its check time and validity limit. The approval must have been issued before or at the final check. A stale or future snapshot leaves freshness indeterminate; an explicitly revoked credential or approval is a contradiction.

Execution must occur within the final snapshot's validity interval and maximum age. The control observation must precede or coincide with execution and still be fresh at that time. Execution binds both snapshot and control digests. This makes the asserted sequence reviewable; **it does not close the race between a check and execution, establish continuous revocation monitoring, or prove an atomic enforcement boundary**.

Control evidence names three routes: the approved gate, direct signer access and deployment-mediated signer access. A signed observation of a reachable bypass produces an authorization/control failure even while cryptographic integrity stays valid. An unobserved route produces an indeterminate result. These are synthetic scoped observations, not a test that actually compromises a deployment controller. A controller with privileged power to replace the gate, signer, observer or runtime remains outside the trust boundary. Its absence from evidence cannot prove that no bypass exists.

## On-chain delegation is a separate proposition

[EIP-7702](https://eips.ethereum.org/EIPS/eip-7702#behavior) processes authorization tuples before transaction execution. A valid zero-address authorization clears code; skipped tuples need not fail the outer transaction. Applied delegation changes can persist even if subsequent execution reverts. Accordingly, this experiment never infers code state from the receipt status alone.

The signed chain observation includes the run, operation and execution digests; chain and wallet; observation time; state block number/hash; transaction hash and inclusion block number/hash; receipt status; observed account code; and a finality statement. For a delegation request, code must equal `0xef0100 || target`. For a clear request, it must be empty `0x`. An off-chain withdrawal stop, expired application credential or advanced nonce is not an observation that code has been cleared.

Version 0 requires the state observation and transaction inclusion to identify the **same block number and hash**. A prior state block is a contradiction. A later block is indeterminate because no ancestry proof is implemented. There is no reorganization handling, light-client proof, independent timestamp authority or global/current-state guarantee. Even a `finalized` value is a statement by the configured observer, not cryptographically verified consensus finality. Local EVM observations use `observed_block`, not public-chain finality.

The EVM suite checks persistent re-execution, valid clearing, stale clear tuples, chain mismatch, chain ID zero behavior, nonce advancement, and state persistence across reverted execution. Its adapter also feeds real local receipts, blocks, code and authorization bytes into signed evidence. The basic verifier's nonzero `operation.chain_id` identifies the observed chain; this is distinct from an EIP-7702 authorization tuple whose chain ID can be zero.

The adapter binds each receipt to its own authorization bytes by transaction hash. It decodes the actual EIP-7702 tuple's chain ID, delegation target and nonce and derives `delegate` versus `clear_delegation` from that target. These observed fields populate `execution.actual_operation` separately from the intended operation. A different target or action produces `execution_match=INVALID`, including when a skipped tuple leaves a prior state that happens to match the intention; `delegation_state` can correctly remain `VALID` for that observed state.

The tuple does not encode application identity, amount or destination; those fields remain synthetic context in this test adapter. Its observation and evaluation times are illustrative clocks derived from local block timestamps; they are not independently collected wall-clock evidence. Policy, approval, control statements and evidence-signing keys remain synthetic even when the EVM observations are real local execution results. This test-adapter binding does not extend the general verifier into an Ethereum semantic decoder or a production observer.

## Cases and expected separation

`fixtures.py` generates deterministic bundles in memory; all names, accounts, evidence keys and controller observations are synthetic. None is Binance evidence or a reconstruction of a production incident.

| Fixture | Integrity | Authorization | Execution match | Delegation state |
| --- | --- | --- | --- | --- |
| `authorized` | VALID | VALID | VALID | VALID |
| `approval_mismatch` | VALID | INVALID | VALID | VALID |
| `missing_approval` | VALID | INDETERMINATE | INDETERMINATE | VALID |
| `stop_with_delegation` | VALID | VALID | INDETERMINATE | INVALID |
| `clear_observed` | VALID | VALID | VALID | VALID |
| `deployment_bypass` | VALID | INVALID | VALID | VALID |
| `unknown_controller` | VALID | INDETERMINATE | VALID | VALID |
| `credential_revoked` | VALID | INVALID | VALID | VALID |

Security tests also cover real signature tampering, wrong-role keys, altered signing bytes, exact intent substitutions, policy changes, stale/revoked proofs, time-order contradictions, malformed JSON, later-block ambiguity and missing independent observations.

## Relationship to existing work

The [proposal](../../proposals/wallet-authorization-evidence/README.md) maps this work to existing experiments and the DAP registry direction. The [pre-record gate](../pre-record-gate/README.md) already models authorization, exact approvals, durable dispatch intent and no automatic resend; the [OS-isolated gate](../os-isolated-gate/README.md) and [control-state evidence](../control-state-evidence/README.md) already expose privileged-controller and advisory-control limits. Those implementations and their fixed artifacts are unchanged.

[PR #43](https://github.com/veritaschain/vap-spec/pull/43) and [PR #44](https://github.com/veritaschain/vap-spec/pull/44) remain separate. The latter's synthetic integrity/authorization and observation-boundary cases are conceptually reused. Its unmerged code is not imported, and its fixed five-claim `experimental-evidence-result-v0` schema is not extended or repurposed. This experiment has its own four-claim schema and adoption would require a separate review.
