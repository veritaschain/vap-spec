"""Bounded custom SHA-256 commitment demonstration, not a VAP verifier."""

import hashlib
import json
import unittest


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).digest()


def root(leaves):
    if not leaves:
        raise ValueError("empty")
    nodes = [hashlib.sha256(b"\x00" + digest(value)).digest() for value in leaves]
    while len(nodes) > 1:
        nodes = [hashlib.sha256(b"\x01" + nodes[i] + nodes[i + 1]).digest()
                 if i + 1 < len(nodes) else nodes[i] for i in range(0, len(nodes), 2)]
    return nodes[0]


class IntegrityTests(unittest.TestCase):
    def test_fixed_small_tree_vectors(self):
        # Calculated separately with recursive largest-power-of-two splits
        # over literal ASCII JSON b'{"id":0}', ... . These pin this custom
        # SHA256(0x00 || SHA256(JSON)) leaf convention, not VAP conformance.
        vectors = {
            1: "9f7fab123ddcfc95a635352348e24c3dfa7067b9b10e509577e957125ea4992d",
            2: "5d026342a7e931fd740e93c74423fef0cf7a751b8d1dc5bbd62343ff0af1ad16",
            3: "8d6ce55d59b8b0c514a74dd39d0ec54c2c7ccc01ce7e22916885eb82effa9073",
            5: "73c4c2dba35abdf8074d7154b7c3e46f064329324d47f1b3ac083d46944ff6e7",
        }
        for count, expected in vectors.items():
            with self.subTest(count=count):
                self.assertEqual(root([{"id": i} for i in range(count)]).hex(), expected)

    def test_empty_input_is_rejected(self):
        with self.assertRaises(ValueError):
            root([])

    def test_local_commitment_changes_after_mutation(self):
        events = [{"id": i, "state": "observed"} for i in range(5)]
        committed = root(events)
        events[2]["state"] = "altered"
        self.assertNotEqual(committed, root(events))

    def test_submitted_subset_is_not_the_committed_batch(self):
        events = [{"id": i} for i in range(5)]
        self.assertNotEqual(root(events), root(events[:-1]))

    def test_reordering_changes_commitment(self):
        events = [{"id": i} for i in range(5)]
        self.assertNotEqual(root(events), root(list(reversed(events))))

    def test_different_histories_can_have_the_same_collected_commitment(self):
        observed = {"channel": "instrumented", "event": {"id": 1}}
        unseen = {"channel": "outside", "event": {"id": 2}}
        history_one = [observed]
        history_two = [observed, unseen]

        def capture(history):
            return [entry["event"] for entry in history if entry["channel"] == "instrumented"]

        self.assertNotEqual(history_one, history_two)
        self.assertNotEqual(root([entry["event"] for entry in history_one]),
                            root([entry["event"] for entry in history_two]))
        self.assertEqual(capture(history_one), capture(history_two))
        self.assertEqual(root(capture(history_one)), root(capture(history_two)))
        # Two distinct full histories produce the same collected evidence.
        # This finite counterexample cannot reveal events outside the collector.


if __name__ == "__main__":
    unittest.main()

