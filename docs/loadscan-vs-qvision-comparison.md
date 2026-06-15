# Loadscan vs Q-Vision

This document compares Loadscan and Q-Vision side by side based on publicly available Loadscan information and the current Q-Vision project scope.

## Executive Summary

Loadscan and Q-Vision operate in the same quarry dispatch environment, but they solve different primary problems.

- **Loadscan** is a payload measurement product focused on accurate truck and conveyor volume measurement using laser/LIDAR scanning hardware.
- **Q-Vision** is a dispatch intelligence product focused on aggregate grade verification, contamination detection, vehicle traceability, anomaly detection, and anti-theft monitoring using camera-based computer vision.

In simple terms:

- **Loadscan answers:** "How much material is this truck or conveyor carrying?"
- **Q-Vision answers:** "Is the right material leaving the site, in the right truck, at the right time, and is anything suspicious happening?"

## Side-by-Side Comparison

| Dimension | Loadscan | Q-Vision |
|---|---|---|
| Core problem solved | Accurate bulk payload volume measurement | Aggregate grade verification, dispatch control, and theft/anomaly monitoring |
| Primary technology | Laser/LIDAR volumetric scanning hardware | Camera-based computer vision |
| What it measures | Truck or conveyor volume | Stone size grade, contamination/mixed load, truck event evidence |
| Output focus | Quantity measurement | Material verification plus operational traceability |
| Accuracy claim | Publicly claims trade-certified volumetric accuracy around +/-1% | Current focus is classification accuracy for 6 mm, 10 mm, 12 mm, and 20 mm grade detection, not trade-certified quantity measurement |
| Hardware model | Purpose-built gantry/scanner systems, fixed/mobile/trailer/custom | Standard cameras plus local compute, lower infrastructure burden |
| Installation complexity | Higher, industrial hardware deployment | Lower, camera-gate deployment |
| Use at dispatch gate | Yes, mainly to verify quantity/payload | Yes, mainly to verify material type and dispatch legitimacy |
| Mixed-load detection | Indirect through scan/profile workflow | Direct design goal through 5-zone analysis and mismatch detection |
| Vehicle traceability | RFID and scanner-linked load records | Planned ANPR, truck-wise logging, entry/exit monitoring |
| Theft detection | Not the main product story | Core value proposition |
| Reconciliation | Payload and movement reporting | Planned production vs dispatch vs stock reconciliation |
| Alerts | Operational reporting and system outputs | Real-time anomaly alerts and owner notifications |
| Cloud/offline model | Includes MyScanner cloud service and proprietary ecosystem | Designed for offline/local ownership with split-storage security |
| Pricing model | Quote-based industrial capital purchase plus add-ons/support | Project/service delivery model tailored to quarry workflow |
| Best-fit buyer | Quarry or mining operator needing certified quantity measurement | Quarry owner needing dispatch surveillance, grade verification, and anti-theft control |
| Competitive position | Established industrial measurement incumbent | Workflow-focused, lighter-weight quarry intelligence system |

## Overlap and Difference

## Where They Overlap

- Quarry and mining dispatch operations
- Material movement visibility
- Reduction of disputes and losses
- Better operational records and decision support

## Where Loadscan Is Stronger

- Trade-grade volumetric measurement
- Industrial credibility and certifications
- Mature hardware product line
- Payload optimization for mining and bulk handling

## Where Q-Vision Is Stronger

- Material grade verification
- Mixed-load and contamination detection
- ANPR-linked dispatch control
- Theft detection and reconciliation workflow
- Offline, owner-controlled deployment
- Lower infrastructure and deployment complexity

## Strategic Positioning

Q-Vision should not be positioned as a direct replacement for Loadscan unless it also targets certified volumetric payload measurement.

The cleaner positioning is:

- **Loadscan:** payload quantity metrology
- **Q-Vision:** dispatch intelligence, grade verification, and anti-theft automation

## Practical Buying View

A quarry customer would typically choose between the two based on the primary business problem:

- If the main requirement is **high-confidence, trade-grade quantity measurement**, Loadscan is the more natural fit.
- If the main requirement is **dispatch surveillance, material mismatch detection, truck traceability, and theft prevention**, Q-Vision is the stronger fit.
- In some operations, the two could even be complementary: Loadscan for quantity measurement and Q-Vision for dispatch control and anomaly intelligence.

## Bottom Line

Loadscan is a **measurement product**.

Q-Vision is an **operations control product**.

They are related in market context, but they are not the same category of solution.