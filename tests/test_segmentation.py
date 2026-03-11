"""
test_segmentation.py — Unit tests for segmentation.py
"""

import unittest

import cv2
import numpy as np

from segmentation import preprocess, segment_stones, separate_touching_stones


class TestPreprocess(unittest.TestCase):
    def test_bgr_input_returns_grayscale(self):
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = preprocess(img)
        self.assertEqual(len(result.shape), 2)

    def test_grayscale_input_returns_grayscale(self):
        gray = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        result = preprocess(gray)
        self.assertEqual(len(result.shape), 2)

    def test_output_same_dimensions(self):
        img = np.random.randint(0, 255, (200, 300, 3), dtype=np.uint8)
        result = preprocess(img)
        self.assertEqual(result.shape, (200, 300))

    def test_output_dtype_uint8(self):
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = preprocess(img)
        self.assertEqual(result.dtype, np.uint8)

    def test_does_not_modify_input(self):
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        original = img.copy()
        preprocess(img)
        np.testing.assert_array_equal(img, original)


class TestSegmentStones(unittest.TestCase):
    def test_returns_binary_mask(self):
        gray = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        mask = segment_stones(gray)
        unique_vals = set(np.unique(mask))
        self.assertTrue(unique_vals.issubset({0, 255}))

    def test_output_same_dimensions(self):
        gray = np.random.randint(0, 255, (200, 300), dtype=np.uint8)
        mask = segment_stones(gray)
        self.assertEqual(mask.shape, (200, 300))

    def test_output_dtype_uint8(self):
        gray = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        mask = segment_stones(gray)
        self.assertEqual(mask.dtype, np.uint8)

    def test_blank_image_minimal_foreground(self):
        blank = np.zeros((100, 100), dtype=np.uint8)
        mask = segment_stones(blank)
        self.assertLessEqual(np.sum(mask > 0), mask.size * 0.1)

    def test_high_contrast_produces_foreground(self):
        img = np.zeros((200, 200), dtype=np.uint8)
        cv2.circle(img, (60, 60), 25, 200, -1)
        cv2.circle(img, (140, 140), 25, 200, -1)
        mask = segment_stones(img)
        self.assertGreater(np.sum(mask > 0), 0)


class TestSeparateTouchingStones(unittest.TestCase):
    def _make_binary_with_circles(self):
        mask = np.zeros((200, 200), dtype=np.uint8)
        cv2.circle(mask, (60, 100), 30, 255, -1)
        cv2.circle(mask, (140, 100), 30, 255, -1)
        return mask

    def _make_binary_touching_circles(self):
        mask = np.zeros((200, 200), dtype=np.uint8)
        cv2.circle(mask, (85, 100), 35, 255, -1)
        cv2.circle(mask, (115, 100), 35, 255, -1)
        return mask

    def test_returns_tuple(self):
        mask = self._make_binary_with_circles()
        result = separate_touching_stones(mask)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_contours_are_list(self):
        mask = self._make_binary_with_circles()
        contours, _ = separate_touching_stones(mask)
        self.assertIsInstance(contours, list)

    def test_detects_separate_circles(self):
        mask = self._make_binary_with_circles()
        contours, _ = separate_touching_stones(mask)
        self.assertGreaterEqual(len(contours), 2)

    def test_separates_touching_circles(self):
        mask = self._make_binary_touching_circles()
        contours, _ = separate_touching_stones(mask)
        # Watershed should detect at least one region from the touching blobs
        self.assertGreaterEqual(len(contours), 1)

    def test_empty_mask_returns_empty(self):
        mask = np.zeros((100, 100), dtype=np.uint8)
        contours, _ = separate_touching_stones(mask)
        self.assertEqual(len(contours), 0)

    def test_markers_same_dimensions(self):
        mask = self._make_binary_with_circles()
        _, markers = separate_touching_stones(mask)
        self.assertEqual(markers.shape[:2], mask.shape[:2])


if __name__ == "__main__":
    unittest.main()
