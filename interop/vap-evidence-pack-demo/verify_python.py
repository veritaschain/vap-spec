from __future__ import annotations
import argparse, base64, collections, hashlib, json, sys
from pathlib import Path
from typing import Any
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

class VerificationError(Exception): pass

def canonical(value: Any) -> bytes:
    def validate(v: Any) -> None:
        if isinstance(v, float): raise VerificationError("floats are forbidden")
        if isinstance(v, dict):
            for k, item in v.items():
                if not isinstance(k, str): raise VerificationError("non-string key")
                validate(item)
        elif isinstance(v, list):
            for item in v: validate(item)
        elif v is not None and not isinstance(v, (str, int, bool)): raise VerificationError("unsupported type")
    validate(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()

def sha256(data: bytes) -> bytes: return hashlib.sha256(data).digest()
def unsigned_event(e): return {k:v for k,v in e.items() if k not in {"payload_hash","signature"}}
def verify_sig(obj,key_id,sig,keys):
    try:
        key=Ed25519PublicKey.from_public_bytes(base64.b64decode(keys[key_id],validate=True))
        key.verify(base64.b64decode(sig,validate=True),canonical(obj))
    except (KeyError,ValueError,InvalidSignature) as exc: raise VerificationError(f"invalid signature for {key_id}") from exc

def merkle_root(events):
    nodes=[sha256(b"\x00"+canonical(e)) for e in events]
    if not nodes: return sha256(b"").hex()
    while len(nodes)>1: nodes=[sha256(b"\x01"+nodes[i]+(nodes[i+1] if i+1<len(nodes) else nodes[i])) for i in range(0,len(nodes),2)]
    return nodes[0].hex()

def verify_pack(pack):
    checks=[]
    if pack.get("evidence_pack_version")!="0.1.0-demo" or pack.get("profile")!="VAP-COMMON": raise VerificationError("unsupported Evidence Pack profile")
    keys,events=pack["public_keys"],pack["events"]
    ids=set(); seq=[]
    for e in events:
        if e["event_id"] in ids: raise VerificationError("duplicate event_id")
        ids.add(e["event_id"]); seq.append(e["sequence_no"])
        u=unsigned_event(e)
        if sha256(canonical(u)).hex()!=e["payload_hash"]: raise VerificationError(f"payload hash mismatch: {e['event_id']}")
        verify_sig({**u,"payload_hash":e["payload_hash"]},e["key_id"],e["signature"],keys)
    checks.append("event-authenticity")
    if seq!=list(range(1,len(events)+1)): raise VerificationError("sequence_no is not contiguous from 1")
    checks.append("sequence-continuity")
    root=merkle_root(events)
    if root!=pack["merkle"]["root"]: raise VerificationError("Merkle root mismatch")
    checks.append("collection-integrity")
    scope_hash=sha256(canonical(pack["scope"])).hex()
    if scope_hash!=pack["scope_commitment"]: raise VerificationError("scope commitment mismatch")
    checks.append("scope-commitment")
    for field in ("producer_manifest","observer_receipt","external_anchor_receipt"):
        r=pack[field]; body={k:v for k,v in r.items() if k!="signature"}; verify_sig(body,r["key_id"],r["signature"],keys)
        if r["merkle_root"]!=root: raise VerificationError(f"{field} root disagreement")
        if r["scope_commitment"]!=scope_hash: raise VerificationError(f"{field} scope disagreement")
        if r["event_count"]!=len(events): raise VerificationError(f"{field} event count disagreement")
    checks.append("cross-party-agreement")
    attempts=collections.Counter(e["provenance"]["attempt_id"] for e in events if e["event_type"]=="AI_DECISION_ATTEMPT")
    outcomes=collections.Counter(e["provenance"]["attempt_id"] for e in events if e["event_type"]=="AI_DECISION_OUTCOME")
    if any(v!=1 for v in [*attempts.values(),*outcomes.values()]): raise VerificationError("attempt or outcome cardinality is not exactly one")
    if set(attempts)!=set(outcomes): raise VerificationError(f"completeness invariant failed; missing_outcomes={sorted(set(attempts)-set(outcomes))}")
    if len(attempts)!=pack["scope"]["expected_attempt_count"]: raise VerificationError("expected attempt count mismatch")
    checks.append("completeness-invariant")
    return checks

def main():
    p=argparse.ArgumentParser(); p.add_argument("evidence_pack",type=Path); a=p.parse_args()
    try: checks=verify_pack(json.loads(a.evidence_pack.read_text()))
    except (OSError,json.JSONDecodeError,KeyError,TypeError,VerificationError) as exc: print(f"FAIL: {exc}"); return 1
    print("PASS: "+", ".join(checks)); return 0
if __name__=="__main__": sys.exit(main())
