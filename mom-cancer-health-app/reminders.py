import json
import os
from datetime import datetime, time


def _app_dir():
    return os.path.dirname(os.path.abspath(__file__))


def default_reminders_path():
    return os.path.join(_app_dir(), "data", "reminders.json")


def _parse_time(time_str):
    parts = time_str.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid time format '{time_str}'. Use HH:MM (24-hour).")
    hour, minute = int(parts[0]), int(parts[1])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Invalid time '{time_str}'.")
    return time(hour, minute)


def load_reminders(path=None):
    path = path or default_reminders_path()
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    reminders = []
    for item in raw:
        reminder = {
            "id": item["id"],
            "text": item["text"],
            "time": item["time"],
            "time_obj": _parse_time(item["time"]),
        }
        reminders.append(reminder)

    reminders.sort(key=lambda r: r["time_obj"])
    return reminders


def build_fallback_reminders():
    """Used if reminders.json is missing or invalid."""
    defaults = [
        (
            "water",
            "Drink plenty of water to flush your bladder.\nGo get Starbucks water since it's your fav",
            "09:00",
        ),
        (
            "spicy_foods",
            "Avoid spicy foods (Like Papa Joes pasta meal)\nto reduce bladder irritation.",
            "12:00",
        ),
        (
            "appointment",
            "Check if your follow-up appointment\nis scheduled (every 6 weeks!!!!).",
            "15:00",
        ),
        (
            "caffeine",
            "Limit caffeine intake to prevent\nbladder irritation. You don't want\nto be awake anyways. Hahahh",
            "17:00",
        ),
        (
            "dinner",
            "Consider getting a healthy dinner with Sara :)\nto support bladder health.",
            "18:30",
        ),
    ]
    return [
        {
            "id": rid,
            "text": text,
            "time": t,
            "time_obj": _parse_time(t),
        }
        for rid, text, t in defaults
    ]
