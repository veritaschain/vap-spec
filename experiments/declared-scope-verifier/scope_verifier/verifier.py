"""Separate current-framework checks from unadopted scope semantics."""

from . import ADAPTER, BASELINE, VERSION
from .crypto import (InputError, MAX_ITEMS, authenticate, canonical, digest,
                     hex_bytes, inclusion, leaf_hash, merkle_root, natural)


def aggregate(checks):
    states = [check["result"] for check in checks]
    if "failed" in states:
        return "failed"
    if not states or "indeterminate" in states:
        return "indeterminate"
    return "verified"


class Checks:
    def __init__(self):
        self.items = []

    def add(self, name, state, reason, evidence):
        self.items.append(dict(check=name, result=state, reason=reason, evidence=evidence))
        return state == "verified"

    def test(self, name, condition, reason, evidence):
        return self.add(name, "verified" if condition else "failed", reason, evidence)


class Evaluation:
    def __init__(self, package, trust, at, simulate):
        self.p, self.trust = package, trust
        self.at = natural(at, 2**53 - 1)
        self.simulate = simulate and trust.get("purpose") == "synthetic-test-only"
        self.crypto = Checks()
        self.requirements = Checks()
        self.records = {}
        self.proofs = {}
        self.record_valid = {}
        self.anchor_ok = False
        self.index_ok = False
        self.index = []
        self.policy_ok = False

    def signed(self, obj, kind, ref):
        state, reason = authenticate(obj, self.trust, kind)
        ok = self.crypto.add(ref + ".signature", state, reason, [ref])
        if obj is None:
            return False
        body = obj["body"]
        binding = (body["kind"] == kind and body["evaluation_id"] == self.trust["evaluation_id"]
                   and body["policy_digest"] == self.trust["policy_digest"])
        return self.crypto.test(ref + ".binding", binding,
                                "Object kind, evaluation and policy must match evaluator inputs", [ref]) and ok

    def receipt(self, obj, target, purpose, ref):
        if obj is None:
            self.crypto.add(ref, "indeterminate", "Required external receipt is absent", [ref])
            return False
        ok = self.signed(obj, "receipt", ref)
        body = obj["body"]
        ok = self.crypto.test(ref + ".target", body["target_digest"] == target and
                              body["purpose"] == purpose, "Exact receipt target and purpose binding", [ref]) and ok
        natural(body["accepted_at"], 2**53 - 1)
        natural(body["uncertainty"], 86400)
        if body["accepted_at"] + body["uncertainty"] > self.at:
            self.crypto.add(ref + ".availability", "indeterminate",
                            "Receipt is not established by the evaluator's time", [ref])
            return False
        if body.get("adapter") != "synthetic-receipt/1" or not self.simulate:
            self.crypto.add(ref + ".trust_path", "indeterminate",
                            "Only a simulated receipt adapter exists; use explicit synthetic mode for fixtures", [ref])
            return False
        self.crypto.add(ref + ".trust_path", "verified",
                        "Simulation: test key authenticates the receipt; no independent time attestation", [ref])
        return ok

    def core(self):
        p = self.p
        if p["format"] != ADAPTER:
            raise InputError("Unsupported evidence adapter")
        if not isinstance(p["events"], list) or len(p["events"]) > MAX_ITEMS:
            raise InputError("Unsupported event collection")
        self.policy = p["policy"]
        if self.policy["adapter"] != ADAPTER or self.policy["multiplicity"] != "exactly-one-per-obligation":
            raise InputError("Unimplemented adapter or multiplicity policy")
        self.policy_ok = self.crypto.test("policy.binding", digest(self.policy) == self.trust["policy_digest"],
                                         "Policy digest must be pinned outside the package", ["policy", "trust.policy_digest"])
        self.anchor_ok = self.signed(p.get("anchor"), "anchor", "anchor") and self.policy_ok
        if not p.get("anchor"):
            raise InputError("This adapter requires an anchor object")
        anchor = p["anchor"]["body"]
        batch = anchor["batch"]
        size = natural(batch["event_count"])
        self.index = p["batch_index"]
        if not isinstance(self.index, list) or len(self.index) > MAX_ITEMS:
            raise InputError("Unsupported batch index")
        ids = [entry["event_id"] for entry in self.index]
        index_good = (len(self.index) == size and len(set(ids)) == size and
                      digest(self.index) == batch["index_digest"] and
                      merkle_root([hex_bytes(e["leaf_hash"]) for e in self.index]).hex() == batch["merkle_root"] and
                      batch["first_event_id"] == (ids[0] if ids else None) and
                      batch["last_event_id"] == (ids[-1] if ids else None) and
                      batch["policy_digest"] == self.trust["policy_digest"])
        self.index_ok = self.crypto.test("anchor.index", index_good,
                                        "Signed index digest, distinct IDs, root, count, endpoints and policy binding",
                                        ["anchor.batch", "batch_index"]) and self.anchor_ok
        receipt_ok = self.receipt(p.get("anchor_receipt"), digest(p["anchor"]), "anchor", "anchor_receipt")
        self.anchor_ok = self.anchor_ok and receipt_ok
        delivered_ids, indices = [], []
        hash_checks, sig_checks, proof_checks = [], [], []
        for pos, event in enumerate(p["events"]):
            ref = f"events[{pos}]"
            body = event["signed"]["body"]
            event_id = body["event_id"]
            if not isinstance(event_id, str) or not event_id:
                raise InputError("Event ID must be a nonempty string")
            sig_ok = self.signed(event["signed"], "event", ref + ".signed")
            source_ok = event["signed"]["key_id"] in self.policy["event_signers"].get(body["source_id"], [])
            sig_ok = self.crypto.add(ref + ".source", "verified" if source_ok else "indeterminate",
                                     "Signer authorization for the named source", [ref, "policy"]) and sig_ok
            hash_ok = self.crypto.test(ref + ".hash", digest(body) == event["event_hash"],
                                       "SHA-256 of RFC 8785 canonical event body", [ref])
            index = natural(event["index"])
            proof_ok = (index < len(self.index) and self.index[index] == {
                "event_id": event_id, "source_id": body["source_id"], "event_type": body["event_type"],
                "leaf_hash": leaf_hash(body).hex(),
            } and inclusion(leaf_hash(body), index, size, event["path"], batch["merkle_root"]))
            proof_ok = self.crypto.test(ref + ".inclusion", proof_ok,
                                        "RFC 6962 inclusion and authenticated index identity", [ref, "anchor", "batch_index"])
            valid = sig_ok and hash_ok and proof_ok and self.index_ok and self.anchor_ok
            delivered_ids.append(event_id)
            indices.append(index)
            self.records.setdefault(event_id, []).append(body)
            self.record_valid.setdefault(event_id, []).append(valid)
            hash_checks.append(hash_ok)
            sig_checks.append(sig_ok)
            proof_checks.append(proof_ok)
        if not isinstance(p.get("commitment_proofs", []), list) or len(p.get("commitment_proofs", [])) > MAX_ITEMS:
            raise InputError("Unsupported commitment proof collection")
        for pos, proof in enumerate(p.get("commitment_proofs", [])):
            ref = f"commitment_proofs[{pos}]"
            index = natural(proof["index"])
            identity = {k: proof[k] for k in ("event_id", "event_type", "source_id", "leaf_hash")}
            valid = (index < len(self.index) and self.index[index] == identity and
                     inclusion(hex_bytes(proof["leaf_hash"]), index, size, proof["path"], batch["merkle_root"]))
            valid = self.crypto.test(ref, valid, "Hidden payload commitment bound to the authenticated batch index",
                                     [ref, "anchor", "batch_index"]) and self.index_ok and self.anchor_ok
            self.proofs.setdefault(proof["event_id"], []).append({"valid": valid, **identity})
        req = self.requirements
        req.add("INT-001/003", "verified" if all(hash_checks) else "failed",
                "Implemented JCS and event hashes for supplied event bodies only", ["events"])
        req.test("INT-002", len(set(delivered_ids)) == len(delivered_ids),
                 "Distinct supplied event IDs; UUIDv7 is not imposed by this adapter", ["events"])
        signature_failure = any(c["check"].startswith("events[") and c["check"].endswith(".signature") and
                                c["result"] == "failed" for c in self.crypto.items)
        req.add("INT-005", "verified" if all(sig_checks) else ("failed" if signature_failure else "indeterminate"),
                "Ed25519 event signatures requested by this experiment policy; framework requirement is SHOULD", ["events"])
        req.add("INT-006", "verified" if self.anchor_ok and self.index_ok and all(proof_checks) else
                ("failed" if aggregate(self.crypto.items) == "failed" else "indeterminate"),
                "Signed Merkle root, inclusion and external receipt; simulation only when explicitly enabled",
                ["anchor", "anchor_receipt", "events", "batch_index"])
        complete = (len(delivered_ids) == size and len(set(delivered_ids)) == size and
                    set(indices) == set(range(size)) and set(delivered_ids) == set(ids))
        completeness = "verified" if complete else "failed"
        if complete and not all(hash_checks + sig_checks + proof_checks):
            completeness = "indeterminate"
        req.add("INT-008", completeness if self.index_ok and self.anchor_ok else "indeterminate",
                "Reconcile delivery with the original authenticated batch, including count, IDs, range and policy; "
                "a valid subset is not a complete batch", ["anchor", "batch_index", "events"])
        for name, reason in {
            "INT-004": "Profile-specific sequencing beyond Merkle position is not implemented",
            "INT-007": "Operational continuity, fallback and assurance evidence are not implemented",
            "INT-009": "Recovery authorization and bounds are not implemented",
        }.items():
            req.add(name, "indeterminate", reason, [])

    def experimental(self):
        x = self.p.get("experimental")
        findings, unresolved = [], []
        scope_checks = Checks()

        def unknown(code, reason, evidence):
            unresolved.append(dict(code=code, reason=reason, evidence=evidence))

        def violation(code, reason, evidence):
            findings.append(dict(code=code, reason=reason, evidence=evidence,
                                 occurrence_of_underlying_actions="not_determined"))

        def finish(expected=None, satisfied=0, accounted=False, dispositions=None):
            return dict(result="not_met" if findings else ("indeterminate" if unresolved else "met"),
                        expected_distinct_obligations=expected, satisfied_distinct_obligations=satisfied,
                        inventory_accounted_for=accounted, presentation_states=dispositions or {},
                        violations=findings, unresolved=unresolved, checks=scope_checks.items,
                        occurrence_of_underlying_actions="not_determined",
                        claim_boundary="Declared synthetic observation boundary and exact evaluation policy only")

        if not x:
            unknown("extension_missing", "Experimental sidecars not supplied", ["experimental"])
            return finish()
        scope_env = x.get("scope")
        scope_ok = self.signed(scope_env, "scope", "experimental.scope")
        if not scope_env:
            unknown("scope_missing", "No scope declaration", ["experimental.scope"])
            return finish()
        scope = scope_env["body"]
        scope_digest = digest(scope_env)
        pinned = self.crypto.test("scope.approval_binding", scope_digest == self.trust.get("scope_digest"),
                                  "Exact approved revision pinned by evaluator outside package; amendments are not auto-accepted",
                                  ["experimental.scope", "trust.scope_digest"])
        scope_ok = scope_ok and pinned and self.policy_ok
        cutoff = natural(scope["commitment_cutoff"], 2**53 - 1)
        start = natural(scope["start"], 2**53 - 1)
        end = natural(scope["end"], 2**53 - 1)
        deadline = natural(scope["submission_deadline"], 2**53 - 1)
        if not cutoff < start <= end <= deadline:
            raise InputError("Unsupported or inconsistent scope interval/deadlines")
        if scope["revision"] != "1" or scope.get("previous_revision") is not None:
            unknown("amendment_unsupported", "Amendments require separate original and revised assessments", ["experimental.scope"])
        if scope["closure_rule"] != "signed-source-enumeration-v1":
            unknown("closure_rule_unsupported", "Unimplemented source closure rule", ["experimental.scope"])
        if scope["inventory_mode"] not in ("fixed", "derived") or scope["derivation_rule"] != "explicit-obligations-v1":
            unknown("derivation_unsupported", "Unimplemented expected-set derivation", ["experimental.scope"])
            return finish()
        receipt = x.get("scope_receipt")
        timing_ok = self.receipt(receipt, scope_digest, "scope", "experimental.scope_receipt")
        if timing_ok and scope_ok:
            body = receipt["body"]
            if body["accepted_at"] + body["uncertainty"] <= cutoff:
                scope_checks.add("advance_commitment", "verified", "Latest simulated receipt bound is no later than cutoff",
                                 ["experimental.scope_receipt"])
            else:
                register = x.get("timing_register")
                register_ok = self.signed(register, "register", "experimental.timing_register") if register else False
                if register_ok:
                    r = register["body"]
                    if type(r["closed"]) is not bool:
                        raise InputError("Register closure must be a boolean")
                    natural(r["closed_at"], 2**53 - 1)
                    natural(r["first_accepted_at"], 2**53 - 1)
                    register_ok = self.crypto.test("register.binding", r["scope_digest"] == scope_digest and
                                                   r["receipt_digest"] == digest(receipt) and
                                                   r["register_id"] == self.policy["timing_register_id"],
                                                   "Closed-register receipt and scope binding", ["experimental.timing_register"])
                    if (register_ok and r["closed"] is True and r["closed_at"] >= r["first_accepted_at"] and
                            r["closed_at"] <= self.at and r["first_accepted_at"] == body["accepted_at"] and
                            r["first_accepted_at"] - body["uncertainty"] > cutoff):
                        violation("late_first_acceptance", "Simulated closed trusted register proves first qualifying acceptance missed deadline",
                                  ["experimental.scope", "experimental.scope_receipt", "experimental.timing_register", "trust"])
                    else:
                        unknown("timing_unresolved", "Register does not establish a definite timing violation", ["experimental.timing_register"])
                else:
                    unknown("late_receipt_only", "Late receipt does not establish whether an earlier qualifying receipt exists",
                            ["experimental.scope_receipt"])
        else:
            unknown("advance_commitment_unknown", "Advance timing or authority is unresolved", ["experimental.scope", "experimental.scope_receipt"])
        if not scope_ok:
            unknown("scope_authority", "Approved evaluation scope has not been established", ["experimental.scope", "trust"])
            return finish()

        def sidecar(name, kind):
            env = x.get(name)
            if env is None:
                return False
            valid = self.signed(env, kind, "experimental." + name)
            valid = self.crypto.test(name + ".scope_binding", env["body"]["scope_digest"] == scope_digest,
                                     "Sidecar belongs to the exact scope revision", ["experimental." + name]) and valid
            return valid

        inventory_ok = sidecar("inventory", "inventory")
        closure_ok = sidecar("closure", "closure")
        manifest_ok = sidecar("manifest", "manifest")
        inventory = x["inventory"]["body"] if x.get("inventory") else None
        closure = x["closure"]["body"] if x.get("closure") else None
        manifest = x["manifest"]["body"] if x.get("manifest") else None
        if manifest_ok:
            if type(manifest["final"]) is not bool:
                raise InputError("Manifest finality must be a boolean")
            natural(manifest["finalized_at"], 2**53 - 1)
            manifest_ok = self.crypto.test("manifest.package_binding", manifest["anchor_digest"] == digest(self.p["anchor"]) and
                                           manifest["delivery_digest"] == digest({"events": self.p["events"],
                                                                                 "commitment_proofs": self.p.get("commitment_proofs", [])}),
                                           "Manifest binds exact delivery bytes and original anchor", ["experimental.manifest", "events", "anchor"])
        if closure_ok:
            if type(closure["closed"]) is not bool:
                raise InputError("Source closure must be a boolean")
            natural(closure["closed_at"], 2**53 - 1)
            closure_ok = self.crypto.test("closure.configuration", closure["configuration_digest"] == scope["configuration_digest"] and
                                          closure["source_id"] == scope["expectation_source"] and
                                          closure["end"] == end and closure["closed_at"] >= end,
                                          "Closure source, boundary end and configuration binding", ["experimental.closure", "experimental.scope"])
        expected = None
        if inventory_ok:
            expected = inventory["obligations"]
            if not isinstance(expected, list) or len(expected) > MAX_ITEMS:
                raise InputError("Invalid obligation collection")
            ids = [item["id"] for item in expected]
            if len(ids) != len(set(ids)):
                raise InputError("Duplicate expected obligation IDs")
            if scope["inventory_mode"] == "fixed":
                inventory_ok = self.crypto.test("inventory.fixed_commitment", digest(expected) == scope["expected_digest"],
                                               "Fixed expected enumeration bound before cutoff", ["experimental.scope", "experimental.inventory"])
            elif closure_ok and x.get("source_records") is not None:
                derived = [record["obligation"] for record in x["source_records"]]
                inventory_ok = self.crypto.test("inventory.derived_commitment",
                                               closure["source_records_digest"] == digest(x["source_records"]) and
                                               derived == expected and closure["expected_digest"] == digest(expected),
                                               "Reproduce expected set from closure-bound source records under explicit-obligations-v1",
                                               ["experimental.source_records", "experimental.closure", "experimental.inventory"])
            else:
                inventory_ok = False
        if inventory_ok and closure_ok:
            closure_ok = self.crypto.test("closure.inventory_binding", closure["expected_digest"] == digest(expected),
                                          "Closure binds the exact expected enumeration", ["experimental.closure", "experimental.inventory"])
        if not inventory_ok:
            unknown("expected_set_unknown", "Expected inventory cannot be authenticated or reproduced", ["experimental.inventory", "experimental.closure"])
            expected = None
        if not closure_ok or not closure["closed"] or closure["closed_at"] > self.at:
            unknown("source_unclosed", "Expected-set source closure is absent or not yet established", ["experimental.closure"])
        elif closure["observation_gaps"]:
            unknown("observation_gap", "Authenticated source reports unresolved observation gaps; signature does not cure them", ["experimental.closure"])
        if not manifest_ok:
            unknown("manifest_unknown", "Exact final delivery manifest is unavailable or invalid", ["experimental.manifest"])
        # A pinned scope can define individual obligations even when E cannot be reconstructed.
        obligations = expected if expected is not None else scope.get("individually_required", [])
        satisfied = 0
        accounted = expected is not None and manifest_ok
        dispositions = {}
        entries = manifest["entries"] if manifest_ok else []
        if len({entry["id"] for entry in entries}) != len(entries):
            raise InputError("Duplicate manifest obligation IDs")
        entries = {entry["id"]: entry for entry in entries}
        final = manifest_ok and manifest["final"] is True and deadline <= manifest["finalized_at"] <= self.at
        if not final:
            unknown("delivery_pending", "Delivery is not authenticated and finalized after its deadline", ["experimental.manifest"])
        for obligation in obligations:
            oid = obligation["id"]
            entry = entries.get(oid)
            state = entry["state"] if entry else "unaccounted"
            if state not in ("included", "withheld", "unavailable", "unaccounted"):
                raise InputError("Unknown presentation state")
            dispositions[state] = dispositions.get(state, 0) + 1
            accounted = accounted and entry is not None
            refs = ["experimental.scope", "experimental.inventory", "experimental.manifest", "trust"]
            full = obligation["disclosure"] == "full"
            if obligation["event_type"] == "notification_receipt":
                n = obligation["notification"]
                natural(n["deadline"], 2**53 - 1)
                if n["stage"] not in ("attempted", "transport_accepted", "delivered_endpoint", "human_acknowledged"):
                    unknown("notification_stage_unsupported", "Unimplemented notification acknowledgement stage", refs)
                    continue
                if n["deadline"] > self.at:
                    unknown("notification_pending", oid + ": notification evidence deadline has not elapsed", refs)
                    continue
            if obligation["disclosure"] not in ("full", "commitment"):
                unknown("disclosure_unsupported", "Unimplemented disclosure policy", refs)
                continue
            if state != "included" and self.records.get(oid):
                unknown("manifest_disposition_conflict", oid + ": manifest disposition conflicts with supplied material; do not infer absence", refs + ["events"])
                continue
            if state in ("withheld", "unavailable") and full and final:
                violation("required_evidence_" + state, f"{oid}: required full evidence explicitly {state}; underlying action remains unknown", refs)
                continue
            if state == "withheld" and not full:
                proofs = self.proofs.get(oid, [])
                proof_ok = len(proofs) == 1 and proofs[0]["valid"]
                if proof_ok:
                    if proofs[0]["source_id"] == obligation["source_id"] and proofs[0]["event_type"] == obligation["event_type"]:
                        satisfied += 1
                    else:
                        violation("commitment_type_mismatch", oid + ": anchored commitment contradicts required source/type", refs + ["commitment_proofs", "anchor"])
                else:
                    unknown("commitment_unverified", oid + ": required commitment proof is missing or invalid", refs + ["commitment_proofs"])
                continue
            if state == "included":
                records = self.records.get(oid, [])
                if len(records) == 1 and all(self.record_valid[oid]):
                    record = records[0]
                    if record["source_id"] != obligation["source_id"] or record["event_type"] != obligation["event_type"]:
                        violation("record_type_mismatch", oid + ": valid record contradicts required source/type", refs + ["events"])
                    elif obligation["event_type"] == "notification_receipt" and not self.notification_matches(record, obligation):
                        violation("notification_receipt_mismatch", oid + ": valid receipt contradicts trigger, recipient, stage or deadline", refs + ["events"])
                    else:
                        satisfied += 1
                elif len(records) > 1 and all(self.record_valid[oid]) and final:
                    violation("duplicate_delivery", oid + ": multiplicity rule requires exactly one record", refs + ["events"])
                elif not records and final:
                    source_closed = closure_ok and closure["closed"] is True and closure["closed_at"] <= self.at and obligation["source_id"] in closure["closed_sources"]
                    if obligation["event_type"] == "notification_receipt" and not source_closed:
                        unknown("notification_evidence_unclosed", oid + ": inclusion claim lacks receipt and source closure", refs + ["experimental.closure"])
                    else:
                        violation("missing_delivery", oid + ": claimed inclusion contradicted by exact finalized delivery", refs + ["events"])
                else:
                    unknown("included_record_unverified", oid + ": manifest inclusion claim cannot be established", refs + ["events"])
            elif state == "unaccounted" and final:
                source_closed = closure_ok and closure["closed"] is True and closure["closed_at"] <= self.at and obligation["source_id"] in closure["closed_sources"]
                if obligation["event_type"] == "notification_receipt" and not source_closed:
                    unknown("notification_evidence_unclosed", oid + ": missing receipt with unclosed source; occurrence unknown", refs + ["experimental.closure"])
                else:
                    violation("missing_delivery", oid + ": identified required evidence absent from finalized delivery", refs)
            else:
                unknown("delivery_unresolved", oid + ": required evidence not yet established", refs)
        for relation in scope["relationships"]:
            if relation["rule"] != "payload-value-equality-v1":
                unknown("relationship_unsupported", "Unimplemented relationship rule", ["experimental.scope"])
                continue
            left, right = relation["left"], relation["right"]
            if (len(self.records.get(left, [])) == len(self.records.get(right, [])) == 1 and
                    all(self.record_valid[left]) and all(self.record_valid[right])):
                equal = self.records[left][0]["payload"]["value"] == self.records[right][0]["payload"]["value"]
                if not equal:
                    violation("source_disagreement", "Authenticated producer and execution observations violate agreed equality; truth of either is unresolved",
                              ["experimental.scope", "events:" + left, "events:" + right, "anchor", "trust"])
            else:
                unknown("relationship_unverified", "Cannot establish both sides of required relationship", ["experimental.scope", "events"])
        if aggregate(self.crypto.items) != "verified":
            unknown("cryptographic_prerequisite", "Some required cryptographic checks failed or are unresolved; independent violations are retained",
                    [item["check"] for item in self.crypto.items if item["result"] != "verified"])
        return finish(len(expected) if expected is not None else None, satisfied, bool(accounted), dispositions)

    @staticmethod
    def notification_matches(record, obligation):
        required = obligation["notification"]
        observed = record["payload"]
        return (all(observed.get(key) == required[key] for key in ("trigger", "recipient", "stage")) and
                type(observed.get("at")) is int and 0 <= observed["at"] <= required["deadline"])


