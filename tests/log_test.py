import pytest
from log_service.log import app as flask_app
from log_service.models import Log
from shared.db import db

@pytest.fixture
def app():
    """
    Fixture to configure the Flask app for testing.
    """
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use in-memory SQLite database
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with flask_app.app_context():
        db.create_all()

        # Clear all existing data
        db.session.query(Log).delete()

        # Preload some logs for testing
        logs = [
            Log(message="Admin added new inventory item Laptop"),
            Log(message="Customer added item T-Shirt to favorites"),
        ]
        db.session.bulk_save_objects(logs)
        db.session.commit()

        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Fixture to provide a test client for Flask.
    """
    return app.test_client()


def test_get_logs(client):
    """
    Test retrieving all logs.
    """
    response = client.get("/logs")
    assert response.status_code == 200

    data = response.get_json()
    assert len(data) == 2  # Preloaded logs
    assert data[0]["message"] == "Admin added new inventory item Laptop"
    assert data[1]["message"] == "Customer added item T-Shirt to favorites"


def test_add_log(client):
    """
    Test adding a new log entry.
    """
    response = client.post("/add-log", json={"message": "Admin deleted inventory item Laptop"})
    assert response.status_code == 200

    data = response.get_json()
    assert data["message"] == "Admin deleted inventory item Laptop"


def test_add_log_missing_message(client):
    """
    Test adding a log entry with a missing 'message' field.
    """
    response = client.post("/add-log", json={})
    assert response.status_code == 400  # Bad request
    assert b"Bad request" in response.data
