# Fixed research distribution: protection review

**24 October 2026 (JST).** This records repository controls and their limits. The
research extension remains **unadopted**; independent third-party reproduction
has **not been established**. No specification, implementation or fixed artifact
was changed by this review.

## Controls applied and checked

- The active [research-tag ruleset](https://github.com/veritaschain/vap-spec/rules/25774130)
  prohibits updates and deletions of `refs/tags/research-kit-*`, with no bypass
  actors or exclusions. Creating a differently named tag remains possible.
- A disposable matching tag was created for an enforcement check. Both a forced
  update and deletion were rejected by GitHub with HTTP 422 ("Cannot update this
  protected ref." / "Cannot delete this tag"). Only that disposable tag was
  temporarily excluded for cleanup; the exclusion was then removed. The actual
  distribution tag was never excluded or modified. The final ruleset was read
  back as active, with no exclusions and no bypass for the current maintainer.
- `research-kit-b1af0dc-20261024` still points to
  `b1af0dc9d368b466bf74e7c1b2a6808fb41949ae`. Release ID `422515153`, its publication
  time and all five asset IDs, sizes, digests and update times matched the records
  taken before this review. The release was neither deleted nor republished.
- Release immutability is now enabled for **future releases**. GitHub reports
  `enabled: true` and `enforced_by_owner: false` for this repository setting.
  [GitHub documents that this setting does not apply retroactively](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/prevent-release-changes).

## Write-access review

The repository is owned by the `veritaschain` user account. The visible
collaborator listing contained only that account, with administrator access.
No deploy keys, repository Actions secrets or environments were listed. Default
workflow-token permissions were read-only and workflow approval of pull requests
was disabled. All four existing workflows declared `contents: read` and pinned
their action dependencies to commit hashes. No additional write credential was
identified in those workflows. No credential was revoked on the basis of an
assumption that it was unused.

The available CLI credential could not enumerate user-installed GitHub Apps
(the endpoint requires a GitHub App user token). This review therefore **does not
establish a complete inventory of Apps, OAuth grants or personal access tokens**.
The maintainer's authenticated CLI retains administrative/write access. Account
security settings and other credentials were not changed.

## Remaining limits and correction policy

The existing release still reports **`immutable: false`**. Tag protection does
not lock its assets: a credential with sufficient release-write permission can
still replace or delete those files. Ordinary existing CI workflows lack that
write permission, but this is **not complete asset immutability**. Administrators
can also change repository rules or settings. The ruleset enforcement check is
not a claim of protection against an administrator changing the controls.

Continue to preserve the separate copies and compare the published checksums.
Keep this distribution and its historical evidence unchanged. Corrections must
use a new version identifier and checksum, with a dated notice referring to the
affected version. Do not silently replace an old ZIP or revise expected results
to turn a failed reproduction into a success. Future distributions should use
the enabled immutable-release workflow. None of these controls establishes host
authenticity, production suitability or evaluator independence.
