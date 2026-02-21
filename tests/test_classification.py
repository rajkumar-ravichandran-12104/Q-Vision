"""
test_classification.py — Unit tests for classification.py
"""

import unittest

from classification import check_mismatch, classify_load, classify_zone


def _dist(pct_6=0, pct_10=0, pct_20=0):
    """Helper: build a minimal distribution dict."""
    other = max(0, 100 - pct_6 - pct_10 - pct_20)
    return {
        "count": 100,
        "pct_6mm": float(pct_6),
        "pct_10mm": float(pct_10),
        "pct_20mm": float(pct_20),
        "pct_other": float(other),
    }


class TestClassifyZone(unittest.TestCase):
    def test_classify_6mm_dominant(self):
        result = classify_zone(_dist(pct_6=85))
        self.assertEqual(result["label"], "6mm")
        self.assertGreaterEqual(result["confidence_pct"], 80.0)

    def test_classify_10mm_dominant(self):
        result = classify_zone(_dist(pct_10=90))
        self.assertEqual(result["label"], "10mm")

    def test_classify_20mm_dominant(self):
        result = classify_zone(_dist(pct_20=82))
        self.assertEqual(result["label"], "20mm")

    def test_classify_mixed_no_dominant(self):
        result = classify_zone(_dist(pct_6=30, pct_10=35, pct_20=20))
        self.assertEqual(result["label"], "mixed")

    def test_result_has_required_keys(self):
        result = classify_zone(_dist(pct_6=85))
        self.assertIn("label", result)
        self.assertIn("confidence_pct", result)
        self.assertIn("distribution", result)

    def test_boundary_exactly_80_pct(self):
        # Exactly at the threshold should classify as that class
        result = classify_zone(_dist(pct_6=80))
        self.assertEqual(result["label"], "6mm")

    def test_below_threshold_is_mixed(self):
        result = classify_zone(_dist(pct_6=79))
        # 79% is below min_pct=80, so should NOT classify as 6mm
        self.assertNotEqual(result["label"], "6mm")


class TestClassifyLoad(unittest.TestCase):
    def _make_zone_results(self, labels):
        """Create a list of zone result dicts from a list of labels."""
        return [
            {"label": lbl, "confidence_pct": 85.0 if lbl != "mixed" else 0.0}
            for lbl in labels
        ]

    def test_five_zones_agree_high_confidence(self):
        zones = self._make_zone_results(["10mm", "10mm", "10mm", "10mm", "10mm"])
        result = classify_load(zones)
        self.assertEqual(result["label"], "10mm")
        self.assertFalse(result["is_mixed"])
        self.assertEqual(result["warning"], "")

    def test_four_zones_agree(self):
        zones = self._make_zone_results(["6mm", "6mm", "6mm", "6mm", "10mm"])
        result = classify_load(zones)
        self.assertEqual(result["label"], "6mm")
        self.assertFalse(result["is_mixed"])

    def test_three_zones_agree_warning(self):
        zones = self._make_zone_results(["20mm", "20mm", "20mm", "10mm", "6mm"])
        result = classify_load(zones)
        self.assertEqual(result["label"], "20mm")
        self.assertFalse(result["is_mixed"])
        self.assertIn("contamination", result["warning"].lower())

    def test_no_majority_mixed_load(self):
        zones = self._make_zone_results(["6mm", "10mm", "20mm", "mixed", "mixed"])
        result = classify_load(zones)
        self.assertTrue(result["is_mixed"])
        self.assertEqual(result["label"], "MIXED LOAD")
        self.assertIn("MIXED LOAD", result["warning"])

    def test_empty_zones(self):
        result = classify_load([])
        self.assertTrue(result["is_mixed"])
        self.assertEqual(result["label"], "UNKNOWN")

    def test_result_has_required_keys(self):
        zones = self._make_zone_results(["10mm"] * 5)
        result = classify_load(zones)
        for key in ("label", "confidence", "zone_details", "warning", "is_mixed"):
            self.assertIn(key, result)


class TestCheckMismatch(unittest.TestCase):
    def _classification(self, label):
        return {"label": label}

    def test_match(self):
        result = check_mismatch(self._classification("10mm"), "10mm")
        self.assertTrue(result["match"])
        self.assertIn("✅", result["message"])

    def test_mismatch(self):
        result = check_mismatch(self._classification("6mm"), "10mm")
        self.assertFalse(result["match"])
        self.assertIn("⚠️", result["message"])

    def test_case_insensitive(self):
        result = check_mismatch(self._classification("10mm"), "10MM")
        self.assertTrue(result["match"])

    def test_mixed_vs_expected(self):
        result = check_mismatch(self._classification("MIXED LOAD"), "20mm")
        self.assertFalse(result["match"])


if __name__ == "__main__":
    unittest.main()
