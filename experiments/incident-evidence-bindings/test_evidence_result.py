import unittest
from evidence_result import Claim, PROPOSITIONS, make_result, encode_result

class ResultTests(unittest.TestCase):
    def sample(self):
        return {k: Claim("INDETERMINATE") for k in PROPOSITIONS}

    def test_independent_verdicts(self):
        claims = self.sample()
        claims["integrity"] = Claim("VALID", ("receipt-1",))
        claims["authorization"] = Claim("INVALID", ("policy-1",))
        result = make_result(claims, case_id="T07")
        self.assertEqual(result["claims"]["integrity"]["verdict"], "VALID")
        self.assertEqual(result["claims"]["authorization"]["verdict"], "INVALID")
        self.assertEqual(result["claims"]["observed_egress"]["verdict"], "INDETERMINATE")
        self.assertTrue(result["synthetic"])

    def test_valid_requires_evidence(self):
        claims = self.sample()
        claims["integrity"] = Claim("VALID")
        with self.assertRaises(ValueError):
            make_result(claims, case_id="T07")

    def test_missing_claim_rejected(self):
        claims = self.sample()
        del claims["causality"]
        with self.assertRaises(ValueError):
            make_result(claims, case_id="T02")

    def test_non_synthetic_rejected(self):
        with self.assertRaises(ValueError):
            make_result(self.sample(), case_id="T01", synthetic=False)

    def test_external_url_reference_rejected(self):
        claims = self.sample()
        claims["integrity"] = Claim("VALID", ("https://example.com/secret",))
        with self.assertRaises(ValueError):
            make_result(claims, case_id="T07")

    def test_deterministic_encoding(self):
        result = make_result(self.sample(), case_id="T08")
        self.assertEqual(encode_result(result), encode_result(result))
        self.assertIn(b'experimental-evidence-result-v0', encode_result(result))

if __name__ == "__main__":
    unittest.main()
