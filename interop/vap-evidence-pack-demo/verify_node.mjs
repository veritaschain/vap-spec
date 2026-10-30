import fs from 'node:fs';
import crypto from 'node:crypto';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { TextDecoder } from 'node:util';

// This file implements only the local experimental contract, not VAP conformance.
const CONTRACT_ID = 'vap-interop-demo/0.2.0';
const CANONICALIZATION = 'DEMO-ASCII-SAFEINT-JSON-v1';
const MAX_BYTES = 2 * 1024 * 1024;
const MAX_DEPTH = 16;
const MAX_STRING_LENGTH = 1024;
const EVENT_TYPES = ['AI_DECISION_ATTEMPT', 'AI_DECISION_OUTCOME'];
const ROLE_RECORDS = [
  ['producer_manifest', 'producer', 'PRODUCER_MANIFEST'],
  ['observer_receipt', 'observer', 'OBSERVER_RECEIPT'],
  ['demo_anchor_receipt', 'anchor', 'DEMO_ANCHOR_RECEIPT'],
];
const SPKI_ED25519_PREFIX = Buffer.from('302a300506032b6570032100', 'hex');

export class VerificationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'VerificationError';
  }
}

class UsageError extends Error {}

function reject(message) {
  throw new VerificationError(message);
}

function printable(value, label, nonempty = false) {
  if (typeof value !== 'string' ||
      value.length > MAX_STRING_LENGTH ||
      (nonempty && value.length === 0) ||
      Array.from(value).some((character) => {
        const code = character.charCodeAt(0);
        return code < 0x20 || code > 0x7e;
      })) {
    reject(label + ' must be ' + (nonempty ? 'nonempty ' : '') +
      'printable ASCII of at most 1024 characters');
  }
}

function isPlainObject(value) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

/**
 * Encode the constrained JSON value domain independently of native object order.
 * Integer token spelling is additionally enforced by strictParse on file input.
 */
export function canonical(value) {
  function encode(current, depth) {
    if (depth > MAX_DEPTH) reject('JSON nesting exceeds 16');
    if (current === null) return 'null';
    if (typeof current === 'string') {
      printable(current, 'JSON string');
      return JSON.stringify(current);
    }
    if (typeof current === 'boolean') return current ? 'true' : 'false';
    if (typeof current === 'number') {
      if (!Number.isSafeInteger(current) || Object.is(current, -0)) {
        reject('JSON numbers must be safe integers, excluding negative zero');
      }
      return String(current);
    }
    if (Array.isArray(current)) {
      if (Reflect.ownKeys(current).length !== current.length + 1) {
        reject('JSON arrays cannot have missing or additional properties');
      }
      const values = [];
      for (let index = 0; index < current.length; index += 1) {
        const descriptor = Object.getOwnPropertyDescriptor(current, String(index));
        if (!descriptor || !descriptor.enumerable || !Object.hasOwn(descriptor, 'value')) {
          reject('JSON arrays must contain ordinary values at every index');
        }
        values.push(encode(descriptor.value, depth + 1));
      }
      return '[' + values.join(',') + ']';
    }
    if (isPlainObject(current)) {
      const keys = Reflect.ownKeys(current);
      if (keys.some((key) => typeof key !== 'string')) reject('JSON object keys must be strings');
      keys.sort();
      const members = [];
      for (const key of keys) {
        printable(key, 'JSON object key');
        const descriptor = Object.getOwnPropertyDescriptor(current, key);
        if (!descriptor.enumerable || !Object.hasOwn(descriptor, 'value')) {
          reject('JSON objects must contain ordinary enumerable values');
        }
        members.push(JSON.stringify(key) + ':' + encode(descriptor.value, depth + 1));
      }
      return '{' + members.join(',') + '}';
    }
    reject('unsupported JSON value type');
  }
  return Buffer.from(encode(value, 0), 'utf8');
}

/**
 * Parse JSON while retaining enough lexical information to reject duplicate keys,
 * fractional/exponent forms, unsafe integers and negative zero before coercion.
 */
