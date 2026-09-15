"""Privacy-minimized SQLite storage for local pilot sessions."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    condition_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    consent_version TEXT NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS trials (
    session_id TEXT NOT NULL,
    trial_index INTEGER NOT NULL,
    event_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    PRIMARY KEY (session_id, trial_index),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);
"""


class StudyStore:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def create_session(self, session_id: str, condition: str, created_at: str) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO sessions VALUES (?, ?, ?, ?, 0)",
                (session_id, condition, created_at, "pilot-v1"),
            )

    def save_trial(
        self, session_id: str, trial: int, event_id: str, payload: dict[str, object]
    ) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO trials VALUES (?, ?, ?, ?)",
                (session_id, trial, event_id, json.dumps(payload)),
            )

    def complete(self, session_id: str) -> None:
        with self.connect() as connection:
            connection.execute(
                "UPDATE sessions SET completed = 1 WHERE session_id = ?", (session_id,)
            )

    def delete_session(self, session_id: str) -> bool:
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            return cursor.rowcount > 0
