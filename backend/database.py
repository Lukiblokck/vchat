# ─────────────────────────────────────────────
#  database.py  –  SQLite: setup y consultas
# ─────────────────────────────────────────────

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "chat.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea las tablas si no existen. Migra columnas nuevas si ya existía la BD."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS messages (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                room      TEXT    NOT NULL DEFAULT 'general',
                username  TEXT    NOT NULL,
                text      TEXT    NOT NULL,
                type      TEXT    NOT NULL DEFAULT 'text',
                timestamp TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS users_online (
                code      TEXT PRIMARY KEY,
                username  TEXT NOT NULL,
                room      TEXT NOT NULL DEFAULT 'general',
                joined_at TEXT NOT NULL
            );
        """)
        # migración: añade columna 'type' si la BD ya existía sin ella
        cols = [r[1] for r in conn.execute("PRAGMA table_info(messages)").fetchall()]
        if "type" not in cols:
            conn.execute("ALTER TABLE messages ADD COLUMN type TEXT NOT NULL DEFAULT 'text'")


def save_message(room: str, username: str, text: str, msg_type: str = "text") -> dict:
    timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO messages (room, username, text, type, timestamp) VALUES (?, ?, ?, ?, ?)",
            (room, username, text, msg_type, timestamp),
        )
        return {
            "id": cursor.lastrowid,
            "room": room,
            "username": username,
            "text": text,
            "type": msg_type,
            "timestamp": timestamp,
        }


def get_recent_messages(room: str, limit: int = 50) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, room, username, text, type, timestamp
            FROM messages
            WHERE room = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (room, limit),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]