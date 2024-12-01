from flask import Flask, jsonify, abort, request
from flask_cors import CORS
import requests

from shared.db import db, ma, bcrypt
from shared.token import jwt, extract_auth_token, decode_token
from shared.token import INVENTORY_PATH, CUSTOMER_PATH, LOG_PATH
from favorite_service.models import Favorite, favorite_schema, favorites_schema
from favorite_service.models import Wishlist, wishlist_schema, wishlists_schema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lab-project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)
ma.init_app(app)

CORS(app)


@app.route('/favorite:<int:inventory_id>', methods=['POST'])
def add_favorite(inventory_id):
    '''
    Add Favorite.

    Requires:
        customer_id (int)
        inventory_id (int)

    Returns:
        200: Favorite Added
        400: Bad Request
        401: Unauthorized
        403: Invalid Token
        404: Not Found
        500: Server Error
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        customer_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    try:
        customer = requests.get(f"{CUSTOMER_PATH}/customer:{customer_id}")

        if customer.status_code == 404:
            return abort(401, "Unauthorized")
        
        inventory = requests.get(f"{INVENTORY_PATH}/inventory:{inventory_id}")

        if inventory.status_code == 404:
            return abort(404, "Item Not Found")
        
        favorite = Favorite.query.filter_by(customer_id=customer_id, inventory_id=inventory_id).first()

        if favorite:
            return abort(400, "Item Already Favorite")

        favorite = Favorite(customer_id=customer_id, inventory_id=inventory_id)

        db.session.add(favorite)
        db.session.commit()
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Added item {inventory.json()['name']} as favorite to customer: {customer.json()['username']}"})

        return jsonify(favorite_schema.dump(favorite)), 200
    except Exception as e:
        print(e)
        return abort(500, "Server Error")



@app.route('/favorite:<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    '''
    Delete Favorite by id.

    Requires:
        favorite_id (int)

    Returns:
        200: Favorite Deleted
        400: Bad Request
        401: Unauthorized
        403: Invalid Token
        404: Favorite Not Found
        500: Server Error
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        customer_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    try:
        customer = requests.get(f"{CUSTOMER_PATH}/customer:{customer_id}")

        if customer.status_code == 404:
            return abort(401, "Unauthorized")
        
        favorite = Favorite.query.filter_by(favorite_id=favorite_id).first()

        if not favorite:
            return abort(404, "Favorite Not Found")

        db.session.delete(favorite)
        db.session.commit()
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Deleted favorite item {favorite_id} to customer: {customer.json()['username']}"})

        return {"Message": "Favorite Deleted"}, 200
    except Exception as e:
        print(e)
        return abort(500, "Server Error")


@app.route('/favorite:<int:favorite_id>', methods=['GET'])
def get_favorite(favorite_id):
    '''
    Get Favorite by id.

    Requires:
        favorite_id (int)

    Returns:
        200: Favorite Schema
        404: Favorite Not Found
        500: Server Error
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        customer_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    customer = requests.get(f"{CUSTOMER_PATH}/customer:{customer_id}")

    if customer.status_code == 404:
        return abort(401, "Unauthorized")
    
    favorite = Favorite.query.filter_by(favorite_id=favorite_id).first()

    if not favorite:
        return abort(404, "Favorite Not Found")
    
    if favorite.customer_id != customer_id:
        return abort(401, "Unauthorized")
    
    return jsonify(favorite_schema.dump(favorite)), 200


@app.route('/favorites', methods=['GET'])
def get_favorites():
    '''
    Get all customer favorites.
    
    Returns:
        200: Favorites Schema
        401: Unauthorized
        403: Invalid Token
        500: Server Error
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        customer_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    try:
        customer = requests.get(f"{CUSTOMER_PATH}/customer:{customer_id}")

        if customer.status_code == 404:
            return abort(401, "Unauthorized")
        
        favorites = Favorite.query.filter_by(customer_id=customer_id).all()

        return jsonify(favorites_schema.dump(favorites)), 200
    except Exception as e:
        return abort(500, "Server Error")


@app.route('/wishlist:<int:inventory_id>', methods=['POST'])
def add_wishlist(inventory_id):
    '''
    Add Wishlist.

    Requires:
        inventory_id (int)

    Returns:
        200: Wishlist Schema
        400: Bad Request
        401: Unauthorized
        403: Invalid Token
        404: Item Not Found
        500: Server Error
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        customer_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    try:
        customer = requests.get(f"{CUSTOMER_PATH}/customer:{customer_id}")

        if customer.status_code == 404:
            return abort(401, "Unauthorized")
        
        inventory = requests.get(f"{INVENTORY_PATH}/inventory:{inventory_id}")

        if inventory.status_code == 404:
            return abort(404, "Item Not Found")
        
        wishlist = Wishlist(customer_id=customer_id, inventory_id=inventory_id)

        db.session.add(wishlist)
        db.session.commit()
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Added item {inventory.json()['name']} as wishlist to customer: {customer.json()['username']}"})

        return jsonify(wishlist_schema.dump(wishlist)), 200
    except Exception as e:
        return abort(500, "Server Error")


@app.route('/wishlist:<int:wishlist_id>', methods=['DELETE'])
def delete_wishlist(wishlist_id):
    '''
    Delete Wishlist.

    Requires:
        wishlist_id (int)

    Returns:
        200: Wishlist Deleted
        400: Bad Request
        401: Unauthorized
        403: Invalid Token
        404: Wishlist Not Found
        500: Server Error
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        customer_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    try:
        customer = requests.get(f"{CUSTOMER_PATH}/customer:{customer_id}")

        if customer.status_code == 404:
            return abort(401, "Unauthorized")
        
        wishlist = Wishlist.query.filter_by(wishlist_id=wishlist_id).first()

        if not wishlist:
            return abort(404, "Wishlist Not Found")
        
        db.session.delete(wishlist)
        db.session.commit()
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Deleted wishlist item {wishlist_id} of customer: {customer.json()['username']}"})

        return {"Message": "Wishlist Deleted"}, 200
    except Exception as e:
        return abort(500, "Server Error")


@app.route('/wishlists', methods=['GET'])
def get_wishlists():
    '''
    Get customer wishlists.
    
    Returns:
        200: Wishlists Schema
        401: Unauthorized
        403: Invalid Token
        500: Server Error
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        customer_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    try:
        customer = requests.get(f"{CUSTOMER_PATH}/customer:{customer_id}")

        if customer.status_code == 404:
            return abort(401, "Unauthorized")
        
        wishlists = Wishlist.query.filter_by(customer_id=customer_id).all()

        return jsonify(wishlists_schema.dump(wishlists)), 200
    except Exception as e:
        return abort(500, "Server Error")


@app.route('/wishlist:<int:wishlist_id>', methods=['GET'])
def get_wishlist(wishlist_id):
    '''
    Get wishlist by id.

    Requires:
        wishlist_id (int)

    Returns:
        200: Wishlist Schema
        404: Wishlist Not Found
        500: Server Error
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        customer_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    try:
        customer = requests.get(f"{CUSTOMER_PATH}/customer:{customer_id}")

        if customer.status_code == 404:
            return abort(401, "Unauthorized")
        
        wishlist = Wishlist.query.filter_by(wishlist_id=wishlist_id).first()

        if not wishlist:
            return abort(404, "Wishlist Not Found")
        
        return jsonify(wishlist_schema.dump(wishlist)), 200
    except Exception as e:
        return abort(500, "Server Error")
    

if __name__ == '__main__':
    app.run(debug=True, port=5150)