export function strictParse(text) {
  if (typeof text !== 'string') reject('JSON input must be text');
  if (Buffer.byteLength(text, 'utf8') > MAX_BYTES) reject('JSON input exceeds 2 MiB');
  if (text.charCodeAt(0) === 0xfeff) reject('UTF-8 BOM is not permitted');
  let offset = 0;

  function syntax(message) {
    reject(message + ' at character ' + offset);
  }

  function whitespace() {
    while (offset < text.length &&
           (text[offset] === ' ' || text[offset] === '\n' ||
            text[offset] === '\r' || text[offset] === '\t')) {
      offset += 1;
    }
  }

  function stringValue() {
    if (text[offset] !== '"') syntax('expected JSON string');
    const beginning = offset;
    offset += 1;
    while (offset < text.length) {
      const character = text[offset];
      offset += 1;
      if (character === '"') {
        let result;
        try {
          // The enclosing parser handles object membership and duplicates.
          // Native JSON parsing is used only for one isolated string token.
          result = JSON.parse(text.slice(beginning, offset));
        } catch {
          syntax('invalid JSON string escape or control character');
        }
        printable(result, 'JSON string');
        return result;
      }
      if (character === '\\') offset += 1;
    }
    syntax('unterminated JSON string');
  }

  function numberValue() {
    const beginning = offset;
    if (text[offset] === '-') offset += 1;
    if (text[offset] === '0') {
      offset += 1;
      if (/[0-9]/.test(text[offset] || '')) syntax('leading zero is not permitted');
    } else {
      if (!/[1-9]/.test(text[offset] || '')) syntax('expected integer digits');
      while (/[0-9]/.test(text[offset] || '')) offset += 1;
    }
    if (text[offset] === '.' || text[offset] === 'e' || text[offset] === 'E') {
      syntax('fractional and exponent number tokens are not permitted');
    }
    const token = text.slice(beginning, offset);
    if (token === '-0') syntax('negative zero is not permitted');
    const result = Number(token);
    if (!Number.isSafeInteger(result)) syntax('integer is outside the safe range');
    return result;
  }

  function value(depth) {
    whitespace();
    if (depth > MAX_DEPTH) syntax('JSON nesting exceeds 16');
    const character = text[offset];
    if (character === '"') return stringValue();
    if (character === '{') {
      offset += 1;
      whitespace();
      const object = Object.create(null);
      const seen = new Set();
      if (text[offset] === '}') {
        offset += 1;
        return object;
      }
      while (true) {
        whitespace();
        const key = stringValue();
        if (seen.has(key)) syntax('duplicate JSON object key');
        seen.add(key);
        whitespace();
        if (text[offset] !== ':') syntax('expected colon');
        offset += 1;
        object[key] = value(depth + 1);
        whitespace();
        if (text[offset] === '}') {
          offset += 1;
          return object;
        }
        if (text[offset] !== ',') syntax('expected comma or closing brace');
        offset += 1;
      }
    }
    if (character === '[') {
      offset += 1;
      whitespace();
      const array = [];
      if (text[offset] === ']') {
        offset += 1;
        return array;
      }
      while (true) {
        array.push(value(depth + 1));
        whitespace();
        if (text[offset] === ']') {
          offset += 1;
          return array;
        }
        if (text[offset] !== ',') syntax('expected comma or closing bracket');
        offset += 1;
      }
    }
    for (const [token, result] of [['true', true], ['false', false], ['null', null]]) {
      if (text.startsWith(token, offset)) {
        offset += token.length;
        return result;
      }
    }
    if (character === '-' || /[0-9]/.test(character || '')) return numberValue();
    syntax('expected JSON value');
  }

  const result = value(0);
  whitespace();
  if (offset !== text.length) syntax('unexpected trailing input');
  return result;
}

function exactObject(value, fields, label) {
  if (!isPlainObject(value)) reject(label + ' must be an object');
  const actual = Object.keys(value);
  if (actual.length !== fields.length || actual.some((key) => !fields.includes(key))) {
    reject(label + ' has missing or unsupported fields');
  }
}

