"""Shared pytest fixtures.

Tests run against a temporary SQLite database and the real trained model.
If the model artifact does not exist yet, it is trained once here so the
suite works on a fresh clone after `pip install -r requirements.txt`.
"""

import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Use an isolated database for tests — must be set before app imports.
_test_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_test_db.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db.name}"

MODEL_PATH = PROJECT_ROOT / "models" / "ticket_classifier.joblib"
if not MODEL_PATH.exists():
    import train_model

    train_model.train()

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_tickets_table():
    """Give every test an empty tickets table."""
    from app.database import SessionLocal
    from app.models import Ticket

    db = SessionLocal()
    db.query(Ticket).delete()
    db.commit()
    db.close()
    yield
