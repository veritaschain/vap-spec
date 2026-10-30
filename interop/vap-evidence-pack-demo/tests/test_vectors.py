"""Fixed-byte reproducibility, published schemas and independent tree vectors."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from verify_python import CHECKS, CONTRACT_ID, canonical, load_json, merkle_root, verify_pack

VECTORS = HERE / "test-vectors"


class FixedVectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((VECTORS / "manifest.json").read_text(encoding="ascii"))
        cls.commands = ([sys.executable, str(HERE / "verify_python.py")],
                        ["node", str(HERE / "verify_node.mjs")])

    def test_manifest_covers_all_fixed_bytes(self):
        manifest = self.manifest
        self.assertEqual(manifest["contract_id"], CONTRACT_ID)
        self.assertEqual(manifest["manifest_version"], "demo-vector-manifest/1")
        self.assertEqual(len(manifest["files"]), 10)
        self.assertEqual({p.name for p in VECTORS.iterdir()},
                         set(manifest["files"]) | {"manifest.json"})
        for name, expected in manifest["files"].items():
            with self.subTest(file=name):
                content = (VECTORS / name).read_bytes()
                self.assertEqual(len(content), expected["bytes"])
                self.assertEqual(hashlib.sha256(content).hexdigest(), expected["sha256"])
        vectors = manifest["vectors"]
        self.assertEqual(len(vectors), 8)
        self.assertEqual(sum(v["expected_verdict"] == "PASS" for v in vectors), 2)
        self.assertEqual(sum(v["expected_verdict"] == "FAIL" for v in vectors), 6)
        self.assertEqual({v["pack"] for v in vectors}, set(manifest["files"]) -
                         {"demo-trust.json", "demo-trust-six.json"})

    def test_every_fixture_has_the_published_structural_shape(self):
        # Negative fixtures are deliberately structurally valid: cryptographic
        # and relational rejection must be performed by the two verifiers.
        for filename, artifact_names in (
            ("evidence-pack.schema.json", [v["pack"] for v in self.manifest["vectors"]]),
            ("demo-trust.schema.json", ["demo-trust.json", "demo-trust-six.json"]),
        ):
            schema = json.loads((HERE / "schema" / filename).read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema)
            for name in artifact_names:
                with self.subTest(schema=filename, file=name):
                    validator.validate(load_json(VECTORS / name))

    def test_both_clis_obey_all_fixed_expectations(self):
        for vector in self.manifest["vectors"]:
            results = []
            for command in self.commands:
                with self.subTest(file=vector["pack"], verifier=command[0]):
                    result = subprocess.run(
                        [*command, str(VECTORS / vector["pack"]), "--trust",
                         str(VECTORS / vector["trust"]), "--json"],
                        capture_output=True, text=True, timeout=20, cwd=HERE)
                    # An exception, usage error or missing dependency is never
                    # accepted as evidence that a negative vector was rejected.
                    self.assertEqual(result.returncode, vector["expected_exit_code"], result.stderr)
                    output = json.loads(result.stdout)
                    self.assertEqual(set(output), {"contract_id", "verdict", "checks", "error"})
                    self.assertEqual(output["contract_id"], CONTRACT_ID)
                    self.assertEqual(output["verdict"], vector["expected_verdict"])
                    if result.returncode == 0:
                        self.assertEqual(output["checks"], CHECKS)
                        self.assertIsNone(output["error"])
                    else:
                        self.assertEqual(output["checks"], [])
                        self.assertIsInstance(output["error"], str)
                        self.assertTrue(output["error"])
                    results.append((output["verdict"], output["checks"]))
            self.assertEqual(results[0], results[1])

    def test_positive_roots_and_scope_are_fixed(self):
        for vector in self.manifest["vectors"]:
            if vector["expected_verdict"] != "PASS":
                continue
            with self.subTest(file=vector["pack"]):
                pack = load_json(VECTORS / vector["pack"])
                trust = load_json(VECTORS / vector["trust"])
                self.assertEqual(verify_pack(pack, trust), CHECKS)
                self.assertEqual(pack["merkle"]["root"], vector["merkle_root"])
                self.assertEqual(merkle_root(pack["events"]), vector["merkle_root"])
                self.assertEqual(pack["scope_commitment"], vector["scope_commitment"])
        self.assertEqual(len(load_json(VECTORS / "valid-six-events.json")["events"]), 6)

    def test_check_generation_does_not_write(self):
        before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in VECTORS.iterdir()}
        result = subprocess.run([sys.executable, str(HERE / "generate_demo.py"), "--check"],
                                capture_output=True, text=True, timeout=20, cwd=HERE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in VECTORS.iterdir()}
        self.assertEqual(before, after)

    def test_explicit_generation_reproduces_committed_files(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(HERE / "generate_demo.py"), "--output-dir", directory],
                capture_output=True, text=True, timeout=20, cwd=HERE)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({p.name for p in Path(directory).iterdir()},
                             {p.name for p in VECTORS.iterdir()})
            for path in VECTORS.iterdir():
                self.assertEqual((Path(directory) / path.name).read_bytes(), path.read_bytes())
        result = subprocess.run([sys.executable, str(HERE / "generate_demo.py")],
                                capture_output=True, text=True, timeout=20, cwd=HERE)
        self.assertEqual(result.returncode, 2, "generator must require an explicit mode")

    def test_rfc6962_empty_three_and_five_leaf_roots(self):
        # Independent fixed expectations for literal leaf bytes b'"a"' ...
        # b'"e"', obtained from RFC 6962 section 2.1's explicit splits:
        # 3 = node(node(a,b),c); 5 = node(node(node(a,b),node(c,d)),e).
        # This catches the historical duplicate-padding tree, including its
        # non-power-of-two behavior, without using the generator for an oracle.
        cases = [
            ([], "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            (list("abc"), "167d364c005b98256a1cae3249a00143460f084dfa6819392e70f0bd92821bd5"),
            (list("abcde"), "e8a452705e5b9ec5a85e89d6aa82ab55e36e2ab52a52c2850ffc19fc4887fbe3"),
        ]
        for leaves, expected in cases:
            self.assertEqual(merkle_root(leaves), expected)
        probe = """import {merkleRoot} from './verify_node.mjs';
