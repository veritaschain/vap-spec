#!/bin/sh
# Existing first-party checks only; dependency installation is a separate step.
set -eu

if [ "$#" -ne 0 ]; then
    printf '%s\n' 'Usage: sh interop/vap-evidence-pack-demo/reproduce.sh' >&2
    exit 2
fi

demo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$demo_dir"
demo_python=${VAP_DEMO_PYTHON:-python3}

"$demo_python" - <<'PY'
import importlib.metadata
import sys

if sys.version_info[:2] != (3, 12):
    raise SystemExit("ERROR: the recorded toolchain requires Python 3.12")
for name, expected in (("cryptography", "50.0.2"), ("jsonschema", "4.25.1")):
    try:
        actual = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        raise SystemExit(f"ERROR: install the documented requirements; missing {name}") from None
    if actual != expected:
        raise SystemExit(f"ERROR: {name} must be {expected}; found {actual}")
    print(f"{name}={actual}", flush=True)
print(f"Python={sys.version.split()[0]}", flush=True)
PY

node -e 'if (process.versions.node.split(".")[0] !== "24") { console.error("ERROR: the recorded toolchain requires Node.js 24"); process.exit(2); } console.log("Node=" + process.versions.node);'
"$demo_python" generate_demo.py --check
exec "$demo_python" -m unittest discover -s tests -v
