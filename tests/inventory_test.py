import pytest
from unittest.mock import patch
from inventory_service.inventory import app as flask_app
from inventory_service.models import Inventory, Category
from shared.db import db
from shared.token import create_token

# Mock valid admin token
VALID_TOKEN = create_token(1)


@pytest.fixture
def app():
    """
    Fixture to configure the Flask app for testing, preloading some inventory items.
    """
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use in-memory SQLite database
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with flask_app.app_context():
        db.create_all()

        # Add initial inventory items
        inventory_items = [
            Inventory(name="Laptop", category=Category.ELECTRONICS, price=999.99, description="A powerful laptop", count=10),
            Inventory(name="T-Shirt", category=Category.CLOTHES, price=19.99, description="Comfortable cotton T-shirt", count=50),
        ]
        db.session.bulk_save_objects(inventory_items)
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


@pytest.fixture
def auth_headers():
    """
    Fixture to provide authorization headers for requests.
    """
    return {"Authorization": f"Bearer {VALID_TOKEN}"}


@patch("requests.get")
@patch("requests.post")
def test_add_inventory(mock_post, mock_get, client, auth_headers):
    """
    Test adding a new inventory item.
    """
    # Mock admin service response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"admin_id": 1, "username": "adminuser"}

    # Mock log service response
    mock_post.return_value.status_code = 200

    response = client.post("/inventory", json={
        "name": "Smartphone",
        "category": "electronics",
        "price": 599.99,
        "description": "A high-end smartphone",
        "count": 20
    }, headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Smartphone"
    assert data["category"] == "electronics"
    assert data["price"] == 599.99
    assert data["count"] == 20


@patch("requests.get")
@patch("requests.post")
def test_update_inventory(mock_post, mock_get, client, auth_headers):
    """
    Test updating an existing inventory item.
    """
    # Mock admin service response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"admin_id": 1, "username": "adminuser"}

    # Mock log service response
    mock_post.return_value.status_code = 200

    # Update inventory item (e.g., "Laptop")
    response = client.put("/inventory:1", json={
        "price": 899.99,
        "count": 15
    }, headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 899.99
    assert data["count"] == 15


@patch("requests.get")
@patch("requests.post")
def test_delete_inventory(mock_post, mock_get, client, auth_headers):
    """
    Test deleting an inventory item.
    """
    # Mock admin service response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"admin_id": 1, "username": "adminuser"}

    # Mock log service response
    mock_post.return_value.status_code = 200

    # Delete inventory item (e.g., "Laptop")
    response = client.delete("/inventory:1", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json()["Message"] == "Item Deleted Successfully"


def test_get_inventory(client):
    """
    Test retrieving all inventory items.
    """
    response = client.get("/inventory")
    assert response.status_code == 200

    data = response.get_json()
    assert len(data) == 2  # Preloaded items: "Laptop" and "T-Shirt"


def test_get_inventory_by_id(client):
    """
    Test retrieving an inventory item by ID.
    """
    response = client.get("/inventory:1")  # Retrieve "Laptop"
    assert response.status_code == 200

    data = response.get_json()
    assert data["name"] == "Laptop"


def test_get_inventory_by_name(client):
    """
    Test retrieving an inventory item by name.
    """
    response = client.get("/inventory:Laptop")
    assert response.status_code == 200

    data = response.get_json()
    assert data["name"] == "Laptop"


@patch("requests.get")
def test_unauthorized_add_inventory(mock_get, client):
    """
    Test adding inventory without proper authorization.
    """
    # Mock admin service response as unauthorized
    mock_get.return_value.status_code = 404

    response = client.post("/inventory", json={
        "name": "Smartphone",
        "category": "electronics",
        "price": 599.99,
        "description": "A high-end smartphone",
        "count": 20
    })

    assert response.status_code == 403  # Unauthorized
