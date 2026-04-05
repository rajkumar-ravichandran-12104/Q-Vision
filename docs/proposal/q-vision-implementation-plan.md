# Q-Vision: Detailed Implementation Plan

## All Phases — Technical & Operational Breakdown

**Version:** 1.0  
**Date:** March 2026  
**Project:** Quarry Material Monitoring & Anti-Theft System

---

## Overview

| Phase | Name | Duration | Depends On |
|-------|------|----------|------------|
| Phase 1 | Core Intelligence Engine | Month 1 | — |
| Phase 2 | Live Surveillance & Auto-Capture | Month 1–2 | Phase 1 |
| Phase 3 | Vehicle Identification (ANPR) | Month 2–3 | Phase 2 |
| Phase 4 | Material Reconciliation & Theft Detection | Month 3–4 | Phase 2, Phase 3 |
| Phase 5 | Owner Dashboard, Mobile Access & Data Security | Month 3–4 | Phase 1 (parallel) |
| Phase 6 | Deployment, Training & Support | Month 4–5 | All phases |

```
Month 1          Month 2          Month 3          Month 4          Month 5
┌──────────┐
│ Phase 1  │
│ Core     │
│ Engine   │
└────┬─────┘
     │  ┌──────────────┐
     └─>│   Phase 2    │
        │ Surveillance │
        └────┬────┬────┘
             │    │  ┌──────────────┐
             │    └─>│   Phase 3    │
             │       │    ANPR      │
             │       └──────┬───────┘
             │              │  ┌──────────────┐
             │              └─>│   Phase 4    │
             │                 │Reconciliation│
             │                 └──────────────┘
        ┌────┴──────────────────────┐
        │        Phase 5            │
        │ Dashboard + Data Security │
        └───────────────────────────┘
                                          ┌──────────────┐
                                          │   Phase 6    │
                                          │  Deployment  │
                                          └──────────────┘
```

---

---

## Phase 1: Core Intelligence Engine

**Duration:** Month 1  
**Investment:** ₹12,00,000  
**Status:** POC completed (12mm, 20mm classification demo working)

### What This Phase Delivers

The brain of the system — the computer vision engine that looks at stone aggregate and determines what grade it is, whether it's contaminated, and how confident the system is about the result.

### Detailed Tasks

#### 1.1 Stone Grade Classification

| Task | Description |
|------|-------------|
| Image preprocessing | CLAHE contrast enhancement + Gaussian noise reduction for dusty/uneven quarry lighting |
| Stone segmentation | Otsu thresholding + morphological operations to isolate individual stones from background |
| Watershed separation | Separate touching/overlapping stones into individual particles |
| Particle measurement | Calculate equivalent diameter of each stone in millimeters |
| Size distribution | Compute min, max, mean, median, standard deviation across all detected particles |
| Grade classification | Map particle size distribution to grade: 6mm, 10mm, 12mm, or 20mm |
| Confidence scoring | Percentage-based confidence: how sure the system is about the classification |

#### 1.2 Multi-Zone Analysis (5-Zone Sampling)

The system doesn't just look at one spot — it samples 5 zones across the truck bed to catch mixed loads or contamination.

```
┌─────────────┬─────────────┐
│             │             │
│  Zone 1     │   Zone 2    │
│  Top-Left   │  Top-Right  │
│             │             │
├──────┬──────┴──────┬──────┤
│      │   Zone 5    │      │
│      │   Center    │      │
│      │             │      │
├──────┴──────┬──────┴──────┤
│             │             │
│  Zone 3     │   Zone 4    │
│ Bottom-Left │Bottom-Right │
│             │             │
└─────────────┴─────────────┘
```

| Task | Description |
|------|-------------|
| Zone extraction | Divide camera frame into 5 zones (4 quadrants + center) |
| Per-zone classification | Each zone classified independently |
| Majority voting | Final grade = majority vote across 5 zones (need 3+ agreement) |
| Contamination detection | If zones disagree significantly → flag as "Mixed Load" |
| Mismatch check | Compare classified grade against expected grade (invoice/order) |

#### 1.3 Camera Calibration System

