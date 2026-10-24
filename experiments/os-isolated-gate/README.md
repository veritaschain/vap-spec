# OS-isolated mock pre-record gate — experimental, unadopted

This separate research experiment tests Linux enforcement around the merged PR #11
mock gate: distinct non-root UIDs, private namespaces and volumes, kernel file
permissions, and direct API reachability. It uses synthetic records and ephemeral
keys only. No real API or external service is invoked by the runtime roles.

**Unadopted experimental extension.** No formal proposal number or applicable
release is assigned. This is not a VAP v1.2 requirement, conformance implementation,
production security boundary, or independent reproduction. The v1.2 specification,
existing declared-scope verifier, PR #11 gate, proposal text, DOC-SYNC and K3 are
unchanged. The new adapter imports their existing code without editing it.

## Boundary being exercised

| Role | UID:GID | Networks | Writable storage |
| --- | --- | --- | --- |
| agent | 10001:10001 | frontend | own disposable log volume |
| gate | 10002:10002 | frontend, audit, backend | own volume |
| audit | 10003:10003 | audit | signed ledger in SQLite |
| backend | 10004:10004 | backend | mock effects in SQLite |
| open-backend | 10005:10005 | backend | separate deliberately unauthenticated mock effects |

All runtime roots are read-only, capabilities are dropped, `no-new-privileges` is
set, and the default Docker seccomp profile remains enabled. No host ports or
Docker socket are mounted/published. Each role sees only its own read-only config
volume and private keys. Foreign-role keys are absent from its mount namespace.
Shared **non-secret** canaries (0700 role directory, 0400 file) additionally test
that the other four UIDs receive kernel `EACCES`, not just a missing-file error.

The trusted controller owns Docker authority and creates fresh Ed25519 keys. A
one-shot network-less setup container runs as root with only CHOWN, DAC_OVERRIDE
and FOWNER to initialize named-volume ownership. It never acts as an agent or a
runtime service. No probe elevates a runtime role. The controller intentionally
adds/removes one network membership for negative controls and removes only its
randomly named project's containers, volumes, networks and image afterward.

The unchanged gate previously used loopback endpoints. The new process injects a
transport adapter accepting exactly `http://audit:8080` and
`http://backend:8080`. It follows no redirects or proxy environment variables.
Its gate HTTP entry point only accepts `/execute`; callers cannot choose a URL,
proxy path or CONNECT tunnel. Payloads retain the original signatures and binding
checks. The new services bind inside their container network namespaces only.

## Reproduce

Use a disposable **Linux Docker Engine** with Docker Compose v2 and Python 3.12+
(the trusted controller needs permission to manage Docker). The image is pinned
by digest and Python dependencies use the prior verifier's pinned versions.
From this directory:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m isolation_lab run-suite
```

The last command builds the image, provisions the mock lab, executes all sixteen
cases, writes `generated/`, and cleans up. Exit 0 requires the exact case inventory,
all expected outcomes, and successful teardown. Missing Docker, an incomplete
run or cleanup failure is not a passing result. If a controller is forcibly killed,
remove only the project named `vap-isolation-<run suffix>` shown in Docker, not
unrelated resources. The Docker build needs registry/package-network access;
the runtime roles use three private, internal bridge networks.

To recheck a saved evidence bundle without Docker, use the unchanged verifier
and native receipt checks through this thin entry point:

```sh
.venv/bin/python -m isolation_lab verify-evidence generated/evidence.json
```

This checks actual signatures/bindings and recomputes both reports. It does not
re-execute the OS experiment or authenticate the host's network observations.

A dedicated `.github/workflows/os-isolated-gate.yml` runs the actual Linux lab
and the unchanged gate/verifier regression and acceptance suites. Local Mac
controller tests do **not** establish Linux OS isolation. See `results/` for
retained actual execution records when available; the script alone is not a result.

## Sixteen measured cases

| Case | Expected observation |
| --- | --- |
| 01 | Actual UIDs/GIDs, distinct mount/PID/network namespaces, zero capabilities, no-new-privileges and seccomp; `setuid(0)` rejected |
| 02 | Own config/canary readable; all foreign UID canaries fail with `EACCES` |
| 03 | Code/config writes rejected; only own role config mounted; no seed or engine socket |
| 04 | Exact expected internal network memberships and no published ports |
| 05 | Authorized gate path creates one effect and one backend handler invocation |
| 06 | Agent direct backend **literal IPv4** request cannot connect; healthy target, unchanged counters |
| 07 | Direct audit literal IPv4 request cannot connect; audit remains healthy |
| 08 | Direct unauthenticated mock API IPv4 request cannot connect; zero handler invocations/effects |
| 09 | Unsupported target denied and `/proxy` unavailable; effect count unchanged |
| 10 | CONNECT tunnel unavailable; effect count unchanged |
| 11 | Deleting an agent log leaves signed ledger unchanged; exported actual evidence verifies in both modes, with scope judgment only in experimental mode |
| 12 | Audit stopped: a second independently authorized operation is blocked before any backend invocation |
| 13 | Audit restarted: first result/evidence persist, retry does not resend |
| 14 | Controller adds backend network to agent: connection works, normal backend returns 403 and makes no new effect |
| 15 | Same added route reaches the deliberately unauthenticated API and creates an effect: **bypass guarantee is false** |
| 16 | Controller removes added route: direct connection again denied, target stays healthy |

Case 15 is expected to expose a bypass. “All expectations matched” means the
controls behaved as predicted, **not** that every tested topology was secure.
Cases 06–08 distinguish transport denial from application authentication. A
healthy target and the reachable negative control prevent an absent or crashed
API from being mistaken for effective isolation. Backend counters are read from
its actual persisted handler/effect tables by the trusted controller.

Reports keep raw probe observations, sanitized runtime inspection, Docker/Compose/
kernel versions, source commit/digest and cleanup status. The evidence bundle is
built from actual signed audit events and backend receipts, then passed through
the **unchanged** existing verifier. `vap-v1.2` does not acquire scope evaluation;
`experimental-scope` stays explicitly unadopted. Cryptographic integrity and
scope fulfillment remain separate fields. No `signature_valid` input flag is used.
All identity/approval/time evidence is synthetic; the scope receipt is signed by a
test key and is **not independent third-party time evidence**. Fixed logical times
are fixture values, not assertions about wall-clock issuance or production expiry.

## Limits and interpretation

The hostile role in this experiment is the unprivileged agent. The host kernel,
Docker daemon/controller, setup, gate, audit and backend are trusted. Containers
share a kernel. We do not test kernel exploits, privileged-host access, daemon
compromise, rootless/user-namespace deployments, malicious trusted services,
ptrace escapes, side channels or resource-exhaustion resistance. A privileged
operator can change network memberships, as the negative control demonstrates.

Only this IPv4 topology and these enumerated paths are measured. Internal Docker
networks do not by themselves prove host services unreachable. Host bridge
services, IPv6, alternate transports, arbitrary egress, other API credentials and
uncontrolled real-world routes are **not established**. No real endpoint or host
port is probed. Production deployment would require its own enforced routing,
identity, key management, revocation/clock and failure analysis. Docker isolation
is a configuration-dependent OS boundary, not a new VAP cryptographic guarantee.

Reference behavior: Docker documents [network membership and service discovery](https://docs.docker.com/compose/how-tos/networking/),
[internal networks](https://docs.docker.com/reference/compose-file/networks/),
[bridge isolation](https://docs.docker.com/engine/network/drivers/bridge/), and
[runtime service controls](https://docs.docker.com/reference/compose-file/services/).
Actual observations in this lab, rather than those configuration descriptions
alone, determine the test result.
