import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd

DB_PATH = Path(__file__).parent / "malaria.db"


def get_connection():
    """Return a new sqlite3 connection. Caller is responsible for closing it,
    or use it inside a `with` block."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the table if it doesn't exist yet. Safe to call multiple times."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS state_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                month TEXT NOT NULL,          -- stored as 'DD-MM-YYYY' to match existing CSVs
                log_cases REAL NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(state, month)
            )
            """
        )
        conn.commit()


def list_states() -> list[str]:
    """Return a sorted list of distinct state names currently in the database."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT state FROM state_data ORDER BY state"
        ).fetchall()
    return [r[0] for r in rows]


def get_state_data(state: str) -> pd.DataFrame:
    """Return all records for a state as a DataFrame, sorted by month (chronological)."""
    with get_connection() as conn:
        df = pd.read_sql_query(
            "SELECT month, log_cases FROM state_data WHERE state = ? ORDER BY month",
            conn,
            params=(state.lower(),),
        )
    if not df.empty:
        # Parse 'DD-MM-YYYY' for correct chronological sort, then format back
        df["_sort"] = pd.to_datetime(df["month"], format="%d-%m-%Y")
        df = df.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)
    df.rename(columns={"log_cases": "LogCases", "month": "Month"}, inplace=True)
    return df


def add_or_update_value(state: str, month: str, log_cases: float):
    """
    Insert a new (state, month) record, or update it if that month already
    exists for that state.

    state    : e.g. "assam"  (will be lowercased/stripped for consistency)
    month    : string in 'DD-MM-YYYY' format, e.g. "01-05-2024"
    log_cases: float value
    """
    state = state.strip().lower()
    # validate the date format early so bad input fails loudly, not silently
    datetime.strptime(month, "%d-%m-%Y")

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO state_data (state, month, log_cases, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(state, month) DO UPDATE SET
                log_cases = excluded.log_cases,
                updated_at = excluded.updated_at
            """,
            (state, month, log_cases, datetime.utcnow().isoformat()),
        )
        conn.commit()


def delete_value(state: str, month: str):
    """Delete a specific (state, month) record."""
    state = state.strip().lower()
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM state_data WHERE state = ? AND month = ?",
            (state, month),
        )
        conn.commit()


def bulk_add_dataframe(state: str, df: pd.DataFrame):
    """
    Add/update many rows at once from a DataFrame with columns ['Month', 'LogCases'].
    Used by the CSV migration script, but also handy for bulk CSV upload from the UI.
    """
    state = state.strip().lower()
    with get_connection() as conn:
        now = datetime.utcnow().isoformat()
        rows = [
            (state, str(row["Month"]).strip(), float(row["LogCases"]), now)
            for _, row in df.iterrows()
        ]
        conn.executemany(
            """
            INSERT INTO state_data (state, month, log_cases, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(state, month) DO UPDATE SET
                log_cases = excluded.log_cases,
                updated_at = excluded.updated_at
            """,
            rows,
        )
        conn.commit()
