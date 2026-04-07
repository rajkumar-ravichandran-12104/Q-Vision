"""
Quick diagnostic: prints raw diameter distribution for an image.
Usage: python debug_diameters.py path/to/12mm_image.jpg
"""
import sys
import numpy as np
from collections import Counter

from config import FIXED_PX_PER_MM, RULER_CROP_TOP
from measurement import measure_particles, compute_distribution
from segmentation import preprocess, segment_stones, separate_touching_stones
from utils import load_image, resize_if_needed
from zones import extract_zones


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        print("Usage: python debug_diameters.py <image_path>")
        sys.exit(1)

    image = load_image(path)
    image = resize_if_needed(image)

    if RULER_CROP_TOP > 0:
        h = image.shape[0]
        image = image[int(h * RULER_CROP_TOP):]

    px_per_mm = FIXED_PX_PER_MM
    print(f"px_per_mm = {px_per_mm}")
    print(f"Image shape (after crop/resize): {image.shape}\n")

    zones = extract_zones(image)
    all_diameters = []

    for i, zone in enumerate(zones):
        prep = preprocess(zone)
        mask = segment_stones(prep)
        contours, _ = separate_touching_stones(mask)
        particles = measure_particles(contours, px_per_mm)
        diams = sorted([p["diameter_mm"] for p in particles])
        all_diameters.extend(diams)

        print(f"--- Zone {i+1}: {len(diams)} particles ---")
        if diams:
            print(f"  Min: {min(diams):.2f}  Max: {max(diams):.2f}  Mean: {np.mean(diams):.2f}")
            # Bucket into ranges
            arr = np.array(diams)
            b0_8   = int(np.sum((arr >= 0)  & (arr < 8)))
            b8_14  = int(np.sum((arr >= 8)  & (arr < 14)))
            b10_18 = int(np.sum((arr >= 10) & (arr < 18)))
            b14_50 = int(np.sum((arr >= 14) & (arr < 50)))
            b18_50 = int(np.sum((arr >= 18) & (arr < 50)))
            total = len(arr)
            print(f"  0-8mm (6mm rule):   {b0_8:3d} ({100*b0_8/total:.1f}%)")
            print(f"  8-14mm (10mm rule): {b8_14:3d} ({100*b8_14/total:.1f}%)")
            print(f"  10-18mm (12mm rule):{b10_18:3d} ({100*b10_18/total:.1f}%)")
            print(f"  14-50mm (20mm rule):{b14_50:3d} ({100*b14_50/total:.1f}%)")
            print(f"  18-50mm (20mm disp):{b18_50:3d} ({100*b18_50/total:.1f}%)")
            print(f"  All diameters: {[round(d,1) for d in diams]}")
        print()

    # Overall
    if all_diameters:
        arr = np.array(all_diameters)
        total = len(arr)
        print(f"=== OVERALL: {total} particles ===")
        print(f"  Mean: {arr.mean():.2f}  Median: {np.median(arr):.2f}  Std: {arr.std():.2f}")
        b0_8   = int(np.sum((arr >= 0)  & (arr < 8)))
        b8_14  = int(np.sum((arr >= 8)  & (arr < 14)))
        b10_18 = int(np.sum((arr >= 10) & (arr < 18)))
        b14_50 = int(np.sum((arr >= 14) & (arr < 50)))
        print(f"  0-8mm  (6mm rule) : {b0_8:3d} / {total} = {100*b0_8/total:.1f}%")
        print(f"  8-14mm (10mm rule): {b8_14:3d} / {total} = {100*b8_14/total:.1f}%")
        print(f"  10-18mm(12mm rule): {b10_18:3d} / {total} = {100*b10_18/total:.1f}%")
        print(f"  14-50mm(20mm rule): {b14_50:3d} / {total} = {100*b14_50/total:.1f}%")


if __name__ == "__main__":
    main()
