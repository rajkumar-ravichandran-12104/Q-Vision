"""
main.py — CLI entry point for the Q-Vision aggregate size verification pipeline.
"""

import argparse
import os
import sys

from calibration import detect_ruler
from classification import check_mismatch, classify_load, classify_zone
from logger import log_result
from measurement import compute_distribution, measure_particles
from segmentation import preprocess, segment_stones, separate_touching_stones
from utils import load_image, resize_if_needed
from zones import extract_zones


# ---------------------------------------------------------------------------
# Colour helpers (ANSI codes; gracefully degraded on Windows without ANSI)
# ---------------------------------------------------------------------------
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def _color(text: str, code: str) -> str:
    if sys.stdout.isatty():
        return f"{code}{text}{RESET}"
    return text


def run_pipeline(image_path: str, truck_id: str, expected_material: str = None, manual_px_per_mm: float = None) -> dict:
    """
    Run the full Q-Vision classification pipeline on a single image.

    Parameters
    ----------
    image_path : str
        Path to the truck bed image.
    truck_id : str
        Identifier for the truck.
    expected_material : str, optional
        Expected aggregate grade from invoice (e.g. "10mm").
    manual_px_per_mm : float, optional
        Manual override for px/mm calibration. If provided, skips ruler detection.
        If not provided, uses FIXED_PX_PER_MM from config (if set), then falls
        back to auto ruler detection.

    Returns
    -------
    dict
        Full result including classification, confidence, zone details, and
        optional mismatch information.
    """
    from config import FIXED_PX_PER_MM, RULER_CROP_TOP

    # 1. Load and resize image
    image = load_image(image_path)
    image = resize_if_needed(image)

    # 1b. Crop out ruler area from top of image (if present)
    if RULER_CROP_TOP > 0:
        h = image.shape[0]
        crop_rows = int(h * RULER_CROP_TOP)
        image = image[crop_rows:, :, :]

    # 2. Determine px_per_mm (priority: manual > config fixed > auto ruler)
    if manual_px_per_mm and manual_px_per_mm > 0:
        px_per_mm = manual_px_per_mm
        print(_color(f"  Calibration (manual): {px_per_mm:.4f} px/mm", GREEN))
    elif FIXED_PX_PER_MM and FIXED_PX_PER_MM > 0:
        px_per_mm = FIXED_PX_PER_MM
        print(_color(f"  Calibration (fixed camera): {px_per_mm:.4f} px/mm", GREEN))
    else:
        try:
            px_per_mm = detect_ruler(image)
            print(_color(f"  Calibration (auto ruler): {px_per_mm:.4f} px/mm", GREEN))
        except ValueError as exc:
            print(_color(f"  [WARNING] {exc}. Using fallback 5.0 px/mm.", YELLOW))
            px_per_mm = 5.0  # sensible default for quarry images

    # 3. Extract 5 zones
    zones = extract_zones(image)

    # 4. Process each zone
    zone_results = []
    all_diameters = []
    for idx, zone in enumerate(zones):
        preprocessed = preprocess(zone)
        binary_mask = segment_stones(preprocessed)
        contours, _ = separate_touching_stones(binary_mask)
        particles = measure_particles(contours, px_per_mm)
        diameters = [p["diameter_mm"] for p in particles]
        all_diameters.extend(diameters)
        distribution = compute_distribution(diameters)
        zone_result = classify_zone(distribution)
        zone_results.append(zone_result)
        print(
            f"  Zone {idx + 1}: label={zone_result['label']!r:10s} "
            f"conf={zone_result['confidence_pct']:.1f}%  "
            f"particles={distribution['count']}"
        )

    # 5. Overall classification via majority vote
    classification = classify_load(zone_results)
    classification["distribution"] = compute_distribution(all_diameters)

    # 6. Check mismatch against invoice
    mismatch = None
    if expected_material:
        mismatch = check_mismatch(classification, expected_material)
        classification["mismatch"] = mismatch

    # 7. Log result
    log_result(truck_id, image_path, classification)

    # Include px_per_mm so callers (e.g. dashboard) can reuse the calibrated value
    classification["px_per_mm"] = px_per_mm

    return classification


def print_result(result: dict) -> None:
    """Print the classification result to the console with coloured output."""
    label = result["label"]
    confidence = result["confidence"]
    warning = result.get("warning", "")
    is_mixed = result.get("is_mixed", False)
    dist = result.get("distribution", {})

    print()
    print(_color("=" * 60, BOLD))
    if is_mixed:
        print(_color(f"  CLASSIFICATION : {label}", RED))
    else:
        print(_color(f"  CLASSIFICATION : {label}", GREEN))
    print(f"  CONFIDENCE     : {confidence:.1f}%")
    if warning:
        print(_color(f"  WARNING        : {warning}", YELLOW))

    if dist.get("count", 0) > 0:
        print()
        print("  SIZE DISTRIBUTION SUMMARY")
        print(f"    Total particles : {dist['count']}")
        print(f"    Mean diameter   : {dist['mean_mm']:.2f} mm")
        print(f"    Std deviation   : {dist['std_mm']:.2f} mm")
        print(f"    Range           : {dist['min_mm']:.2f} – {dist['max_mm']:.2f} mm")
        print(f"    % in 0-8mm   (6mm class)  : {dist['pct_6mm']:.1f}%")
        print(f"    % in 8-14mm  (10mm class) : {dist['pct_10mm']:.1f}%")
        print(f"    % in 14-18mm (12mm class) : {dist['pct_12mm']:.1f}%")
        print(f"    % in 18-50mm (20mm class) : {dist['pct_20mm']:.1f}%")
        print(f"    % other (oversize)         : {dist['pct_other']:.1f}%")

    if "mismatch" in result:
        print()
        mm = result["mismatch"]
        color = GREEN if mm["match"] else RED
        print(_color(f"  INVOICE CHECK  : {mm['message']}", color))

    print(_color("=" * 60, BOLD))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Q-Vision: AI-Based Aggregate Size Verification System"
    )
    parser.add_argument("image", nargs="?", help="Path to truck bed image")
    parser.add_argument(
        "--truck-id", default="TRUCK-001", help="Truck identifier (default: TRUCK-001)"
    )
    parser.add_argument(
        "--expected",
        default=None,
        help="Expected material grade from invoice (e.g. 10mm)",
    )
    parser.add_argument(
        "--batch",
        default=None,
        metavar="DIRECTORY",
        help="Batch mode: process all images in a directory",
    )
    args = parser.parse_args()

    if args.batch:
        # Batch mode
        if not os.path.isdir(args.batch):
            print(_color(f"Error: {args.batch!r} is not a directory.", RED))
            sys.exit(1)
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}
        images = [
            os.path.join(args.batch, f)
            for f in sorted(os.listdir(args.batch))
            if os.path.splitext(f)[1].lower() in image_extensions
        ]
        if not images:
            print(_color(f"No images found in {args.batch!r}.", YELLOW))
            sys.exit(0)
        for i, img_path in enumerate(images):
            print(f"\n[{i + 1}/{len(images)}] Processing: {img_path}")
            try:
                result = run_pipeline(img_path, args.truck_id, args.expected)
                print_result(result)
            except Exception as exc:
                print(_color(f"  Error processing {img_path}: {exc}", RED))
    elif args.image:
        if not os.path.isfile(args.image):
            print(_color(f"Error: image file {args.image!r} not found.", RED))
            sys.exit(1)
        print(f"\nProcessing: {args.image}")
        try:
            result = run_pipeline(args.image, args.truck_id, args.expected)
            print_result(result)
        except Exception as exc:
            print(_color(f"Error: {exc}", RED))
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
