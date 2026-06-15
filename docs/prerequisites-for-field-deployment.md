# Q-Vision — Prerequisites for Field Deployment

> Hardware specifications and setup requirements for production deployment at quarry loading stations.
> Meeting Agenda — 30 May 2026

---

## 1. Camera Specification

### Primary Camera

| Parameter | Specification |
|-----------|--------------|
| **Model** | Hikrobot MV-CS200-10GC |
| **Resolution** | 20MP (5472 × 3648) |
| **Sensor** | 1.1" CMOS, Color |
| **Interface** | GigE Vision (Gigabit Ethernet) |
| **Mount** | C-mount |
| **Frame rate** | 3–5 fps (sufficient for static truck inspection) |
| **Power** | PoE (Power over Ethernet, 802.3af) |
| **Operating temp** | -10°C to 60°C |
| **Body IP rating** | IP30 (requires external enclosure for quarry) |

### Why 20MP is Required

All four materials (6mm, 12mm, 20mm, M-Sand) must be classified perfectly. At field distance (1.5–2.5m), minimum pixel density needed:

| Material | Real size | Pixels at 20MP (2m, 16mm lens) | Detection method |
|----------|-----------|-------------------------------|-----------------|
| 6mm stones | 4–8mm | 25–40px | Segmentation + measurement |
| 12mm stones | 8–20mm | 40–100px | Segmentation + measurement |
| 20mm stones | 14–50mm | 70–250px | Segmentation + measurement |
| M-Sand | 0.15–4.75mm | N/A | Texture (GLCM) — scale-independent |

Pipeline requires minimum **15–20px per particle diameter** for reliable segmentation. 20MP ensures all four materials are detectable with margin.

---

## 2. Lens Specification

