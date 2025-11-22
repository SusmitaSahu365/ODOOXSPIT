import sqlite3
import os
from flask import g

# Database file placed next to this module (backend/stockmaster.db)
DB_PATH = os.path.join(os.path.dirname(__file__), "stockmaster.db")


def get_db():
    """Return a database connection for the current Flask request context.

    Connections are stored on `flask.g` and closed automatically at teardown.
    This avoids leaving multiple open connections that can cause "database is locked".
    """
    if "db" not in g:
        # increase timeout and allow threaded access in dev server
        g.db = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Create the database tables if they don't exist.

    This function opens/closes its own connection so it won't keep the DB locked.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login_id TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        );
    """)
    # Table to store one-time-passwords for password resets
    conn.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login_id TEXT,
            otp TEXT,
            expires_at INTEGER,
            used INTEGER DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()

    # No extra columns required when password-reset flow is disabled.


def init_app(app):
    """Register database teardown with the Flask app."""
    app.teardown_appcontext(close_db)
