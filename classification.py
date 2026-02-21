"""
classification.py — Rule-based aggregate classification, majority voting, and
mismatch detection for Q-Vision pipeline.
"""

from config import CLASSIFICATION_RULES, MAJORITY_THRESHOLD


def classify_zone(distribution: dict) -> dict:
    """
    Classify a single zone based on its size distribution.

    The zone is labelled with the aggregate class (6mm / 10mm / 20mm) whose
    percentage exceeds the configured ``min_pct`` threshold.  If no class
    reaches its threshold, the zone is labelled "mixed".

    Parameters
    ----------
    distribution : dict
        Output of :func:`measurement.compute_distribution`.

    Returns
    -------
    dict
        Keys: 'label', 'confidence_pct', 'distribution'
    """
    best_label = "mixed"
    best_pct = 0.0

    pct_map = {
        "6mm":  distribution.get("pct_6mm", 0.0),
        "10mm": distribution.get("pct_10mm", 0.0),
        "20mm": distribution.get("pct_20mm", 0.0),
    }

    for label, rule in CLASSIFICATION_RULES.items():
        pct = pct_map.get(label, 0.0)
        if pct >= rule["min_pct"] and pct > best_pct:
            best_label = label
            best_pct = pct

    # If no dominant class found, fall back to whichever has the most particles
    if best_label == "mixed":
        dominant = max(pct_map, key=pct_map.get)
        best_pct = pct_map[dominant]

    return {
        "label": best_label,
        "confidence_pct": round(best_pct, 2),
        "distribution": distribution,
    }


def classify_load(zone_results: list) -> dict:
    """
    Classify the entire truck load using majority voting across all zones.

    - ≥ MAJORITY_THRESHOLD (default 4) zones agree → classified (high confidence)
    - Exactly 3 zones agree → classified with "Possible contamination" warning
    - No majority → "MIXED LOAD"

    Parameters
    ----------
    zone_results : list[dict]
        Each element is the output of :func:`classify_zone`.

    Returns
    -------
    dict
        Keys: 'label', 'confidence', 'zone_details', 'warning', 'is_mixed'
    """
    if not zone_results:
        return {
            "label": "UNKNOWN",
            "confidence": 0.0,
            "zone_details": [],
            "warning": "No zones analysed.",
            "is_mixed": True,
        }

    label_votes: dict = {}
    for zr in zone_results:
        lbl = zr["label"]
        label_votes[lbl] = label_votes.get(lbl, 0) + 1

    # Best voted label
    best_label = max(label_votes, key=label_votes.get)
    vote_count = label_votes[best_label]
    total_zones = len(zone_results)

    # Average confidence across zones that voted for the winning label
    agreeing = [zr for zr in zone_results if zr["label"] == best_label]
    avg_confidence = (
        sum(z["confidence_pct"] for z in agreeing) / len(agreeing)
        if agreeing
        else 0.0
    )

    warning = ""
    is_mixed = False

    if vote_count >= MAJORITY_THRESHOLD:
        # High confidence
        pass
    elif vote_count == 3:
        warning = "Possible contamination detected — only 3/5 zones agree."
    else:
        # No majority
        best_label = "MIXED LOAD"
        is_mixed = True
        warning = "MIXED LOAD detected — no majority across zones. Dispatch blocked."
        avg_confidence = 0.0

    return {
        "label": best_label,
        "confidence": round(avg_confidence, 2),
        "zone_details": zone_results,
        "warning": warning,
        "is_mixed": is_mixed,
    }


def check_mismatch(classification: dict, expected_material: str) -> dict:
    """
    Compare the pipeline classification against the expected material from invoice.

    Parameters
    ----------
    classification : dict
        Output of :func:`classify_load`.
    expected_material : str
        Expected material label (e.g. "10mm").

    Returns
    -------
    dict
        Keys: 'match' (bool), 'message' (str)
    """
    detected = classification.get("label", "")
    match = detected.lower() == expected_material.lower()
    if match:
        message = (
            f"✅ Classification matches invoice: {detected} == {expected_material}"
        )
    else:
        message = (
            f"⚠️  MISMATCH — Detected: {detected} | Invoice expects: {expected_material}"
        )
    return {"match": match, "message": message}
