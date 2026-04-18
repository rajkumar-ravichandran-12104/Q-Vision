"""
texture_classifier.py — GLCM-based texture analysis for M-Sand detection.

M-Sand grains (0.15–4.75mm) are too small to segment individually at 30cm
camera height. Instead, we detect M-Sand by its distinctive fine, uniform
texture using Gray-Level Co-occurrence Matrix (GLCM) features and a
contour-count heuristic.
"""

import cv2
import numpy as np

from config import (
    MSAND_HOMOGENEITY_THRESH,
    MSAND_MAX_CONTOUR_COUNT,
    MSAND_CONTRAST_THRESH,
    MSAND_ENERGY_THRESH,
)


def compute_glcm(gray: np.ndarray, distances=(1, 3), angles=(0, np.pi / 4, np.pi / 2)) -> np.ndarray:
    """
    Compute a normalized Gray-Level Co-occurrence Matrix.

    Uses quantized grayscale levels (64 bins) for efficiency.

    Parameters
    ----------
    gray : np.ndarray
        Grayscale image (uint8).
    distances : tuple
        Pixel distances for co-occurrence pairs.
    angles : tuple
        Angles in radians for co-occurrence directions.

    Returns
    -------
    np.ndarray
        Normalized GLCM matrix (64×64), averaged across all distance/angle combos.
    """
    levels = 64
    quantized = (gray // 4).astype(np.uint8)  # 256 → 64 levels

    glcm = np.zeros((levels, levels), dtype=np.float64)

    rows, cols = quantized.shape
    for d in distances:
        for angle in angles:
            dx = int(round(d * np.cos(angle)))
            dy = int(round(-d * np.sin(angle)))

            # Compute valid coordinate ranges
            r_start = max(0, -dy)
            r_end = min(rows, rows - dy)
            c_start = max(0, -dx)
            c_end = min(cols, cols - dx)

            if r_start >= r_end or c_start >= c_end:
                continue

            region_i = quantized[r_start:r_end, c_start:c_end]
            region_j = quantized[r_start + dy:r_end + dy, c_start + dx:c_end + dx]

            # Accumulate co-occurrences
            for i_val, j_val in zip(region_i.ravel(), region_j.ravel()):
                glcm[i_val, j_val] += 1

    # Symmetric and normalize
    glcm = glcm + glcm.T
    total = glcm.sum()
    if total > 0:
        glcm /= total

    return glcm


def glcm_features(glcm: np.ndarray) -> dict:
    """
    Extract texture features from a GLCM matrix.

    Parameters
    ----------
    glcm : np.ndarray
        Normalized GLCM (NxN).

    Returns
    -------
    dict
        Keys: 'homogeneity', 'contrast', 'energy', 'correlation'
    """
    levels = glcm.shape[0]
    i_idx, j_idx = np.meshgrid(np.arange(levels), np.arange(levels), indexing='ij')

    diff = np.abs(i_idx - j_idx).astype(np.float64)

    homogeneity = np.sum(glcm / (1.0 + diff))
    contrast = np.sum(glcm * (diff ** 2))
    energy = np.sum(glcm ** 2)

    # Correlation
    mu_i = np.sum(i_idx * glcm)
    mu_j = np.sum(j_idx * glcm)
    sigma_i = np.sqrt(np.sum(((i_idx - mu_i) ** 2) * glcm))
    sigma_j = np.sqrt(np.sum(((j_idx - mu_j) ** 2) * glcm))

    if sigma_i > 0 and sigma_j > 0:
        correlation = np.sum(((i_idx - mu_i) * (j_idx - mu_j) * glcm)) / (sigma_i * sigma_j)
    else:
        correlation = 0.0

    return {
        "homogeneity": round(float(homogeneity), 4),
        "contrast": round(float(contrast), 4),
        "energy": round(float(energy), 6),
        "correlation": round(float(correlation), 4),
    }


def detect_msand(zone_image: np.ndarray, contour_count: int) -> dict:
    """
    Determine if a zone image contains M-Sand based on texture features
    and the number of segmented contours.

    Parameters
    ----------
    zone_image : np.ndarray
        BGR or grayscale zone image.
    contour_count : int
        Number of contours found by the stone segmentation pipeline for this zone.

    Returns
    -------
    dict
        Keys:
        - 'is_msand' (bool): True if zone is classified as M-Sand
        - 'homogeneity' (float): GLCM homogeneity value
        - 'contrast' (float): GLCM contrast value
        - 'contour_count' (int): passed-through contour count
        - 'confidence' (float): 0-100 confidence score
    """
    if len(zone_image.shape) == 3:
        gray = cv2.cvtColor(zone_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = zone_image.copy()

    # Resize to ~256px for fast GLCM computation
    h, w = gray.shape
    scale = 256 / max(h, w)
    small = cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    glcm = compute_glcm(small)
    features = glcm_features(glcm)

    homogeneity = features["homogeneity"]
    contrast = features["contrast"]

    # Decision: M-Sand has LOW homogeneity + HIGH contrast + LOW energy
    # (many tiny sharp grain edges vs smooth stone surfaces)
    texture_score = (
        homogeneity <= MSAND_HOMOGENEITY_THRESH
        and contrast >= MSAND_CONTRAST_THRESH
        and features["energy"] <= MSAND_ENERGY_THRESH
    )
    contour_score = contour_count <= MSAND_MAX_CONTOUR_COUNT

    is_msand = texture_score and contour_score

    # Confidence: how strongly the signals agree
    if is_msand:
        h_margin = (MSAND_HOMOGENEITY_THRESH - homogeneity) / max(MSAND_HOMOGENEITY_THRESH, 0.01)
        c_margin = (contrast - MSAND_CONTRAST_THRESH) / max(MSAND_CONTRAST_THRESH, 0.01)
        confidence = min(100.0, 60.0 + 20.0 * h_margin + 20.0 * c_margin)
    else:
        confidence = 0.0

    return {
        "is_msand": is_msand,
        "homogeneity": homogeneity,
        "contrast": contrast,
        "energy": features["energy"],
        "correlation": features["correlation"],
        "contour_count": contour_count,
        "confidence": round(confidence, 1),
    }
