# Q-Vision — Saturday Call Agenda

**Date:** 31 May 2026 (Saturday, 11 AM)  
**Duration:** 20–30 minutes  
**Purpose:** Hardware purchase decision + Home POC plan + Software licensing

---

## 1. Hardware Needed (His Action — Purchase)

### Camera + Lenses (~₹55,000–75,000)

| Item | Model | Why | Cost |
|------|-------|-----|------|
| Industrial Camera | Hikrobot MV-CS200-10GC (20MP, GigE) | High resolution needed to detect even 6mm stones accurately | ₹35,000–45,000 |
| Field Lens | 16mm f/1.4, C-mount (≥1.1" sensor) | For quarry installation (1.5–2.5m distance) | ₹8,000–12,000 |
| Test Lens | 25mm f/1.4, C-mount (≥1.1" sensor) | For home POC testing (0.5–1.0m distance) | ₹8,000–12,000 |

> **Key point to mention:** Camera + lenses are reusable — same camera goes from home POC to field. Not buying twice.

### Accessories (~₹8,000–12,000)

- PoE Injector — ₹1,000 (single cable for power + data)
- Cat6 Ethernet cable (10–30m, outdoor) — ₹500–1,500
- IP67 Camera Enclosure — ₹3,000–5,000 (dust/rain protection at quarry)
- Mounting arm — ₹3,000–5,000

### Edge PC / Processing Machine (~₹30,000–50,000)

- Intel i5, 16GB RAM, 512GB SSD, Gigabit Ethernet port
- Options: Beelink Mini S12 Pro / Intel NUC / Mini tower
- Runs 24/7 at quarry site
- No GPU needed — current system doesn't require it

### Total Hardware: ~₹1,00,000–1,30,000 per station

---

## 2. Home POC Plan (My Action — Before Field Deployment)

**Tell him:** "Before we go to your quarry, I'll prove the entire system end-to-end at home with the same camera that'll go to field."

### What I'll Do

| Step | What | Timeline |
|------|------|----------|
| 1 | Receive camera + 25mm lens | After purchase (2–3 days shipping) |
| 2 | Set up on my desk — camera pointing down at stone samples | Day 1 |
| 3 | Calibrate with ruler at 0.5–1.0m distance | Day 1 |
| 4 | Test ALL 4 materials: 6mm, 12mm, 20mm, M-Sand | Day 2–3 |
| 5 | Run full pipeline: capture → segment → classify → log | Day 3 |
| 6 | Validate accuracy across all grades | Day 3–4 |
| 7 | Share results with him (photos + classification output) | Day 4 |

**POC Success Criteria:**
- All 4 materials classified correctly
- 90%+ accuracy
- Full pipeline running without manual intervention

**Duration:** 3–4 days after receiving hardware

> **Say this:** "Once home POC is validated, we swap the 25mm lens for 16mm lens and install at your quarry. Same camera, same software — just a lens change."

---

## 3. Software Licensing Discussion

**Context:** He mentioned product sales in the last meeting. This needs clarity.

### Frame it like this:

> *"Bhai, for your quarry deployment — that's a one-time project. I build it, install it, you own it. No monthly fees, no subscriptions.*
>
> *For the product idea — selling to other quarries — that's a separate business conversation. We can structure that as a partnership once your quarry is running and proven. But the first deployment is what makes the product credible."*

### What to establish on this call:

- **His quarry = paid project** (scope and investment to be shared in a follow-up document)
- **Product sales = future partnership** (discussed separately, after deployment is live)
- **No subscription model for him** — one-time investment for his own quarry
- **Licensing for other quarries** — to be structured together when the time comes

---

## 4. Things to Get From Him

### Must ask on this call:

| Question | Why You Need It |
|----------|----------------|
| "How many loading stations/gates?" | Determines how many cameras + PCs needed |
| "What truck types come to your quarry?" | Need bed height measurements for calibration |
| "Is night operation needed?" | If yes, add LED panel to budget |
| "Where exactly will the camera be mounted?" | Need height and position — affects lens choice |
| "Do you have an existing PC at site or buying new?" | Edge PC planning |
| "Who will be the on-site person during installation?" | Coordination for field visit |

### Development Machine — MacBook Air M5 (My Requirement)

**What to say:**

> *"For me to work on this full-time and access the field machine remotely from Chennai, I need a dedicated development machine. My office laptop can't be used — it's restricted. I'll need a MacBook Air M5. This is part of the project setup."*

| Item | Spec | Cost |
|------|------|------|
| MacBook Air M5 | 16GB RAM, 512GB SSD | ~₹1,30,000–1,50,000 |

**Why it's justified:**
- Office laptop has restrictions — can't install project tools or run remote access software
- Need to SSH/remote into the quarry field machine from Chennai (400km away)
- Need to run Python, OpenCV, camera SDK, testing — all locally
- This is the only machine that connects your development to his field deployment
- Without it, you literally cannot do the work

**Frame it as project cost, not personal purchase.**

---

### Nice to get (if conversation flows):

| Question | Why |
|----------|-----|
| "What's your timeline expectation?" | Align expectations |
| "Do you want me to send you a purchase list you can forward to dealer?" | Makes it easy for him to act |

---

## 5. Call Flow — How to Run the 20 Minutes

| Time | Topic | Your Tone |
|------|-------|-----------|
| 0–2 min | Quick greeting, "let me walk you through what we need" | Professional, energetic |
| 2–8 min | Hardware specs — camera, lenses, PC, total cost ~₹1–1.3L | Clear, factual |
| 8–12 min | Home POC plan — "I'll prove everything works before going to site" | Confident, reassuring |
| 12–15 min | Ask the questions (gates, trucks, night, mounting) | Curious, taking notes |
| 15–18 min | Software licensing — "your quarry is a project, product is separate" | Firm but casual |
| 18–20 min | Next step: "I'll send you the purchase list today + full plan this week" | Closing, action-oriented |

---

## 6. One Sentence About Pricing (Plant the Seed)

At the end, naturally say:

> *"I'll also send you the full deployment plan with the investment breakdown — so you have everything in one place."*

**Do NOT discuss ₹50L on this call.** Just mention the document is coming. Price discussion happens when he's read it or on the next call.

---

## After the Call — Immediate Actions

1. Send him **hardware purchase list** (models, dealer links, costs) — same day
2. Send him **deployment plan with pricing** — within 2–3 days
3. Order your own dev setup if needed
4. Wait for camera to arrive → start home POC
