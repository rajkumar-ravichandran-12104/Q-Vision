# Q-Vision — POC Camera Setup Guide

> iPhone 17 Pro Max setup for prototype testing.
> Updated: 11 March 2026

---

## Requirements

| Item | Specification |
|------|--------------|
| Camera | iPhone 17 Pro Max |
| Ruler | Steel 30cm ruler |
| Surface | Black chart paper |
| Mount | Phone stand / clamp / tripod |
| Lighting | Indirect daylight or diffused lamp |

---

## Q1: At What Height to Take the Photo?

**Recommended: 40–50 cm** for tabletop POC

- 30cm ruler fits fully in frame at this height
- Stones fill most of the frame
- Sharp focus is easy at this distance

Test this: Hold phone at ~45cm, check if stones fill 70%+ of frame. Adjust up/down accordingly.

> **Important:** Whatever height you choose — fix it every time using a stand/mount. All photos must be taken from the same height.

---

## Q2: Where to Place the Ruler?

```
iPhone 17 Pro Max (45cm above, straight down)
              📱
               |
               ↓
┌──────────────────────────────┐
│                              │
│  📏 ruler (flat, left side)  │
│                              │
│   ● ● ● ● ● ● ● ● ● ●      │
│   ● ● ● ● ● ● ● ● ● ●      │  ← stones spread here
│   ● ● ● ● ● ● ● ● ● ●      │
│                              │
└──────────────────────────────┘
        black chart paper
```

- Flat on the black chart paper
- **Beside the stones** (not under them)
- **Same surface level** as the stones
- Any edge (left, right, top) — doesn't matter
- Ruler only needed for the **one-time calibration photo**

---

## Q3: iPhone Focus Setting?

- **Camera mode:** Photo (default)
- **Aspect ratio:** 4:3 (default)
- **Before shooting:** Tap on the **stones** on screen to lock focus
- **Do NOT use:** Portrait mode, Cinematic mode, or zoom lens
- **HDR:** Keep on (default)
- **Flash:** Off — use natural/room light instead

---

## Other Requirements

| Item | Requirement |
|------|------------|
| Lighting | Indirect daylight or diffused lamp — no harsh shadows |
| Phone mount | Any clamp or tripod holding phone straight down at fixed height |
| Photo transfer | AirDrop photos to Mac after shooting |
| Stone spread | Fill 70%+ of frame — not just a handful |

---

## Calibration Steps (One-Time)

1. Spread stones on black chart paper
2. Place steel ruler flat **beside** the stones (same surface level)
3. Mount iPhone at fixed height (~45cm), pointing straight down
4. Tap on stones to lock focus
5. Take the photo → AirDrop to Mac
6. Open in Preview, zoom into the ruler
7. Count pixels between two marks far apart (e.g. 0cm to 10cm = 100mm)
8. Calculate: `px_per_mm = pixel_count ÷ mm_distance`
9. Set in `config.py`: `FIXED_PX_PER_MM = <your_value>`
10. **Remove ruler — never needed again**

### Example
- Marks used: 0cm to 10cm = **100mm**
- Pixels between those marks in photo = **520 px**
- `px_per_mm = 520 ÷ 100 = 5.2`
- Set `FIXED_PX_PER_MM = 5.2` in `config.py`

---

## Pre-Shot Checklist

- [ ] Black chart paper flat on table
- [ ] Stones spread, covering 70%+ of area
- [ ] Steel ruler flat beside stones on same surface
- [ ] iPhone mounted straight down at ~45cm
- [ ] Tap on stones to lock focus
- [ ] Lighting even, no harsh shadows
- [ ] Take photo → AirDrop to Mac → measure pixels → set `FIXED_PX_PER_MM`

---

## After Calibration — Testing

```bash
# 6mm sample
python main.py sample_images/6mm_sample.jpg --truck-id POC-001 --expected 6mm

# 12mm sample (maps to 10mm class: 8–12mm range)
python main.py sample_images/12mm_sample.jpg --truck-id POC-002 --expected 10mm

# 20mm sample
python main.py sample_images/20mm_sample.jpg --truck-id POC-003 --expected 20mm
```

Or use the dashboard:
```bash
streamlit run dashboard.py
# Open http://localhost:8501
```