| Task | Description |
|------|-------------|
| Ruler detection | Auto-detect ruler/scale bar in calibration image |
| Pixel-to-mm conversion | Calculate exact px/mm ratio for the specific camera + distance setup |
| Calibration validation | Bounds checking to reject bad calibrations |
| Manual calibration mode | Operator can manually enter px/mm if auto-detection fails |
| Per-gate calibration storage | Each gate/camera can have its own calibration profile |

#### 1.4 Testing with Actual Quarry Samples

| Task | Description |
|------|-------------|
| Collect sample images | 50+ photos per grade from client's actual quarry (all 4 grades) |
| Different lighting conditions | Morning, afternoon, overcast, shade, artificial light |
| Wet vs dry material | Stone looks different when wet — system must handle both |
| Threshold tuning | Adjust classification boundaries to match client's specific material |
| Accuracy validation | Target: 90%+ correct classification across all grades |
| Edge case handling | Mixed loads, very dusty conditions, partial truck views |

### Phase 1 Deliverables

- [ ] Working classification engine for all 4 grades (6mm, 10mm, 12mm, 20mm)
- [ ] 5-zone analysis with contamination detection
- [ ] Camera calibration tool (auto + manual)
- [ ] Tested and tuned with client's actual material samples
- [ ] Accuracy report: grade-wise success rate

### Milestone Demo

Show client: upload a photo of his quarry truck → system classifies all 5 zones, shows grade, confidence %, and whether it's mixed/contaminated.

---

---

## Phase 2: Live Surveillance & Auto-Capture

**Duration:** Month 1–2  
**Investment:** ₹10,00,000  
**Depends on:** Phase 1

### What This Phase Delivers

Transform the system from "upload a photo" to "cameras automatically capture and analyze every truck passing through the gate — 24/7, no human needed."

### Hardware Required (Client's Cost, Separate)

| Item | Specification | Qty per Gate | Est. Cost |
|------|--------------|-------------|-----------|
| IP Camera | Hikvision/Dahua, 2–5MP, PoE, IP66, IR night vision | 1–2 | ₹8,000–15,000 |
| ANPR Camera | Dedicated number plate camera (or second angle of main cam) | 1 | ₹10,000–20,000 |
| PoE Switch | 4/8 port, powers cameras via LAN cable | 1 | ₹3,000–5,000 |
| On-site PC/Server | Intel i5+, 8GB+ RAM, 1TB HDD, Ubuntu/Windows | 1 | ₹40,000–60,000 |
| UPS | Protect PC from power cuts, 1–2 hour backup | 1 | ₹5,000–10,000 |
| LAN Cabling | CAT6 cable from cameras to PC | As needed | ₹2,000–5,000 |
| Mounting hardware | Camera brackets, poles, weatherproof housing | As needed | ₹3,000–5,000 |

**Total hardware per gate: ₹70,000–1,20,000**  
**For 3 gates: ₹2,10,000–3,60,000** (within the ₹3–5L estimate)

### Detailed Tasks

#### 2.1 RTSP Camera Integration

| Task | Description |
|------|-------------|
| RTSP stream reader | Connect to IP camera's live video feed via RTSP protocol |
| Multi-camera support | Handle 2–3 cameras simultaneously (one per gate) |
| Frame extraction | Pull individual frames from the live stream for analysis |
| Camera health monitoring | Detect if camera goes offline, sends alert |
| Reconnection logic | Auto-reconnect if camera feed drops (power cut, network blip) |
| Configuration per camera | Each camera has its own RTSP URL, resolution, angle settings |

#### 2.2 Automatic Truck Detection & Capture

| Task | Description |
|------|-------------|
| Motion detection | Detect when a truck enters the camera's field of view |
| Truck presence confirmation | Distinguish truck from person/animal/vehicle passing by |
| Optimal frame capture | Wait for truck to be fully in frame, then capture best frame |
| Multi-frame analysis | Capture 3–5 frames per truck, pick the best quality one |
| Trigger logging | Record exact timestamp of every capture event |
| Gate status tracking | Know if gate is idle / truck approaching / truck in position / truck leaving |

#### 2.3 24/7 Operation

| Task | Description |
|------|-------------|
| Day mode | Normal color image processing |
| Night mode (IR) | Handle infrared/low-light images from camera's IR LEDs |
| Auto-switching | System adapts processing based on lighting conditions |
| Continuous operation | Run as a background service, auto-start on boot |
| Crash recovery | If software crashes, auto-restart within 30 seconds |
| Log rotation | Manage log files so disk doesn't fill up |

