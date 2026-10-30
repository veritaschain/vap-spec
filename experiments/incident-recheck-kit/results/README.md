# Offline kit execution records

This directory records the kit's tested commit, exact execution source manifest,
archive SHA-256 and retrieved CI results. Original pilot evidence is retained
separately in [the fixed capture](../snapshots/2026-10-30-ci/provenance.json).

The implementation is undergoing its first complete local and CI validation.
No independent reproduction or VAP conformance claim is made. A successful kit
run rechecks the saved 53 cases and does not repeat the original pilot actions.

Result documents and JSON in this directory are outside the archived payload
and execution source manifest; recording the obtained result cannot alter the
ZIP bytes whose checksum is being recorded.
