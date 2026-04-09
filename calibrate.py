"""
Q-Vision Calibration Helper
----------------------------
Run this script, click on the 0cm ruler mark, then the 10cm ruler mark.
It will calculate px_per_mm and update config.py automatically.

Usage:
    python calibrate.py path/to/your/image.jpeg
"""

import sys
import cv2
import numpy as np

PIPELINE_MAX_DIM = 2000  # must match MAX_IMAGE_DIM in config.py


clicks = []


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicks.append((x, y))
        img = param["image"]
        label = "0 cm" if len(clicks) == 1 else "10 cm"
        cv2.circle(img, (x, y), 8, (0, 255, 0), -1)
        cv2.putText(img, label, (x + 12, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.imshow("Q-Vision Calibration", img)
        print(f"  Clicked {label} at X={x}, Y={y}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python calibrate.py path/to/image.jpeg")
        sys.exit(1)

    path = sys.argv[1]
    img = cv2.imread(path)
    if img is None:
        print(f"ERROR: Cannot open image: {path}")
        sys.exit(1)

    # Resize for display if too large (keep aspect ratio)
    h, w = img.shape[:2]
    original_h, original_w = h, w
    max_dim = 1400
    scale = 1.0
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    display = img.copy()
    cv2.namedWindow("Q-Vision Calibration", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Q-Vision Calibration", on_mouse, {"image": display})

    print("\n=== Q-Vision Calibration ===")
    print("Step 1: Click on the 0 cm mark on the ruler")
    print("Step 2: Click on the 10 cm mark on the ruler")
    print("Press Q to quit without saving.\n")

    cv2.imshow("Q-Vision Calibration", display)

    while True:
        key = cv2.waitKey(50) & 0xFF
        if key == ord('q'):
            print("Cancelled.")
            break
        if len(clicks) >= 2:
            x0, _ = clicks[0]
            x1, _ = clicks[1]
            pixel_distance = abs(x1 - x0) / scale  # undo display scaling

            span_input = input("\nHow many mm between your two clicks? (e.g. 300 for 0–30cm, 100 for 0–10cm): ").strip()
            span_mm = float(span_input) if span_input else 100.0

            # pixel_distance is in original image space
            # Apply same resize factor the pipeline uses (MAX_IMAGE_DIM=2000)
            pipeline_scale = min(1.0, PIPELINE_MAX_DIM / max(original_h, original_w))
            effective_pixel_distance = pixel_distance * pipeline_scale
            px_per_mm = effective_pixel_distance / span_mm
            px_per_mm = round(px_per_mm, 4)

            print(f"\n--- Result ---")
            print(f"  0cm  X = {int(clicks[0][0] / scale)}")
            print(f"  10cm X = {int(clicks[1][0] / scale)}")
            print(f"  Original pixel distance = {pixel_distance:.1f} px")
            print(f"  Pipeline resize scale   = {pipeline_scale:.4f}  ({original_w}x{original_h} → {PIPELINE_MAX_DIM}px max)")
            print(f"  Effective pixel distance = {effective_pixel_distance:.1f} px")
            print(f"  px_per_mm = {effective_pixel_distance:.1f} / {span_mm:.0f} = {px_per_mm}")

            # Update config.py
            config_path = "config.py"
            try:
                with open(config_path, "r") as f:
                    content = f.read()

                import re
                new_content = re.sub(
                    r"FIXED_PX_PER_MM\s*=\s*[^\n]+",
                    f"FIXED_PX_PER_MM = {px_per_mm}  # auto-calibrated",
                    content
                )

                with open(config_path, "w") as f:
                    f.write(new_content)

                print(f"\n✓ config.py updated: FIXED_PX_PER_MM = {px_per_mm}")
                print("  You can now run: streamlit run dashboard.py")
            except Exception as e:
                print(f"\nCould not update config.py: {e}")
                print(f"  Manually set in config.py:  FIXED_PX_PER_MM = {px_per_mm}")

            cv2.waitKey(2000)
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
