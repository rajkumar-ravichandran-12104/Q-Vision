"""
test_measurement.py — Unit tests for measurement.py
"""

import math
import unittest

import cv2
import numpy as np

from measurement import compute_distribution, measure_particles


def _circle_contour(radius_px: int, cx: int = 50, cy: int = 50) -> np.ndarray:
    """Return a synthetic circular contour with the given radius."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    cv2.circle(mask, (cx, cy), radius_px, 255, -1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours[0]


class TestMeasureParticles(unittest.TestCase):
    def test_single_circle_diameter(self):
        radius = 20  # px
        contour = _circle_contour(radius)
        px_per_mm = 4.0
        particles = measure_particles([contour], px_per_mm)
        self.assertEqual(len(particles), 1)
        p = particles[0]
        # Expected: d = 2*sqrt(area/pi) / px_per_mm
        area_px = cv2.contourArea(contour)
        expected_d = 2.0 * math.sqrt(area_px / math.pi) / px_per_mm
        self.assertAlmostEqual(p["diameter_mm"], expected_d, places=2)

    def test_tiny_contour_filtered(self):
        """Contour with area < MIN_CONTOUR_AREA should be filtered out."""
        mask = np.zeros((50, 50), dtype=np.uint8)
        cv2.circle(mask, (25, 25), 1, 255, -1)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        particles = measure_particles(contours, 5.0)
        # Area of r=1 circle is ~pi ≈ 3.14, less than MIN_CONTOUR_AREA=10
        self.assertEqual(len(particles), 0)

    def test_multiple_contours(self):
        c1 = _circle_contour(20, cx=25, cy=25)
        c2 = _circle_contour(15, cx=75, cy=75)
        particles = measure_particles([c1, c2], px_per_mm=5.0)
        self.assertEqual(len(particles), 2)
        # Larger contour should have larger diameter
        self.assertGreater(particles[0]["diameter_mm"], particles[1]["diameter_mm"])

    def test_particle_has_required_keys(self):
        contour = _circle_contour(20)
        particles = measure_particles([contour], px_per_mm=5.0)
        self.assertIn("diameter_mm", particles[0])
        self.assertIn("area_px", particles[0])
        self.assertIn("contour", particles[0])

    def test_empty_contours(self):
        particles = measure_particles([], px_per_mm=5.0)
        self.assertEqual(particles, [])


class TestComputeDistribution(unittest.TestCase):
    def test_empty_diameters(self):
        result = compute_distribution([])
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["pct_6mm"], 0.0)

    def test_all_6mm_class(self):
        # All diameters within 4–8 mm
        diameters = [5.0, 5.5, 6.0, 6.5, 7.0]
        result = compute_distribution(diameters)
        self.assertEqual(result["count"], 5)
        self.assertEqual(result["pct_6mm"], 100.0)
        self.assertEqual(result["pct_10mm"], 0.0)
        self.assertEqual(result["pct_20mm"], 0.0)

    def test_all_10mm_class(self):
        # All in 8-14mm display bin
        diameters = [9.0, 10.0, 11.0, 12.0, 13.0]
        result = compute_distribution(diameters)
        self.assertEqual(result["pct_10mm"], 100.0)
        self.assertEqual(result["pct_6mm"], 0.0)

    def test_all_20mm_class(self):
        # All in 18-50mm display bin
        diameters = [19.0, 20.0, 25.0, 30.0, 35.0]
        result = compute_distribution(diameters)
        self.assertEqual(result["pct_20mm"], 100.0)

    def test_mixed_distribution(self):
        # 2 in 6mm (0-8), 2 in 10mm (8-14), 1 oversize (>50)
        diameters = [5.0, 6.0, 9.0, 12.0, 55.0]
        result = compute_distribution(diameters)
        self.assertEqual(result["pct_6mm"], 40.0)
        self.assertEqual(result["pct_10mm"], 40.0)
        self.assertEqual(result["pct_other"], 20.0)

    def test_stats_keys_present(self):
        diameters = [5.0, 10.0, 20.0]
        result = compute_distribution(diameters)
        for key in ("min_mm", "max_mm", "mean_mm", "median_mm", "std_mm"):
            self.assertIn(key, result)

    def test_single_value(self):
        result = compute_distribution([6.0])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["min_mm"], 6.0)
        self.assertEqual(result["max_mm"], 6.0)


if __name__ == "__main__":
    unittest.main()
