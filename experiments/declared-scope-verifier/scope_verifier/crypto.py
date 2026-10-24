"""JCS, Ed25519 envelopes and RFC 6962 SHA-256 inclusion proofs.

The envelope is a local, versioned experiment contract, not a VAP wire format.
Only the fixture generator imports private-key functionality.
"""

import hashlib
import json
import re
from pathlib import Path

import rfc8785
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from . import ADAPTER

MAX_BYTES = 32 * 1024 * 1024
MAX_ITEMS = 10000


class InputError(ValueError):
    pass


def object_value(value, name):
    if not isinstance(value, dict):
        raise InputError(name + " must be an object")
    return value


def array_value(value, name):
    if not isinstance(value, list) or len(value) > MAX_ITEMS:
        raise InputError(name + " must be an array of at most 10000 items")
    return value


def string_value(value, name):
    if not isinstance(value, str) or not value:
        raise InputError(name + " must be a nonempty string")
    return value


def string_array(value, name):
    return [string_value(item, name + " item") for item in array_value(value, name)]


def canonical(value):
    try:
        return rfc8785.dumps(value)
    except (ValueError, TypeError, RecursionError) as exc:
        raise InputError("Value is outside the supported JCS data model") from exc


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def strict_json(path):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise InputError("Duplicate JSON key: " + key)
            out[key] = value
        return out

    def invalid_constant(value):
        raise InputError("Non-finite JSON number: " + value)

    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise InputError("Input exceeds 32 MiB")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=invalid_constant)
        canonical(value)
        return value
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise InputError("Invalid JSON input") from exc


def natural(value, maximum=MAX_ITEMS):
    if type(value) is not int or not 0 <= value <= maximum:
        raise InputError("Expected a bounded nonnegative integer")
    return value


def hex_bytes(value, length=32):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{%d}" % (length * 2), value):
        raise InputError("Invalid lowercase hexadecimal value")
    return bytes.fromhex(value)


def signing_bytes(envelope):
    return (ADAPTER + "\x00").encode() + canonical({
        "algorithm": envelope["algorithm"], "key_id": envelope["key_id"],
        "body": envelope["body"],
    })


def authenticate(envelope, trust, role):
    if not isinstance(envelope, dict):
        return "indeterminate", "missing signed object"
    if envelope.get("algorithm") != "Ed25519":
        return "indeterminate", "unsupported signature algorithm"
    if "signature" not in envelope or "body" not in envelope:
        return "indeterminate", "signature or signed body unavailable"
    key = object_value(trust["keys"], "trust.keys").get(envelope.get("key_id"))
    if key is None:
        return "indeterminate", "no evaluator-authorized key for this role"
    object_value(key, "trust key")
    if role not in string_array(key["roles"], "trust key roles"):
        return "indeterminate", "no evaluator-authorized key for this role"
    try:
        Ed25519PublicKey.from_public_bytes(hex_bytes(key["public_key"])).verify(
            hex_bytes(envelope["signature"], 64), signing_bytes(envelope))
    except InvalidSignature:
        return "failed", "Ed25519 signature mismatch"
    return "verified", "Ed25519 signature verified under evaluator trust configuration"


def leaf_hash(body):
    return hashlib.sha256(b"\x00" + canonical(body)).digest()


def node_hash(left, right):
    return hashlib.sha256(b"\x01" + left + right).digest()


def split(size):
    return 1 << ((size - 1).bit_length() - 1)


def merkle_root(leaves):
    if not leaves:
        return hashlib.sha256(b"").digest()
    if len(leaves) == 1:
        return leaves[0]
    k = split(len(leaves))
    return node_hash(merkle_root(leaves[:k]), merkle_root(leaves[k:]))


def audit_path(leaves, index):
    if not 0 <= index < len(leaves):
        raise InputError("Merkle index out of range")
    if len(leaves) == 1:
        return []
    k = split(len(leaves))
    if index < k:
        return audit_path(leaves[:k], index) + [merkle_root(leaves[k:]).hex()]
    return audit_path(leaves[k:], index - k) + [merkle_root(leaves[:k]).hex()]


def inclusion(leaf, index, size, path, root):
    natural(size)
    natural(index)
    if not size or index >= size or not isinstance(path, list) or len(path) > 64:
        return False
    siblings = [hex_bytes(item) for item in path]
    cursor = 0

    def fold(i, n):
        nonlocal cursor
        if n == 1:
            return leaf
        k = split(n)
        child = fold(i, k) if i < k else fold(i - k, n - k)
        if cursor == len(siblings):
            raise InputError("Truncated Merkle proof")
        sibling = siblings[cursor]
        cursor += 1
        return node_hash(child, sibling) if i < k else node_hash(sibling, child)

    try:
        result = fold(index, size)
    except InputError:
        return False
    return cursor == len(siblings) and result == hex_bytes(root)
