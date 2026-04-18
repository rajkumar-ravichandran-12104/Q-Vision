"""Debug texture values for M-Sand images to calibrate thresholds."""
import sys
import numpy as np
from config import FIXED_PX_PER_MM, RULER_CROP_TOP
from segmentation import preprocess, segment_stones, separate_touching_stones
from texture_classifier import detect_msand
from utils import load_image, resize_if_needed
from zones import extract_zones


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        print("Usage: python debug_texture.py <image_path>")
        sys.exit(1)

    image = load_image(path)
    image = resize_if_needed(image)
    if RULER_CROP_TOP > 0:
        h = image.shape[0]
        image = image[int(h * RULER_CROP_TOP):]

    print(f"Image shape: {image.shape}")
    print()

    zones = extract_zones(image)
    for i, zone in enumerate(zones):
        prep = preprocess(zone)
        mask = segment_stones(prep)
        contours, _ = separate_touching_stones(mask)

        result = detect_msand(zone, len(contours))

        print(f"--- Zone {i+1} ---")
        print(f"  Homogeneity : {result['homogeneity']:.4f}  (thresh >= 0.30)")
        print(f"  Contrast    : {result['contrast']:.1f}     (thresh <= 50.0)")
        print(f"  Energy      : {result['energy']:.6f}")
        print(f"  Correlation : {result['correlation']:.4f}")
        print(f"  Contours    : {result['contour_count']}      (thresh <= 15)")
        print(f"  Is M-Sand?  : {result['is_msand']}")
        print()


if __name__ == "__main__":
    main()