function integer(value, minimum, maximum, label) {
  if (typeof value !== 'number' || !Number.isSafeInteger(value) ||
      Object.is(value, -0) || value < minimum || value > maximum) {
    reject(label + ' must be an integer from ' + minimum + ' to ' + maximum);
  }
}

function equal(value, expected, label) {
  if (value !== expected) reject(label + ' is unsupported or does not match');
}

function digest(value, label) {
  if (typeof value !== 'string' || value.length !== 64 || /[^a-f0-9]/.test(value)) {
    reject(label + ' must be a lowercase SHA-256 digest');
  }
}

function base64Bytes(value, length, label) {
  if (typeof value !== 'string' || value.length === 0) {
    reject(label + ' must be canonical padded base64');
  }
  const bytes = Buffer.from(value, 'base64');
  if (bytes.length !== length || bytes.toString('base64') !== value) {
    reject(label + ' must be canonical padded base64 for ' + length + ' bytes');
  }
  return bytes;
}

function timestamp(value, label) {
  if (typeof value !== 'string' || value.length !== 20) {
    reject(label + ' must be a UTC timestamp of exactly 20 characters');
  }
  const match = /^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})Z$/.exec(value);
  if (!match) reject(label + ' must have YYYY-MM-DDTHH:MM:SSZ form');
  const [, yearText, monthText, dayText, hourText, minuteText, secondText] = match;
  const [year, month, day, hour, minute, second] =
    [yearText, monthText, dayText, hourText, minuteText, secondText].map(Number);
  const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (year < 1 || month < 1 || month > 12 || day < 1 || day > days[month - 1] ||
      hour > 23 || minute > 59 || second > 59) {
    reject(label + ' is not a real UTC calendar value');
  }
}

function validateScope(scope) {
  exactObject(scope, [
    'chain_id', 'batch_id', 'policy_id', 'window_start', 'window_end',
    'in_scope_event_types', 'expected_attempt_count', 'completeness_rule',
  ], 'scope');
  for (const key of ['chain_id', 'batch_id', 'policy_id']) printable(scope[key], 'scope.' + key, true);
  timestamp(scope.window_start, 'scope.window_start');
  timestamp(scope.window_end, 'scope.window_end');
  if (scope.window_start > scope.window_end) reject('scope window is reversed');
  if (!Array.isArray(scope.in_scope_event_types) ||
      scope.in_scope_event_types.length !== EVENT_TYPES.length ||
      scope.in_scope_event_types.some((item, index) => item !== EVENT_TYPES[index])) {
    reject('scope.in_scope_event_types is unsupported');
  }
  integer(scope.expected_attempt_count, 1, 64, 'scope.expected_attempt_count');
  equal(scope.completeness_rule, 'ATTEMPT_OUTCOME_BIJECTION', 'scope.completeness_rule');
}

function validateEvent(event, index) {
  const label = 'events[' + index + ']';
  exactObject(event, [
    'contract_id', 'chain_id', 'event_id', 'sequence_no', 'event_type',
    'timestamp', 'issuer_id', 'key_id', 'policy_id', 'model_id',
    'provenance', 'payload_hash', 'signature',
  ], label);
  equal(event.contract_id, CONTRACT_ID, label + '.contract_id');
  for (const key of ['chain_id', 'event_id', 'issuer_id', 'key_id', 'policy_id', 'model_id']) {
    printable(event[key], label + '.' + key, true);
  }
  integer(event.sequence_no, 1, 128, label + '.sequence_no');
  if (!EVENT_TYPES.includes(event.event_type)) reject(label + '.event_type is unsupported');
  timestamp(event.timestamp, label + '.timestamp');
  digest(event.payload_hash, label + '.payload_hash');
  base64Bytes(event.signature, 64, label + '.signature');
  const provenance = event.provenance;
  const common = ['attempt_id', 'actor', 'action'];
  if (event.event_type === 'AI_DECISION_ATTEMPT') {
    exactObject(provenance, [...common, 'input_hash', 'context'], label + '.provenance');
    digest(provenance.input_hash, label + '.provenance.input_hash');
    exactObject(provenance.context, ['jurisdiction'], label + '.provenance.context');
    printable(provenance.context.jurisdiction, label + '.provenance.context.jurisdiction', true);
  } else {
    exactObject(provenance, [...common, 'outcome', 'reason_code', 'human_review_required'], label + '.provenance');
    if (!['APPROVED', 'DENIED_AUTOMATION'].includes(provenance.outcome)) {
      reject(label + '.provenance.outcome is unsupported');
    }
    printable(provenance.reason_code, label + '.provenance.reason_code', true);
    if (typeof provenance.human_review_required !== 'boolean') {
      reject(label + '.provenance.human_review_required must be boolean');
    }
  }
  for (const key of common) printable(provenance[key], label + '.provenance.' + key, true);
}

