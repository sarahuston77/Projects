import os
import sqlite3
from datetime import date, datetime, timedelta

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


def get_logging_streak(today=None):
    """Number of consecutive days (ending today) with at least one log entry."""
    if today is None:
        today = date.today()

    with _connect() as conn:
        rows = conn.execute(
            "SELECT DISTINCT substr(created_at, 1, 10) AS day FROM log_entries"
        ).fetchall()

    logged_days = {row["day"] for row in rows}
    streak = 0
    cursor = today
    while cursor.isoformat() in logged_days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _streak_banner(streak):
    if streak == 0:
        return "Log today to start a streak!"
    milestones = {7: "🎉 One full week!", 30: "🏆 30 days strong!", 100: "🌟 100 days!"}
    suffix = f"  {milestones[streak]}" if streak in milestones else ""
    return f"🔥 {streak}-day logging streak!{suffix}"


def format_weekly_summary(days=7):
    logs = get_logs_since(days)
    streak = get_logging_streak()

    if not logs:
        return (
            "No sleep or mood logs yet.\nLog today to start your history.\n\n"
            + _streak_banner(streak)
        )

    by_day = {}
    sleep_values, mood_values = [], []
    for row in logs:
        dt = datetime.fromisoformat(row["created_at"])
        day_key = dt.date().isoformat()
        if day_key not in by_day:
            by_day[day_key] = {"label": dt.strftime("%a %b %d"), "sleep": None, "mood": None}
        by_day[day_key][row["entry_type"]] = row["value"]
        if row["entry_type"] == "sleep":
            sleep_values.append(row["value"])
        elif row["entry_type"] == "mood":
            mood_values.append(row["value"])

    def _avg(values):
        return f"{sum(values) / len(values):.1f}" if values else "—"

    lines = [
        f"This week (last {days} days):",
        f"  Average sleep: {_avg(sleep_values)}    Average mood: {_avg(mood_values)}",
        f"  {_streak_banner(streak)}",
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