def verify(package, trust, mode, evaluation_time, allow_synthetic=False):
    if mode not in ("vap-v1.2", "experimental-scope"):
        raise InputError("An explicit supported mode is required")
    try:
        canonical(package)
        canonical(trust)
        evaluation = Evaluation(package, trust, evaluation_time, allow_synthetic)
        evaluation.core()
        scope = evaluation.experimental() if mode == "experimental-scope" else None
        return {
            "implementation_version": VERSION, "format": ADAPTER, "mode": mode,
            "specification": {"version": "VAP v1.2.0 Draft 3", "commit": BASELINE},
            "proposal_status": "experimental_unadopted" if scope is not None else "not_applied",
            "environment": "synthetic_simulation" if evaluation.simulate else "offline_non_simulated",
            "evaluation_id": trust["evaluation_id"], "evaluation_time": evaluation_time,
            "policy_digest": trust["policy_digest"], "input_digest": digest(package), "trust_digest": digest(trust),
            "integrity": {"result": aggregate(evaluation.crypto.items), "checks": evaluation.crypto.items,
                          "claim_boundary": "Supplied objects and named bindings only; absent payloads are not verified"},
            "v1_2_requirements": evaluation.requirements.items, "scope_fulfillment": scope,
            "overall_pass": None, "full_vap_conformance": "not_assessed",
            "limits": ["Research adapter, not a standardized VAP Evidence Pack format",
                       "Synthetic receipt keys do not establish independent time or institutional independence",
                       "No production RFC 3161, SCITT, blockchain or log trust-path adapter",
                       "No reconstruction of unobserved activity, prevention, certification or legal-compliance conclusion",
                       "INT-004 profile sequencing, INT-007 continuity and INT-009 recovery remain unimplemented"],
        }
    except (KeyError, TypeError, IndexError, ValueError, RecursionError) as exc:
        raise InputError("Invalid or unsupported evidence structure: " + str(exc)) from exc
