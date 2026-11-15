# Configured Ed25519 keys in payment and cloud experiments

This is a local implementation restriction for the current experimental code,
added on 15 November 2026. It does not amend VAP v1.2 Draft 3, a VCP profile,
signature domains, evidence schemas or the published interoperability contract.

## Problem and admission rule

The affected entry points previously passed any correctly sized configured
public key to the cryptography backend. With an identity public key deliberately
adopted as caller trust, the backend could accept a constructed signature without
a private-key operation. Local evidence could then receive a supported or valid
signature result. This requires weak caller-selected trust; an evidence envelope
cannot replace an existing ordinary strong trusted key.

Before a configured key can authenticate evidence, the current implementations
now require immutable 32-byte input and reject:

- All eight pure small-order points.
- All 38 encodings whose y coordinate is outside the Ed25519 field.
- The two invalid sign aliases for points with x equal to zero.

All entries in configured trust maps are checked, including unused keys. These
are input/configuration errors, not positive evidence conclusions. The admission
check runs before the relevant store, journal or provider action in constructors.
Direct receipt, acknowledgment, readback and portable-package verification also
checks its explicitly supplied key.

Curve decoding, signature R/S handling and the verification equation remain with
the existing cryptography backend. The rule does not assert prime-subgroup
membership or separately reject all mixed-order points. It does not establish a
signer's identity, authority or independence, truthful provider statements,
trusted time, complete collection or production readiness.

## Current coverage

| Experiment | Current admission boundary | Failure behavior |
| --- | --- | --- |
| Payment API evidence | Every key in the caller role map | `ValueError` before assessment |
| Wallet authorization evidence | Every key in the caller role map | `ValueError` before assessment |
| Payment runtime | Adapter provider pin and direct receipt verification | `ValueError`; no journal is created by rejected construction |
| Payment authorization | Every configured role key; saved-record recheck reconstructs the same configuration | Invalid construction raises `ValueError`; unassessable saved trust produces `UNVERIFIABLE` |
| Payment collector | Client pin, direct acknowledgment and challenge readback verification | `ValueError` |
| Cloud credential evidence | Every key in the caller trust map | `ValueError` before assessment |
| Cloud credential collector | Store construction/initialization and portable snapshot verification | Existing `CollectorError` or `PackError` with `invalid_trusted_public_key` |

The four independently importable base experiments retain the same small local
helper. Runtime-dependent payment modules reuse the runtime helper; cloud
collector and portable snapshots reuse the cloud evidence helper. This preserves
the existing module/dependency boundaries without adding a runtime package.

## Regression checks

From the repository root:

```bash
python -m pip install -r experiments/cloud-credential-evidence/requirements.txt
python -W error::ResourceWarning -m unittest discover -s experiments/ed25519-key-admission/tests -v
python -O -W error::ResourceWarning -m unittest discover -s experiments/ed25519-key-admission/tests -v
```

The 18 methods exercise the public entry points, the eight small-order and 40
noncanonical encodings, unused configured keys, rejection before local I/O,
saved-record handling, strong-key positive controls and unchanged bounded
evidence results. The tests use synthetic keys and temporary local fixtures. A
loopback-only provider test verifies that rejected input causes no provider
attempt or effect, while the existing valid control still produces one synthetic
effect. No external payment service, account, wallet, RPC or cloud endpoint is
contacted.

The dedicated workflow runs this suite on Python 3.12 and 3.14 with the cloud
experiment's pinned cryptography requirement, normally and with `python -O`.
Existing per-experiment workflows continue to test their own requirements and
normal behavior, including the separate in-memory EVM suite.

## Historical source and evidence boundaries

The fixed `research-distribution/2026-11-06-payment-collector/` archive contains
its own copied source. Its historical sources, recorded results, lock files and
SHA-256 inventory are unchanged. Rechecking that distribution executes the
historical implementation; it does not establish that the new admission rule
was present in that historical code. Use the current `experiments/` paths above
to evaluate this repair.

No previously issued signature, fixture, schema, specification, release tag or
historical result is rewritten by this change. The existing incident-assessor
guard and its separately pinned historical consumers are described in
[the incident baseline guide](../INCIDENT_BASELINES.md).
