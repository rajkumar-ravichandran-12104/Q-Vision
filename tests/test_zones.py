"""
test_zones.py — Unit tests for zones.py
"""

import unittest

import cv2
import numpy as np

from zones import draw_zones, extract_zones


class TestExtractZones(unittest.TestCase):
    def setUp(self):
        # Create a synthetic 400x600 BGR image with a gradient
        self.h, self.w = 400, 600
        self.image = np.random.randint(0, 255, (self.h, self.w, 3), dtype=np.uint8)

    def test_returns_five_zones(self):
        zones = extract_zones(self.image)
        self.assertEqual(len(zones), 5)

    def test_zone_types_are_ndarray(self):
        zones = extract_zones(self.image)
        for zone in zones:
            self.assertIsInstance(zone, np.ndarray)

    def test_zone_count_parameter_ignored_gracefully(self):
        # zone_count parameter doesn't raise, always returns 5
        zones = extract_zones(self.image, zone_count=3)
        self.assertEqual(len(zones), 5)

    def test_top_left_zone_dimensions(self):
        zones = extract_zones(self.image)
        # Zone 0 is top-left: should be (h//2) x (w//2)
        zone_tl = zones[0]
        expected_h = self.h // 2
        expected_w = self.w // 2
        self.assertEqual(zone_tl.shape[0], expected_h)
        self.assertEqual(zone_tl.shape[1], expected_w)

    def test_top_right_zone_dimensions(self):
        zones = extract_zones(self.image)
        zone_tr = zones[1]
        self.assertEqual(zone_tr.shape[0], self.h // 2)
        self.assertEqual(zone_tr.shape[1], self.w // 2)

    def test_bottom_left_zone_dimensions(self):
        zones = extract_zones(self.image)
        zone_bl = zones[2]
        self.assertEqual(zone_bl.shape[0], self.h // 2)
        self.assertEqual(zone_bl.shape[1], self.w // 2)

    def test_bottom_right_zone_dimensions(self):
        zones = extract_zones(self.image)
        zone_br = zones[3]
        self.assertEqual(zone_br.shape[0], self.h // 2)
        self.assertEqual(zone_br.shape[1], self.w // 2)

    def test_center_zone_is_smaller_than_full(self):
        zones = extract_zones(self.image)
        center = zones[4]
        self.assertLess(center.shape[0], self.h)
        self.assertLess(center.shape[1], self.w)

    def test_center_zone_is_half_dimensions(self):
        zones = extract_zones(self.image)
        center = zones[4]
        # Center zone is 25%-75% in each dimension = 50% of h and w
        self.assertEqual(center.shape[0], self.h // 2)
        self.assertEqual(center.shape[1], self.w // 2)

    def test_zones_contain_image_data(self):
        zones = extract_zones(self.image)
        for zone in zones:
            self.assertGreater(zone.size, 0)

    def test_works_with_grayscale(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        zones = extract_zones(gray)
        self.assertEqual(len(zones), 5)


class TestDrawZones(unittest.TestCase):
    def setUp(self):
        self.image = np.zeros((400, 600, 3), dtype=np.uint8)

    def test_returns_ndarray(self):
        result = draw_zones(self.image)
        self.assertIsInstance(result, np.ndarray)

    def test_does_not_modify_original(self):
        original = self.image.copy()
        draw_zones(self.image)
        np.testing.assert_array_equal(self.image, original)

    def test_output_has_same_shape(self):
        result = draw_zones(self.image)
        self.assertEqual(result.shape, self.image.shape)

    def test_output_differs_from_blank(self):
        result = draw_zones(self.image)
        # Annotations should have changed at least some pixels
        self.assertFalse(np.array_equal(result, self.image))


if __name__ == "__main__":
    unittest.main()
