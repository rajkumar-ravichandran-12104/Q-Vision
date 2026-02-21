"""
logger.py — SQLite logging for Q-Vision classification results.
"""

import json
import sqlite3
from datetime import datetime

from config import DB_PATH


def init_db(db_path: str = DB_PATH) -> None:
    """
    Create the SQLite results table if it does not already exist.

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS results (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp         TEXT    NOT NULL,
                truck_id          TEXT,
                image_path        TEXT,
                classification    TEXT,
                confidence        REAL,
                distribution_json TEXT,
                zones_json        TEXT,
                warning           TEXT,
                is_mixed          INTEGER
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def log_result(truck_id: str, image_path: str, result: dict, db_path: str = DB_PATH) -> None:
    """
    Insert a classification result into the database.

    Parameters
    ----------
    truck_id : str
        Identifier for the truck being inspected.
    image_path : str
        Path to the analysed image.
    result : dict
        Output of :func:`classification.classify_load`, optionally augmented
        with a 'distribution' key containing the overall size distribution.
    db_path : str
        Path to the SQLite database file.
    """
    init_db(db_path)
    ts = datetime.utcnow().isoformat()
    label = result.get("label", "")
    confidence = result.get("confidence", 0.0)
    distribution_json = json.dumps(result.get("distribution", {}))
    zones_json = json.dumps(result.get("zone_details", []), default=str)
    warning = result.get("warning", "")
    is_mixed = int(result.get("is_mixed", False))

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO results
                (timestamp, truck_id, image_path, classification, confidence,
                 distribution_json, zones_json, warning, is_mixed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (ts, truck_id, image_path, label, confidence,
             distribution_json, zones_json, warning, is_mixed),
        )
        conn.commit()
    finally:
        conn.close()


def get_history(limit: int = 50, db_path: str = DB_PATH) -> list:
    """
    Retrieve recent classification results.

    Parameters
    ----------
    limit : int
        Maximum number of rows to return (most recent first).
    db_path : str
        Path to the SQLite database file.

    Returns
    -------
    list[dict]
        List of result records as dictionaries.
    """
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM results ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_stats(db_path: str = DB_PATH) -> dict:
    """
    Aggregate statistics across all inspection records.

    Returns
    -------
    dict
        Keys:
        - 'total_inspections': int
        - 'mixed_count': int
        - 'classification_counts': dict mapping label -> count
        - 'avg_confidence': float
    """
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        total = conn.execute("SELECT COUNT(*) FROM results").fetchone()[0]
        mixed = conn.execute(
            "SELECT COUNT(*) FROM results WHERE is_mixed = 1"
        ).fetchone()[0]
        avg_conf = conn.execute(
            "SELECT AVG(confidence) FROM results"
        ).fetchone()[0] or 0.0
        rows = conn.execute(
            "SELECT classification, COUNT(*) as cnt FROM results GROUP BY classification"
        ).fetchall()
        classification_counts = {r[0]: r[1] for r in rows}
    finally:
        conn.close()

    return {
        "total_inspections": total,
        "mixed_count": mixed,
        "classification_counts": classification_counts,
        "avg_confidence": round(avg_conf, 2),
    }
