import pytest
from unittest.mock import patch
from admin_service.admin import app as flask_app
from shared.db import db
from shared.token import create_token
import uuid  # To generate unique usernames

# Test Data
VALID_ADMIN = {
    "username": "admin",
    "password": "pass"
}
INVALID_ADMIN = {
    "username": "",
    "password": "short"
}

# Mock valid token for testing
VALID_TOKEN = create_token(1)


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
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Fixture to provide a test client for Flask.
    """
    return app.test_client()


@pytest.fixture
def auth_headers():
    """
    Fixture to provide authorization headers for requests.
    """
    return {"Authorization": f"Bearer {VALID_TOKEN}"}


@patch("requests.get")
@patch("requests.post")
def test_create_admin_success(mock_post, mock_get, client, auth_headers):
    """
    Test the /create-admin route with valid data.
    """
    # Generate a unique username
    unique_admin = {
        "username": f"admin_{uuid.uuid4().hex}",
        "password": "pass"
    }

    # Mock the admin service response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"admin_id": 1, "username": "admin1"}

    # Mock the log service response
    mock_post.return_value.status_code = 200

    response = client.post("/create-admin", json=unique_admin, headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert data["username"] == unique_admin["username"]


@patch("requests.get")
@patch("requests.post")
def test_duplicate_admin_creation(mock_post, mock_get, client, auth_headers):
    """
    Test the /create-admin route with duplicate usernames.
    """
    # Generate a unique username for this test
    unique_admin = {
        "username": f"admin_{uuid.uuid4().hex}",
        "password": "pass"
    }

    # Mock the admin service response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"admin_id": 1, "username": "admin"}

    # Mock the log service response
    mock_post.return_value.status_code = 200

    client.post("/create-admin", json=unique_admin, headers=auth_headers)  # First creation
    response = client.post("/create-admin", json=unique_admin, headers=auth_headers)  # Duplicate creation
    assert response.status_code == 500  # Username already taken


@patch("requests.post")
def test_create_admin_unauthorized(mock_post, client):
    """
    Test the /create-admin route when unauthorized.
    """
    # Mock the log service response
    mock_post.return_value.status_code = 200

    response = client.post("/create-admin", json=VALID_ADMIN)  # No auth headers
    assert response.status_code == 403  # Forbidden
