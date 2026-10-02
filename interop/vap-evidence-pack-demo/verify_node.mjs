import fs from 'node:fs';
import crypto from 'node:crypto';
class VerificationError extends Error {}
function canonical(value){
  function validate(v){if(typeof v==='number'&&!Number.isInteger(v))throw new VerificationError('floats are forbidden');if(Array.isArray(v))return v.forEach(validate);if(v!==null&&typeof v==='object')return Object.values(v).forEach(validate);if(!['string','number','boolean'].includes(typeof v)&&v!==null)throw new VerificationError('unsupported type');}
  validate(value);
  function stable(v){if(Array.isArray(v))return `[${v.map(stable).join(',')}]`;if(v!==null&&typeof v==='object')return `{${Object.keys(v).sort().map(k=>`${JSON.stringify(k)}:${stable(v[k])}`).join(',')}}`;return JSON.stringify(v);}
  return Buffer.from(stable(value));
}
const sha256=d=>crypto.createHash('sha256').update(d).digest();
const hexSha=d=>sha256(d).toString('hex');
function rawKey(raw){return crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),raw]),format:'der',type:'spki'});}
function verifySig(obj,keyId,sig,keys){try{if(!crypto.verify(null,canonical(obj),rawKey(Buffer.from(keys[keyId],'base64')),Buffer.from(sig,'base64')))throw new VerificationError(`invalid signature for ${keyId}`);}catch(e){if(e instanceof VerificationError)throw e;throw new VerificationError(`invalid signature for ${keyId}`);}}
function unsignedEvent(e){return Object.fromEntries(Object.entries(e).filter(([k])=>!['payload_hash','signature'].includes(k)));}
function merkleRoot(events){let nodes=events.map(e=>sha256(Buffer.concat([Buffer.from([0]),canonical(e)])));if(!nodes.length)return sha256(Buffer.alloc(0)).toString('hex');while(nodes.length>1){const next=[];for(let i=0;i<nodes.length;i+=2){const r=i+1<nodes.length?nodes[i+1]:nodes[i];next.push(sha256(Buffer.concat([Buffer.from([1]),nodes[i],r])));}nodes=next;}return nodes[0].toString('hex');}
function verifyPack(pack){
  const checks=[];if(pack.evidence_pack_version!=='0.1.0-demo'||pack.profile!=='VAP-COMMON')throw new VerificationError('unsupported Evidence Pack profile');
  const ids=new Set(),seq=[];
  for(const e of pack.events){if(ids.has(e.event_id))throw new VerificationError('duplicate event_id');ids.add(e.event_id);seq.push(e.sequence_no);const u=unsignedEvent(e);if(hexSha(canonical(u))!==e.payload_hash)throw new VerificationError(`payload hash mismatch: ${e.event_id}`);verifySig({...u,payload_hash:e.payload_hash},e.key_id,e.signature,pack.public_keys);}
  checks.push('event-authenticity');if(seq.some((v,i)=>v!==i+1))throw new VerificationError('sequence_no is not contiguous from 1');checks.push('sequence-continuity');
  const root=merkleRoot(pack.events);if(root!==pack.merkle.root)throw new VerificationError('Merkle root mismatch');checks.push('collection-integrity');
  const scopeHash=hexSha(canonical(pack.scope));if(scopeHash!==pack.scope_commitment)throw new VerificationError('scope commitment mismatch');checks.push('scope-commitment');
  for(const field of ['producer_manifest','observer_receipt','external_anchor_receipt']){const r=pack[field];const body=Object.fromEntries(Object.entries(r).filter(([k])=>k!=='signature'));verifySig(body,r.key_id,r.signature,pack.public_keys);if(r.merkle_root!==root)throw new VerificationError(`${field} root disagreement`);if(r.scope_commitment!==scopeHash)throw new VerificationError(`${field} scope disagreement`);if(r.event_count!==pack.events.length)throw new VerificationError(`${field} event count disagreement`);}
  checks.push('cross-party-agreement');
  const counts=t=>{const m=new Map();for(const e of pack.events.filter(e=>e.event_type===t)){const id=e.provenance.attempt_id;m.set(id,(m.get(id)||0)+1);}return m;};
  const a=counts('AI_DECISION_ATTEMPT'),o=counts('AI_DECISION_OUTCOME');if([...a.values(),...o.values()].some(v=>v!==1))throw new VerificationError('attempt or outcome cardinality is not exactly one');
  const ak=[...a.keys()].sort(),ok=[...o.keys()].sort();if(JSON.stringify(ak)!==JSON.stringify(ok))throw new VerificationError(`completeness invariant failed; attempts=${JSON.stringify(ak)}, outcomes=${JSON.stringify(ok)}`);if(a.size!==pack.scope.expected_attempt_count)throw new VerificationError('expected attempt count mismatch');checks.push('completeness-invariant');return checks;
}
try{const path=process.argv[2];if(!path)throw new VerificationError('usage: node verify_node.mjs <evidence-pack.json>');const pack=JSON.parse(fs.readFileSync(path,'utf8'));console.log(`PASS: ${verifyPack(pack).join(', ')}`);}catch(e){console.log(`FAIL: ${e.message}`);process.exit(1);}