function validatePack(pack) {
  exactObject(pack, [
    'contract_id', 'canonicalization', 'hash_algorithm', 'signature_algorithm',
    'scope', 'scope_commitment', 'events', 'merkle',
    'producer_manifest', 'observer_receipt', 'demo_anchor_receipt',
  ], 'pack');
  equal(pack.contract_id, CONTRACT_ID, 'contract_id');
  equal(pack.canonicalization, CANONICALIZATION, 'canonicalization');
  equal(pack.hash_algorithm, 'SHA-256', 'hash_algorithm');
  equal(pack.signature_algorithm, 'Ed25519', 'signature_algorithm');
  validateScope(pack.scope);
  digest(pack.scope_commitment, 'scope_commitment');
  if (!Array.isArray(pack.events) || pack.events.length < 2 || pack.events.length > 128) {
    reject('events must be an array with 2 through 128 entries');
  }
  pack.events.forEach(validateEvent);
  exactObject(pack.merkle, ['algorithm', 'root'], 'merkle');
  equal(pack.merkle.algorithm, 'RFC6962-SHA256', 'merkle.algorithm');
  digest(pack.merkle.root, 'merkle.root');
  for (const [field, , recordType] of ROLE_RECORDS) {
    const record = pack[field];
    exactObject(record, [
      'record_type', 'key_id', 'merkle_root', 'scope_commitment',
      'event_count', 'issued_at', 'signature',
    ], field);
    equal(record.record_type, recordType, field + '.record_type');
    printable(record.key_id, field + '.key_id', true);
    digest(record.merkle_root, field + '.merkle_root');
    digest(record.scope_commitment, field + '.scope_commitment');
    integer(record.event_count, 1, 128, field + '.event_count');
    timestamp(record.issued_at, field + '.issued_at');
    base64Bytes(record.signature, 64, field + '.signature');
  }
}

function validateTrust(trust) {
  exactObject(trust, ['contract_id', 'trust_version', 'scope_commitment', 'roles'], 'trust');
  equal(trust.contract_id, CONTRACT_ID, 'trust.contract_id');
  equal(trust.trust_version, 'demo-trust/1', 'trust.trust_version');
  digest(trust.scope_commitment, 'trust.scope_commitment');
  exactObject(trust.roles, ['producer', 'observer', 'anchor'], 'trust.roles');
  const keyIds = new Set();
  const keyValues = new Set();
  const publicKeys = Object.create(null);
  for (const role of ['producer', 'observer', 'anchor']) {
    const entry = trust.roles[role];
    exactObject(entry, ['key_id', 'public_key'], 'trust.roles.' + role);
    printable(entry.key_id, 'trust.roles.' + role + '.key_id', true);
    const raw = base64Bytes(entry.public_key, 32, 'trust.roles.' + role + '.public_key');
    const rawHex = raw.toString('hex');
    if (keyIds.has(entry.key_id) || keyValues.has(rawHex)) {
      reject('trust roles must use distinct key identifiers and public keys');
    }
    keyIds.add(entry.key_id);
    keyValues.add(rawHex);
    publicKeys[role] = raw;
  }
  return publicKeys;
}

function without(object, excluded) {
  return Object.fromEntries(Object.entries(object).filter(([key]) => !excluded.includes(key)));
}

