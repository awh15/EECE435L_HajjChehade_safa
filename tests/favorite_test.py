import pytest
from unittest.mock import patch
from favorite_service.favorite import app as flask_app
from inventory_service.models import Inventory, Category
from shared.db import db
from shared.token import create_token

# Mock valid token
VALID_TOKEN = create_token(1)

@pytest.fixture
def app():
    """
    Fixture to configure the Flask app for testing, preloading inventory items with IDs 1 and 2.
    """
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use in-memory SQLite database
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with flask_app.app_context():
        db.create_all()

        # Add initial inventory items with IDs 1 and 2
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
def test_add_favorite(mock_post, mock_get, client, auth_headers):
    """
    Test adding an item to favorites.
    """
    # Mock customer service response
    mock_get.side_effect = [
        # First call: CUSTOMER_PATH
        type("MockResponse", (), {"status_code": 200, "json": lambda: {"user_id": 1, "username": "testuser"}}),
        # Second call: INVENTORY_PATH
        type("MockResponse", (), {"status_code": 200, "json": lambda: {"inventory_id": 1, "name": "Laptop"}}),
    ]

    # Mock log service response
    mock_post.return_value.status_code = 200

    # Add "Laptop" to favorites
    response = client.post("/favorite:1", headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert data["inventory_id"] == 1



@patch("requests.get")
@patch("requests.post")
def test_delete_favorite(mock_post, mock_get, client, auth_headers):
    """
    Test deleting a favorite item.
    """
    # Mock customer service response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"user_id": 1, "username": "testuser"}

    # Mock log service response
    mock_post.return_value.status_code = 200

    # Add favorite first
    client.post("/favorite:1", headers=auth_headers)  # Add "Laptop" to favorites

    # Delete favorite
    response = client.delete("/favorite:1", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["Message"] == "Favorite Deleted"


@patch("requests.get")
def test_get_favorites(mock_get, client, auth_headers):
    """
    Test retrieving all favorite items for a customer.
    """
    # Mock customer service response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"user_id": 1, "username": "testuser"}

    # Add items to favorites
    client.post("/favorite:1", headers=auth_headers)  # Add "Laptop"
    client.post("/favorite:2", headers=auth_headers)  # Add "T-Shirt"

    # Retrieve all favorites
    response = client.get("/favorites", headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert len(data) == 2
    assert data[0]["inventory_id"] == 1
    assert data[1]["inventory_id"] == 2


@patch("requests.get")
@patch("requests.post")
def test_add_wishlist(mock_post, mock_get, client, auth_headers):
    """
    Test adding an item to the wishlist.
    """
    # Mock customer service response
    mock_get.side_effect = [
        # First call: CUSTOMER_PATH
        type("MockResponse", (), {"status_code": 200, "json": lambda: {"user_id": 1, "username": "testuser"}}),
        # Second call: INVENTORY_PATH
        type("MockResponse", (), {"status_code": 200, "json": lambda: {"inventory_id": 2, "name": "T-Shirt"}}),
    ]

    # Mock log service response
    mock_post.return_value.status_code = 200

    # Add "T-Shirt" to wishlist
    response = client.post("/wishlist:2", headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert data["inventory_id"] == 2


@patch("requests.get")
@patch("requests.post")
def test_delete_wishlist(mock_post, mock_get, client, auth_headers):
    """
    Test deleting an item from the wishlist.
    """
    # Mock customer service response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"user_id": 1, "username": "testuser"}

    # Mock log service response
    mock_post.return_value.status_code = 200

    # Add item to wishlist
    client.post("/wishlist:2", headers=auth_headers)  # Add "T-Shirt" to wishlist

    # Delete wishlist item
    response = client.delete("/wishlist:1", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["Message"] == "Wishlist Deleted"
