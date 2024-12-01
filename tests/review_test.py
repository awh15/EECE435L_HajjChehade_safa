import pytest
from unittest.mock import patch
from review_service.review import app as flask_app
from review_service.models import Review
from shared.db import db
from shared.token import create_token

# Mock valid customer and admin tokens
VALID_CUSTOMER_TOKEN = create_token(1)  # Customer ID 1
VALID_ADMIN_TOKEN = create_token(99)    # Admin ID 99


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

        # Preload some reviews for testing
        reviews = [
            Review(customer_id=1, inventory_id=1, rating=5, comment="Great product!"),
            Review(customer_id=1, inventory_id=2, rating=4, comment="Good quality."),
        ]
        db.session.bulk_save_objects(reviews)
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
    return {"Authorization": f"Bearer {VALID_ADMIN_TOKEN}"}


@patch("requests.get")
@patch("requests.post")
def test_submit_review(mock_post, mock_get, client, customer_headers):
    """
    Test submitting a new review.
    """
    # Mock customer validation
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"user_id": 1, "full_name": "John Doe"}

    # Mock log service
    mock_post.return_value.status_code = 200

    response = client.post("/review", json={
        "inventory_id": 3,
        "rating": 5,
        "comment": "Amazing product!"
    }, headers=customer_headers)

    assert response.status_code == 201
    data = response.get_json()
    assert data["inventory_id"] == 3
    assert data["rating"] == 5
    assert data["comment"] == "Amazing product!"


@patch("requests.get")
@patch("requests.post")
def test_update_review(mock_post, mock_get, client, customer_headers):
    """
    Test updating an existing review.
    """
    # Mock customer validation
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"user_id": 1, "full_name": "John Doe"}

    # Mock log service
    mock_post.return_value.status_code = 200

    response = client.put("/review", json={
        "review_id": 1,
        "rating": 4,
        "comment": "Updated review: still great!"
    }, headers=customer_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data["rating"] == 4
    assert data["comment"] == "Updated review: still great!"


@patch("requests.get")
@patch("requests.post")
def test_delete_review_by_customer(mock_post, mock_get, client, customer_headers):
    """
    Test deleting a review by the customer.
    """
    # Mock customer validation
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"user_id": 1, "full_name": "John Doe"}

    # Mock log service
    mock_post.return_value.status_code = 200

    # Delete the review
    response = client.delete("/review", json={"review_id": 1}, headers=customer_headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Review deleted"



@patch("requests.get")
@patch("requests.post")
def test_delete_review_by_admin(mock_post, mock_get, client, admin_headers):
    """
    Test deleting a review by the admin.
    """
    # Mock admin validation
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"admin_id": 99, "username": "adminuser"}

    # Mock log service
    mock_post.return_value.status_code = 200

    response = client.delete("/review", json={"review_id": 2}, headers=admin_headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Review deleted"


def test_get_product_reviews(client):
    """
    Test retrieving reviews for a specific product.
    """
    response = client.get("/product-reviews:1")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["inventory_id"] == 1


@patch("requests.get")
def test_get_customer_reviews(mock_get, client, admin_headers):
    """
    Test retrieving all reviews from a specific customer.
    """
    # Mock admin validation
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"admin_id": 99, "username": "adminuser"}

    response = client.get("/customer-reviews", json={"customer_id": 1}, headers=admin_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2  # Customer 1 has two reviews


@patch("requests.get")
@patch("requests.post")
def test_moderate_review_flagging(mock_post, mock_get, client, admin_headers):
    """
    Test flagging a review during moderation.
    """
    # Mock admin validation
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"admin_id": 99, "username": "adminuser"}

    # Mock log service
    mock_post.return_value.status_code = 200

    response = client.post("/moderate-reviews", json={"review_id": 2, "flag": True}, headers=admin_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["flag"] is True
