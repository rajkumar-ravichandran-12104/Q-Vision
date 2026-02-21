"""
utils.py — Shared utility functions for Q-Vision pipeline.
"""

import cv2
import numpy as np

from config import MAX_IMAGE_DIM, MIN_CONTOUR_AREA


def load_image(path: str) -> np.ndarray:
    """Load and validate an image from the given file path."""
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(f"Could not load image: {path}")
    return image


def resize_if_needed(image: np.ndarray, max_dim: int = MAX_IMAGE_DIM) -> np.ndarray:
    """Resize image proportionally if its largest dimension exceeds max_dim."""
    h, w = image.shape[:2]
    largest = max(h, w)
    if largest <= max_dim:
        return image
    scale = max_dim / largest
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def draw_contours_with_labels(
    image: np.ndarray,
    particles: list,
    px_per_mm: float = 1.0,
) -> np.ndarray:
    """
    Annotate image with measured diameters for each particle.

    Parameters
    ----------
    image : np.ndarray
        BGR image to annotate.
    particles : list[dict]
        List of dicts with keys 'contour' and 'diameter_mm'.
    px_per_mm : float
        Pixels per millimetre (used for centroid calculation only).

    Returns
    -------
    np.ndarray
        Annotated copy of the image.
    """
    annotated = image.copy()
    for p in particles:
        contour = p.get("contour")
        diameter_mm = p.get("diameter_mm", 0)
        if contour is None:
            continue
        area = cv2.contourArea(contour)
        if area < MIN_CONTOUR_AREA:
            continue
        M = cv2.moments(contour)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        cv2.drawContours(annotated, [contour], -1, (0, 255, 0), 1)
        label = f"{diameter_mm:.1f}mm"
        cv2.putText(
            annotated,
            label,
            (cx - 15, cy),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )
    return annotated
