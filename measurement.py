"""
measurement.py — Compute equivalent particle diameters and size distribution statistics.
"""

import math
import numpy as np
import cv2

from config import MIN_CONTOUR_AREA, CLASSIFICATION_RULES, MAX_PARTICLE_DIAMETER_MM


def measure_particles(contours: list, px_per_mm: float) -> list:
    """
    Measure the equivalent diameter (in mm) of each stone particle contour.

    For each contour:
    - Compute contour area in pixels.
    - Skip contours smaller than MIN_CONTOUR_AREA.
    - Equivalent diameter: d = 2 * sqrt(area / pi)
    - Convert pixel diameter to mm using px_per_mm.

    Parameters
    ----------
    contours : list
        List of contours from OpenCV (e.g. from watershed segmentation).
    px_per_mm : float
        Pixels per millimetre calibration ratio.

    Returns
    -------
    list[dict]
        Each dict has keys: 'diameter_mm', 'area_px', 'contour'.
    """
    particles = []
    for cnt in contours:
        area_px = cv2.contourArea(cnt)
        if area_px < MIN_CONTOUR_AREA:
            continue
        diameter_px = 2.0 * math.sqrt(area_px / math.pi)
        diameter_mm = diameter_px / px_per_mm
        if diameter_mm > MAX_PARTICLE_DIAMETER_MM:
            continue  # skip ruler / artifacts
        particles.append(
            {
                "diameter_mm": diameter_mm,
                "area_px": area_px,
                "contour": cnt,
            }
        )
    return particles


def compute_distribution(diameters_mm: list) -> dict:
    """
    Compute size distribution statistics from a list of particle diameters.

    Returns min, max, mean, median, std and percentage of particles falling
    into each aggregate size class (6 mm, 10 mm, 20 mm).

    Parameters
    ----------
    diameters_mm : list[float]
        Particle diameters in millimetres.

    Returns
    -------
    dict
        Keys:
        - 'count': total particle count
        - 'min_mm', 'max_mm', 'mean_mm', 'median_mm', 'std_mm': basic stats
        - 'pct_6mm', 'pct_10mm', 'pct_20mm', 'pct_other': percentage in each class
    """
    if not diameters_mm:
        return {
            "count": 0,
            "min_mm": 0.0,
            "max_mm": 0.0,
            "mean_mm": 0.0,
            "median_mm": 0.0,
            "std_mm": 0.0,
            "pct_6mm": 0.0,
            "pct_10mm": 0.0,
            "pct_12mm": 0.0,
            "pct_20mm": 0.0,
            "pct_other": 0.0,
            "diameters": [],
        }

    arr = np.array(diameters_mm, dtype=float)
    total = len(arr)

    # Non-overlapping display bins for distribution percentages
    display_bins = {
        "6mm":  (0, 8),
        "10mm": (8, 14),
        "12mm": (14, 18),
        "20mm": (18, 50),
    }
    counts = {}
    for key, (lo, hi) in display_bins.items():
        counts[key] = int(np.sum((arr >= lo) & (arr < hi)))

    in_class = sum(counts.values())
    other = total - in_class

    def pct(n):
        return round(100.0 * n / total, 2) if total > 0 else 0.0

    return {
        "count": total,
        "min_mm": round(float(arr.min()), 3),
        "max_mm": round(float(arr.max()), 3),
        "mean_mm": round(float(arr.mean()), 3),
        "median_mm": round(float(np.median(arr)), 3),
        "std_mm": round(float(arr.std()), 3),
        "pct_6mm": pct(counts.get("6mm", 0)),
        "pct_10mm": pct(counts.get("10mm", 0)),
        "pct_12mm": pct(counts.get("12mm", 0)),
        "pct_20mm": pct(counts.get("20mm", 0)),
        "pct_other": pct(other),
        "diameters": diameters_mm,
    }
