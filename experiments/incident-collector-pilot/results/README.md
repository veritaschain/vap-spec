# Preserved CI captures

The [implementation workflow](https://github.com/veritaschain/vap-spec/actions/runs/41030433885)
ran directly on commit `7b3c8e4a2e8205b550a0b5a6764a7687375d0050`.
Both matrix jobs passed: 41 test methods, zero skips, 18 actual loopback scenarios,
18 matched finite expectations and 18 saved-export rechecks per runtime.
The captures completed on 2026-10-30 at approximately 18:02 JST.

| Runtime | Tests | Measured scenarios | Offline rechecks | Original archive |
|---|---:|---:|---:|---|
| Python 3.12.15 | 41, zero skips | 18/18 | 18 | [capture-python-3.12.zip](capture-python-3.12.zip) |
| Python 3.14.9 | 41, zero skips | 18/18 | 18 | [capture-python-3.14.zip](capture-python-3.14.zip) |

These are two runtime captures of the **same 18 scenarios**, not 36 distinct
requirements. Each archive contains the original `summary.json` and 18 original
case JSON files. The bytes were downloaded from GitHub Actions and matched against
the artifact API's SHA-256; the ZIPs were not reconstructed or recompressed.
Public artifacts contain no secret keys or payload plaintext, and exclude the
temporary databases.

[ci-record.json](ci-record.json) records run/job/artifact identities and exact
hashes. The saved archives were also rechecked locally with Python audit events
blocking network and process execution. That is an offline recheck of the saved
observations, not an independent repeat of the experiments.

## Exact byte identities

| File | SHA-256 |
|---|---|
| `capture-python-3.12.zip` | `bdd3944936e01ab6e673394b1bfbd4727653ed7136cae502fc9570c0e2943348` |
| 3.12 archive's `summary.json` | `80aa54f50f7cbaffcab5cd9b4c6720d0f11d30eb2a35c5f90c70a9872c5c131a` |
| `capture-python-3.14.zip` | `30d6e82389ac9ed377c267ca52788831c1875035848df95215ee2405a75f4f9b` |
| 3.14 archive's `summary.json` | `0494a5ff56ffa38684b14353e362a763b2796b67e2762f8714596fe1a7e06b3d` |

The shared 176-file execution source identity is
`efff3250a1c808168c137572517f2ec10268b6b1a7cd2524a27eb0d81a421b15`.
It includes the unchanged 154 historical inputs, whose identity remains
`1b6187b8d732e299de389e957601b96ad971f908f1b96cc6da11d2662e2efb3b`.
This provenance directory and root navigation are not execution inputs, so adding
these preserved outputs does not alter the measured source identity.

## Recheck a saved capture

Use the complete matching repository checkout and pinned dependencies described
in the experiment README. From the experiment directory, first compare the ZIP's
SHA-256 with the separately trusted value above. Extract that verified ZIP to a
fresh directory, then pass the corresponding independently obtained summary hash:

```sh
sha256sum results/capture-python-3.12.zip
python -m zipfile -e results/capture-python-3.12.zip generated/saved-python-3.12
python -m collector_pilot verify-exports generated/saved-python-3.12 \
  --expected-summary-sha256 80aa54f50f7cbaffcab5cd9b4c6720d0f11d30eb2a35c5f90c70a9872c5c131a
```

The expected hash must come from a trusted checkout or another trusted channel;
a self-asserted hash shipped with an unknown capture does not establish origin.
The verifier checks original case bytes, source identity, declared signatures,
exact bindings, chronology, unchanged assessor results and finite expectations.
It does not send requests, resume uploads or claim independent event truth.

## Interpreting the measured outcomes

- **CP-02:** stopped collector, zero collector rows and zero payload attempts.
- **CP-04:** metadata commit followed by lost acknowledgement, one collector row,
  zero payload attempts, then a fresh authenticated `FOUND` after restart.
  Repeated execution still returns `REPLAY_NO_SEND`.
- **CP-06:** collector stopped after acknowledgement, so failed final readback
  blocks the payload even though the earlier metadata row remains stored.
- **CP-07–09:** expired authorization, wrong receipt binding or wrong nonce each
  blocks the payload. A present metadata row alone cannot authorize it.
- **CP-14:** concurrent callers produce one collection and one payload attempt.
- **CP-15:** receiver row exists after its response is lost; gateway outcome
  remains unknown and a repeat request is not sent.
- **CP-01/16:** a permitted controlled attempt has final-gate `ALLOW` and a valid
  receiver receipt, while later observed-action authorization remains `REVIEW`.

The collector and receiver remain controlled by the same synthetic operator.
These captures do not establish continuous availability, all-route protection,
independent reproduction, provider deletion, legal compliance or conformance.
