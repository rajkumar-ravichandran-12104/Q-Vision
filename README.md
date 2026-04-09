# Q-Vision — AI-Based Aggregate Size Verification System

> Classical OpenCV pipeline for verifying crushed stone aggregate sizes (6mm / 10mm / 20mm / mixed) loaded in quarry dispatch trucks — **no YOLO, no neural networks**.

---

## Problem Statement

Quarries dispatch trucks loaded with crushed stone aggregate of specific size grades (6 mm, 10 mm, 20 mm).  A wrong-size or mixed load reaching the customer causes costly rejections.  Q-Vision provides an automated, camera-based check at the dispatch gate to verify the aggregate grade before the truck leaves.

---

## Features

- 🎯 **Rule-based classification** — 6 mm / 10 mm / 20 mm / mixed load detection
- 📐 **Physical ruler calibration** — real-world mm measurements from any camera
- 🗺 **5-zone sampling** — catches mixed loads that single-image analysis would miss
- 🌊 **Watershed segmentation** — separates touching stones accurately
- 📊 **Size distribution statistics** — min/max/mean/median/std + per-class %
- 🗳 **Majority voting** — robust classification across all zones
- 🗃 **SQLite logging** — timestamped records per truck, no server needed
- 🖥 **Streamlit dashboard** — drag-and-drop UI, histogram, zone breakdown, history
- ⚙️ **Offline capable** — runs on any laptop, no GPU, no internet

---

## Architecture

```
Fixed camera
     │
     ▼
┌──────────────┐
│   main.py    │  CLI / orchestrator
└──────┬───────┘
       │
       ├─► calibration.py  ── Ruler detection → px/mm ratio
       │
       ├─► zones.py        ── Extract 5 sampling zones
       │
       ├─► segmentation.py ── CLAHE → Adaptive threshold → Watershed
       │
       ├─► measurement.py  ── Equivalent diameter per particle
       │
       ├─► classification.py── Zone label + majority vote
       │
       ├─► logger.py       ── SQLite INSERT
       │
       └─► dashboard.py    ── Streamlit UI
```

---

## Project Structure

```
Q-Vision/
├── main.py              # CLI entry point — runs full pipeline
├── calibration.py       # Ruler detection + px/mm conversion
├── zones.py             # Extract 5 sampling zones from truck bed
├── segmentation.py      # Preprocessing + adaptive threshold + watershed
├── measurement.py       # Compute equivalent diameter per particle contour
├── classification.py    # Rule-based classification + confidence scoring
├── logger.py            # SQLite logging
├── dashboard.py         # Streamlit dashboard UI
├── config.py            # All configurable parameters
├── utils.py             # Shared utility functions
├── requirements.txt     # Python dependencies
├── sample_images/       # Drop test images here
│   └── .gitkeep
└── tests/
    ├── __init__.py
    ├── test_calibration.py
    ├── test_measurement.py
    ├── test_classification.py
    └── test_zones.py
```

---

## Zone Layout

```
┌─────────┬─────────┐
│  Zone 1 │  Zone 2 │
│ top-left│top-right│
│         │         │
│    ┌────┴────┐    │
│    │ Zone 5  │    │
├────┤ center  ├────┤
│    │         │    │
│    └────┬────┘    │
│  Zone 3 │  Zone 4 │
│bot-left │bot-right│
└─────────┴─────────┘
```

---

## Classification Rules

| Grade | Size Range | Threshold |
|-------|-----------|-----------|
| 6 mm  | 4 – 8 mm  | ≥ 80% of particles |
| 10 mm | 8 – 12 mm | ≥ 80% of particles |
| 20 mm | 16 – 25 mm | ≥ 80% of particles |
| Mixed | —         | No single range dominates (< 50%) |

## Majority Vote

| Zones agreeing | Result |
|---|---|
| 4 or 5 | ✅ Classified (high confidence) |
| 3      | ⚠️ Classified with contamination warning |
| < 3    | 🚫 MIXED LOAD — dispatch blocked |

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/rajkumar-ravichandran-12104/Q-Vision.git
cd Q-Vision

# 2. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Usage

### CLI (single image)

```bash
python main.py sample_images/truck01.jpg --truck-id TRUCK-042 --expected 10mm
```

### CLI (batch mode)

```bash
python main.py --batch sample_images/ --truck-id TRUCK-042 --expected 10mm
```

### Streamlit Dashboard

```bash
streamlit run dashboard.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Configuration

All parameters live in `config.py`:

| Parameter | Default | Description |
|---|---|---|
| `MIN_CONTOUR_AREA` | 10 px | Minimum particle area to consider |
| `ZONE_COUNT` | 5 | Number of sampling zones |
| `CLAHE_CLIP_LIMIT` | 2.0 | Contrast enhancement strength |
| `ADAPTIVE_THRESH_BLOCK_SIZE` | 11 | Adaptive threshold block size |
| `ADAPTIVE_THRESH_C` | 2 | Adaptive threshold constant |
| `CALIBRATION_MIN` | 2.0 px/mm | Minimum valid calibration ratio |
| `CALIBRATION_MAX` | 10.0 px/mm | Maximum valid calibration ratio |
| `MAJORITY_THRESHOLD` | 4 | Zones that must agree for classification |
| `CONFIDENCE_THRESHOLD` | 50 % | Minimum confidence to accept result |
| `DB_PATH` | `qvision_logs.db` | SQLite database file path |

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Future Scope

- GPU-accelerated processing for higher throughput
- RTSP/live camera stream support
- REST API wrapper for integration with ERP/WMS systems
- Mobile app for on-site inspection
- Historical trend analysis and contamination alerts

---

## License

MIT License — see `LICENSE` for details.
