# Execution records

The editing environment forbids socket creation. Local unit verification therefore
does not establish real HTTP execution; four live-network test methods are explicitly
skipped there. Required CI runs set PILOT_NETWORK_TESTS=1 and reject all skips.

Actual network-run summaries will be recorded here only after retrieving completed
CI results. Each summary identifies its source manifest, toolchain, measured scenario
observations and cleanup status. Full public evidence and synthetic runtime databases
are retained in the associated GitHub Actions artifact for 30 days. They contain no
private signing keys or payload plaintext.

A matched negative control does not establish security or VAP/CAP conformance.
