"""
dashboard.py — Streamlit dashboard for Q-Vision aggregate size verification.

Run with:
    streamlit run dashboard.py
"""

import os
import tempfile

import cv2
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from classification import check_mismatch, classify_load, classify_zone
from logger import get_history, get_stats, init_db
from main import run_pipeline
from measurement import compute_distribution, measure_particles
from segmentation import preprocess, segment_stones, separate_touching_stones
from utils import draw_contours_with_labels, load_image, resize_if_needed
from zones import draw_zones, extract_zones

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Q-Vision — Aggregate Verification",
    page_icon="🪨",
    layout="wide",
)

st.title("🪨 Q-Vision — AI-Based Aggregate Size Verification")
st.caption(
    "Classical OpenCV pipeline for verifying crushed stone aggregate sizes "
    "loaded in quarry dispatch trucks."
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    truck_id = st.text_input("Truck ID", value="TRUCK-001")
    expected_material = st.selectbox(
        "Expected material (from invoice)",
        options=["(none)", "6mm", "12mm", "20mm", "msand"],
    )
    if expected_material == "(none)":
        expected_material = None

    st.divider()
    st.subheader("� Calibration")
    st.caption("Camera held at approx **30–35 cm** above the stone surface.")
    calibration_mode = st.radio(
        "Calibration mode",
        options=[
            "Auto (detect ruler in image)",
            "Manual (enter px/mm value)",
        ],
        index=1,
        help="For a fixed-distance camera, use Manual mode with a pre-calibrated px/mm value.",
    )
    manual_px_per_mm = None
    if calibration_mode == "Manual (enter px/mm value)":
        manual_px_per_mm = st.number_input(
            "Pixels per mm",
            min_value=0.5,
            max_value=50.0,
            value=4.7374,
            step=0.1,
            format="%.4f",
            help="One-time setup: place a ruler at ~30 cm height, take a photo, "
                 "measure pixel distance between two marks, divide by mm. "
                 "E.g. if 100 px spans 10 mm → enter 10.0",
        )
    st.caption(
        "💡 **One-time calibration:** Place a ruler on the stone surface, "
        "take a photo at ~30 cm height, measure pixel distance of a known length, "
        "divide pixels ÷ mm = your px/mm value."
    )

    st.divider()
    st.subheader("�📊 Global Statistics")
    stats = get_stats()
    st.metric("Total Inspections", stats["total_inspections"])
    st.metric("Mixed-load Alerts", stats["mixed_count"])
    st.metric("Avg Confidence", f"{stats['avg_confidence']:.1f}%")

# ---------------------------------------------------------------------------
# Main area — tabs
# ---------------------------------------------------------------------------
tab_analyse, tab_history = st.tabs(["🔬 Analyse Image", "📋 Inspection History"])

# ===========================  ANALYSE TAB  ==================================
with tab_analyse:
    st.subheader("Upload Truck Bed Image")
    uploaded = st.file_uploader(
        "Choose an image (JPG / PNG / BMP)", type=["jpg", "jpeg", "png", "bmp"]
    )

    if uploaded is not None:
        # Save to a temporary file so OpenCV can read it
        suffix = os.path.splitext(uploaded.name)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        image = load_image(tmp_path)
        image = resize_if_needed(image)

        col_img, col_zones = st.columns(2)
        with col_img:
            st.image(
                cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
                caption="Original image",
                width="stretch",
            )
        with col_zones:
            zone_vis = draw_zones(image)
            st.image(
                cv2.cvtColor(zone_vis, cv2.COLOR_BGR2RGB),
                caption="Sampling zones",
                width="stretch",
            )

        if st.button("▶ Run Analysis", type="primary"):
            with st.spinner("Running pipeline…"):
                result = run_pipeline(tmp_path, truck_id, expected_material, manual_px_per_mm)

            # --- Classification result ---
            label = result["label"]
            confidence = result["confidence"]
            warning = result.get("warning", "")
            is_mixed = result.get("is_mixed", False)

            st.divider()
            # Prominent display of concluded material
            st.header(f"🎯 Concluded Material: {label}")
            if is_mixed:
                st.error("🚫 Mixed load detected — dispatch blocked!")
            elif label == "msand":
                st.success("✅ Verified as M-Sand (texture-based detection)")
            else:
                st.success(f"✅ Verified as {label} aggregate")

            r1, r2, r3 = st.columns(3)
            with r1:
                if is_mixed:
                    st.error(f"🚫 {label}")
                else:
                    st.success(f"✅ {label}")
            with r2:
                st.metric("Confidence", f"{confidence:.1f}%")
            with r3:
                if warning:
                    st.warning(warning)
                else:
                    st.info("No warnings")

            # --- Mismatch ---
            if expected_material and "mismatch" in result:
                mm = result["mismatch"]
                if mm["match"]:
                    st.success(mm["message"])
                else:
                    st.error(mm["message"])

            # --- Size distribution histogram ---
            dist = result.get("distribution", {})

            # --- M-Sand texture details (if detected) ---
            msand_details = result.get("msand_details", [])
            msand_zone_count = sum(1 for d in msand_details if d.get("is_msand"))
            if msand_zone_count > 0:
                st.subheader("🏖 M-Sand Texture Analysis")
                st.info(f"{msand_zone_count}/5 zones detected as M-Sand via texture analysis")
                tex_cols = st.columns(5)
                for i, (tc, md) in enumerate(zip(tex_cols, msand_details)):
                    with tc:
                        st.markdown(f"**Zone {i+1}**")
                        st.metric("Homogeneity", f"{md['homogeneity']:.3f}")
                        st.metric("Contrast", f"{md['contrast']:.1f}")
                        st.metric("Contours", md['contour_count'])
                        if md['is_msand']:
                            st.success("M-Sand ✓")
                        else:
                            st.caption("Stone")

            if dist.get("count", 0) > 0:
                st.subheader("📊 Particle Size Distribution")
                # Re-run measurement to get raw diameters for histogram
                hist_px_per_mm = result.get("px_per_mm", 5.0)
                zones = extract_zones(image)
                all_diameters = []
                for zone in zones:
                    prep = preprocess(zone)
                    mask = segment_stones(prep)
                    cnts, _ = separate_touching_stones(mask)
                    particles = measure_particles(cnts, hist_px_per_mm)
                    all_diameters.extend(p["diameter_mm"] for p in particles)

                if all_diameters:
                    fig, ax = plt.subplots(figsize=(8, 3))
                    ax.hist(all_diameters, bins=30, color="steelblue", edgecolor="white")
                    ax.axvspan(4, 8, alpha=0.15, color="green", label="6 mm class")
                    ax.axvspan(8, 12, alpha=0.15, color="orange", label="10 mm class")
                    ax.axvspan(16, 25, alpha=0.15, color="red", label="20 mm class")
                    ax.set_xlabel("Diameter (mm)")
                    ax.set_ylabel("Particle count")
                    ax.set_title("Equivalent Diameter Distribution")
                    ax.legend(fontsize=8)
                    st.pyplot(fig)
                    plt.close(fig)

                # Stats table
                st.subheader("📐 Distribution Statistics")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.table(
                        {
                            "Metric": ["Count", "Mean (mm)", "Median (mm)", "Std (mm)", "Min (mm)", "Max (mm)"],
                            "Value": [
                                int(dist["count"]),
                                round(dist['mean_mm'], 2),
                                round(dist['median_mm'], 2),
                                round(dist['std_mm'], 2),
                                round(dist['min_mm'], 2),
                                round(dist['max_mm'], 2),
                            ],
                        }
                    )
                with col_b:
                    st.table(
                        {
                            "Size Class": ["0-8 mm (6mm)", "8-18 mm (12mm)", "18-50 mm (20mm)", "Other"],
                            "% of particles": [
                                f"{dist['pct_6mm']:.1f}%",
                                f"{dist['pct_12mm']:.1f}%",
                                f"{dist['pct_20mm']:.1f}%",
                                f"{dist['pct_other']:.1f}%",
                            ],
                        }
                    )

            # --- Zone breakdown ---
            st.subheader("🗺 Zone-by-Zone Results")
            zone_cols = st.columns(5)
            zone_names = ["Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right", "Center"]
            zone_colors = ["🔵", "🟢", "🔴", "🟡", "🟣"]
            for i, (zcol, zr) in enumerate(zip(zone_cols, result.get("zone_details", []))):
                with zcol:
                    st.markdown(f"{zone_colors[i]} **Zone {i+1}**")
                    st.caption(zone_names[i])
                    lbl = zr.get("label", "?")
                    conf = zr.get("confidence_pct", 0)
                    if lbl == "msand":
                        st.info(f"{lbl} — {conf:.0f}%")
                    elif lbl == "mixed":
                        st.warning(f"{lbl} — {conf:.0f}%")
                    else:
                        st.success(f"{lbl} — {conf:.0f}%")

        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

# ===========================  HISTORY TAB  ==================================
with tab_history:
    st.subheader("Recent Inspection Logs")
    history = get_history(limit=50)
    if history:
        import pandas as pd

        df = pd.DataFrame(history)[
            ["id", "timestamp", "truck_id", "classification", "confidence", "warning", "is_mixed"]
        ]
        df["is_mixed"] = df["is_mixed"].map({0: "No", 1: "Yes"})
        st.dataframe(df, width="stretch")
    else:
        st.info("No inspection records found. Run an analysis to populate the log.")
