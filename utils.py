"""
utils.py — Shared utility functions for Q-Vision pipeline.
"""

import cv2
import numpy as np
from PIL import Image, ExifTags

from config import MAX_IMAGE_DIM, MIN_CONTOUR_AREA


def _apply_exif_orientation(path: str) -> np.ndarray:
    """Read an image and apply EXIF orientation (handles iPhone photos)."""
    pil_img = Image.open(path)
    try:
        exif = pil_img._getexif()
        if exif:
            orientation_key = next(
                (k for k, v in ExifTags.TAGS.items() if v == "Orientation"), None
            )
            if orientation_key and orientation_key in exif:
                orientation = exif[orientation_key]
                if orientation == 3:
                    pil_img = pil_img.rotate(180, expand=True)
                elif orientation == 6:
                    pil_img = pil_img.rotate(270, expand=True)
                elif orientation == 8:
                    pil_img = pil_img.rotate(90, expand=True)
    except (AttributeError, StopIteration):
        pass
    arr = np.array(pil_img)
    # PIL gives RGB; OpenCV uses BGR
    if len(arr.shape) == 3 and arr.shape[2] == 3:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    elif len(arr.shape) == 3 and arr.shape[2] == 4:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    return arr


def load_image(path: str) -> np.ndarray:
    """Load and validate an image, applying EXIF orientation if present."""
    try:
        image = _apply_exif_orientation(path)
    except Exception:
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