#### 2.4 On-Site Hardware Coordination

| Task | Description |
|------|-------------|
| Camera placement planning | Site visit — determine exact mounting positions per gate |
| Angle optimization | Camera angle to see truck bed clearly from 2–3m height |
| Network setup | LAN cabling from cameras to on-site PC |
| PC setup | Install OS, software, configure auto-start |
| Testing | Verify all cameras feeding correctly, day and night |

### Phase 2 Deliverables

- [ ] Live RTSP feed working from all gate cameras
- [ ] Automatic truck detection and frame capture
- [ ] 24/7 operation with day/night mode
- [ ] Auto-restart on crash, reconnect on camera dropout
- [ ] On-site PC configured and all hardware installed
- [ ] Each gate captures + classifies automatically without human intervention

### Milestone Demo

Take client to the gate → truck passes → system auto-captures, classifies, and logs the result on screen. No button clicks, no human involvement. Show it working in both day and night.

---

---

## Phase 3: Vehicle Identification (ANPR)

**Duration:** Month 2–3  
**Investment:** ₹8,00,000  
**Depends on:** Phase 2

### What This Phase Delivers

Every truck that passes is identified by its number plate — automatically. The system knows WHICH truck carried WHAT material, WHEN, and whether it was authorized.

### Detailed Tasks

#### 3.1 Number Plate Recognition Engine

| Task | Description |
|------|-------------|
| Plate detection | Locate the number plate region in the camera frame |
| Plate extraction | Crop and enhance the plate area for reading |
| OCR (character recognition) | Read the plate text: e.g., "TN 38 AB 1234" |
| Indian plate format handling | Handle yellow commercial plates, white plates, different state formats |
| Dirty/damaged plate handling | Enhancement for dusty, mud-covered, bent plates (common in quarries) |
| Confidence scoring | How sure the system is about the plate reading |
| Manual correction option | If OCR fails, operator can manually type the plate number |

#### 3.2 Vehicle Database

| Task | Description |
|------|-------------|
| Vehicle registry | Store all known trucks: plate number, owner, capacity, authorized material |
| Driver database | Link drivers to vehicles (optional — can add later) |
| Authorization list | Which trucks are authorized to pick up which material |
| Blacklist | Flag specific vehicles (known offenders, banned trucks) |
| Auto-learn | New plates automatically added to database on first appearance |
| Search & filter | Look up any vehicle by plate number, date range, material carried |

#### 3.3 Entry/Exit Matching

| Task | Description |
|------|-------------|
| Entry detection | Log truck entering the quarry (empty) |
| Exit detection | Log truck leaving the quarry (loaded) |
| Entry-exit pairing | Match each exit with its corresponding entry |
| Unauthorized exit alert | Truck exits loaded but never entered properly → immediate alert |
| Time tracking | How long each truck spent inside the quarry |
| Multiple trips detection | Flag trucks making unusually many trips per day |

#### 3.4 Repeat Offender Tracking

| Task | Description |
|------|-------------|
| Anomaly scoring | Each vehicle gets a risk score based on history |
| Flagging rules | Auto-flag: too many trips, odd timing (late night), mismatches |
| Weekly offender report | Top 10 suspicious vehicles of the week |
| Pattern detection | Same truck, same time, same gate — habitual unauthorized dispatch |

### Phase 3 Deliverables

- [ ] Automatic number plate reading for every passing truck
- [ ] Vehicle database with authorization management
- [ ] Entry/exit matching with unauthorized exit alerts
- [ ] Repeat offender tracking with risk scoring
- [ ] Searchable vehicle history log

### Milestone Demo

Truck passes the gate → screen shows: plate "TN 38 AB 1234", material "12mm", authorized "YES", confidence 94%. Show the vehicle history for that truck — all past visits, materials carried, timestamps.

---

---

## Phase 4: Material Reconciliation & Theft Detection

**Duration:** Month 3–4  
**Investment:** ₹8,00,000  
**Depends on:** Phase 2, Phase 3

### What This Phase Delivers

The "catch the thief" engine. Cross-references all data — production, dispatch, weighbridge, truck logs — to find exactly where material is going missing, how much, and when.

### Detailed Tasks