function sha256(bytes) {
  return crypto.createHash('sha256').update(bytes).digest();
}

function verifySignature(body, signature, rawKey, label) {
  const signatureBytes = base64Bytes(signature, 64, label + ' signature');
  let matches = false;
  try {
    const publicKey = crypto.createPublicKey({
      key: Buffer.concat([SPKI_ED25519_PREFIX, rawKey]),
      format: 'der',
      type: 'spki',
    });
    matches = crypto.verify(null, canonical(body), publicKey, signatureBytes);
  } catch (error) {
    if (error instanceof VerificationError) throw error;
    reject(label + ' signature cannot be verified');
  }
  if (!matches) reject(label + ' signature does not match the supplied role key');
}

/** RFC 6962 section 2.1 MTH; leaf data is the complete canonical signed event. */
export function merkleRoot(events) {
  if (!Array.isArray(events)) reject('Merkle inputs must be an array');
  const leaves = events.map((event) => sha256(Buffer.concat([Buffer.from([0]), canonical(event)])));
  function subtree(first, end) {
    const count = end - first;
    if (count === 0) return sha256(Buffer.alloc(0));
    if (count === 1) return leaves[first];
    let split = 1;
    while (split * 2 < count) split *= 2;
    return sha256(Buffer.concat([
      Buffer.from([1]), subtree(first, first + split), subtree(first + split, end),
    ]));
  }
  return subtree(0, leaves.length).toString('hex');
}

export function verifyPack(pack, trust) {
  // Defensive value-domain checks also cover callers using the exported API.
  canonical(pack);
  canonical(trust);
  validatePack(pack);
  const publicKeys = validateTrust(trust);
  const checks = ['contract-and-shape'];

  const scopeCommitment = sha256(canonical(pack.scope)).toString('hex');
  equal(pack.scope_commitment, scopeCommitment, 'pack scope commitment');
  equal(trust.scope_commitment, scopeCommitment, 'externally supplied scope commitment');
  checks.push('pinned-scope');

  for (const event of pack.events) {
    equal(event.key_id, trust.roles.producer.key_id, 'event producer key identifier');
    const payloadHash = sha256(canonical(without(event, ['payload_hash', 'signature']))).toString('hex');
    equal(event.payload_hash, payloadHash, 'event payload hash');
    verifySignature(without(event, ['signature']), event.signature, publicKeys.producer, 'event');
  }
  checks.push('event-signatures');

  const eventIds = new Set();
  let previousTimestamp = '';
  for (let index = 0; index < pack.events.length; index += 1) {
    const event = pack.events[index];
    if (eventIds.has(event.event_id)) reject('duplicate event identifier');
    eventIds.add(event.event_id);
    equal(event.sequence_no, index + 1, 'event sequence number');
    equal(event.chain_id, pack.scope.chain_id, 'event chain identifier');
    equal(event.policy_id, pack.scope.policy_id, 'event policy identifier');
    if (event.timestamp < pack.scope.window_start || event.timestamp > pack.scope.window_end) {
      reject('event timestamp is outside the declared inclusive window');
    }
    if (event.timestamp < previousTimestamp) reject('event timestamps are not nondecreasing');
    previousTimestamp = event.timestamp;
  }
  checks.push('sequence-and-scope');

  const root = merkleRoot(pack.events);
  equal(pack.merkle.root, root, 'Merkle root');
  checks.push('rfc6962-root');

  for (const [field, role] of ROLE_RECORDS) {
    const record = pack[field];
    equal(record.key_id, trust.roles[role].key_id, field + ' role key identifier');
    verifySignature(without(record, ['signature']), record.signature, publicKeys[role], field);
    equal(record.merkle_root, root, field + ' Merkle root');
    equal(record.scope_commitment, scopeCommitment, field + ' scope commitment');
    equal(record.event_count, pack.events.length, field + ' event count');
    if (record.issued_at < pack.scope.window_end) reject(field + ' timestamp precedes the window end');
  }
  checks.push('role-receipts');

  const attempts = new Map();
  const outcomes = new Map();
  for (const event of pack.events) {
    const group = event.event_type === 'AI_DECISION_ATTEMPT' ? attempts : outcomes;
    const id = event.provenance.attempt_id;
    if (group.has(id)) reject('attempt/outcome identifier occurs more than once within its event type');
    group.set(id, event.sequence_no);
  }
  if (attempts.size !== outcomes.size || attempts.size !== pack.scope.expected_attempt_count) {
    reject('attempt/outcome cardinality does not match the pinned scope');
  }
  for (const [id, sequence] of attempts) {
    if (!outcomes.has(id)) reject('recorded attempt has no corresponding outcome');
    if (outcomes.get(id) <= sequence) reject('outcome does not follow its attempt');
  }
  checks.push('attempt-outcome-bijection');
  return checks;
}

