# DOC-SYNC

This file is newly created. On 2026-10-21 JST a GitHub code search for
`filename:DOC-SYNC.md` in the `veritaschain` organization returned
`total_count` 0 (`GET /search/code`). No earlier DOC-SYNC was found in this
repository or in that organization search, so there is no prior entry to
continue. Every entry below was confirmed retrospectively on 2026-10-21 JST.
The entries are not contemporaneous notes written when the events happened.

The verifier of each entry is **VSO 主任, via the GitHub API**. That verifies
this record. It is not an approval of a historical pull request, tag, release,
or case. No approving review is recorded unless the API returned one. No git
tag was created, moved, deleted, or annotated while this file was written. No
signed object was altered.

VAP in this repository remains **v1.2.0, Draft Specification (Draft 3)**. That
status is not VCP's release status. VCP v1.2 events below are events in
`veritaschain/vcp-spec`.

**DOC-SYNC entry time for every entry:** 2026-10-21 JST.

JST is nine hours ahead of UTC. UTC values below are copied from the API.
JST clock times are those UTC values plus nine hours. Where the API gave
seconds, the JST time keeps the seconds. A shorter JST form that drops the
seconds is noted only where it matches that conversion.

---

## 1. vcp-spec pull request #1 — VCP v1.2 GA text on main

### Event time

`merged_at` **2026-10-07T16:19:10Z**, which is **2026-10-08 01:19:10 JST**
(2026-10-08 01:19 JST).

### DOC-SYNC entry time

2026-10-21 JST.

### Pull request, commit, tag, and files

