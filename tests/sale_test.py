import pytest
from unittest.mock import patch
from sale_service.sale import app as flask_app
from sale_service.models import Sale
from inventory_service.models import Inventory, Category
from customer_service.models import Customer
from shared.db import db
from shared.token import create_token

# Mock tokens
VALID_CUSTOMER_TOKEN = create_token(1)  # Customer ID 1
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MzI3ODA2NTYsImlkIjoxfQ.T37k5vuFQO2YUKSVPL3mnqIJTwIw7-y0uIXaUYJZgOg"


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
        
        # Add initial customer
        customer = Customer(
            full_name="John Doe", 
            username="johndoe", 
            password="pass",
            age=30, 
            address="123 Main St", 
            gender="MALE", 
            marital_status="SINGLE"
        )
        db.session.add(customer)

        inventory_items = [
            Inventory(name="Laptop", category=Category.ELECTRONICS, price=999.99, description="A powerful laptop", count=10),
            Inventory(name="T-Shirt", category=Category.CLOTHES, price=19.99, description="Comfortable cotton T-shirt", count=50),
        ]
        db.session.bulk_save_objects(inventory_items)

        # Preload some sales
        sales = [
            Sale(inventory_id=1, customer_id=1, quantity=1, price=999.99),
        ]
        db.session.bulk_save_objects(sales)
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
def customer_headers():
    """
    Fixture to provide headers for a valid customer token.
    """
    return {"Authorization": f"Bearer {VALID_CUSTOMER_TOKEN}"}


@pytest.fixture
def admin_headers():
    """
    Fixture to provide headers for a valid admin token.
    """
    return {"Authorization": f"Bearer {ADMIN_TOKEN}"}


@patch("requests.get")
def test_get_goods(mock_get, client):
    """
    Test retrieving all goods.
    """
    # Mock inventory service response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [
        {"name": "Laptop", "price": 999.99, "count": 10},
        {"name": "T-Shirt", "price": 19.99, "count": 50},
    ]

    response = client.get("/goods")
    assert response.status_code == 200

    data = response.get_json()
    assert len(data) == 2
    assert data[0]["name"] == "Laptop"
    assert data[0]["price"] == 999.99


@patch("requests.get")
def test_get_good(mock_get, client):
    """
    Test retrieving a single good by ID.
    """
    # Mock inventory service response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"name": "Laptop", "price": 999.99, "count": 10}

    response = client.get("/good:1")
    assert response.status_code == 200

    data = response.get_json()
    assert data["name"] == "Laptop"
    assert data["price"] == 999.99

@patch("requests.get")
@patch("requests.post")
@patch("requests.put")
def test_make_sale_good_not_found(mock_put, mock_post, mock_get, client, customer_headers):
    """
    Test making a sale when the good is not found in the inventory.
    """
    # Mock customer details retrieval
    mock_get.side_effect = [
    type("MockResponse", (), {"status_code": 200, "json": lambda: {"user_id": 1, "full_name": "John Doe", "balance": 1500.00}}),
    type("MockResponse", (), {"status_code": 200, "json": lambda: {"inventory_id": 1, "name": "Laptop", "price": 999.99, "count": 10}})
    ]

    # Mock inventory and log service interactions
    mock_put.return_value.status_code = 200
    mock_post.return_value.status_code = 200

    # Attempt to make a sale for a non-existent good
    response = client.post("/sale", json={"good_name": "NonExistentGood"}, headers=customer_headers)
    assert response.status_code == 404  # Good not found
    assert response.get_json()["message"] == "Good or User not found"

@patch("requests.get")
@patch("requests.post")
@patch("requests.put")
def test_make_sale(mock_put, mock_post, mock_get, client, customer_headers):
    """
    Test making a sale where customer balance is updated via its route.
    """
    # Mock customer and inventory service responses
    mock_get.side_effect = [
        # First call: CUSTOMER_PATH
        type("MockResponse", (), {"status_code": 200, "json": lambda: {"user_id": 1, "full_name": "John Doe", "balance": 1500.00}}),
        # Second call: INVENTORY_PATH
        type("MockResponse", (), {"status_code": 200, "json": lambda: {"inventory_id": 1, "name": "Laptop", "price": 999.99, "count": 10}})
    ]

    # Mock inventory update and log service
    mock_put.return_value.status_code = 200
    mock_post.return_value.status_code = 200

    # Proceed with making a sale
    response = client.post("/sale", json={"good_name": "Laptop"}, headers=customer_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert data["inventory_id"] == 1
    assert data["price"] == 999.99
    assert data["quantity"] == 1


@patch("requests.get")
@patch("requests.post")
def test_make_sale_insufficient_balance(mock_post, mock_get, client, customer_headers):
    """
    Test making a sale when the customer has insufficient balance.
    """
    # Mock customer service response
    mock_get.side_effect = [
        # First call: CUSTOMER_PATH
        type("MockResponse", (), {"status_code": 200, "json": lambda: {"user_id": 1, "full_name": "John Doe", "balance": 500.00}}),
        # Second call: INVENTORY_PATH
        type("MockResponse", (), {"status_code": 200, "json": lambda: {"inventory_id": 1, "name": "Laptop", "price": 999.99, "count": 10}})
    ]

    response = client.post("/sale", json={"good_name": "Laptop"}, headers=customer_headers)
    assert response.status_code == 400

    data = response.get_json()
    assert data["error"] == "User 'John Doe' does not have enough money"


@patch("requests.get")
@patch("requests.post")
def test_make_sale_out_of_stock(mock_post, mock_get, client, customer_headers):
    """
    Test making a sale when the good is out of stock.
    """
    # Mock customer service response
    mock_get.side_effect = [
        # First call: CUSTOMER_PATH
        type("MockResponse", (), {"status_code": 200, "json": lambda: {"user_id": 1, "full_name": "John Doe", "balance": 1500.00}}),
        # Second call: INVENTORY_PATH
        type("MockResponse", (), {"status_code": 200, "json": lambda: {"inventory_id": 1, "name": "Laptop", "price": 999.99, "count": 0}})
    ]

    response = client.post("/sale", json={"good_name": "Laptop"}, headers=customer_headers)
    assert response.status_code == 400

    data = response.get_json()
    assert data["error"] == "Item 'Laptop' is out of stock"
