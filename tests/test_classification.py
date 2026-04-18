"""
test_classification.py — Unit tests for classification.py
"""

import unittest

from classification import check_mismatch, classify_load, classify_zone


def _dist(pct_6=0, pct_12=0, pct_20=0):
    """Helper: build a distribution dict with diameters matching the percentages."""
    total = 100
    diameters = []
    diameters.extend([5.0] * pct_6)     # 5mm -> 6mm class (0-8)
    diameters.extend([15.0] * pct_12)   # 15mm -> 12mm class (8-18)
    diameters.extend([25.0] * pct_20)   # 25mm -> 20mm class (18-50)
    remaining = total - len(diameters)
    diameters.extend([80.0] * remaining)  # outside all ranges
    other = max(0, 100 - pct_6 - pct_12 - pct_20)
    return {
        "count": total,
        "pct_6mm": float(pct_6),
        "pct_12mm": float(pct_12),
        "pct_20mm": float(pct_20),
        "pct_other": float(other),
        "diameters": diameters,
    }


class TestClassifyZone(unittest.TestCase):
    def test_classify_6mm_dominant(self):
        result = classify_zone(_dist(pct_6=85))
        self.assertEqual(result["label"], "6mm")
        self.assertGreaterEqual(result["confidence_pct"], 80.0)

    def test_classify_12mm_dominant(self):
        result = classify_zone(_dist(pct_12=90))
        self.assertEqual(result["label"], "12mm")

    def test_classify_20mm_dominant(self):
        result = classify_zone(_dist(pct_20=82))
        self.assertEqual(result["label"], "20mm")

    def test_classify_mixed_no_dominant(self):
        result = classify_zone(_dist(pct_6=30, pct_12=35, pct_20=20))
        self.assertEqual(result["label"], "mixed")

    def test_result_has_required_keys(self):
        result = classify_zone(_dist(pct_6=85))
        self.assertIn("label", result)
        self.assertIn("confidence_pct", result)
        self.assertIn("distribution", result)

    def test_boundary_exactly_80_pct(self):
        # Exactly at threshold (60) should classify
        result = classify_zone(_dist(pct_6=60))
        self.assertEqual(result["label"], "6mm")

    def test_below_threshold_is_mixed(self):
        result = classify_zone(_dist(pct_6=59))
        # 59% is below min_pct=60, so should NOT classify as 6mm
        self.assertNotEqual(result["label"], "6mm")


class TestClassifyLoad(unittest.TestCase):
    def _make_zone_results(self, labels):
        """Create a list of zone result dicts from a list of labels."""
        return [
            {"label": lbl, "confidence_pct": 85.0 if lbl != "mixed" else 0.0}
            for lbl in labels
        ]

    def test_five_zones_agree_high_confidence(self):
        zones = self._make_zone_results(["12mm", "12mm", "12mm", "12mm", "12mm"])
        result = classify_load(zones)
        self.assertEqual(result["label"], "12mm")
        self.assertFalse(result["is_mixed"])
        self.assertEqual(result["warning"], "")

    def test_four_zones_agree(self):
        zones = self._make_zone_results(["6mm", "6mm", "6mm", "6mm", "12mm"])
        result = classify_load(zones)
        self.assertEqual(result["label"], "6mm")
        self.assertFalse(result["is_mixed"])

    def test_three_zones_agree_warning(self):
        zones = self._make_zone_results(["20mm", "20mm", "20mm", "12mm", "6mm"])
        result = classify_load(zones)
        self.assertEqual(result["label"], "20mm")
        self.assertFalse(result["is_mixed"])
        self.assertIn("contamination", result["warning"].lower())

    def test_no_majority_mixed_load(self):
        zones = self._make_zone_results(["6mm", "12mm", "20mm", "mixed", "mixed"])
        result = classify_load(zones)
        self.assertTrue(result["is_mixed"])
        self.assertEqual(result["label"], "MIXED LOAD")
        self.assertIn("MIXED LOAD", result["warning"])

    def test_empty_zones(self):
        result = classify_load([])
        self.assertTrue(result["is_mixed"])
        self.assertEqual(result["label"], "UNKNOWN")

    def test_result_has_required_keys(self):
        zones = self._make_zone_results(["12mm"] * 5)
        result = classify_load(zones)
        for key in ("label", "confidence", "zone_details", "warning", "is_mixed"):
            self.assertIn(key, result)


class TestCheckMismatch(unittest.TestCase):
    def _classification(self, label):
        return {"label": label}

    def test_match(self):
        result = check_mismatch(self._classification("12mm"), "12mm")
        self.assertTrue(result["match"])
        self.assertIn("✅", result["message"])

    def test_mismatch(self):
        result = check_mismatch(self._classification("6mm"), "12mm")
        self.assertFalse(result["match"])
        self.assertIn("⚠️", result["message"])

    def test_case_insensitive(self):
        result = check_mismatch(self._classification("12mm"), "12MM")
        self.assertTrue(result["match"])

    def test_mixed_vs_expected(self):
        result = check_mismatch(self._classification("MIXED LOAD"), "20mm")
        self.assertFalse(result["match"])


if __name__ == "__main__":
    unittest.main()