| Item | Value |
| --- | --- |
| Repository | `veritaschain/vcp-spec` |
| Pull request | [#1](https://github.com/veritaschain/vcp-spec/pull/1), "VCP v1.2: Production Ready (GA 2026-07-06) — spec text, normative annex, JSON Schema" |
| State at confirmation | closed, merged |
| Merge commit | `f833b52e52310900ce82f6d0726b635667a4f55b` (short `f833b52`) |
| Merge commit parents | `7208a1ba6feca276bfe01c17f4cec49142b81049` (main before the merge), `52ee817caa27e9a70a4a2a151ed12bfd9372a947` |
| Base / head | `main` / `vcp-v1-2-ga-cutover` |
| Merged by (API login) | `veritaschain` |
| Tag | none. This merge is not `v1.2.0` |

Files in the pull request (14):

- `README.md`
- `VCP-Specification-v1_2_en.md`, `VCP-Specification-v1_2_ja.md`, `VCP-Specification-v1_2_zh.md`
- `VSO-SPEC-CHANGE-001.md` (added at the repository root)
- `spec/v1.2/README.md`
- `spec/v1.2/VCP-Specification-v1_2_en.md`, `spec/v1.2/VCP-Specification-v1_2_ja.md`, `spec/v1.2/VCP-Specification-v1_2_zh.md`
- `spec/v1.2/VSO-SPEC-CHANGE-001.md` (added)
- `spec/v1.2/vcp-event-v1.2.json` (added)
- `docs/QUICKSTART.md`, `examples/README.md`, `spec/v1.1/README.md`

### Before

At parent `7208a1ba6feca276bfe01c17f4cec49142b81049`, `README.md` carried the
badge `VCP-v1.2 RC1` and the version table row **v1.2 / Release Candidate
(RC1) — current / 2026-05-31**. The same README already said "zero breaking
changes". `spec/v1.2/` did not yet contain `VSO-SPEC-CHANGE-001.md` or
`vcp-event-v1.2.json` (both appear as additions in this pull request). No
`v1.2.0` tag pointed at this commit, because the tag did not exist yet
(see entry 3).

### After

Main contained the GA specification text, the normative annex
`VSO-SPEC-CHANGE-001`, and `spec/v1.2/vcp-event-v1.2.json`. At `f833b52`,
`README.md` called v1.2 **Production Ready (GA)** and the version table said
"current (tag `v1.2.0`)" with date 2026-07-06 (RC1: 2026-05-31). The known-issues
section said: "The Production Ready text is the RC1 text with its status, dates
and one informative legal note updated; there was no technical change."
`spec/v1.2/README.md` at the same commit said the same, and named tag `v1.2.0`.
That tag name in the README was ahead of the git tag: the tag was created later,
and not at this commit.

The pull request body retrieved on 2026-10-21 opens with a note dated
2026-10-09. That note says the original review remains a historical record and
is not an independent approval, and that this merge alone did not resolve the
blockers later fixed by pull request #2. The note is later than `merged_at`.
It is not treated as an approval that existed when the pull request merged.

### Reason

Publish the VCP v1.2 text that had been declared Production Ready (GA) on
2026-07-06, together with its normative annex and JSON Schema, into
`veritaschain/vcp-spec`. Until this merge, the repository showed RC1.

### Impact

Readers of main after `f833b52` and before pull request #2 were told that GA
was technically the RC1 text and that tag `v1.2.0` was current. Both of those
statements were superseded by pull request #2 and by the later tag, which
points at `b23acb266f88df81d960d36d58fb64ceaa0dd5ed`, not at `f833b52`.
`spec/v1.2/GA-CONSISTENCY.md` on the tagged commit says the `f833b52` merge
contained two P1 wire-contract inconsistencies, and that no `v1.2.0` tag
existed when that correction was prepared.

### Verifier and evidence

Verifier: VSO 主任, via the GitHub API, on 2026-10-21 JST.

- `GET /repos/veritaschain/vcp-spec/pulls/1` — `merged_at` `2026-10-07T16:19:10Z`, `merge_commit_sha` `f833b52e52310900ce82f6d0726b635667a4f55b`, `merged_by.login` `veritaschain`, `state` `closed`.
- `GET /repos/veritaschain/vcp-spec/pulls/1/files` — 14 files, as listed above.
- `GET /repos/veritaschain/vcp-spec/commits/f833b52e52310900ce82f6d0726b635667a4f55b` — parents as listed; message begins "Merge pull request #1 from veritaschain/vcp-v1-2-ga-cutover".
- `GET /repos/veritaschain/vcp-spec/contents/README.md?ref=7208a1ba6feca276bfe01c17f4cec49142b81049` — RC1 badge and version row.
- `GET /repos/veritaschain/vcp-spec/contents/README.md?ref=f833b52e52310900ce82f6d0726b635667a4f55b` and the same for `spec/v1.2/README.md` — GA wording, tag name in prose, and the "no technical change" sentence.
- `GET /repos/veritaschain/vcp-spec/pulls/1/reviews` — one review, id `5445011686`, `state` `COMMENTED`, `submitted_at` `2026-10-07T16:06:33Z`, on commit `52ee817caa27e9a70a4a2a151ed12bfd9372a947`. The body begins "Release review: HOLD / do not merge or create v1.2.0 yet." This is not an approving review. No `APPROVED` review was returned.

### Not yet reflected, owner, next action

At the time of this merge, the consistency correction, the real `v1.2.0` tag,
and the public VAP host were still ahead. Those are entries 2, 3, and 4.
What remains true about this commit: it must not be treated as the tagged GA.
Owner: maintainers of `veritaschain/vcp-spec` (the follow-up already on the
tagged commit). Next action: cite tag `v1.2.0` / `b23acb266f88df81d960d36d58fb64ceaa0dd5ed`
when a VCP v1.2 GA commit is required. Do not move the tag back to `f833b52`.

---

## 2. vcp-spec pull request #2 — GA contract correction

### Event time

`merged_at` **2026-10-09T08:33:29Z**, which is **2026-10-09 17:33:29 JST**
(2026-10-09 17:33 JST).

### DOC-SYNC entry time

2026-10-21 JST.

### Pull request, commit, tag, and files

| Item | Value |
| --- | --- |
| Repository | `veritaschain/vcp-spec` |
| Pull request | [#2](https://github.com/veritaschain/vcp-spec/pull/2), "Fix v1.2 GA blockers: canonical events, ERASURE encoding and regression fixtures" |
| State at confirmation | closed, merged |
| Merge commit | `b23acb266f88df81d960d36d58fb64ceaa0dd5ed` |
| Changed files (API `changed_files`) | 103 (6577 additions, 380 deletions) |
| Commits reported on the pull request | 2, plus this merge commit on main |
| Merged by (API login) | `veritaschain` |
| Tag | this commit is the target of lightweight tag `v1.2.0` (entry 3). The tag is not this pull request |

The 103 paths are the schemas, the new legacy schema, the annex, the
Japanese / English / Chinese text, the READMEs, the new consistency note,
83 fixtures, tests, and CI:

- Schemas: `spec/v1.2/vcp-event-v1.2.json`; new `spec/v1.2/vcp-event-v1.2-rc-legacy.json`
- Annex: `VSO-SPEC-CHANGE-001.md` and `spec/v1.2/VSO-SPEC-CHANGE-001.md`
- Text: `VCP-Specification-v1_2_en.md`, `VCP-Specification-v1_2_ja.md`, `VCP-Specification-v1_2_zh.md`, and the same three names under `spec/v1.2/`
- READMEs: `README.md`, `spec/v1.2/README.md`, `tests/fixtures/v1.2/README.md`
- New `spec/v1.2/GA-CONSISTENCY.md`
- Tests and CI: `tests/test_v1_2_contract.py`, `tools/validate_v1_2.py`, `requirements-test.txt`, `.github/workflows/validate-v1.2.yml`, plus `.gitignore` and `tests/fixtures/v1.2/manifest.json`
- 83 fixture JSON files under `tests/fixtures/v1.2/valid/` and `tests/fixtures/v1.2/invalid/`

The fixture directory in the file list has 85 paths. Two of them are
`tests/fixtures/v1.2/README.md` and `tests/fixtures/v1.2/manifest.json`. The
other 83 are the fixtures. 20 paths outside those 83 fixtures, plus the 83,
equal 103.

### Before

Main was at `f833b52` (entry 1). The README known-issues section said the
Production Ready text was the RC1 text with status, dates, and one informative
legal note updated, and that there was no technical change. The version table
named tag `v1.2.0` although that tag was not yet a git ref. The "zero breaking
changes" sentence was already present (it was present on RC1 main as well).

### After

The tagged tree withdraws the RC1-equals-GA claim. Root `README.md` at
`b23acb266f88df81d960d36d58fb64ceaa0dd5ed` says:

> The 2026-10-09 consistency correction changes pre-GA ERASURE encoding and
> registers the Annex system events. It is not technically identical to RC1.

`spec/v1.2/README.md` at the same commit says:

> The 2026-10-09 GA consistency correction changes the untagged pre-GA ERASURE
> encoding and adds the five Annex system codes to the schema. **This is not
> technically identical to RC1.**

`GA-CONSISTENCY.md` states the corrected contract: five system codes are
registered in the schema and in the EN/JA/ZH registry; ERASURE uses
`Payload.VCP-PRIVACY.ErasureDetails`; the pre-GA compact schema remains only
for explicit archival reads; inclusion proofs for an ERASURE event are detached
from its hashed payload. The GA schema registers these five codes:
`SYS_ANCHOR_FAILOVER`, `SYS_ANCHOR_MIGRATION`, `SYS_AUDIT`, `SYS_CHECKPOINT`,
`SYS_RECOVERY_ANNOUNCE`. The compatibility table in that file says the
RC1-to-GA technical-identity claim is withdrawn because the correction changes
wire format and validation, and that a pre-GA compact ERASURE producer is
deliberately rejected by the GA schema.

The same READMEs still contain a conflicting "zero breaking changes" line.
Root `README.md`:

> v1.2 is a protocol-compatible / certification-stricter update: zero breaking
> changes, all v1.0 and v1.1 events remain valid.

`spec/v1.2/README.md` still says it introduces **zero breaking changes**, and
also says "Untagged v1.2 ERASURE migration is explicitly breaking
(Annex §3.4.3)." Both lines are in the tagged tree. This entry does not remove
either line. Removing one would be a further change to `vcp-spec`, and this
record does not rewrite that repository.

### Reason

Close the two P1 wire-contract inconsistencies in the untagged GA merge:
register the five system codes, and replace the inconsistent pre-GA compact
ERASURE encoding with the canonical payload, with an explicit historical schema
for archival reads. `GA-CONSISTENCY.md` says historical signed records stay
unchanged and that signed bytes must not be rewritten.

### Impact

VCP v1.2 GA, as tagged, is not technically identical to RC1. ERASURE format and
verification changed for untagged pre-GA producers. Five `SYS_*` codes were
added. Consumers who implemented against RC1, or against `f833b52`, do not
automatically match the tagged schema. The README's "zero breaking changes"
line conflicts with that correction and with the "explicitly breaking" ERASURE
sentence in `spec/v1.2/README.md`. VAP requirement identifiers are a separate
document; this entry does not change them.

### Verifier and evidence

Verifier: VSO 主任, via the GitHub API, on 2026-10-21 JST.

- `GET /repos/veritaschain/vcp-spec/pulls/2` — `merged_at` `2026-10-09T08:33:29Z`, `merge_commit_sha` `b23acb266f88df81d960d36d58fb64ceaa0dd5ed`, `changed_files` 103, `commits` 2, `merged_by.login` `veritaschain`.
- `GET /repos/veritaschain/vcp-spec/pulls/2/files` (paginated) — 103 filenames, counted above.
- `GET /repos/veritaschain/vcp-spec/commits/b23acb266f88df81d960d36d58fb64ceaa0dd5ed` — committer date `2026-10-09T08:33:28Z`. That is the commit date, one second before `merged_at`. It is not a tag date.
- `GET /repos/veritaschain/vcp-spec/contents/README.md?ref=b23acb266f88df81d960d36d58fb64ceaa0dd5ed` and `spec/v1.2/README.md` and `spec/v1.2/GA-CONSISTENCY.md` at the same ref — the sentences quoted above.
- `GET /repos/veritaschain/vcp-spec/contents/spec/v1.2/vcp-event-v1.2.json?ref=b23acb266f88df81d960d36d58fb64ceaa0dd5ed` — the five `SYS_*` codes listed above.
- `GET /repos/veritaschain/vcp-spec/pulls/2/reviews` — empty array. No approving review is recorded.

### Not yet reflected, owner, next action

The conflicting "zero breaking changes" line is still in the tagged READMEs.
Owner: maintainers of `veritaschain/vcp-spec`. Next action: a later errata or
revision may remove or qualify that line. This DOC-SYNC does not edit
`vcp-spec`, and it is not authority to move tag `v1.2.0`. Site reflection of
the tagged text is entry 4. The K3 case is entry 5.

---

## 3. Tag `v1.2.0`

### Event time

The git tag is lightweight. Its creation date is **unknown**. It is not
inferred from the commit date.

The tag points at commit `b23acb266f88df81d960d36d58fb64ceaa0dd5ed`. That
commit's committer date is `2026-10-09T08:33:28Z` (2026-10-09 17:33:28 JST).
That date belongs to the commit. It is recorded here so it is not reused as
a tag date.

### DOC-SYNC entry time

2026-10-21 JST.

### Pull request, commit, tag, and files

| Item | Value |
| --- | --- |
| Repository | `veritaschain/vcp-spec` |
| Tag | `v1.2.0` (`refs/tags/v1.2.0`) |
| Tag object type | `commit` (lightweight). Not an annotated tag |
| Target commit | `b23acb266f88df81d960d36d58fb64ceaa0dd5ed` (pull request #2 merge commit) |
| Files | the tree of that commit, including the 103 paths in entry 2. The tag itself is a ref, not a file change |
| Pull request | #2 is the merge that produced the target commit. The tag is a separate ref |

A GitHub Release object also exists for tag name `v1.2.0`
(<https://github.com/veritaschain/vcp-spec/releases/tag/v1.2.0>).
`GET /repos/veritaschain/vcp-spec/releases/tags/v1.2.0` returned
`created_at` `2026-10-09T08:33:28Z`, `published_at` `2026-10-09T08:36:11Z`
(2026-10-09 17:36:11 JST), `target_commitish` `main`, `draft` false,
`prerelease` false. `created_at` equals the commit's committer date. It is
not used as the git tag's creation date. `published_at` is the Release
object's publication time only.

### Before

No `refs/tags/v1.2.0` existed when `GA-CONSISTENCY.md` was written (that file
says so). Pull request #1's README nevertheless named the tag. The HOLD review
on pull request #1 said not to create `v1.2.0` yet.

### After

`refs/tags/v1.2.0` resolves to `b23acb266f88df81d960d36d58fb64ceaa0dd5ed`.
It does not resolve to `f833b52`. There is no tagger identity and no tagger
date, because the ref's object type is `commit`.

### Reason

Point `v1.2.0` at the corrected main commit after pull request #2, not at the
uncorrected pull request #1 merge. `GA-CONSISTENCY.md` states that order:
create the tag only at the corrected commit, and do not replace an existing tag.

### Impact

The citable VCP v1.2 GA commit is `b23acb266f88df81d960d36d58fb64ceaa0dd5ed`.
Anything that still tracks `f833b52`, RC1, or the "no technical change"
sentence is not tracking the tag. Absence of a tagger date means the moment
the ref was created cannot be stated from the git object.

### Verifier and evidence

Verifier: VSO 主任, via the GitHub API, on 2026-10-21 JST.

- `GET /repos/veritaschain/vcp-spec/git/refs/tags/v1.2.0` — `object.type` `commit`, `object.sha` `b23acb266f88df81d960d36d58fb64ceaa0dd5ed`.
- `GET /repos/veritaschain/vcp-spec/git/tags/b23acb266f88df81d960d36d58fb64ceaa0dd5ed` — HTTP 404. That SHA is a commit, not an annotated tag object.
- `GET /repos/veritaschain/vcp-spec/commits/b23acb266f88df81d960d36d58fb64ceaa0dd5ed` — committer date as above, not adopted as the tag date.
- `GET /repos/veritaschain/vcp-spec/releases/tags/v1.2.0` — Release fields as above, distinguished from the git tag.

No signature on the tag was found, because there is no tag object. None was
added.

### Not yet reflected, owner, next action

The tag date stays unknown. Owner: whoever would otherwise backfill a date
(do not). Next action: leave the lightweight tag as it is. Do not annotate it,
move it, or delete and recreate it in order to manufacture a creation date.
Downstream pages that still say RC1 are entry 4.

---

## 4. Site reflection of VCP v1.2

### Event time

Two surfaces, observed on the DOC-SYNC entry date. They are not one event.

- `veritaschain/vcp-site` pull request [#78](https://github.com/veritaschain/vcp-site/pull/78) `merged_at` **2026-10-09T08:36:53Z**, which is **2026-10-09 17:36:53 JST**. Merge commit `a790ce2b198ba988454ff94111513356815d0bbb`. Title: "Refresh current-version and IETF status statements (VCP v1.2 GA, CPP v1.4, active I-Ds) — en/ja/zh".
- `https://vap.veritaschain.org/` response on 2026-10-21: `Last-Modified: Thu, 20 Aug 2026 19:18:51 GMT`.

### DOC-SYNC entry time

2026-10-21 JST.

### Pull request, commit, tag, and files

| Item | Value |
| --- | --- |
| vcp-spec tag this reflection is about | `v1.2.0` at `b23acb266f88df81d960d36d58fb64ceaa0dd5ed` |
| vcp-site pull request | #78, merged, merge commit `a790ce2b198ba988454ff94111513356815d0bbb` |
| Open vcp-site pull requests on 2026-10-21 | #52 only, "certificationページ削除" (<https://github.com/veritaschain/vcp-site/pull/52>). It is not a v1.2 GA reflection |
| `vap.veritaschain.org` | not a GitHub repository. Response header `server: nginx` |

`GA-CONSISTENCY.md` listed "Merge vcp-site PR #78" as release gate 5, after the
tag and after vap-spec pull request #9. Pull request #78 is merged. A pending
vcp-site pull request for this reflection was **not** found. This entry does
not invent one.

`https://veritaschain.org/vap/` on 2026-10-21 was served with `server: GitHub.com`
and the page text included "v1.2 Released" for VCP. That host is the GitHub
Pages site from `vcp-site`, not `vap.veritaschain.org`.

### Before

`GA-CONSISTENCY.md` treated vcp-site publication as a step that had to follow
the tag. `vap.veritaschain.org`, as still served on 2026-10-21, labels VCP
with the chip text `v1.2 RC1`.

### After

vcp-site pull request #78 is merged, and `https://veritaschain.org/vap/` shows
VCP v1.2 as Released. `https://vap.veritaschain.org/` is unchanged relative to
its `Last-Modified` of 20 August 2026 GMT and still shows `v1.2 RC1`.

### Reason

The tagged specification and the VAP registry in this repository record VCP
v1.2 as Released. A public page that still says RC1 does not match that tag.

### Impact

Anyone who reads `vap.veritaschain.org` still sees VCP v1.2 RC1. Anyone who
reads `veritaschain.org/vap/` sees v1.2 Released. The two hosts disagree.
Merging a vcp-site pull request does not update the nginx host.

### Verifier and evidence

Verifier: VSO 主任, via the GitHub API, on 2026-10-21 JST, plus the HTTP
responses below for the hosts the API does not store.

- `gh pr view 78 --repo veritaschain/vcp-site` — `state` `MERGED`, `mergedAt` `2026-10-09T08:36:53Z`, `mergeCommit.oid` `a790ce2b198ba988454ff94111513356815d0bbb`.
- `gh pr list --repo veritaschain/vcp-site --state open` — pull request #52 only.
- `GET https://vap.veritaschain.org/` — `server: nginx`, `last-modified: Thu, 20 Aug 2026 19:18:51 GMT`, body contains `v1.2 RC1` on the VCP card.
- `GET https://veritaschain.org/vap/` — `server: GitHub.com`, body contains "v1.2 Released" for VCP.

No approval of the nginx host was found, and none is added.

### Not yet reflected, owner, next action

Not yet reflected: `https://vap.veritaschain.org/`, which is hosted outside
GitHub. Owner: the operator of that host, VSO, operated by VeritasChain Co., Ltd.
Next action: update that host from tag `v1.2.0` so it no longer presents VCP
v1.2 as RC1. Do not treat vcp-site #78, which is already merged, as that update,
and do not open a vcp-site pull request on the claim that one is already pending.

---

## 5. K3-VCP-BLIND-001

### Event time

No migration event is recorded. The fact being registered is the absence of an
automatic move onto VCP v1.2 GA. Confirmation date of that fact for this file:
2026-10-21 JST. There is no separate API timestamp for a case revision, because
the case file was not returned by the organization code search.

### DOC-SYNC entry time

2026-10-21 JST.

### Pull request, commit, tag, and files

| Item | Value |
| --- | --- |
| Case | K3-VCP-BLIND-001, described for this entry as case v0.4 |
| VCP versions named by that description | VCP v1.2 RC1 and v1.0 |
| VCP GA tag | `v1.2.0` at `b23acb266f88df81d960d36d58fb64ceaa0dd5ed` (entries 2 and 3) |
| Pull request | none in this confirmation |
| Files in `veritaschain` | `GET /search/code` for `K3-VCP-BLIND-001 org:veritaschain` returned `total_count` 0 on 2026-10-21. The case text was not retrieved. This entry does not quote it |

The statement under confirmation is: case v0.4 references VCP v1.2 RC1 and
v1.0, so there is no automatic migration to GA. That statement is recorded
because it is the impact to track. It is not a quotation from a file this
confirmation opened.

### Before

The case, as described, is pinned to VCP v1.2 RC1 and v1.0.

### After

No new case revision is recorded here. Tagging VCP v1.2 GA does not by itself
move the case onto GA. Version confirmation with the K3 evaluator is pending.

### Reason

RC1 and GA are not technically identical (entry 2). A case that cites RC1 and
v1.0 cannot be treated as assessed against tag `v1.2.0` without a new
confirmation.

### Impact

K3-VCP-BLIND-001 does not automatically migrate to VCP v1.2 GA. Results,
fixtures, or conclusions tied to RC1 or to v1.0 stay tied to those versions
until the evaluator confirms otherwise. This file does not change the case.

### Verifier and evidence

Verifier: VSO 主任, via the GitHub API, on 2026-10-21 JST.

- `GET /search/code?q=K3-VCP-BLIND-001+org:veritaschain` — `total_count` 0.
- Entries 2 and 3 for the GA tag and for the RC1 difference.
- No evaluator message, approval, or case commit was returned. None is added.

### Not yet reflected, owner, next action

Not yet reflected: a confirmed VCP version for K3-VCP-BLIND-001 against tag
`v1.2.0`. Owner: the K3 evaluator. Next action: the evaluator confirms whether
the case remains on v0.4's cited versions (VCP v1.2 RC1 and v1.0) or is
reissued against the tagged GA text. Until that confirmation, do not describe
the case as migrated.

---

## What this file does not record

- No approval of pull request #1, pull request #2, tag `v1.2.0`, vcp-site #78,
  or K3-VCP-BLIND-001, beyond the API fields cited above. The pull request #1
  review that was returned is a HOLD comment, not an approval. Pull request #2
  returned no reviews.
- No tag creation date for `v1.2.0`.
- No edit to any tag, release, or signed object.
- The VAP CAB-independence errata in this repository is a separate commit. It
  is not one of the VCP events above, and it does not change VAP's version or
  status.
