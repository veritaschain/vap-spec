# Local publication pilot — implementation contract

Experimental application adapter, version 0.1.0, synthetic only. The unchanged
incident assessor remains advisory: `publication_action: REVIEW` is never
rewritten to ALLOW. A separate explicitly signed reviewer authorization can
authorize this pilot's exact local export. It does not prove human inspection,
publisher acceptance, legal compliance or complete AI provenance.

## Shared primitives

`publication_pilot.protocol` supplies `InputError`, `canonical`, `digest`,
`timestamp`, `utc_now`, `sha256_bytes`, `sign_message`, `verify_message`,
`sign_record`, `public_key`, `decode_json`, `identifier`, `MAX_HTML` (1 MiB).
Message signatures use domain `publication-pilot-control/0.1\0`, real Ed25519,
and exact `algorithm/key_id/body/signature` envelopes. `verify_message` takes
`(envelope, public_hex, key_id, kind)` and returns the verified body. It does not
validate body-specific fields. Existing assessor records retain their domain.

## Editor and rendering (editor.py)

`Editor(document_id, collector_secret, collector_key_id, clock=utc_now)` provides
`set_block(block_id, text, activity="import")` and `snapshot()`.
Activities are `import`, `manual_edit`, `generation`, `substantive_editing`,
`proofreading`, `translation`. AI-labelled operations are explicitly simulated
adapter operations; no external model is called. Imports/manual edits do not
establish human-only origin. Blocks contain plain text, never supplied HTML.

Every actual replacement records sequence, previous signed-envelope hash,
document/block identities, before/after document hashes, output text, activity
and current observation time. A separately signed checkpoint binds the final
sequence, chain head and complete final document. Replaying verifies all
signatures, chronology, before/after transitions and checkpoint equality.
Maximum 64 operations, 16 blocks, 8192 characters per block, bounded total JSON.

`verify_snapshot(snapshot, collector_public, collector_key_id)` returns exactly:

```
document_id, revision_id, blocks, observed_activities, adopted, source_sha256,
lineage_sha256, observed_at
```

`blocks` is the final ordered list of `{block_id, text}`. `source_sha256` hashes
the JCS final document state. `lineage_sha256` hashes the full snapshot.
`observed_activities` lists all AI-labelled activities recorded in the session,
even if subsequently replaced. `adopted` contains only blocks whose last write
was an AI-labelled operation, each as `{block_id, revision_id, sha256, activity,
observed_at}`; `sha256` hashes the final block's UTF-8 bytes. A manual edit after
an AI edit invalidates exact-output adoption, without erasing the earlier event.

`disclosure_text(disclosure)` accepts exactly `{activities, scope}` with sorted
unique supported AI activities and scope `recorded_local_session_only`; it
produces deterministic plain text that states simulation and unknown outside
origin. Empty activities never mean human-only authorship.
`render_html(view, disclosure)` produces deterministic UTF-8 bytes for one
self-contained escaped HTML file with all final blocks and a visible disclosure
section. No scripts, external assets, supplied markup, time-dependent rendering,
embedded artifact self-hash or approval insertion. Verification may reconstruct
expected bytes; the gate publishes the captured approved bytes unchanged.

## Local one-shot publisher (store.py)

`LocalPublisher(root, destination_id, secret, key_id, clock=utc_now)` owns
controller-trusted directories, SQLite WAL/FULL journal and receipt key.
`publish(request_id, fingerprint, html_bytes, disclosure_sha256, *,
before_link=None, after_link=None)` returns a public result with
`state`, `attempted`, `visible_name`, `receipt`, `journal_state`, `reason`.
`before_link` runs after private staging + durable one-shot intent, immediately
before the atomic link; a False return blocks. Exceptions leave unknown state.
`after_link` is a trusted harness fault hook after visible creation. Runtime
inputs cannot choose these hooks, directory paths or filenames.

States: `LOCAL_OUTPUT_CONFIRMED`, `BLOCKED_WITHOUT_PUBLICATION`,
`OUTCOME_UNKNOWN`, `REPLAY_NO_PUBLICATION`, `REQUEST_ID_CONFLICT`.
`attempted` records whether the atomic publication call was entered, not whether
it succeeded. Name is SHA-256(request_id UTF-8) + `.html`.

Write and fsync an exclusive private stage, atomically claim the request in the
journal, validate acknowledgement, invoke before_link, then use non-overwriting
same-filesystem `os.link`, fsync the public directory, read back without following
symlinks, verify regular-file identity, hash and length, sign and persist receipt.
Existing names are never replaced or adopted. Identical/restarted requests never
retry; different fingerprints conflict. A visible file may remain after an
unknown result. Cleanup never deletes the visible output.

Receipt body exact fields: `kind: local_publication_receipt`, `request_id`,
`fingerprint`, `artifact_sha256`, `disclosure_sha256`, `byte_length`,
`destination_id`, `visible_name`, `observed_at`.
`get(request_id)` returns the stored journal row or None; `inspect()` returns
`{visible_count, files}` where files map safe visible basenames to
`{sha256, byte_length}`. A read-only current inspection is not historical proof.
Fault-injection seams may be `_claim`, `_finish`; document exact signatures.

## Candidate, reviewer and gate (root-owned)

Candidate JSON exact fields: `format`, `source`, `disclosure`, `html`, `evidence`.
The evidence is an unchanged-assessor publication input. Trust is supplied
separately, and gate configuration independently pins trusted keys/issuers,
destination/route and publication policy ID/version/digest/stage.

Payload digest identifies final HTML INCLUDING disclosure. Source/lineage digests
are separate measurements. Only exactly observed adopted blocks become current
publication_activity records. All observed session activity remains in the
signed lineage and structured disclosure. The application release policy may
exclude a session activity even when its output was later replaced; this is
publication eligibility, not a retroactive legal determination about prior use.

Approval is `{release, evidence}`: a pilot `release_approval` message plus an
existing `publication_approval` signed record. Release body exact fields:
`kind`, `request_id`, `candidate_sha256`, `artifact_sha256`, `disclosure_sha256`,
`policy_sha256`, `destination_id`, `approved_at`, `valid_until`, `decision`
(`approve`), `review_scope` (`exact_local_artifact_and_disclosure`). Both records
must name the pinned reviewer key/issuer, bind the same target and validity.
The candidate digest excludes approval, avoiding a self-reference.

The gate validates the original evaluator pin, captures candidate/approval once,
verifies the edit chain and measured render, requires disclosed activities to
cover every observed session activity, checks pinned venue/policy, verifies the
separate approval, and calls the unchanged assessor with actual current time.
Every required signature/role and full binding must qualify. A prohibition or
unresolved policy prevents local output, regardless of reviewer signature.
Final policy/approval validity is rechecked in before_link. Preflight and final
assessment frames are retained for recomputation. Neither filesystem output nor
local receipt is converted into publication_dispatch/publication_receipt.

All roles share one controller and host user. No OS isolation, independent
authority, real AI generation, external publication or complete coverage is
claimed. A deliberate outside-gate write is a negative control. Normative
specifications, original incident catalogue and both earlier runtimes stay fixed.
