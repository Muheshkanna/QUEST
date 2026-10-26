"""SQLite database persistence for user profiles, grades, quest progression, and password authentication."""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def get_db_path() -> Path:
    candidates = [
        Path(__file__).resolve().parents[2] / "data" / "users.db",
        Path.cwd() / "data" / "users.db",
        Path(__file__).resolve().parents[2] / ".data" / "users.db",
    ]
    for c in candidates:
        if c.parent.is_dir():
            return c
    return Path.cwd() / "users.db"


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with random 16-byte salt."""
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{salt.hex()}${derived.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored salt$hash in constant time."""
    if not stored_hash or "$" not in stored_hash:
        return False
    try:
        salt_hex, hash_hex = stored_hash.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000).hex()
        return secrets.compare_digest(hash_hex, expected)
    except Exception:
        return False


def init_db() -> None:
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    password_hash TEXT DEFAULT '',
                    grade INTEGER NOT NULL DEFAULT 5,
                    level INTEGER NOT NULL DEFAULT 1,
                    current_xp INTEGER NOT NULL DEFAULT 0,
                    xp_to_next_level INTEGER NOT NULL DEFAULT 1000,
                    total_xp INTEGER NOT NULL DEFAULT 0,
                    streak_days INTEGER NOT NULL DEFAULT 0,
                    streak_shields INTEGER NOT NULL DEFAULT 0,
                    equipped_title TEXT DEFAULT 'Seeker Initiate',
                    state_json TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            # Automatic schema migration for password_hash column if table already exists
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(users);")
            columns = [row["name"] for row in cur.fetchall()]
            if "password_hash" not in columns:
                conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT DEFAULT '';")

            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);"
            )
    finally:
        conn.close()


def get_user(name: str, include_hash: bool = False) -> Optional[Dict[str, Any]]:
    clean_name = name.strip()
    if not clean_name:
        return None
    key = clean_name.lower()

    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT username, display_name, password_hash, grade, level, current_xp,
                   xp_to_next_level, total_xp, streak_days, streak_shields,
                   equipped_title, state_json, created_at, updated_at
            FROM users
            WHERE username = ?
            """,
            (key,),
        )
        row = cur.fetchone()
        if not row:
            return None

        state_data: Dict[str, Any] = {}
        if row["state_json"]:
            try:
                state_data = json.loads(row["state_json"])
            except Exception:
                state_data = {}

        result = {
            "name": row["display_name"],
            "grade": int(row["grade"]),
            "level": int(row["level"]),
            "currentXp": int(row["current_xp"]),
            "xpToNextLevel": int(row["xp_to_next_level"]),
            "totalXp": int(row["total_xp"]),
            "streakDays": int(row["streak_days"]),
            "streakShields": int(row["streak_shields"]),
            "equippedTitle": row["equipped_title"] or "Seeker Initiate",
            "hasPassword": bool(row["password_hash"]),
            "state": state_data,
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
        }
        if include_hash:
            result["password_hash"] = row["password_hash"]
        return result
    finally:
        conn.close()


def register_user(name: str, password: str, grade: int = 5) -> Dict[str, Any]:
    """Register a new unique scholar account with a password and grade."""
    display_name = name.strip()
    if not display_name:
        raise ValueError("Scholar name is required")
    if not password or len(password.strip()) < 3:
        raise ValueError("Password must be at least 3 characters long")
    if grade not in (5, 6):
        grade = 5

    key = display_name.lower()
    init_db()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE username = ?", (key,))
        if cur.fetchone():
            raise ValueError(f"A scholar with the name '{display_name}' already exists. Please choose a unique name or sign in.")

        pwd_hash = hash_password(password.strip())
        now_iso = datetime.now(timezone.utc).isoformat()

        with conn:
            conn.execute(
                """
                INSERT INTO users (
                    username, display_name, password_hash, grade, level, current_xp,
                    xp_to_next_level, total_xp, streak_days, streak_shields,
                    equipped_title, state_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    key,
                    display_name,
                    pwd_hash,
                    grade,
                    1,
                    0,
                    1000,
                    0,
                    0,
                    0,
                    "Seeker Initiate",
                    "{}",
                    now_iso,
                    now_iso,
                ),
            )
        return get_user(display_name) or {}
    finally:
        conn.close()


def authenticate_user(name: str, password: str) -> Dict[str, Any]:
    """Authenticate returning scholar by name and password, loading their saved session."""
    display_name = name.strip()
    if not display_name:
        raise ValueError("Scholar name is required")
    if not password:
        raise ValueError("Password is required to access your saved session")

    user = get_user(display_name, include_hash=True)
    if not user:
        raise LookupError(f"Scholar '{display_name}' not found. Please create an account.")

    stored_hash = user.get("password_hash", "")
    if stored_hash:
        if not verify_password(password.strip(), stored_hash):
            raise PermissionError("Incorrect password for this scholar account. Please try again.")

    # Return clean user profile without password hash
    return get_user(display_name) or {}


def save_user(data: Dict[str, Any], password: Optional[str] = None) -> Dict[str, Any]:
    display_name = str(data.get("name", "")).strip()
    if not display_name:
        raise ValueError("Name cannot be empty")
    key = display_name.lower()

    grade = int(data.get("grade", 5))
    if grade not in (5, 6):
        grade = 5

    level = max(1, int(data.get("level", 1)))
    current_xp = max(0, int(data.get("currentXp", 0)))
    xp_to_next = max(100, int(data.get("xpToNextLevel", 1000)))
    total_xp = max(0, int(data.get("totalXp", 0)))
    streak_days = max(0, int(data.get("streakDays", 0)))
    streak_shields = max(0, int(data.get("streakShields", 0)))
    equipped_title = str(data.get("equippedTitle") or "Seeker Initiate")

    state_obj = data.get("state")
    if not isinstance(state_obj, dict):
        state_obj = {}
    state_json = json.dumps(state_obj)

    now_iso = datetime.now(timezone.utc).isoformat()

    init_db()
    conn = get_connection()
    try:
        # Check if user has an existing password hash
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE username = ?", (key,))
        row = cur.fetchone()
        existing_hash = row["password_hash"] if row else ""

        pwd_hash = hash_password(password.strip()) if password and password.strip() else existing_hash

        with conn:
            conn.execute(
                """
                INSERT INTO users (
                    username, display_name, password_hash, grade, level, current_xp,
                    xp_to_next_level, total_xp, streak_days, streak_shields,
                    equipped_title, state_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    display_name = excluded.display_name,
                    password_hash = CASE WHEN excluded.password_hash != '' THEN excluded.password_hash ELSE users.password_hash END,
                    grade = excluded.grade,
                    level = excluded.level,
                    current_xp = excluded.current_xp,
                    xp_to_next_level = excluded.xp_to_next_level,
                    total_xp = excluded.total_xp,
                    streak_days = excluded.streak_days,
                    streak_shields = excluded.streak_shields,
                    equipped_title = excluded.equipped_title,
                    state_json = excluded.state_json,
                    updated_at = excluded.updated_at
                """,
                (
                    key,
                    display_name,
                    pwd_hash,
                    grade,
                    level,
                    current_xp,
                    xp_to_next,
                    total_xp,
                    streak_days,
                    streak_shields,
                    equipped_title,
                    state_json,
                    now_iso,
                    now_iso,
                ),
            )
        return get_user(display_name) or {}
    finally:
        conn.close()
