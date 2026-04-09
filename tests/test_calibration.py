"""
test_calibration.py — Unit tests for calibration.py
"""

import math
import unittest

import numpy as np

from calibration import detect_ruler, validate_calibration


class TestValidateCalibration(unittest.TestCase):
    def test_valid_ratio_lower_bound(self):
        self.assertTrue(validate_calibration(2.0))

    def test_valid_ratio_upper_bound(self):
        self.assertTrue(validate_calibration(10.0))

    def test_valid_ratio_middle(self):
        self.assertTrue(validate_calibration(5.0))

    def test_invalid_ratio_too_low(self):
        self.assertFalse(validate_calibration(0.9))

    def test_invalid_ratio_too_high(self):
        self.assertFalse(validate_calibration(20.1))

    def test_invalid_ratio_zero(self):
        self.assertFalse(validate_calibration(0.0))

    def test_invalid_ratio_negative(self):
        self.assertFalse(validate_calibration(-1.0))


class TestDetectRuler(unittest.TestCase):
    def _make_ruler_image(self, width=600, height=200, tick_spacing_px=500):
        """
        Create a synthetic image with two thin vertical tick marks separated by
        tick_spacing_px pixels so that the calibration can be verified.
        """
        img = np.zeros((height, width, 3), dtype=np.uint8)
        # Draw two white vertical tick marks
        x1 = (width - tick_spacing_px) // 2
        x2 = x1 + tick_spacing_px
        for x in (x1, x2):
            img[height // 4 : 3 * height // 4, x : x + 3] = 255
        return img, tick_spacing_px

    def test_detect_ruler_returns_float(self):
        img, _ = self._make_ruler_image(tick_spacing_px=500)
        px_per_mm = detect_ruler(img)
        self.assertIsInstance(px_per_mm, float)

    def test_detect_ruler_value_in_range(self):
        img, spacing = self._make_ruler_image(tick_spacing_px=500)
        px_per_mm = detect_ruler(img)
        # spacing / 100 mm should be approximately correct
        expected = spacing / 100.0  # 5.0
        self.assertAlmostEqual(px_per_mm, expected, delta=1.5)

    def test_detect_ruler_raises_on_blank_image(self):
        blank = np.zeros((100, 100, 3), dtype=np.uint8)
        with self.assertRaises(ValueError):
            detect_ruler(blank)


if __name__ == "__main__":
    unittest.main()
