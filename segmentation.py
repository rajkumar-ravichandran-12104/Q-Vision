"""
segmentation.py — Preprocessing, adaptive thresholding, morphology, and watershed
segmentation of stone particles for Q-Vision pipeline.
"""

import cv2
import numpy as np

from config import (
    CLAHE_CLIP_LIMIT,
    CLAHE_TILE_GRID_SIZE,
    ADAPTIVE_THRESH_BLOCK_SIZE,
    ADAPTIVE_THRESH_C,
    WATERSHED_DIST_THRESH,
)


def preprocess(image: np.ndarray) -> np.ndarray:
    """
    Prepare an image for segmentation.

    Steps:
    1. Convert to grayscale.
    2. Apply CLAHE for contrast enhancement.
    3. Apply bilateral filter for edge-preserving denoising.

    Parameters
    ----------
    image : np.ndarray
        BGR or grayscale input image.

    Returns
    -------
    np.ndarray
        Preprocessed grayscale image.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    clahe = cv2.createCLAHE(
        clipLimit=CLAHE_CLIP_LIMIT,
        tileGridSize=CLAHE_TILE_GRID_SIZE,
    )
    enhanced = clahe.apply(gray)
    # Gaussian blur to smooth stone surface texture before thresholding
    # (5,5) kernel preserves 6mm stone boundaries while still removing noise
    denoised = cv2.GaussianBlur(enhanced, (5, 5), 0)
    return denoised


def segment_stones(preprocessed_image: np.ndarray) -> np.ndarray:
    """
    Produce a binary mask isolating stone particles.

    Steps:
    1. Adaptive Gaussian thresholding.
    2. Morphological opening to remove small noise.
    3. Morphological closing to fill small holes.

    Parameters
    ----------
    preprocessed_image : np.ndarray
        Grayscale preprocessed image from :func:`preprocess`.

    Returns
    -------
    np.ndarray
        Binary mask (uint8, values 0 or 255).
    """
    # Use Otsu thresholding — works for both light-on-dark and dark-on-light
    _, binary = cv2.threshold(
        preprocessed_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Auto-detect polarity: stones should fill 15-75% of image.
    # If foreground is too small, stones are likely bright (light-on-dark) and
    # Otsu already marks them white.  If foreground is too large, invert.
    fg_ratio = (binary > 0).sum() / binary.size
    if fg_ratio > 0.75:
        binary = cv2.bitwise_not(binary)

    # (5,5) kernel with 2 iterations: removes inter-stone texture noise
    # (fixes 12mm "mixed" misclass) while still preserving 6mm stones (~327 px²)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=2)
    return closed


def separate_touching_stones(binary_mask: np.ndarray) -> tuple:
    """
    Separate touching/overlapping stone particles using the watershed algorithm.

    Steps:
    1. Distance transform on the binary mask.
    2. Threshold distance map to find definite foreground (local maxima).
    3. Dilate binary mask for definite background.
    4. Compute unknown region and assign markers.
    5. Run watershed on a 3-channel placeholder image.
    6. Extract contours from each labelled region.

    Parameters
    ----------
    binary_mask : np.ndarray
        Binary mask (uint8) from :func:`segment_stones`.

    Returns
    -------
    tuple[list, np.ndarray]
        (list of contours, labelled image from watershed)
    """
    # Distance transform
    dist = cv2.distanceTransform(binary_mask, cv2.DIST_L2, 5)

    # Threshold to find sure foreground
    _, sure_fg = cv2.threshold(
        dist,
        WATERSHED_DIST_THRESH * dist.max(),
        255,
        cv2.THRESH_BINARY,
    )
    sure_fg = np.uint8(sure_fg)

    # Sure background via dilation
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    sure_bg = cv2.dilate(binary_mask, kernel, iterations=3)

    # Unknown region
    unknown = cv2.subtract(sure_bg, sure_fg)

    # Label markers
    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    # Watershed needs a 3-channel uint8 image
    placeholder = cv2.cvtColor(binary_mask, cv2.COLOR_GRAY2BGR)
    markers = cv2.watershed(placeholder, markers)

    # Extract contours from each unique label (skip background=-1 and border=1)
    contours = []
    labels = np.unique(markers)
    for label in labels:
        if label <= 1:
            continue
        mask = np.zeros_like(binary_mask)
        mask[markers == label] = 255
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours.extend(cnts)

    return contours, markers