Two C-mount lenses required (rated for ≥1.1" sensor):

| Lens | Focal Length | Aperture | Use Case | FOV at 2m |
|------|-------------|----------|----------|-----------|
| **Field lens** | 16mm f/1.4 | f/1.4–f/16 | Production (1.5–2.5m distance) | ~1.4m width |
| **Test lens** | 25mm f/1.4 | f/1.4–f/16 | Home/lab testing (0.5–1.0m) | ~0.7m width |

### Lens Selection Guide

| Distance to material | Recommended lens | FOV | px/mm | 6mm stone pixels |
|---------------------|-----------------|-----|-------|-----------------|
| 0.5m (lab bench) | 25mm | 35cm | 15.6 | 94px ✓✓✓ |
| 1.0m (lab/home) | 25mm | 70cm | 7.8 | 47px ✓✓ |
| 1.5m (field) | 16mm | 1.0m | 5.5 | 33px ✓✓ |
| 2.0m (field) | 16mm | 1.4m | 3.9 | 24px ✓ |
| 2.5m (field max) | 16mm | 1.7m | 3.2 | 19px ✓ |

> **Critical rule:** Camera must be ≤ 2.5m from the material surface (not from the ground — from the top of the loaded aggregate).

---

## 3. Supporting Hardware

| Item | Specification | Est. Cost | Purpose |
|------|--------------|-----------|---------|
| PoE injector | 802.3af, any brand | ₹1,000 | Single-cable power + data |
| Cat6 ethernet cable | 10–30m, outdoor-rated | ₹500–1,500 | Camera to processing unit |
| IP67 camera enclosure | Sized for MV-CS200 body + lens | ₹3,000–5,000 | Dust/rain protection at quarry |
| Mounting arm/gantry | Adjustable, rated 5kg+ | ₹3,000–5,000 | Position camera over truck path |
| Edge processing PC | Intel i5+, 8GB RAM, GigE port, Linux/Windows | ₹30,000–50,000 | Run pipeline + dashboard |

---

## 4. Installation Requirements

### Camera Mounting

```
        Camera (MV-CS200 + 16mm lens)
            |
            |  ≤ 2.5m from material surface
            |
            v
    +---------------------+
    | #### aggregate #### |  <- truck bed (loaded)
    | ################### |
    +---------------------+
           truck
```

- Mount camera **perpendicular (straight down)** — avoid angles
- Position over the **center of the truck loading path**
- Camera must be fixed — no movement or vibration
- Lens focus: set once (manual focus at installation distance), lock with focus ring

### Lighting

- **Daytime operation**: Natural overhead light is sufficient
- **Night/covered areas**: Add diffused LED panel (5000K daylight) — avoid harsh directional light
- No shadows falling across the material from overhead structures

### Network

- GigE camera needs dedicated Gigabit ethernet link to processing PC
- Jumbo frames enabled (MTU 9000) recommended for 20MP images
- PoE provides power — no separate power cable to camera needed

---

## 5. Truck Height Variation — The Key Challenge

### Problem Statement

Camera is fixed at one height. Truck bed heights vary across 5–6 types. This changes the effective camera-to-material distance, which changes the pixel scale — and can cause misclassification.

**Physics:** px_per_mm is inversely proportional to distance.

| Truck type | Bed height | D_effective (camera at 4m) | Scale change vs. reference |
|-----------|-----------|---------------------------|---------------------------|
| Small tipper | 1200mm | 2800mm | -12% (stones appear smaller) |
| Medium tipper (reference) | 1500mm | 2500mm | 0% (calibrated here) |
| Large tipper | 1800mm | 2200mm | +14% (stones appear larger) |
| Trailer | 2000mm | 2000mm | +25% |
| High-body truck | 2200mm | 1800mm | +39% |

A 39% scale error on a 12mm stone makes it appear as ~17mm — still within 12mm range (8–20mm). But a 6mm stone at -12% appears as ~5.3mm — still within 6mm range (0–8mm). **The classification boundaries are wide enough to absorb most truck variation**, but edge cases need the software correction.

### Software Solution (To Be Implemented)

```
D_effective = CAMERA_MOUNTING_HEIGHT_MM − truck_bed_height_mm
px_per_mm_adjusted = px_per_mm_base × (CALIBRATION_REFERENCE_DISTANCE_MM / D_effective)
```

### One-Time Measurements Required

| Measurement | How | Stored in |
|-------------|-----|-----------|
| Camera mounting height from ground | Tape measure, once at installation | `config.py → CAMERA_MOUNTING_HEIGHT_MM` |
| Reference truck bed height | Measure one truck type used for calibration | `config.py → CALIBRATION_REFERENCE_DISTANCE_MM` |
| Each truck type bed height | Measure 5–6 truck types, empty | `config.py → TRUCK_PROFILES` |

### Known Limitation (Accepted)

Material pile height (0.3–0.8m above bed floor when loaded) is not compensated automatically. The classification size boundaries (e.g., 12mm = 8–20mm range) absorb this variance in most cases.

---

## 6. Calibration Procedure (One-Time at Installation)

1. Mount camera at final fixed position
2. Measure camera height from ground → set `CAMERA_MOUNTING_HEIGHT_MM`
3. Drive **reference truck** (pick any one type) under camera
4. Place steel ruler **flat on the material surface** in the truck bed
5. Capture one image
6. Run `python calibrate.py` → click 0cm and 10cm ruler marks
7. System auto-computes `FIXED_PX_PER_MM` for this reference distance
8. Set `CALIBRATION_REFERENCE_DISTANCE_MM` = camera height − reference truck bed height
9. Measure remaining truck types (empty bed heights) → fill `TRUCK_PROFILES` in config
10. Remove ruler — never needed again unless camera moves

---

## 7. Software Changes Required

### config.py — New parameters

```python
# Field deployment: camera mounting height (measure once at installation)
CAMERA_MOUNTING_HEIGHT_MM = None  # e.g., 4000 (4 meters from ground)

# Reference distance used during field calibration
CALIBRATION_REFERENCE_DISTANCE_MM = None  # e.g., 2500 (camera_height - ref_truck_bed)

# Truck type profiles (measure bed heights once per truck type)
TRUCK_PROFILES = {
    "small_tipper":  {"name": "Small Tipper (~1.2m)",  "bed_height_mm": 1200},
    "medium_tipper": {"name": "Medium Tipper (~1.5m)", "bed_height_mm": 1500},
    "large_tipper":  {"name": "Large Tipper (~1.8m)",  "bed_height_mm": 1800},
    "trailer":       {"name": "Trailer (~2.0m)",       "bed_height_mm": 2000},
    "high_body":     {"name": "High Body (~2.2m)",     "bed_height_mm": 2200},
}
```

### main.py — Height adjustment function

```python
def get_height_adjusted_px_per_mm(base_px_per_mm, truck_type=None):
    """Adjust px_per_mm based on truck type (variable camera-to-material distance)."""
    if not truck_type or not CAMERA_MOUNTING_HEIGHT_MM or not CALIBRATION_REFERENCE_DISTANCE_MM:
        return base_px_per_mm  # backward-compatible: no adjustment

    profile = TRUCK_PROFILES.get(truck_type)
    if not profile:
        return base_px_per_mm

    d_effective = CAMERA_MOUNTING_HEIGHT_MM - profile["bed_height_mm"]
    if d_effective <= 0:
        return base_px_per_mm  # safety guard

    return base_px_per_mm * (CALIBRATION_REFERENCE_DISTANCE_MM / d_effective)
```

### dashboard.py — Truck type selector

- Add dropdown in sidebar: "Truck Type" with options from `TRUCK_PROFILES`
- Show effective distance and adjusted px/mm in calibration info section
- Pass selected `truck_type` to `run_pipeline()`

---

## 8. Budget Summary

| Category | Items | Est. Cost |
|----------|-------|-----------|
| Camera + Lenses | MV-CS200-10GC + 16mm + 25mm | ₹45,000–65,000 |
| Accessories | PoE, cable, enclosure, mount | ₹8,000–12,000 |
| Edge PC | Processing unit | ₹30,000–50,000 |
| **Total per station** | | **₹83,000–1,27,000** |

---

## 9. Vendor Contact

- **Hikrobot India**: www.hikrobotics.com
- **SDK**: MVS (Machine Vision Software) — free download, supports Python
- **Local support**: Available in major Indian metros — confirm with dealer for your city
- **Lens suppliers**: Any C-mount industrial lens vendor (Computar, Kowa, or Hikrobot-branded)

---

## 10. Pre-Purchase Checklist

Before ordering, confirm with dealer:

- [ ] MV-CS200-10GC available (or equivalent 20MP GigE model)
- [ ] Lens rated for ≥1.1" sensor (not 2/3" — undersized lens = dark corners)
- [ ] Minimum focus distance of 16mm lens ≤ 1.5m
- [ ] Minimum focus distance of 25mm lens ≤ 0.5m
- [ ] MVS SDK supports your processing OS (Linux/Windows — macOS support limited)
- [ ] PoE compliance confirmed (some older models need 12V adapter instead)
- [ ] IP67 enclosure sizing matches camera + lens combined length

---

## 11. Discussion Points for Meeting

1. **Camera purchase approval** — ₹55–75K for camera + lenses (reusable for both home POC and field)
2. **Truck type list** — Confirm exact 5–6 truck types that visit the quarry; need bed height measurements
3. **Camera mounting location** — Where exactly at the loading station? Height achievable?
4. **Edge PC** — Buy new or repurpose existing machine?
5. **Timeline** — Home POC validation (1 week) → Field installation (1 day) → Calibration (1 hour)
6. **Pile height limitation** — Accept as-is or add operator input for load level?
7. **Night operation** — Required? If yes, add LED panel to budget

---

## 12. Next Steps

| Step | Owner | Timeline |
|------|-------|----------|
| Purchase camera + lenses | — | This week |
| Home POC validation (all 4 materials) | Developer | 3–4 days after receipt |
| Implement truck height adjustment code | Developer | 1 day |
| Measure truck types at quarry | Site team | 1 visit |
| Field installation + calibration | Joint | 1 day |
| Validation with live trucks | Joint | 2–3 days |
