"""Check all declared outcomes against separately generated structured evidence."""

import unittest

from incident_assessor.assess import assess
from incident_assessor.model import strict_json
from suite import CATALOGUE, fixtures


class CatalogueTests(unittest.TestCase):
    def test_all_named_expectations(self):
        cases, generated = strict_json(CATALOGUE)["cases"], fixtures()
        self.assertEqual(len(cases), 23)
        self.assertEqual({case["id"] for case in cases}, set(generated))
        for case in cases:
            with self.subTest(case=case["id"]):
                result = assess(*generated[case["id"]], allow_synthetic=True)
                for field, expected in case["expected"].items():
                    if field != "reasons":
                        self.assertEqual(result["assessments"].get(field), expected, field)
                self.assertEqual(result["full_vap_conformance"], "NOT_ASSESSED")
                self.assertEqual(result["legal_compliance"], "NOT_ASSESSED")


if __name__ == "__main__":
    unittest.main()
