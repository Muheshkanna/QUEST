"""Turso (libSQL cloud) + local SQLite fallback database layer for QUEST.

Uses Turso when TURSO_DATABASE_URL and TURSO_AUTH_TOKEN are set in the environment
(production / Vercel). Falls back to local SQLite for offline development so you
never need a Turso account just to run the project locally.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import httpx


def _use_turso() -> bool:
    """Return True when Turso credentials are present in the environment."""
    return bool(TURSO_URL and TURSO_TOKEN)


# ---------------------------------------------------------------------------
# DDL (shared between both backends – libSQL is SQLite-compatible)
# ---------------------------------------------------------------------------

_CREATE_USERS_DDL = """
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
_CREATE_INDEX_DDL = "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);"

# ---------------------------------------------------------------------------
# Local SQLite helpers (development fallback)
# ---------------------------------------------------------------------------


def _get_local_db_path() -> Path:
    candidates = [
        Path(__file__).resolve().parents[2] / "data" / "users.db",
        Path.cwd() / "data" / "users.db",
        Path(__file__).resolve().parents[2] / ".data" / "users.db",
    ]
    for c in candidates:
        if c.parent.is_dir():
            return c
    return Path.cwd() / "users.db"


def _local_connection() -> sqlite3.Connection:
    db_path = _get_local_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Turso helpers (synchronous HTTP pipeline via httpx - avoids event loop conflicts)
# ---------------------------------------------------------------------------


def _get_turso_config() -> tuple[str, str]:
    """Return normalized (url, token) for Turso."""
    url = os.environ.get("TURSO_DATABASE_URL", "").strip()
    if url.startswith("libsql://"):
        url = "https://" + url[len("libsql://"):]
    elif url.startswith("http://"):
        url = "https://" + url[len("http://"):]
    url = url.rstrip("/")
    token = os.environ.get("TURSO_AUTH_TOKEN", "").strip()
    return url, token


def _use_turso() -> bool:
    """Return True when Turso credentials are present in the environment."""
    url, token = _get_turso_config()
    return bool(url and token)


def _format_hrana_arg(val: Any) -> dict:
    if val is None:
        return {"type": "null"}
    elif isinstance(val, bool):
        return {"type": "integer", "value": "1" if val else "0"}
    elif isinstance(val, int):
        return {"type": "integer", "value": str(val)}
    elif isinstance(val, float):
        return {"type": "float", "value": val}
    elif isinstance(val, bytes):
        import base64
        return {"type": "blob", "base64": base64.b64encode(val).decode("ascii")}
    else:
        return {"type": "text", "value": str(val)}