import fs from 'node:fs';
console.log(JSON.stringify(JSON.parse(fs.readFileSync(0,'utf8')).map(merkleRoot)));"""
        result = subprocess.run(["node", "--input-type=module", "-e", probe],
                                input=json.dumps([leaves for leaves, _ in cases]),
                                capture_output=True, text=True, timeout=20, cwd=HERE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [root for _, root in cases])

    def test_generator_refuses_existing_files_and_dangling_symlinks(self):
        for collision_kind in ("file", "dangling-symlink"):
            with self.subTest(kind=collision_kind), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "output"
                output.mkdir()
                target = output / "valid-pack.json"
                if collision_kind == "file":
                    target.write_bytes(b"historical evidence must remain unchanged")
                else:
                    target.symlink_to(Path(directory) / "does-not-exist.json")
                result = subprocess.run(
                    [sys.executable, str(HERE / "generate_demo.py"), "--output-dir", str(output)],
                    capture_output=True, text=True, timeout=20, cwd=HERE)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual({p.name for p in output.iterdir()}, {"valid-pack.json"})
                if collision_kind == "file":
                    self.assertEqual(target.read_bytes(), b"historical evidence must remain unchanged")
                else:
                    self.assertTrue(target.is_symlink())
                    self.assertFalse(target.exists())

    def test_canonical_bytes_match_for_numeric_keys_and_escaping(self):
        value = {"2": 9007199254740991, "10": -9007199254740991,
                 "nested": {"z": None, "a": False}, "escape": '"\\/', "space": " ~"}
        expected = b'{"10":-9007199254740991,"2":9007199254740991,"escape":"\\\"\\\\/","nested":{"a":false,"z":null},"space":" ~"}'
        self.assertEqual(canonical(value), expected)
        probe = """import {canonical,strictParse} from './verify_node.mjs';
import fs from 'node:fs';
process.stdout.write(canonical(strictParse(fs.readFileSync(0,'utf8'))));"""
        result = subprocess.run(["node", "--input-type=module", "-e", probe],
                                input=json.dumps(value).encode("ascii"),
                                capture_output=True, timeout=20, cwd=HERE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, expected)

    def test_io_errors_are_not_invalid_evidence_verdicts(self):
        for command in self.commands:
            with self.subTest(verifier=command[0]):
                result = subprocess.run(
                    [*command, str(VECTORS / "does-not-exist.json"), "--trust",
                     str(VECTORS / "demo-trust.json"), "--json"],
                    capture_output=True, text=True, timeout=20, cwd=HERE)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)["verdict"], "ERROR")

    def test_human_cli_rejects_duplicate_surrogate_keys_without_traceback(self):
        # Raw escaped unpaired surrogates are invalid, including in a repeated
        # object key. Diagnostic output must itself remain printable.
        with tempfile.TemporaryDirectory() as directory:
            pack_path = Path(directory) / "invalid.json"
            pack_path.write_bytes(b'{"\\ud800":1,"\\ud800":2}')
            for command in self.commands:
                with self.subTest(verifier=command[0]):
                    result = subprocess.run(
                        [*command, str(pack_path), "--trust", str(VECTORS / "demo-trust.json")],
                        capture_output=True, text=True, timeout=20, cwd=HERE)
                    self.assertEqual(result.returncode, 1)
                    self.assertTrue(result.stdout.startswith("FAIL:"), result.stderr)
                    self.assertEqual(result.stderr, "")

    def test_long_option_abbreviations_are_usage_errors(self):
        for command in self.commands:
            with self.subTest(verifier=command[0]):
                result = subprocess.run(
                    [*command, str(VECTORS / "valid-pack.json"), "--tru",
                     str(VECTORS / "demo-trust.json"), "--json"],
                    capture_output=True, text=True, timeout=20, cwd=HERE)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("usage:", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
