# Demonstration Scenario

## Workflow

A fictional insurance-claim triage agent evaluates two requests during a
one-minute capture window.

| Attempt | Recorded result |
|---|---|
| `attempt-001` | Automatic processing denied; human review required because confidence is low |
| `attempt-002` | Automatic processing approved because policy rules were satisfied |

Each request produces exactly two VAP events:

1. `AI_DECISION_ATTEMPT`
2. `AI_DECISION_OUTCOME`

The declared batch rule is:

```text
For every in-scope AI_DECISION_ATTEMPT, exactly one
AI_DECISION_OUTCOME with the same attempt_id MUST exist.
```

Formally, the set of attempt identifiers must equal the set of outcome
identifiers, and every identifier must occur exactly once in each set.

## Evidence parties

| Party | Evidence role |
|---|---|
| AI system operator | Signs individual events and the producer manifest |
| Independent observer | Signs a receipt over the batch root, event count, and scope commitment |
| External receipt service | Signs a timestamped receipt over the same root and scope commitment |
| Offline verifier | Holds only the Evidence Pack and public keys |

## Threats tested

### 1. Event modification

An outcome is changed after signing. The event signature and Merkle root no
longer validate.

### 2. Selective omission with internally valid cryptography

One outcome is removed. The attacker rebuilds the Merkle tree and re-signs all
batch-level records. All cryptographic records are internally consistent, but
the Evidence Pack violates its declared attempt/outcome invariant.

This is the decisive VAP test: collection integrity is not equivalent to
workflow completeness.

### 3. Split view

The observer signs a different root from the producer and receipt service. The
signature is valid, but cross-party root agreement fails.

## Non-claim

This scenario does not claim that an insurance triage system is legally high
risk in every jurisdiction. It is a compact workflow selected to demonstrate
portable VAP evidence semantics.