def _turso_execute(sql: str, args: tuple = ()) -> list[dict]:
    """Execute one SQL statement against Turso HTTP /v2/pipeline synchronously."""
    url, token = _get_turso_config()
    hrana_args = [_format_hrana_arg(a) for a in args]
    payload = {
        "requests": [
            {"type": "execute", "stmt": {"sql": sql, "args": hrana_args}}
        ]
    }
    with httpx.Client(timeout=10.0) as client:
        resp = client.post(
            f"{url}/v2/pipeline",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    res = data["results"][0]
    if res.get("type") == "error":
        err_msg = res.get("error", {}).get("message", "Turso query error")
        raise RuntimeError(f"Turso error: {err_msg}")

    result = res.get("response", {}).get("result", {})
    cols = [c["name"] for c in result.get("cols", [])]
    rows = []
    for raw_row in result.get("rows", []):
        row_dict = {}
        for c, cell in zip(cols, raw_row):
            row_dict[c] = cell.get("value")
        rows.append(row_dict)
    return rows


def _turso_batch(statements: list[dict]) -> None:
    """Execute multiple statements as a single Turso pipeline transaction."""
    url, token = _get_turso_config()
    requests = []
    for s in statements:
        sql = s["sql"]
        raw_args = s.get("args", [])
        hrana_args = [_format_hrana_arg(a) for a in raw_args]
        requests.append({"type": "execute", "stmt": {"sql": sql, "args": hrana_args}})

    payload = {"requests": requests}
    with httpx.Client(timeout=10.0) as client:
        resp = client.post(
            f"{url}/v2/pipeline",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    for res in data.get("results", []):
        if res.get("type") == "error":
            err_msg = res.get("error", {}).get("message", "Turso batch error")
            raise RuntimeError(f"Turso batch error: {err_msg}")


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with a random 16-byte salt."""
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{salt.hex()}${derived.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against the stored salt$hash in constant time."""
    if not stored_hash or "$" not in stored_hash:
        return False
    try:
        salt_hex, hash_hex = stored_hash.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000).hex()
        return secrets.compare_digest(hash_hex, expected)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Schema initialisation
# ---------------------------------------------------------------------------


def init_db() -> None:
    if _use_turso():
        _turso_batch([
            {"sql": _CREATE_USERS_DDL, "args": []},
            {"sql": _CREATE_INDEX_DDL, "args": []},
        ])
        return
    # Local SQLite
    conn = _local_connection()
    try:
        with conn:
            conn.execute(_CREATE_USERS_DDL)
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(users);")
            columns = [row["name"] for row in cur.fetchall()]
            if "password_hash" not in columns:
                conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT DEFAULT '';")
            conn.execute(_CREATE_INDEX_DDL)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Row → profile dict
# ---------------------------------------------------------------------------


def _row_to_profile(row: dict, include_hash: bool = False) -> Dict[str, Any]:
    state_data: Dict[str, Any] = {}
    try:
        state_data = json.loads(row.get("state_json") or "{}")
    except Exception:
        state_data = {}
    result: Dict[str, Any] = {
        "name": row["display_name"],
        "grade": int(row["grade"]),
        "level": int(row["level"]),
        "currentXp": int(row["current_xp"]),
        "xpToNextLevel": int(row["xp_to_next_level"]),
        "totalXp": int(row["total_xp"]),
        "streakDays": int(row["streak_days"]),
        "streakShields": int(row["streak_shields"]),
        "equippedTitle": row.get("equipped_title") or "Seeker Initiate",
        "hasPassword": bool(row.get("password_hash")),
        "state": state_data,
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }
    if include_hash:
        result["password_hash"] = row.get("password_hash", "")
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_user(name: str, include_hash: bool = False) -> Optional[Dict[str, Any]]:
    clean_name = name.strip()
    if not clean_name:
        return None
    key = clean_name.lower()
    init_db()

    _SELECT_SQL = """
        SELECT username, display_name, password_hash, grade, level, current_xp,
               xp_to_next_level, total_xp, streak_days, streak_shields,
               equipped_title, state_json, created_at, updated_at
        FROM users WHERE username = ?
    """

    if _use_turso():
        rows = _turso_execute(_SELECT_SQL, (key,))
        if not rows:
            return None
        return _row_to_profile(rows[0], include_hash=include_hash)

    conn = _local_connection()
    try:
        cur = conn.cursor()
        cur.execute(_SELECT_SQL, (key,))
        row = cur.fetchone()
        if not row:
            return None
        return _row_to_profile(dict(row), include_hash=include_hash)
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

    if get_user(display_name) is not None:
        raise ValueError(
            f"A scholar with the name '{display_name}' already exists. "
            "Please choose a unique name or sign in."
        )

    pwd_hash = hash_password(password.strip())
    now_iso = datetime.now(timezone.utc).isoformat()

    _INSERT_SQL = """
        INSERT INTO users (
            username, display_name, password_hash, grade, level, current_xp,
            xp_to_next_level, total_xp, streak_days, streak_shields,
            equipped_title, state_json, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    args = (key, display_name, pwd_hash, grade, 1, 0, 1000, 0, 0, 0, "Seeker Initiate", "{}", now_iso, now_iso)

    if _use_turso():
        _turso_execute(_INSERT_SQL, args)
    else:
        conn = _local_connection()
        try:
            with conn:
                conn.execute(_INSERT_SQL, args)
        finally:
            conn.close()

    return get_user(display_name) or {}


def authenticate_user(name: str, password: str) -> Dict[str, Any]:
    """Authenticate a returning scholar by name and password, restoring their saved session."""
    display_name = name.strip()
    if not display_name:
        raise ValueError("Scholar name is required")
    if not password:
        raise ValueError("Password is required to access your saved session")

    user = get_user(display_name, include_hash=True)
    if not user:
        raise LookupError(f"Scholar '{display_name}' not found. Please create an account.")

    stored_hash = user.get("password_hash", "")
    if stored_hash and not verify_password(password.strip(), stored_hash):
        raise PermissionError("Incorrect password for this scholar account. Please try again.")

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
    state_json_str = json.dumps(state_obj)
    now_iso = datetime.now(timezone.utc).isoformat()
    init_db()

    existing = get_user(display_name, include_hash=True)
    existing_hash = existing.get("password_hash", "") if existing else ""
    pwd_hash = hash_password(password.strip()) if password and password.strip() else existing_hash

    _UPSERT_SQL = """
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
    """
    args = (
        key, display_name, pwd_hash, grade,
        level, current_xp, xp_to_next, total_xp,
        streak_days, streak_shields, equipped_title,
        state_json_str, now_iso, now_iso,
    )

    if _use_turso():
        _turso_execute(_UPSERT_SQL, args)
    else:
        conn = _local_connection()
        try:
            with conn:
                conn.execute(_UPSERT_SQL, args)
        finally:
            conn.close()

    return get_user(display_name) or {}