#### 4.1 Weighbridge Data Integration

| Task | Description |
|------|-------------|
| Weighbridge data import | Read data from existing weighbridge system (CSV/Excel/database) |
| Weight per truck | Gross weight, tare weight, net material weight |
| Material weight estimation | Cross-reference: camera says "12mm" + weighbridge says "18 tonnes" |
| Weight anomaly detection | Expected weight for 12mm truck = 15–20T. Below 12T or above 22T → alert |
| Auto-matching | Match weighbridge entry to camera capture by truck plate + timestamp |
| Manual weighbridge entry | If no digital weighbridge, operator can type weight manually |

#### 4.2 Daily Material Balance

| Task | Description |
|------|-------------|
| Production input | Daily production numbers per grade (entered by manager or imported) |
| Dispatch tracking | Auto-calculated from camera + weighbridge data |
| Stock calculation | Stock = Yesterday's stock + Today's production - Today's dispatch |
| Balance report | One-page view: produced, dispatched, stock remaining — per grade |
| Gap detection | If dispatch > production + stock → material coming from somewhere unauthorized |
| Historical trend | Weekly/monthly balance trend — is the gap growing or shrinking? |

#### 4.3 Theft Alert Engine

| Task | Description |
|------|-------------|
| Real-time anomaly detection | Triggered whenever data doesn't add up |
| Alert types: | |
| — Unauthorized dispatch | Truck left with material but no corresponding order |
| — Grade mismatch | Order says 12mm but camera detects 20mm loaded |
| — Weight anomaly | Load weight doesn't match expected for that grade |
| — After-hours dispatch | Truck left between 10 PM – 6 AM (configurable) |
| — Excess trips | More trucks dispatched than orders placed |
| — Stock discrepancy | Stock count doesn't match calculated stock |
| Alert severity | Low (info) / Medium (review needed) / High (likely theft) / Critical (confirmed anomaly) |
| Alert delivery | On-screen notification + SMS/WhatsApp to owner |
| False positive handling | Owner can mark alerts as reviewed/false alarm — system learns patterns |

#### 4.4 Shift-Wise Accountability

| Task | Description |
|------|-------------|
| Shift definition | Morning (6AM–2PM), Afternoon (2PM–10PM), Night (10PM–6AM) — configurable |
| Per-shift dispatch report | How much material left during each shift |
| Shift comparison | Compare shifts against each other — which shift has most anomalies? |
| Gate operator log | Who was on duty when an anomaly occurred |
| Shift handover report | Summary at each shift change — totals, alerts, pending actions |

### Phase 4 Deliverables

- [ ] Weighbridge data integration (auto-import or manual entry)
- [ ] Daily material balance: production vs dispatch vs stock
- [ ] Real-time theft alert engine with 6+ anomaly types
- [ ] Alert severity levels with SMS/WhatsApp notification
- [ ] Shift-wise accountability reports
- [ ] Historical trend analysis

### Milestone Demo

Show the owner: "Today, 45 trucks dispatched, 680 tonnes total. Production was 650 tonnes. Stock should be 200 tonnes but calculated stock is 170 tonnes. 30 tonnes gap — here are the 3 suspicious dispatches flagged with HIGH severity."

---

---

## Phase 5: Owner Dashboard, Mobile Access & Data Security

**Duration:** Month 3–4 (parallel with Phase 3–4)  
**Investment:** ₹7,00,000  
**Depends on:** Phase 1 (builds progressively as other phases complete)

### What This Phase Delivers

The control center — everything the owner needs to monitor his quarry from anywhere, plus the encrypted data security architecture that protects all intelligence data.

### Detailed Tasks

#### 5.1 Owner Dashboard (Web)

| Task | Description |
|------|-------------|
| Real-time overview | Live status of all gates, current truck count, today's dispatch total |
| Gate-wise view | Click on any gate → see live feed, last 10 trucks, current status |
| Material breakdown | Pie chart / bar chart: how much of each grade dispatched today |
| Truck log | Scrollable table: timestamp, plate, grade, weight, gate, status (pass/alert) |
| Alert panel | Active alerts with severity badges, one-click review/dismiss |
| Reconciliation view | Production vs dispatch vs stock — with gap highlighted in red |
| Date range filter | View any historical period — today, this week, this month, custom range |
| Export to PDF | One-click report download for any date range |

