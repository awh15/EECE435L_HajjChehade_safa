from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import jwt

from review_service.models import Review, review_schema, reviews_schema
from shared.db import db, ma, bcrypt
from shared.token import extract_auth_token, decode_token, CUSTOMER_PATH, ADMIN_PATH, LOG_PATH

import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lab-project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)
ma.init_app(app)

CORS(app)


@app.route('/review', methods=['POST'])
def submit_review():
    """
    Submit a review for a product.

    :param inventory_id: The ID of the inventory item being reviewed
    :type inventory_id: int
    :param rating: The rating given by the customer
    :type rating: int
    :param comment: The review comment
    :type comment: str
    :raises werkzeug.exceptions.HTTPException: 400 for bad requests, 403 for unauthorized access, 500 for server errors
    :return: JSON representation of the created review
    :rtype: flask.Response
    """

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        customer_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    response = requests.get(f"{CUSTOMER_PATH}/customer:{customer_id}")
    if response.status_code == 404:
        return abort(403, "Unauthorized")
    customer = response.json()
    
    if 'inventory_id' not in request.json or 'rating' not in request.json or 'comment' not in request.json:
        abort(400, "Bad Request")

    inventory_id = request.json['inventory_id']
    rating = request.json['rating']
    comment = request.json['comment']

    review = Review(customer_id=customer['user_id'], inventory_id=inventory_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    
    requests.post(f"{LOG_PATH}/add-log", json={"message": f"Customer {customer['full_name']} added review on item {inventory_id}"})

    return jsonify(review_schema.dump(review)), 201


@app.route('/review', methods=['PUT'])
def update_review():
    """
    Update an existing review.

    :param review_id: The ID of the review to be updated
    :type review_id: int
    :param rating: (Optional) The updated rating
    :type rating: int, optional
    :param comment: (Optional) The updated comment
    :type comment: str, optional
    :raises werkzeug.exceptions.HTTPException: 400 for bad requests, 403 for unauthorized access, 404 if review is not found, 500 for server errors
    :return: JSON representation of the updated review
    :rtype: flask.Response
    """
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        customer_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    response = requests.get(f"{CUSTOMER_PATH}/customer:{customer_id}")
    if response.status_code == 404:
        return abort(403, "Unauthorized")
    customer = response.json()
    
    if 'review_id' not in request.json or ('rating' not in request.json and 'comment' not in request.json):
        abort(400, "Bad Request")
        
    review_id = request.json.get('review_id')
    rating = request.json.get('rating')
    comment = request.json.get('comment')
    
    review = Review.query.filter_by(review_id=review_id).first()
    if not review:
        abort(404, "Review not found")
        
    if review.customer_id != customer['user_id']:
        abort(403, "Unauthorized")

    if rating:
        review.rating = rating
    if comment:
        review.comment = comment
    db.session.commit()
    
    requests.post(f"{LOG_PATH}/add-log", json={"message": f"Customer {customer['full_name']} updated review on item {review.inventory_id}"})
    
    return jsonify(review_schema.dump(review)), 200


@app.route('/review', methods=['DELETE'])
def delete_review():
    """
    Delete an existing review.

    :param review_id: The ID of the review to be deleted
    :type review_id: int
    :raises werkzeug.exceptions.HTTPException: 400 for bad requests, 403 for unauthorized access, 404 if review is not found, 500 for server errors
    :return: Success message confirming the deletion
    :rtype: flask.Response
    """
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    response1 = requests.get(f"{CUSTOMER_PATH}/customer:{id}")
    response2 = requests.get(f"{ADMIN_PATH}/admin:{id}")

    if response1.status_code == 200:
        customer = response1.json()
    
        if 'review_id' not in request.json:
            abort(400, "Bad Request")
            
        review_id = request.json['review_id']
        review = Review.query.filter_by(review_id=review_id).first()
        if not review:
            abort(404, "Review not found")
        if review.customer_id != customer['user_id']:
            abort(403, "Unauthorized")
        db.session.delete(review)
        db.session.commit()
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Customer {customer['full_name']} deleted review on item {review.inventory_id}"})
    
        return jsonify({"message": "Review deleted"}), 200
    
    
    elif response2.status_code == 200:
        admin = response2.json()
        if 'review_id' not in request.json:
            abort(400, "Bad Request")
        review_id = request.json['review_id']
        review = Review.query.filter_by(review_id=review_id).first()
        if not review:
            abort(404, "Review not found")
        db.session.delete(review)
        db.session.commit()
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Admin {admin['username']} deleted review on item {review.inventory_id} from customer {review.customer_id}"})
        return jsonify({"message": "Review deleted"}), 200
        
    else:
        return abort(403, "Unauthorized")



@app.route('/product-reviews:<inventory_id>', methods=['GET'])
def get_product_reviews(inventory_id):
    """
    Get all reviews for a specific product.

    :param inventory_id: The ID of the inventory item
    :type inventory_id: int
    :raises werkzeug.exceptions.HTTPException: 500 for server errors
    :return: JSON representation of all reviews for the product
    :rtype: flask.Response
    """
    try:
        reviews = Review.query.filter_by(inventory_id=inventory_id).all()
        return jsonify(reviews_schema.dump(reviews)), 200
    except:
        return abort(500, "Server Error")


@app.route('/customer-reviews', methods=['GET'])
def get_customer_reviews():
    """
    Get all reviews submitted by a specific customer.

    :param customer_id: The ID of the customer
    :type customer_id: int
    :raises werkzeug.exceptions.HTTPException: 400 for bad requests, 403 for unauthorized access, 500 for server errors
    :return: JSON representation of all reviews submitted by the customer
    :rtype: flask.Response
    """

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    response = requests.get(f"{ADMIN_PATH}/admin:{admin_id}")
    if response.status_code == 404:
        return abort(403, "Unauthorized")
    
    if 'customer_id' not in request.json:
        abort(400, "Bad Request")
        
    customer_id = request.json['customer_id']
    reviews = Review.query.filter_by(customer_id=customer_id).all()
    return jsonify(reviews_schema.dump(reviews)), 200


@app.route('/moderate-reviews', methods=['POST'])
def moderate_reviews():
    """
    Moderate a review (flag or delete).

    :param review_id: The ID of the review to be moderated
    :type review_id: int
    :param flag: The moderation flag (e.g., inappropriate, spam)
    :type flag: str
    :raises werkzeug.exceptions.HTTPException: 400 for bad requests, 403 for unauthorized access, 404 if review is not found, 500 for server errors
    :return: JSON representation of the moderated review or success message for deletion
    :rtype: flask.Response
    """

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    response = requests.get(f"{ADMIN_PATH}/admin:{admin_id}")
    if response.status_code == 404:
        return abort(403, "Unauthorized")
    
    if 'review_id' not in request.json or 'flag' not in request.json:
        abort(400, "Bad Request")
        
    review_id = request.json['review_id']
    flag = request.json['flag']
    review = Review.query.filter_by(review_id=review_id).first()
    if not review:
        abort(404, "Review not found")

    if flag:
        review.flag = flag
        db.session.commit()
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Admin {response.json()['username']} flagged review {review_id}"})
        
        return jsonify(review_schema.dump(review)), 200
    
    db.session.delete(review)
    db.session.commit()
    
    requests.post(f"{LOG_PATH}/add-log", json={"message": f"Admin {response.json['username']} deleted review {review_id}"})
    
    return jsonify({"message": "Review deleted"}), 200


@app.route('/review-details', methods=['GET'])
def get_review_details():
    """
    Retrieve details of a specific review.

    :param review_id: The ID of the review
    :type review_id: int
    :raises werkzeug.exceptions.HTTPException: 400 for bad requests, 403 for unauthorized access, 404 if review is not found, 500 for server errors
    :return: JSON representation of the review details
    :rtype: flask.Response
    """
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    response = requests.get(f"{ADMIN_PATH}/admin:{admin_id}")
    if response.status_code == 404:
        return abort(403, "Unauthorized")
    
    if 'review_id' not in request.json:
        abort(400, "Bad Request")
        
    review_id = request.json['review_id']
    review = Review.query.filter_by(review_id=review_id).first()
    if not review:
        abort(404, "Review not found")
    return jsonify(review_schema.dump(review)), 200



if __name__ == '__main__':
    app.run(debug=True, port=5300)