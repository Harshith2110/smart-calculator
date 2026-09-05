"""
database.py
------------
Handles all SQLite database operations for calculation history.

Uses Python's built-in sqlite3 module, so there's no extra dependency to
install. The database file (calculator.db) is created automatically the
first time the app runs.
"""

import os
import sqlite3
from datetime import datetime, timezone

DB_NAME = os.getenv("DB_PATH", "calculator.db")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Create the history table if it doesn't already exist."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expression TEXT NOT NULL,
            result TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'standard',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_calculation(expression: str, result: str, source: str = "standard"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO history (expression, result, source, created_at) VALUES (?, ?, ?, ?)",
        (expression, result, source, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def get_history(limit: int = 20):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def clear_history():
    conn = get_connection()
    conn.execute("DELETE FROM history")
    conn.commit()
    conn.close()


def get_stats():
    """Basic usage analytics: which operators are used most, total count."""
    conn = get_connection()
    rows = conn.execute("SELECT expression FROM history").fetchall()
    conn.close()

    total = len(rows)
    operator_counts = {"+": 0, "-": 0, "*": 0, "/": 0, "**": 0, "%": 0}
    for row in rows:
        expr = row["expression"]
        for op in operator_counts:
            operator_counts[op] += expr.count(op)

    most_used = max(operator_counts, key=operator_counts.get) if total else None
    return {
        "total_calculations": total,
        "operator_counts": operator_counts,
        "most_used_operator": most_used,
    }
