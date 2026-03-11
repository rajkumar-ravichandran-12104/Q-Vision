"""
config.py — All configurable parameters for Q-Vision pipeline.
"""

# ---------------------------------------------------------------------------
# Fixed-camera calibration (recommended for production)
# ---------------------------------------------------------------------------
# Camera is mounted at a fixed distance of 1.5 m from the truck bed.
# Set FIXED_PX_PER_MM to a known value to skip auto ruler detection.
# To calibrate: place a ruler in the frame at 1.5 m, measure pixel distance
# between two marks of known mm apart, divide pixels by mm.
# Set to None to use auto ruler detection instead.
FIXED_CAMERA_DISTANCE_M = 1.5
FIXED_PX_PER_MM = None  # e.g. 8.0 — set after one-time calibration

# Classification rules: material type -> (min_mm, max_mm, min_pct)
CLASSIFICATION_RULES = {
    "6mm":  {"min_mm": 4,  "max_mm": 8,  "min_pct": 80},
    "10mm": {"min_mm": 8,  "max_mm": 12, "min_pct": 80},
    "20mm": {"min_mm": 16, "max_mm": 25, "min_pct": 80},
}

# Minimum contour area in pixels to filter noise
MIN_CONTOUR_AREA = 50

# Number of sampling zones
ZONE_COUNT = 5

# Zone layout: 2x2 grid + 1 center (as fraction of image dimensions)
ZONE_LAYOUT = {
    "top_left":     (0.0,  0.0,  0.5,  0.5),   # (x_start, y_start, x_end, y_end) as fractions
    "top_right":    (0.5,  0.0,  1.0,  0.5),
    "bottom_left":  (0.0,  0.5,  0.5,  1.0),
    "bottom_right": (0.5,  0.5,  1.0,  1.0),
    "center":       (0.25, 0.25, 0.75, 0.75),
}

# Confidence threshold to accept classification
CONFIDENCE_THRESHOLD = 50.0  # percent

# Majority vote: zones that must agree for high-confidence classification
MAJORITY_THRESHOLD = 4

# CLAHE parameters
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID_SIZE = (8, 8)

# Adaptive thresholding parameters
ADAPTIVE_THRESH_BLOCK_SIZE = 31
ADAPTIVE_THRESH_C = 5

# Calibration validity range (px/mm)
CALIBRATION_MIN = 1.0
CALIBRATION_MAX = 20.0

# SQLite database path
DB_PATH = "qvision_logs.db"

# Image resize limit
MAX_IMAGE_DIM = 2000

# Watershed distance transform threshold (fraction of max distance)
WATERSHED_DIST_THRESH = 0.5