function loadJsonFile(filename) {
  // Bound the read itself, including files whose size changes while being read.
  const descriptor = fs.openSync(filename, 'r');
  const buffer = Buffer.alloc(MAX_BYTES + 1);
  let used = 0;
  try {
    while (used < buffer.length) {
      const count = fs.readSync(descriptor, buffer, used, buffer.length - used, null);
      if (count === 0) break;
      used += count;
    }
  } finally {
    fs.closeSync(descriptor);
  }
  if (used > MAX_BYTES) reject('JSON input exceeds 2 MiB');
  const bytes = buffer.subarray(0, used);
  if (bytes.length >= 3 && bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf) {
    reject('UTF-8 BOM is not permitted');
  }
  let text;
  try {
    text = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes);
  } catch {
    reject('JSON input is not valid UTF-8');
  }
  return strictParse(text);
}

const USAGE = 'usage: node verify_node.mjs PACK --trust TRUST [--json]';

function argumentsFor(argv) {
  let pack;
  let trust;
  let json = false;
  let positionalOnly = false;
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (!positionalOnly && argument === '--') {
      positionalOnly = true;
    } else if (!positionalOnly && argument === '--json') {
      json = true;
    } else if (!positionalOnly && argument === '--trust') {
      if (index + 1 >= argv.length || argv[index + 1].startsWith('-')) {
        throw new UsageError('--trust requires a file path');
      }
      trust = argv[++index];
    } else if (!positionalOnly && argument.startsWith('--trust=')) {
      trust = argument.slice('--trust='.length);
    } else if (!positionalOnly && argument.startsWith('-')) {
      throw new UsageError('unrecognized argument: ' + argument);
    } else if (pack === undefined) {
      pack = argument;
    } else {
      throw new UsageError('only one Evidence Pack path is accepted');
    }
  }
  if (pack === undefined || trust === undefined) throw new UsageError('PACK and --trust TRUST are required');
  return { pack, trust, json };
}

function output(verdict, checks, error, json) {
  if (json) {
    process.stdout.write(JSON.stringify({ contract_id: CONTRACT_ID, verdict, checks, error }) + '\n');
  } else if (verdict === 'PASS') {
    process.stdout.write('PASS (experimental demo only): ' + checks.join(', ') + '\n');
  } else {
    process.stdout.write(verdict + ': ' + error + '\n');
  }
}

function main(argv) {
  if (argv.includes('--help') || argv.includes('-h')) {
    process.stdout.write(USAGE + '\nOffline experimental checks using explicit role keys and a pinned scope.\n');
    return 0;
  }
  let options;
  try {
    options = argumentsFor(argv);
  } catch (error) {
    if (!(error instanceof UsageError)) throw error;
    process.stderr.write(USAGE + '\nerror: ' + error.message + '\n');
    return 2;
  }
  try {
    const pack = loadJsonFile(options.pack);
    const trust = loadJsonFile(options.trust);
    const checks = verifyPack(pack, trust);
    output('PASS', checks, null, options.json);
    return 0;
  } catch (error) {
    const invalid = error instanceof VerificationError;
    output(invalid ? 'FAIL' : 'ERROR', [], error.message || String(error), options.json);
    return invalid ? 1 : 2;
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  process.exitCode = main(process.argv.slice(2));
}

