import pytest
from unittest.mock import patch
from customer_service.customer import app as flask_app
from shared.db import db
from shared.token import create_token
import uuid  # To generate unique usernames for testing

# Test Data
VALID_CUSTOMER = {
    "full_name": "John Doe",
    "username": f"johndoe_{uuid.uuid4().hex}",
    "password": "password123",
    "age": 30,
    "address": "123 Main Street",
    "gender": "male",
    "marital_status": "single"
}
INVALID_CUSTOMER = {
    "full_name": "",
    "username": "",
    "password": "short",
    "age": "invalid",
    "address": "",
    "gender": "invalid",
    "marital_status": "invalid"
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
def test_create_customer_success(mock_post, mock_get, client, auth_headers):
    """
    Test the /customer route for creating a customer with valid data.
    """
    # Mock the log service response
    mock_post.return_value.status_code = 200

    response = client.post("/customer", json=VALID_CUSTOMER, headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert data["username"] == VALID_CUSTOMER["username"]
    assert data["balance"] == 0


@patch("requests.get")
@patch("requests.post")
def test_create_customer_invalid_data(mock_post, mock_get, client, auth_headers):
    """
    Test the /customer route for creating a customer with invalid data.
    """
    response = client.post("/customer", json=INVALID_CUSTOMER, headers=auth_headers)
    assert response.status_code == 400  # Bad Request


@patch("requests.get")
def test_get_customer_by_name(mock_get, client, auth_headers):
    """
    Test retrieving a customer by their full name.
    """
    # Mock the customer service response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = VALID_CUSTOMER

    # Create customer first
    client.post("/customer", json=VALID_CUSTOMER, headers=auth_headers)

    response = client.get(f"/customer:{VALID_CUSTOMER['full_name']}", headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert data["full_name"] == VALID_CUSTOMER["full_name"]


@patch("requests.post")
def test_update_customer(mock_post, client, auth_headers):
    """
    Test updating customer details.
    """
    # Mock the log service response
    mock_post.return_value.status_code = 200

    # Create customer first
    client.post("/customer", json=VALID_CUSTOMER, headers=auth_headers)

    updated_data = {"username": "newusername", "address": "456 Elm Street"}

    response = client.put("/customer", json=updated_data, headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert data["username"] == "newusername"
    assert data["address"] == "456 Elm Street"


@patch("requests.get")
@patch("requests.post")
def test_delete_customer(mock_post, mock_get, client, auth_headers):
    """
    Test deleting a customer.
    """
    # Mock the admin service response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"user_id": 1}

    # Mock the log service response
    mock_post.return_value.status_code = 200

    # Create customer first
    client.post("/customer", json=VALID_CUSTOMER, headers=auth_headers)

    # Attempt to delete customer
    response = client.delete("/customer", json={"customer_id": 1}, headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["Message"] == "Customer Deleted"
