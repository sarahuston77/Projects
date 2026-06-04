import os
import sqlite3
from datetime import datetime, timedelta

DB_NAME = "health_app.db"


def _app_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_db_path():
    data_dir = os.path.join(_app_dir(), "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, DB_NAME)


def _connect():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS log_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_type TEXT NOT NULL,
                value INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reminder_state (
                reminder_id TEXT NOT NULL,
                shown_date TEXT NOT NULL,
                PRIMARY KEY (reminder_id, shown_date)
            );
            """
        )


def save_log(entry_type, value):
    if entry_type not in ("sleep", "mood"):
        raise ValueError("entry_type must be 'sleep' or 'mood'")
    if not 1 <= value <= 10:
        raise ValueError("value must be between 1 and 10")

    created_at = datetime.now().isoformat(timespec="seconds")
    with _connect() as conn:
        conn.execute(
            "INSERT INTO log_entries (entry_type, value, created_at) VALUES (?, ?, ?)",
            (entry_type, value, created_at),
        )


def get_logs_since(days=7):
    cutoff = (datetime.now() - timedelta(days=days)).isoformat(timespec="seconds")
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT entry_type, value, created_at
            FROM log_entries
            WHERE created_at >= ?
            ORDER BY created_at DESC
            """,
            (cutoff,),
        ).fetchall()
    return [dict(row) for row in rows]


SPARK_BARS = "▁▂▃▄▅▆▇█"


def _spark_char(value):
    if value is None:
        return "·"
    idx = max(0, min(7, round((value - 1) * 7 / 9)))
    return SPARK_BARS[idx]


def format_weekly_summary(days=7):
    logs = get_logs_since(days)
    if not logs:
        return "No sleep or mood logs yet.\nLog today to start your history."

    by_day = {}
    for row in logs:
        dt = datetime.fromisoformat(row["created_at"])
        day_key = dt.date().isoformat()
        if day_key not in by_day:
            by_day[day_key] = {"label": dt.strftime("%a %b %d"), "sleep": None, "mood": None}
        by_day[day_key][row["entry_type"]] = row["value"]

    today = datetime.now().date()
    chrono_keys = [(today - timedelta(days=i)).isoformat() for i in range(days - 1, -1, -1)]
    sleep_series = [by_day.get(k, {}).get("sleep") for k in chrono_keys]
    mood_series = [by_day.get(k, {}).get("mood") for k in chrono_keys]

    sleep_present = [v for v in sleep_series if v is not None]
    mood_present = [v for v in mood_series if v is not None]
    sleep_avg = f"{sum(sleep_present)/len(sleep_present):.1f}" if sleep_present else "—"
    mood_avg = f"{sum(mood_present)/len(mood_present):.1f}" if mood_present else "—"

    sleep_spark = "".join(_spark_char(v) for v in sleep_series)
    mood_spark = "".join(_spark_char(v) for v in mood_series)

    lines = [
        f"This week (last {days} days):",
        "",
        f"Sleep:  {sleep_spark}   avg {sleep_avg}",
        f"Mood:   {mood_spark}   avg {mood_avg}",
        "",
    ]
    for day_key in sorted(by_day.keys(), reverse=True):
        parts = by_day[day_key]
        sleep = parts["sleep"] if parts["sleep"] is not None else "—"
        mood = parts["mood"] if parts["mood"] is not None else "—"
        lines.append(f"{parts['label']}:  sleep {sleep},  mood {mood}")

    return "\n".join(lines)


def mark_reminder_shown(reminder_id, shown_date=None):
    if shown_date is None:
        shown_date = datetime.now().date().isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO reminder_state (reminder_id, shown_date)
            VALUES (?, ?)
            """,
            (reminder_id, shown_date),
        )


def was_reminder_shown_today(reminder_id, today=None):
    if today is None:
        today = datetime.now().date().isoformat()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT 1 FROM reminder_state
            WHERE reminder_id = ? AND shown_date = ?
            """,
            (reminder_id, today),
        ).fetchone()
    return row is not None


def get_due_reminders(reminder_configs, now=None):
    if now is None:
        now = datetime.now()

    today = now.date().isoformat()
    current_time = now.time().replace(second=0, microsecond=0)
    due = []

    for reminder in reminder_configs:
        reminder_id = reminder["id"]
        if was_reminder_shown_today(reminder_id, today):
            continue
        scheduled = reminder["time_obj"]
        if current_time >= scheduled:
            due.append(reminder)

    due.sort(key=lambda r: r["time_obj"])
    return due
