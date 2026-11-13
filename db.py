"""Kichik SQLite ombor: foydalanuvchi tili va kunlik foydalanish soni."""
import sqlite3
import threading
from datetime import datetime

import config

_lock = threading.Lock()
_conn = None


def _db():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
        _conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, lang TEXT)")
        _conn.execute(
            "CREATE TABLE IF NOT EXISTS usage ("
            "user_id INTEGER, day TEXT, cnt INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (user_id, day))"
        )
        _conn.commit()
    return _conn


def today():
    return datetime.now(config.TZ).strftime("%Y-%m-%d")


def get_lang(uid):
    with _lock:
        row = _db().execute("SELECT lang FROM users WHERE id=?", (uid,)).fetchone()
    return row[0] if row and row[0] in config.LANGS else None


def set_lang(uid, lang):
    with _lock:
        c = _db()
        c.execute(
            "INSERT INTO users (id, lang) VALUES (?, ?) "
            "ON CONFLICT(id) DO UPDATE SET lang=excluded.lang",
            (uid, lang),
        )
        c.commit()


def used_today(uid):
    with _lock:
        row = _db().execute("SELECT cnt FROM usage WHERE user_id=? AND day=?", (uid, today())).fetchone()
    return row[0] if row else 0


def add_usage(uid):
    with _lock:
        c = _db()
        c.execute(
            "INSERT INTO usage (user_id, day, cnt) VALUES (?, ?, 1) "
            "ON CONFLICT(user_id, day) DO UPDATE SET cnt=cnt+1",
            (uid, today()),
        )
        c.commit()


def left_today(uid):
    """Qolgan limit; adminlar uchun None (cheksiz)."""
    if uid in config.ADMIN_IDS:
        return None
    return max(0, config.DAILY_LIMIT - used_today(uid))
