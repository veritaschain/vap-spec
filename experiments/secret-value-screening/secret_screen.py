"""Pattern screening of synthetic event records for reusable secrets.

Experimental and unadopted. This is not a VAP v1.2 requirement, a conformance
verifier or a secret scanner for production use. It exercises one candidate
rule (register row F13) on synthetic input only.

A match demonstrates that a value of a known secret shape is present in a
screened member. No match is not evidence that a record is free of secrets.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

FOUND = "SECRET_PATTERN_FOUND"
NOT_MATCHED = "NO_PATTERN_MATCHED"
REJECTED = "INPUT_REJECTED"

# Top-level members that are not screened. In v1.2 the event hash is computed
# over the header and payload (section 4.1.3, Mechanism A); the security block
# holds the hash, signatures and anchor references. Which members enter a hash
# or a Merkle leaf is profile-defined; this constant is a local assumption.
UNSCREENED_TOP_LEVEL = frozenset({"security"})

# Member names whose non-empty string value is reported regardless of shape.
SECRET_MEMBER_NAMES = frozenset(
    {
        "password",
        "passwd",
        "secret",
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "bearer_token",
        "private_key",
        "session_cookie",
        "recovery_code",
    }
)

# Shapes searched for inside string values. Order is the reporting order.
VALUE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("pem-private-key", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----")),
    (
        "jwt",
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    ),
    ("bearer-token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{16,}=*")),
    ("url-userinfo", re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s/:@]+:[^\s/@]+@")),
    (
        "cookie-header",
        re.compile(r"(?i)\b(?:set-)?cookie:\s*[^=\s;]+=[^\s;]{16,}"),
    ),
    (
        "named-assignment",
        re.compile(
            r"(?i)\b(?:pass(?:word|wd)?|secret|api[_-]?key|access[_-]?token"
            r"|recovery[_-]?code)\s*[=:]\s*[^\s\"',;]{8,}"
        ),
    ),
)


class InputRejected(ValueError):
    """The input is not a serialization this experiment will screen."""


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise InputRejected(f"duplicate member name: {key!r}")
        out[key] = value
    return out


def parse_event(text: str) -> dict[str, Any]:
    """Parse one event. A byte order mark, duplicate member names and a
    non-object top level are rejected and never repaired."""
    if text.startswith("﻿"):
        raise InputRejected("byte order mark")
    try:
        value = json.loads(text, object_pairs_hook=_no_duplicates)
    except json.JSONDecodeError as exc:
        raise InputRejected(f"not JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise InputRejected("top-level value is not an object")
    return value


def _pointer(parts: tuple[str, ...]) -> str:
    return "".join("/" + p.replace("~", "~0").replace("/", "~1") for p in parts)


def _covered(pointer: str, not_assessed: frozenset[str]) -> bool:
    return any(pointer == p or pointer.startswith(p + "/") for p in not_assessed)


def _walk(value: Any, parts: tuple[str, ...]):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, parts + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, parts + (str(index),))
    else:
        yield parts, value


def screen(event: dict[str, Any], not_assessed: tuple[str, ...] = ()) -> dict[str, Any]:
    """Screen one parsed event.

    ``not_assessed`` lists JSON Pointers that the caller declares withheld or
    encrypted before commitment. They are reported as not assessed; nothing is
    concluded about their content.

    The report carries the pointer, the pattern class and the length of the
    string in which the match occurred. It never carries the matched text.
    """
    skip = frozenset(not_assessed)
    findings: list[dict[str, Any]] = []
    skipped: set[str] = set()
    for parts, leaf in _walk(event, ()):
        if parts and parts[0] in UNSCREENED_TOP_LEVEL:
            continue
        pointer = _pointer(parts)
        if _covered(pointer, skip):
            skipped.add(next(p for p in skip if pointer == p or pointer.startswith(p + "/")))
            continue
        if not isinstance(leaf, str) or not leaf:
            continue
        classes: list[str] = []
        if parts and parts[-1].lower() in SECRET_MEMBER_NAMES:
            classes.append("secret-member-name")
        classes.extend(name for name, pattern in VALUE_PATTERNS if pattern.search(leaf))
        for name in classes:
            findings.append({"pointer": pointer, "class": name, "value_length": len(leaf)})
    declared_absent = sorted(skip - skipped)
    return {
        "result": FOUND if findings else NOT_MATCHED,
        "findings": findings,
        "not_assessed": sorted(skipped),
        "not_assessed_but_absent": declared_absent,
        "complete_coverage": not skipped,
        "screened_scope": "all members except top-level: " + ", ".join(sorted(UNSCREENED_TOP_LEVEL)),
        "limit": "No match is not evidence that no secret is present.",
    }


def screen_text(text: str, not_assessed: tuple[str, ...] = ()) -> dict[str, Any]:
    try:
        event = parse_event(text)
    except InputRejected as exc:
        return {"result": REJECTED, "reason": str(exc), "findings": []}
    return screen(event, not_assessed)


# --- synthetic material ----------------------------------------------------
#
# Case files hold placeholders. The secret-shaped strings are assembled here at
# run time from fragments, so that no secret-shaped literal is stored in the
# repository. Every value is synthetic and grants access to nothing.


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def synthetic_values() -> dict[str, str]:
    filler = "synthetic" + "0" * 24
    jwt = ".".join(
        (
            _b64url(b'{"alg":"none","typ":"JWT"}'),
            _b64url(b'{"sub":"synthetic-subject"}'),
            _b64url(b"synthetic-signature-bytes"),
        )
    )
    pem = "-----BEGIN " + "PRIVATE KEY-----\n" + "U1lOVEhFVElD" * 4 + "\n-----END " + "PRIVATE KEY-----"
    return {
        "{{BEARER}}": "Authorization: " + "Bearer " + filler,
        "{{JWT}}": jwt,
        "{{PEM_PRIVATE_KEY}}": pem,
        "{{URL_USERINFO}}": "https://" + "svc-user" + ":" + "synthetic-pass-0000" + "@example.invalid/export",
        "{{COOKIE}}": "Cookie: " + "session=" + filler,
        "{{ASSIGNMENT}}": "connect with pass" + "word=" + "synthetic-0000-0000",
        "{{OPAQUE_SECRET}}": filler,
        "{{SHA256_OF_LOW_ENTROPY}}": hashlib.sha256(b"synthetic-low-entropy").hexdigest(),
        "{{SHA256_DIGEST}}": hashlib.sha256(b"synthetic input document").hexdigest(),
        "{{BASE64_SIGNATURE}}": base64.b64encode(hashlib.sha512(b"synthetic signature").digest()).decode("ascii"),
    }


def materialize(value: Any, table: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {key: materialize(child, table) for key, child in value.items()}
    if isinstance(value, list):
        return [materialize(child, table) for child in value]
    if isinstance(value, str):
        for placeholder, replacement in table.items():
            value = value.replace(placeholder, replacement)
    return value


def load_cases(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicates)
    return data["cases"]


def run_case(case: dict[str, Any], table: dict[str, str]) -> dict[str, Any]:
    if "raw_text" in case:
        text = materialize(case["raw_text"], table)
    else:
        text = json.dumps(materialize(case["event"], table), ensure_ascii=False)
    report = screen_text(text, tuple(case.get("not_assessed", ())))
    expected = case["expected"]
    observed = {
        "result": report["result"],
        "classes": sorted({f["class"] for f in report["findings"]}),
        "pointers": sorted({f["pointer"] for f in report["findings"]}),
        "not_assessed": report.get("not_assessed", []),
    }
    wanted = {
        "result": expected["result"],
        "classes": sorted(expected.get("classes", [])),
        "pointers": sorted(expected.get("pointers", [])),
        "not_assessed": sorted(expected.get("not_assessed", [])),
    }
    return {
        "id": case["id"],
        "match": observed == wanted,
        "expected": wanted,
        "observed": observed,
        "known_limit": bool(case.get("known_limit", False)),
    }


def run_suite(path: Path) -> dict[str, Any]:
    table = synthetic_values()
    results = [run_case(case, table) for case in load_cases(path)]
    return {
        "cases": len(results),
        "matched": sum(1 for r in results if r["match"]),
        "known_limit_cases": [r["id"] for r in results if r["known_limit"]],
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    suite = sub.add_parser("run-suite", help="run the synthetic cases")
    suite.add_argument("--cases", type=Path, default=Path(__file__).with_name("cases.json"))
    one = sub.add_parser("screen", help="screen one event file")
    one.add_argument("file", type=Path)
    one.add_argument("--not-assessed", action="append", default=[], metavar="JSON_POINTER")
    args = parser.parse_args(argv)
    if args.command == "run-suite":
        summary = run_suite(args.cases)
        json.dump(summary, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0 if summary["matched"] == summary["cases"] else 1
    report = screen_text(args.file.read_text(encoding="utf-8"), tuple(args.not_assessed))
    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if report["result"] == NOT_MATCHED else 1


if __name__ == "__main__":
    raise SystemExit(main())