#### 5.2 Mobile-Optimized View

| Task | Description |
|------|-------------|
| Responsive design | Dashboard works on phone browser — no app install needed |
| Key metrics on top | Today's dispatch count, total tonnes, active alerts — visible at a glance |
| Push-style alerts | SMS or WhatsApp message with alert details + link to dashboard |
| Quick actions | Approve/dismiss alerts from phone |
| Offline summary | Daily summary SMS even if owner doesn't open the dashboard |

#### 5.3 Role-Based Access

| Role | Can See | Can Do |
|------|---------|--------|
| **Owner** | Everything — full analytics, reconciliation, theft reports, all history | Configure system, manage users, download reports, dismiss alerts |
| **Manager** | Today's dispatch, truck log, basic alerts | Acknowledge alerts, add manual entries |
| **Gate Operator** | Current truck status, pass/fail result only | Nothing — view only, cannot modify any data |

| Task | Description |
|------|-------------|
| Login system | Username + password per user |
| Role assignment | Owner assigns roles to manager/operator accounts |
| Audit trail | Log who accessed what and when |
| Session management | Auto-logout after inactivity |

#### 5.4 Data Security Architecture

| Task | Description |
|------|-------------|
| **Encrypted database** | SQLCipher encryption — database file is unreadable without password |
| **Split storage** | Gate machine keeps 24hrs only; Owner machine keeps full history |
| **Auto-purge** | Gate machine deletes records older than 24–48 hours automatically |
| **LAN sync** | Data transfers from gate machine to owner machine via local cable — no internet |
| **Dual dashboard mode** | Gate shows Operator Mode (basic); Owner machine shows full analytics |
| **Hidden owner access** | No visible button for owner mode on gate machine — accessed only via PIN |
| **Auto-lock** | System locks after 5 minutes of inactivity |
| **Emergency wipe** | Hidden keyboard shortcut to instantly clear gate machine data |
| **Tamper-proof logs** | Append-only log file — entries cannot be deleted or modified |
| **Backup system** | Automatic encrypted backup to USB drive (optional secondary backup) |

```
GATE MACHINE                         OWNER MACHINE
┌──────────────────────┐            ┌──────────────────────┐
│ Camera feed          │            │ Full encrypted DB     │
│ Live classification  │   LAN     │ All history           │
│ Operator Mode ONLY   │ ────────> │ Analytics + Reports   │
│ Last 24hrs data      │  (cable)  │ Reconciliation        │
│ Auto-purge nightly   │           │ Theft alerts          │
│ Encrypted DB         │           │ Owner Dashboard       │
│ Emergency wipe ready │           │ Encrypted + backed up │
└──────────────────────┘            └──────────────────────┘
         │                                    │
    Anyone can see:                    Only owner sees:
    "Quality Check Screen"            "Full Intelligence"
```

#### 5.5 Alert & Notification System

| Task | Description |
|------|-------------|
| SMS integration | Twilio or local SMS gateway for alerts |
| WhatsApp integration | WhatsApp Business API for rich alerts with images |
| Alert templates | Pre-formatted messages: "🚨 Unauthorized dispatch at Gate 2 — TN38AB1234 — 12mm — 18T — 2:34 AM" |
| Alert grouping | Don't spam — group similar alerts within 15 minutes |
| Daily digest | End-of-day summary: total trucks, tonnes, alerts, gaps |
| Configurable recipients | Owner + optional manager phone numbers |

### Phase 5 Deliverables

- [ ] Full web dashboard with real-time monitoring
- [ ] Mobile-optimized view accessible from phone browser
- [ ] Role-based access (Owner / Manager / Operator)
- [ ] Encrypted database (SQLCipher) on both machines
- [ ] Split storage with auto-purge on gate machine
- [ ] LAN sync between gate and owner machine
- [ ] Dual dashboard mode (Operator / Owner)
- [ ] Emergency wipe capability
- [ ] SMS/WhatsApp alert system
- [ ] PDF report generation and export

### Milestone Demo

Give owner his phone → show him the dashboard with today's data. Trigger a test alert → WhatsApp pops up on his phone within seconds. Open the gate machine → show him it only has today's basic data. Open the owner machine → show him full history, analytics, reconciliation. Explain: "This is what anyone sees at the gate. This is what only you see."

