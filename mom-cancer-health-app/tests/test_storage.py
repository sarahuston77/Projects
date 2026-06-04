import sqlite3
from datetime import datetime, timedelta

import pytest


def _insert_log(storage, entry_type, value, when):
    with sqlite3.connect(storage.get_db_path()) as conn:
        conn.execute(
            "INSERT INTO log_entries (entry_type, value, created_at) VALUES (?, ?, ?)",
            (entry_type, value, when.isoformat(timespec="seconds")),
        )


def test_save_log_rejects_unknown_type(storage_with_temp_db):
    with pytest.raises(ValueError):
        storage_with_temp_db.save_log("anxiety", 5)


def test_save_log_rejects_out_of_range_value(storage_with_temp_db):
    with pytest.raises(ValueError):
        storage_with_temp_db.save_log("mood", 0)
    with pytest.raises(ValueError):
        storage_with_temp_db.save_log("sleep", 11)


def test_save_and_retrieve_log_roundtrip(storage_with_temp_db):
    storage_with_temp_db.save_log("mood", 7)
    storage_with_temp_db.save_log("sleep", 8)
    logs = storage_with_temp_db.get_logs_since(days=1)
    types = sorted(row["entry_type"] for row in logs)
    assert types == ["mood", "sleep"]


def test_format_weekly_summary_empty_state(storage_with_temp_db):
    summary = storage_with_temp_db.format_weekly_summary()
    assert "No sleep or mood logs yet" in summary
    assert "Log today to start a streak" in summary


def test_logging_streak_counts_consecutive_days(storage_with_temp_db):
    now = datetime.now()
    for offset in (0, 1, 2):
        _insert_log(storage_with_temp_db, "mood", 7, now - timedelta(days=offset))
    assert storage_with_temp_db.get_logging_streak() == 3


def test_logging_streak_breaks_on_gap(storage_with_temp_db):
    now = datetime.now()
    _insert_log(storage_with_temp_db, "mood", 7, now)
    _insert_log(storage_with_temp_db, "mood", 7, now - timedelta(days=2))
    assert storage_with_temp_db.get_logging_streak() == 1


def test_weekly_summary_includes_averages_and_streak(storage_with_temp_db):
    now = datetime.now()
    _insert_log(storage_with_temp_db, "mood", 6, now)
    _insert_log(storage_with_temp_db, "mood", 8, now - timedelta(days=1))
    _insert_log(storage_with_temp_db, "sleep", 7, now)
    summary = storage_with_temp_db.format_weekly_summary()
    assert "Average sleep: 7.0" in summary
    assert "Average mood: 7.0" in summary
    assert "logging streak" in summary


def test_reminder_state_is_idempotent(storage_with_temp_db):
    storage_with_temp_db.mark_reminder_shown("water")
    storage_with_temp_db.mark_reminder_shown("water")  # second call must not raise
    assert storage_with_temp_db.was_reminder_shown_today("water") is True
    assert storage_with_temp_db.was_reminder_shown_today("caffeine") is False
