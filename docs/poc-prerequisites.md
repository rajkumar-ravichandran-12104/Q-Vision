# Q-Vision — POC Prerequisites & Setup Guide

> Reference document for prototype testing with iPhone camera setup.
> Updated: 9 March 2026

---

## 1. Materials Required

| Item | Specification | Purpose |
|------|--------------|---------|
| Sample material — 6mm | Crushed stone aggregate, 6mm grade | Testing 6mm classification |
| Sample material — 12mm | Crushed stone aggregate, 12mm grade | Testing 10mm class (8–12mm range) |
| Sample material — 20mm | Crushed stone aggregate, 20mm grade | Testing 20mm classification |
| Steel ruler (30cm) | Standard steel ruler with mm markings | One-time px/mm calibration |
| Dark surface | Dark cloth / dark cardboard / dark tray | High contrast background for segmentation |
| iPhone | Any model with auto-focus camera | Fixed camera for POC |
| Phone mount | Tripod / clamp arm / fixed stand | Consistent height for all photos |

---

## 2. Camera Setup

### Position
- Mount iPhone **pointing straight down** (perpendicular to the surface)
- Fix at a consistent height (recommended: **40–60 cm** for tabletop POC)
- Use default **4:3 photo mode** — no special camera settings needed
- Any aspect ratio works (4:3, 16:9, 1:1)

### Focus
- **Tap on the stones** on the iPhone screen before each photo to lock focus
- Stone edges must be **sharp and clearly defined** — blurry edges = bad segmentation
- Individual stone textures should be visible

### Lighting
- Use **indirect daylight** or a **diffused lamp**
- Avoid harsh direct light that creates strong shadows
- Shadows between stones confuse the segmentation algorithm
- Keep lighting consistent across all test photos

### Framing
- Fill **at least 70–80%** of the frame with stones
- Extra background space is acceptable — pipeline filters it out
- Avoid having most of the frame empty (< 40% fill = bad results)

```
Ideal ✅                    Acceptable ⚠️              Bad ❌

┌──────────────┐           ┌──────────────┐          ┌──────────────┐
│ stones stones│           │              │          │              │
│ stones stones│           │  stones      │          │              │
│ stones stones│           │  stones      │          │   stones     │
│ stones stones│           │              │          │              │
└──────────────┘           └──────────────┘          └──────────────┘
 ~80-100% filled            ~40% filled               ~10% filled
```

---

## 3. One-Time Calibration (px/mm)

### Setup
```
     iPhone (looking straight down)
         📱
          |
          |  (fixed height)
          |
          ▼
    ┌─────────────────┐
    │  stones stones   │
    │   stones  📏     │  ← ruler flat ON the stones / same surface level
    │  stones stones   │
    └─────────────────┘
       dark surface
```

### Steps
1. Spread sample stones on the dark surface
2. Place the steel ruler **flat on top of the stones** (same level as stone surfaces)
3. Take ONE photo from the fixed iPhone position
4. Open the photo on Mac (Preview or any editor)
5. Zoom into the ruler
6. Count pixels between two marks **far apart** (e.g. 0cm to 10cm = 100mm)
7. Calculate: `px_per_mm = pixel_count ÷ mm_distance`
8. Set value in `config.py`: `FIXED_PX_PER_MM = <your_value>`
9. **Remove the ruler — never needed again** (as long as camera height stays the same)

### Example
- Ruler: 0cm to 10cm = 100mm
- Pixel distance between those two marks = 520 pixels
- `px_per_mm = 520 / 100 = 5.2`
- Set `FIXED_PX_PER_MM = 5.2`

### Important
- Ruler must be at **same height/level** as the stones (not on the camera, not on the ground below)
- Use marks **far apart** for accuracy (100mm+ recommended)
- If you change camera height, recalibrate

---

## 4. Software Prerequisites

### Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Pre-test Code Fixes Required
- [ ] **EXIF rotation fix** — iPhone JPGs have EXIF orientation tags; `cv2.imread` ignores them → photos appear rotated. Fix needed in `utils.py`
- [ ] **Dashboard histogram bug** — Uses hardcoded `5.0` px/mm instead of actual calibrated value. Fix in `dashboard.py`
- [ ] **Set `FIXED_PX_PER_MM`** in `config.py` after calibration photo

### Run Tests
```bash
python -m pytest tests/ -v
```

---

## 5. Testing Protocol

### Per Sample Material
1. Spread ONE material type on the dark surface (don't mix)
2. Take photo from fixed iPhone position
3. Save to `sample_images/` folder with descriptive name

### CLI Test Commands
```bash
# 6mm sample
python main.py sample_images/6mm_sample.jpg --truck-id POC-001 --expected 6mm

# 12mm sample (maps to 10mm class: 8–12mm range)
python main.py sample_images/12mm_sample.jpg --truck-id POC-002 --expected 10mm

# 20mm sample
python main.py sample_images/20mm_sample.jpg --truck-id POC-003 --expected 20mm
```

### Dashboard Test
```bash
streamlit run dashboard.py
# Open http://localhost:8501
# Upload photo → select expected material → Run Analysis
```

### What to Check
- [ ] Classification matches the actual material
- [ ] Confidence is reasonably high (> 60%)
- [ ] Histogram shows particles concentrated in the correct size range
- [ ] No "MIXED LOAD" warning for single-material samples
- [ ] Zone breakdown shows consistency across all 5 zones

---

## 6. Classification Reference

| Material | Size Range | Class Label | Threshold |
|----------|-----------|-------------|-----------|
| 6mm | 4 – 8 mm | `6mm` | ≥ 80% of particles |
| 12mm | 8 – 12 mm | `10mm` | ≥ 80% of particles |
| 20mm | 16 – 25 mm | `20mm` | ≥ 80% of particles |
| Mixed | — | `MIXED LOAD` | No class dominates |

> **Note:** 12mm material falls within the `10mm` class (8–12mm range). Particles between 12–16mm fall into "other".

---

## 7. Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Photo appears sideways | EXIF rotation not handled | Apply EXIF fix in `utils.py` |
| All particles classified as wrong size | Wrong `px_per_mm` value | Recalibrate with ruler |
| Too many particles detected (noise) | Background not dark enough | Use darker surface |
| Too few particles detected | Stones blend into background | Improve lighting/contrast |
| "MIXED LOAD" on single material | Segmentation picking up noise | Tune `MIN_CONTOUR_AREA` in `config.py` |
| Blurry segmentation results | Camera not focused | Tap to focus on stones before shooting |

---

## 8. Learnings Log

> Track observations, parameter adjustments, and results from each test session below.

| Date | Test | Observation | Action Taken |
|------|------|-------------|-------------|
| | | | |