---

---

## Phase 6: Deployment, Training & Support

**Duration:** Month 4–5  
**Investment:** ₹5,00,000  
**Depends on:** All previous phases

### What This Phase Delivers

The system goes live at the quarry. Hardware installed, software configured, operators trained, owner confident. Plus 6 months of support after go-live.

### Detailed Tasks

#### 6.1 Site Preparation & Hardware Installation

| Task | Description |
|------|-------------|
| Site survey | Visit each gate — finalize camera positions, cable routes, PC location |
| Camera mounting | Install cameras at 2–3m height at each gate, weatherproof housing |
| Cable routing | CAT6 LAN cables from cameras to gate PC, gate PC to owner PC |
| PC setup | Install OS, Q-Vision software, configure auto-start on boot |
| UPS installation | Connect PC and cameras to UPS for power-cut protection |
| Network testing | Verify all camera feeds stable, LAN sync working |
| Night testing | Verify IR cameras working after dark |

#### 6.2 System Configuration

| Task | Description |
|------|-------------|
| Per-gate calibration | Run calibration tool at each gate with ruler |
| Grade threshold tuning | Fine-tune classification thresholds with client's actual material |
| Alert rules configuration | Set working hours, shift times, weight thresholds per client preferences |
| User accounts | Create owner, manager, operator accounts with correct roles |
| Backup schedule | Configure automatic encrypted backup (USB or second machine) |
| Auto-purge schedule | Set 24hr or 48hr purge window on gate machines |

#### 6.3 Operator Training

| Session | Audience | Duration | Content |
|---------|----------|----------|---------|
| Session 1 | Gate operators | 2 hours | How the gate screen works, what pass/fail means, when to call manager |
| Session 2 | Manager(s) | 2 hours | Dashboard overview, alert handling, daily report review, manual entry |
| Session 3 | Owner | 1 hour | Full system walkthrough, owner dashboard, mobile access, data security features, emergency wipe |

| Training Material | Description |
|-------------------|-------------|
| Operator quick-reference card | Laminated A4 sheet at each gate — common scenarios and what to do |
| Manager guide | 5-page PDF — dashboard navigation, alert handling, reporting |
| Owner guide | 3-page PDF — mobile access, key metrics, how to check data, emergency procedures |
| Troubleshooting guide | Common issues: camera offline, system frozen, power cut recovery |

#### 6.4 Go-Live & Burn-In Period

| Task | Description |
|------|-------------|
| Soft launch (Week 1) | System runs alongside existing manual process — both capture data |
| Comparison validation | Compare system results vs manual records — verify accuracy |
| Issue fixing | Address any bugs or edge cases found during soft launch |
| Full launch (Week 2) | System takes over as primary monitoring — manual process becomes backup |
| 2-week monitoring | Developer monitors remotely, daily check-in with manager |

#### 6.5 Post-Deployment Support (6 Months)

| Support Type | Response Time | Includes |
|-------------|--------------|----------|
| Critical (system down) | Within 2 hours | Remote fix or on-site visit |
| High (alerts not working, camera issue) | Within 8 hours | Remote diagnosis + fix |
| Medium (report incorrect, minor bug) | Within 24 hours | Remote fix |
| Low (feature request, UI change) | Within 1 week | Evaluation + implementation if minor |

| Support Includes | |
|-----------------|---|
| Bug fixes | Any defects found post-deployment |
| Performance tuning | If accuracy drops due to seasonal changes (rain, dust) |
| Camera recalibration | If cameras are moved or replaced |
| Software updates | Minor improvements and stability fixes |
| Remote monitoring | Periodic check-in to ensure system health |
| Phone support | WhatsApp/call support for manager and owner |

| Support Does NOT Include | |
|-------------------------|---|
| New feature development | Quoted separately |
| Hardware replacement | Client's responsibility (cameras, server, UPS) |
| Internet-related issues | System is offline — no internet dependency |
| Operator errors | Covered by re-training, not software fix |

### Phase 6 Deliverables

- [ ] All cameras installed and tested at every gate
- [ ] On-site PC configured with auto-start and crash recovery
- [ ] System calibrated for each gate with client's material
- [ ] All user accounts created with correct roles
- [ ] 3 training sessions completed (operators, manager, owner)
- [ ] Training materials delivered (printed + PDF)
- [ ] 2-week soft launch completed with validation report
- [ ] Full system go-live
- [ ] 6-month support agreement active

