"""Synthetic cryptographic integrity tests; not a VAP verifier."""
import hashlib, json, unittest
def digest(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).digest()
def root(leaves):
    if not leaves: raise ValueError("empty")
    nodes=[hashlib.sha256(b'\\x00'+digest(x)).digest() for x in leaves]
    while len(nodes)>1:
        nodes=[hashlib.sha256(b'\\x01'+nodes[i]+nodes[i+1]).digest() if i+1<len(nodes) else nodes[i] for i in range(0,len(nodes),2)]
    return nodes[0]
class IntegrityTests(unittest.TestCase):
    def test_anchored_commitment_changes_after_mutation(self):
        events=[{"id":i,"state":"observed"} for i in range(5)]
        committed=root(events)
        events[2]["state"]="altered"
        self.assertNotEqual(committed,root(events))
    def test_submitted_subset_is_not_the_committed_batch(self):
        events=[{"id":i} for i in range(5)]
        self.assertNotEqual(root(events),root(events[:-1]))
    def test_reordering_changes_commitment(self):
        events=[{"id":i} for i in range(5)]
        self.assertNotEqual(root(events),root(list(reversed(events))))
    def test_unobserved_event_is_not_discoverable(self):
        captured=[{"id":1}]
        self.assertEqual(root(captured),root(captured))
        # A valid commitment cannot prove that no external event occurred.
if __name__=="__main__": unittest.main()
