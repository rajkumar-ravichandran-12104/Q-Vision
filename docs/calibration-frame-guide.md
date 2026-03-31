# Q-Vision — Calibration Photo Frame Guide

## Required Frame Structure (4:3 Landscape)

```
iPhone 17 Pro Max — Photo mode — 1x lens — 4:3 ratio
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  |    |    |    |    |    |    |    |    |    |   │  │
│  │  0cm  1    2    3    4    5    6    7    8    9  10cm│ ← RULER (flat, top)
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤      │
│  ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   │
│   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤      │  ← STONES
│  ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   │  (fill 70%+)
│   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤      │
│  ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   │
│   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤   ⬤      │
│                                                         │
└─────────────────────────────────────────────────────────┘
                   BLACK CHART PAPER
```

---

## Checklist Before Shooting

- [ ] Ruler placed **horizontally at the TOP** of frame — flat on paper
- [ ] **0cm mark** clearly visible on the left side
- [ ] **10cm mark** clearly visible (100mm span for calibration)
- [ ] Stones spread below ruler — fill **70%+** of frame
- [ ] Black background visible at edges (not covered fully by stones)
- [ ] **No shadows** falling across the ruler marks
- [ ] iPhone at **1x lens** (not 0.5x or 3x)
- [ ] **Tap on stones** to lock focus before shooting
- [ ] **Flash OFF**
- [ ] Photo format: **JPEG, Actual Size**

---

## px/mm Calculation After Photo

1. Open photo in **Preview** on Mac
2. Move cursor to **0cm mark** on ruler → note **X pixel coordinate**
3. Move cursor to **10cm mark** on ruler → note **X pixel coordinate**
4. Calculate:

```
px_per_mm = (X at 10cm  −  X at 0cm)  ÷  100
```

### Example:
- X at 0cm  = 312 px
- X at 10cm = 832 px
- `px_per_mm = (832 − 312) ÷ 100 = 5.2`

5. Open `config.py` → set:

```python
FIXED_PX_PER_MM = 5.2   # replace with your value
```

---

## How to Read Pixel Coordinates in Preview

1. Open photo in **Preview**
2. Menu → **Tools → Show Inspector** (`Cmd + I`)
3. Hover cursor over the ruler mark
4. Inspector panel shows **X, Y coordinates** in pixels

> Use the **X coordinate** only (horizontal distance along the ruler).
