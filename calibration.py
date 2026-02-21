"""
calibration.py — Ruler detection and px/mm conversion for Q-Vision pipeline.
"""

import cv2
import numpy as np

from config import CALIBRATION_MIN, CALIBRATION_MAX


def detect_ruler(image: np.ndarray) -> float:
    """
    Detect a physical ruler in the image and compute the px/mm ratio.

    The algorithm:
    1. Converts to grayscale and applies Canny edge detection.
    2. Finds contours that look like ruler tick marks (small, narrow rectangles).
    3. Computes pixel distance between the two most separated tick-mark centroids.
    4. Assumes the ruler spans 100 mm between the outermost detected ticks.

    Parameters
    ----------
    image : np.ndarray
        BGR image containing a ruler/scale reference object.

    Returns
    -------
    float
        Pixels per millimetre ratio.

    Raises
    ------
    ValueError
        If the ruler cannot be detected or the computed ratio is out of range.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("Ruler not detected: no contours found in image.")

    # Filter for tick-mark-like contours: small area, moderate aspect ratio
    tick_centroids = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 5 or area > 5000:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        aspect = w / h if h > 0 else 0
        # Tick marks can be very narrow (vertical lines) or horizontal
        if 0.01 <= aspect <= 100:
            cx = x + w // 2
            cy = y + h // 2
            tick_centroids.append((cx, cy))

    if len(tick_centroids) < 2:
        raise ValueError(
            "Ruler not detected: fewer than 2 tick marks found. "
            "Ensure the ruler is visible in the image."
        )

    # Sort by x-coordinate and take the outermost two points
    tick_centroids.sort(key=lambda p: p[0])
    left = tick_centroids[0]
    right = tick_centroids[-1]
    pixel_distance = np.sqrt((right[0] - left[0]) ** 2 + (right[1] - left[1]) ** 2)

    if pixel_distance < 1:
        raise ValueError("Ruler not detected: tick marks are too close together.")

    # Assume the detected span represents 100 mm
    assumed_mm = 100.0
    px_per_mm = pixel_distance / assumed_mm

    if not validate_calibration(px_per_mm):
        raise ValueError(
            f"Calibration out of range: {px_per_mm:.4f} px/mm "
            f"(expected {CALIBRATION_MIN}–{CALIBRATION_MAX})."
        )

    return px_per_mm


def validate_calibration(px_per_mm: float) -> bool:
    """
    Check if the px/mm ratio is within the expected range.

    Parameters
    ----------
    px_per_mm : float
        Pixels per millimetre ratio to validate.

    Returns
    -------
    bool
        True if the ratio is within [CALIBRATION_MIN, CALIBRATION_MAX].
    """
    return CALIBRATION_MIN <= px_per_mm <= CALIBRATION_MAX