### Milestone

Owner receives a WhatsApp message: "Q-Vision is LIVE. Gate 1: ✅ Online. Gate 2: ✅ Online. Gate 3: ✅ Online. Today's first truck: TN38AB1234, 12mm, 18.5T, 6:42 AM. All systems normal."

---

---

## Complete Deliverables Summary

| # | Deliverable | Phase |
|---|------------|-------|
| 1 | Stone grade classification (6mm, 10mm, 12mm, 20mm) | Phase 1 |
| 2 | 5-zone analysis with contamination detection | Phase 1 |
| 3 | Camera calibration system (auto + manual) | Phase 1 |
| 4 | Accuracy validation report with client's material | Phase 1 |
| 5 | Live RTSP camera integration (multi-gate) | Phase 2 |
| 6 | Automatic truck detection and frame capture | Phase 2 |
| 7 | 24/7 operation with day/night mode | Phase 2 |
| 8 | Auto-restart and crash recovery | Phase 2 |
| 9 | Number plate recognition (ANPR) | Phase 3 |
| 10 | Vehicle database with authorization management | Phase 3 |
| 11 | Entry/exit matching with unauthorized alerts | Phase 3 |
| 12 | Repeat offender tracking | Phase 3 |
| 13 | Weighbridge data integration | Phase 4 |
| 14 | Daily material balance (produced vs dispatched vs stock) | Phase 4 |
| 15 | Theft alert engine (6+ anomaly types) | Phase 4 |
| 16 | Shift-wise accountability reports | Phase 4 |
| 17 | Web dashboard with real-time monitoring | Phase 5 |
| 18 | Mobile-optimized view | Phase 5 |
| 19 | Role-based access (Owner / Manager / Operator) | Phase 5 |
| 20 | Encrypted database (SQLCipher) | Phase 5 |
| 21 | Split storage with auto-purge | Phase 5 |
| 22 | Dual dashboard mode (Operator / Owner) | Phase 5 |
| 23 | SMS/WhatsApp alert system | Phase 5 |
| 24 | PDF report generation | Phase 5 |
| 25 | Emergency data wipe | Phase 5 |
| 26 | On-site hardware installation | Phase 6 |
| 27 | Per-gate calibration and tuning | Phase 6 |
| 28 | Operator, Manager, Owner training | Phase 6 |
| 29 | Soft launch + validation | Phase 6 |
| 30 | 6-month post-deployment support | Phase 6 |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Camera gives poor image quality | Classification accuracy drops | Test cameras before bulk purchase; use 4MP+ resolution |
| Dusty/muddy number plates | ANPR fails to read | Image enhancement pipeline; manual correction fallback |
| Power cuts at quarry | System goes down | UPS backup (1–2 hrs); auto-start on power resume |
| Night lighting poor | Night classification unreliable | IR cameras with built-in LEDs; test night mode during Phase 2 |
| Client's material varies by season | Thresholds need re-tuning | Phase 6 support includes recalibration; configurable thresholds |
| Operator resistance | Staff may try to bypass system | Training + owner oversight + tamper-proof logs |
| Network cable damage | Gate-to-owner sync breaks | Use protected cable conduit; USB backup as secondary |

---

## Investment Summary

| Phase | Amount | Payment Trigger |
|-------|--------|-----------------|
| Phase 1: Core Intelligence Engine | ₹12,00,000 | Included in 40% advance |
| Phase 2: Live Surveillance & Auto-Capture | ₹10,00,000 | Phase 1–2 demo delivery |
| Phase 3: Vehicle Identification (ANPR) | ₹8,00,000 | Phase 3–5 delivery |
| Phase 4: Reconciliation & Theft Detection | ₹8,00,000 | Phase 3–5 delivery |
| Phase 5: Dashboard, Mobile & Data Security | ₹7,00,000 | Phase 3–5 delivery |
| Phase 6: Deployment, Training & Support | ₹5,00,000 | Final deployment |
| **Total** | **₹50,00,000** | |
| Hardware (client's cost, separate) | ₹3,00,000 – ₹5,00,000 | Client procures directly |

---

*Document version 1.0 — March 2026*
