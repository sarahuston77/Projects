import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


@pytest.fixture
def storage_with_temp_db(tmp_path, monkeypatch):
    """Provide the storage module wired to an isolated SQLite database per test."""
    import storage

    db_path = tmp_path / "test_health.db"
    monkeypatch.setattr(storage, "get_db_path", lambda: str(db_path))
    storage.init_db()
    return storage
