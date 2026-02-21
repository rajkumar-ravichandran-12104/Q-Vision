"""
zones.py — Extract 5 sampling zones from the truck bed image.
"""

import cv2
import numpy as np

from config import ZONE_COUNT, ZONE_LAYOUT


def extract_zones(image: np.ndarray, zone_count: int = ZONE_COUNT) -> list:
    """
    Divide the image into 5 sampling zones:
      - Zone 1: top-left quadrant
      - Zone 2: top-right quadrant
      - Zone 3: bottom-left quadrant
      - Zone 4: bottom-right quadrant
      - Zone 5: center region (overlapping)

    Parameters
    ----------
    image : np.ndarray
        Input image (BGR or grayscale).
    zone_count : int
        Expected number of zones (kept for API compatibility; always returns 5).

    Returns
    -------
    list[np.ndarray]
        List of cropped zone images.
    """
    h, w = image.shape[:2]
    zones = []
    for name, (xs, ys, xe, ye) in ZONE_LAYOUT.items():
        x1 = int(xs * w)
        y1 = int(ys * h)
        x2 = int(xe * w)
        y2 = int(ye * h)
        zone_crop = image[y1:y2, x1:x2]
        zones.append(zone_crop)
    return zones


def draw_zones(image: np.ndarray) -> np.ndarray:
    """
    Draw zone boundaries on a copy of the image for visualization.

    Parameters
    ----------
    image : np.ndarray
        Input BGR image.

    Returns
    -------
    np.ndarray
        Image with colored zone rectangles drawn on it.
    """
    h, w = image.shape[:2]
    output = image.copy()
    colors = [
        (255, 0, 0),    # Blue  — top-left
        (0, 255, 0),    # Green — top-right
        (0, 0, 255),    # Red   — bottom-left
        (255, 255, 0),  # Cyan  — bottom-right
        (255, 0, 255),  # Magenta — center
    ]
    for i, (name, (xs, ys, xe, ye)) in enumerate(ZONE_LAYOUT.items()):
        x1 = int(xs * w)
        y1 = int(ys * h)
        x2 = int(xe * w)
        y2 = int(ye * h)
        color = colors[i % len(colors)]
        cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            output,
            f"Z{i + 1}:{name}",
            (x1 + 5, y1 + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
            cv2.LINE_AA,
        )
    return output
