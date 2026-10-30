"""Fixed offline verifier entry point, with an in-process Python audit guard.

This guard is intentionally not an OS sandbox. The interpreter, installed
dependencies and host controller remain external trust assumptions.
"""

import importlib
from importlib import metadata
import os
from pathlib import Path
import stat
import sys


DEPENDENCIES = {"cryptography": "50.0.2", "rfc8785": "0.1.4", "cffi": "2.1.1", "pycparser": "3.12"}
_MUTATIONS = {
    "os.remove", "os.unlink", "os.rename", "os.replace", "os.mkdir", "os.rmdir",
    "os.link", "os.symlink", "os.chmod", "os.chown", "os.lchown", "os.chflags",
    "os.lchflags", "os.truncate", "os.utime", "os.setxattr", "os.removexattr",
    "os.chdir", "os.kill", "os.killpg", "shutil.copyfile", "shutil.copymode",
    "shutil.copystat", "shutil.copytree", "shutil.move", "shutil.rmtree",
}
_PROCESSES = {"os.system", "os.fork", "os.forkpty", "os.posix_spawn", "os.posix_spawnp",
              "pty.spawn", "_posixsubprocess.fork_exec", "_winapi.CreateProcess"}
_WRITE_FLAGS = 0
for _flag in ("O_WRONLY", "O_RDWR", "O_CREAT", "O_TRUNC", "O_APPEND", "O_EXCL"):
    _WRITE_FLAGS |= getattr(os, _flag, 0)


def install_audit_guard():
    """Refuse action-capable audited operations and retain every denial event.

    Install only in a disposable worker: Python audit hooks cannot be removed.
    The returned list also detects a denial swallowed by imported code.
    """
    denied = []

    def guard(event, arguments):
        blocked = (event in _MUTATIONS or event in _PROCESSES
                   or event.startswith(("socket.", "subprocess.", "os.spawn", "os.exec", "tempfile.", "sqlite3.connect")))
        if event == "open":
            mode = arguments[1] if len(arguments) > 1 else None
            flags = arguments[2] if len(arguments) > 2 else 0
            blocked = ((type(mode) is str and any(letter in mode for letter in "wax+"))
                       or (type(flags) is int and bool(flags & _WRITE_FLAGS)))
        if blocked:
            denied.append(event)
            raise PermissionError("Offline recheck audit guard refused " + event)

    sys.addaudithook(guard)
    return denied


def _dependency_versions():
    versions = {}
    for name, expected in DEPENDENCIES.items():
        try:
            actual = metadata.version(name)
        except metadata.PackageNotFoundError as exc:
            raise ValueError("Missing pinned dependency: " + name + "==" + expected) from exc
        if actual != expected:
            raise ValueError("Pinned dependency mismatch: " + name + " requires " + expected + ", found " + actual)
        versions[name] = actual
    # Check the loaded module identity as well as the installed distribution
    # metadata. Imports occur only after the worker's audit hook is installed.
    for name, expected in versions.items():
        if getattr(importlib.import_module(name), "__version__", None) != expected:
            raise ValueError("Loaded module version differs from pinned distribution: " + name)
    return versions


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        if len(argv) != 3 or sys.flags.isolated != 1 or not sys.dont_write_bytecode:
            raise ValueError("Worker requires isolated -I -B execution and three fixed arguments")
        source_root = Path(argv[0]).absolute()
        evidence_root = Path(argv[1]).absolute()
        pilot = argv[2]
        if pilot not in {"upload", "publication", "erasure"}:
            raise ValueError("Unsupported fixed pilot")
        if (not stat.S_ISDIR(source_root.lstat().st_mode)
                or not stat.S_ISDIR(evidence_root.lstat().st_mode)
                or source_root.resolve() != Path(__file__).resolve().parents[3]):
            raise ValueError("Worker source root differs from its verified repository topology")
        denied = install_audit_guard()
        kit_root = source_root / "experiments/incident-recheck-kit"
        sys.path.insert(0, str(kit_root))
        from incident_recheck.layout import PILOTS, json_bytes, read_regular, strict_json

        versions = _dependency_versions()
        selected = PILOTS[pilot]
        sys.path.insert(0, str(source_root / "experiments/incident-evidence-assessor"))
        sys.path.insert(0, str(source_root / selected["directory"]))
        suite = importlib.import_module(selected["module"] + ".suite")
        expected_module = source_root / selected["directory"] / selected["module"] / "suite.py"
        if Path(suite.__file__).resolve() != expected_module.resolve():
            raise ValueError("Verifier module did not load from the verified source tree")
        result = suite.verify_exports(evidence_root / pilot)
        flag = "network_reexecuted" if pilot == "upload" else "filesystem_actions_reexecuted"
        if (type(result) is not dict or set(result) != {"verified_exports", flag, "scope"}
                or type(result["verified_exports"]) is not int or result["verified_exports"] != selected["count"]
                or result[flag] is not False or type(result["scope"]) is not str or not result["scope"].strip()):
            raise ValueError("Original verifier returned an unsupported result or action flag")
        summary = strict_json(read_regular(evidence_root / pilot, "summary.json"))
        if summary["source_sha256"] != selected["source_sha256"]:
            raise ValueError("Rechecked summary has an unexpected source identity")
        if denied:
            raise ValueError("A verifier swallowed a refused action: " + ",".join(sorted(set(denied))))
        response = {
            "format": "incident-recheck-worker/0.1", "pilot": pilot,
            "verified_exports": result["verified_exports"], "actions_reexecuted": False,
            "source_sha256": summary["source_sha256"], "dependencies": versions, "guard": "PYTHON_AUDIT_EVENTS",
        }
        sys.stdout.buffer.write(json_bytes(response))
        sys.stdout.buffer.flush()
        return 0
    except Exception as exc:
        print("Offline recheck worker failed: " + type(exc).__name__ + ": " + str(exc)[:2000], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
