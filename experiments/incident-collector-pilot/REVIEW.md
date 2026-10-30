# Threat and evidence review

This additive pilot measures a controlled application path. All policy, gateway,
collector and receiver keys belong to one synthetic controller. Signatures bind
statements to those declared keys; they do not establish independent observation.

## Decisions

1. **Own inputs once.** Immutable payload bytes, complete subject, policy and
   permit bindings are captured before collection. Later caller mutations cannot
   change the measured/sent body or original evaluator context.
2. **Claim before external operations.** The local atomic claim precedes metadata
   RPCs. Committed claims stay consumed through failures, concurrent calls and
   restart. Unestablished claims block the current call. A pre-commit fault is not
   represented as a committed durable marker.
3. **Separate recovery from execution.** Reconciliation validates the saved
   snapshot and pins, then sends only a read-only status query. It never retries
   collection or resumes payload transmission. Current upload authority is
   required for a new, separately bound request.
4. **Use exact fresh evidence.** The collector identity, request ID, complete
   subject digest, policy digest, signed permit digest, payload digest/length,
   signed intent digest and fresh query nonce remain bound across each exchange.
   Cached receipts alone cannot create current health.
5. **Preserve actual time.** A record's pre-commit timestamp is `recorded_at`.
   Commit/readback completes before the receipt is returned. The gateway's real
   verification time supports the final prerequisite only. Postflight never
   rewrites health to the later transport dispatch timestamp.
6. **Retain uncertainty.** Lost collector responses cannot prove no collection;
   lost receiver responses cannot prove no payload receipt. Result persistence
   failure cannot retain a stronger confirmed gateway outcome.
7. **Keep checks reproducible.** Exports retain original messages and evidence
   frames. An externally supplied raw summary hash pins the case bytes; the
   verifier also checks signatures, bindings, chronology and actual source bytes.

## Specific implementation boundaries

The collector uses literal loopback endpoints, bounded JSON and headers,
single-attempt HTTP, exact schemas, strict integer/boolean types and a distinct
signature domain. Request content cannot select a new key, route, namespace or
fault mode. The process restarts only against matching pinned identity/key/DB/
endpoint configuration. Same metadata is idempotent; conflicting metadata under
the same identity is refused.

SQLite WAL/FULL and explicit connection closure are checked by the implementation
and resource-warning tests. These checks do not measure machine power failure,
malicious filesystem edits or hardware durability. The final readback is a
point-in-time observation; it does not establish continuous availability between
that check and transmission. The receiver trusts the gateway's signed dispatch
intent and does not independently verify the collector prerequisite.

The original receiver, transport, journal and assessor are reused without edits.
All 154 historical execution inputs are hashed before importing reused code.
The verifier does not load code or trust keys from an evidence-selected path and
performs no network calls. The Python environment is version-pinned but is not
hermetic; its operating system, libraries and runtime remain explicit assumptions.

The finite scenario catalogue is not an assurance score. No claim is made about
unmanaged upload routes, real PHI, model internals, provider deletion, real-world
key onboarding/revocation, external anchoring, production readiness, legal
compliance or full VAP/CAP conformance.
