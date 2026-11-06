"""Synthetic signing authorities around the unchanged native runtime test harness."""
from __future__ import annotations

import copy
import importlib.util
import os
from pathlib import Path
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parents[1]
WORKER = Path(__file__).with_name("authorization_worker.py")
sys.path.insert(0, str(ROOT))
import authorization_gate as authorization


def _load_runtime_support():
    path = ROOT.parent / "payment-runtime-pilot" / "tests" / "runtime_support.py"
    spec = importlib.util.spec_from_file_location("_authorization_test_native_support", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


native_support = _load_runtime_support()
runtime = native_support.runtime
Process = native_support.Process


class Harness(native_support.Harness):
    def __init__(self, **options):
        super().__init__(**options)
        self.at = authorization.now_ms()
        self.signing_keys = {name: Ed25519PrivateKey.generate() for name in authorization.SLOTS}
        self.key_ids = {name: "synthetic-" + name for name in authorization.SLOTS}
        self.trust = {"approver": {}, "status_authority": {}}
        for name in authorization.SLOTS:
            self.trust[authorization.ROLES[name]][self.key_ids[name]] = self.signing_keys[name].public_key().public_bytes_raw()
        self.identities = {
            self.signing_keys[name].public_key().public_bytes_raw().hex(): {
                "person_id": "synthetic-person-" + role, "roles": [role],
                **{field: self.context[field] for field in runtime.SCOPE_FIELDS},
                "valid_from_ms": self.at - 120000, "valid_until_ms": self.at + 300000,
            }
            for name, role in (("maker_approval", "maker"), ("checker_approval", "checker"))
        }
        self.policy = {
            "schema": authorization.POLICY_SCHEMA, "policy_id": "synthetic-payment-policy",
            "version": "1", "context": copy.deepcopy(self.context),
            "principal_id": "synthetic-requester", "credential_id": "synthetic-application-credential",
            "configuration_digest": self.configuration_digest, "recovery_epoch": self.recovery_epoch,
            "allowed_sources": ["source-A"], "allowed_beneficiaries": ["beneficiary-A"],
            "max_amount_minor": "5000", "valid_from_ms": self.at - 120000,
            "valid_until_ms": self.at + 300000,
        }
        self.evidence = self.make_evidence(self.request)

    def make_evidence(self, request, *, suffix="A", at=None, policy=None):
        at = self.at if at is None else at
        policy = self.policy if policy is None else policy
        request_digest = runtime.bytes_digest(runtime.request_bytes(request))
        policy_digest = authorization.policy_digest(policy)
        evidence = {}
        for name in authorization.APPROVALS:
            body = {
                "schema": authorization.APPROVAL_SCHEMA, "kind": name,
                "approval_id": "synthetic-" + name + "-" + suffix,
                "request_digest": request_digest, "policy_digest": policy_digest,
                "issued_at_ms": at - 1000, "expires_at_ms": at + 60000,
            }
            evidence[name] = authorization.sign_evidence(body, self.key_ids[name], self.signing_keys[name])
        status = {
            "schema": authorization.STATUS_SCHEMA, "kind": "final_status", "status_id": "synthetic-status-" + suffix,
            "request_digest": request_digest, "policy_digest": policy_digest,
            "approval_digests": {name: authorization.bytes_digest(evidence[name]) for name in authorization.APPROVALS},
            "principal_id": policy["principal_id"], "credential_id": policy["credential_id"],
            "configuration_digest": policy["configuration_digest"], "recovery_epoch": policy["recovery_epoch"],
            "observed_at_ms": at - 10, "valid_until_ms": at + 20000,
            "state": "active", "revoked_at_ms": None,
        }
        evidence["final_status"] = authorization.sign_evidence(
            status, self.key_ids["final_status"], self.signing_keys["final_status"])
        return evidence

    def resign(self, evidence, name, **updates):
        payload = authorization.load_json(evidence[name])["payload"]
        payload.update(updates)
        evidence[name] = authorization.sign_evidence(payload, self.key_ids[name], self.signing_keys[name])

    def refresh_status(self, evidence):
        self.resign(evidence, "final_status", approval_digests={
            name: authorization.bytes_digest(evidence[name]) for name in authorization.APPROVALS})

    def gate_config(self, *, policy=None, trust=None, identities=None, max_status_age_ms=30000):
        return authorization.GateConfig(
            copy.deepcopy(self.policy if policy is None else policy),
            copy.deepcopy(self.trust if trust is None else trust),
            copy.deepcopy(self.identities if identities is None else identities),
            max_status_age_ms=max_status_age_ms)

    def gate(self, *, native=None, fault_hook=None, **config_options):
        return authorization.AuthorizedAdapter(
            self.adapter() if native is None else native,
            self.gate_config(**config_options), fault_hook=fault_hook)

    def authorized_worker(self, *, request=None, evidence=None, action="submit", barrier=None):
        config = {
            "runtime": self.adapter_config(),
            "gate": {"policy": self.policy, "trusted_keys": {
                role: {name: public.hex() for name, public in keys.items()}
                for role, keys in self.trust.items()}, "identities": self.identities,
                "max_status_age_ms": 30000},
        }
        config_file = self.next_file("authorization-config", config)
        request_file = self.next_file("authorized-request", self.request if request is None else request)
        evidence_file = self.next_file("signed-evidence", {
            name: raw.hex() for name, raw in (self.evidence if evidence is None else evidence).items()})
        command = [*native_support.PYTHON, str(WORKER), "--config", str(config_file),
                   "--request", str(request_file), "--evidence", str(evidence_file), "--action", action]
        if barrier:
            command.extend(("--barrier", barrier))
        process = Process(command, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.processes.append(process)
        return process
