from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from urllib.parse import quote

from sale_service.models import Sale, sale_schema
from shared.db import db, ma, bcrypt
from shared.token import jwt, extract_auth_token, decode_token, CUSTOMER_PATH, INVENTORY_PATH, LOG_PATH

import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lab-project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)
ma.init_app(app)

CORS(app)

ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MzI3ODA2NTYsImlkIjoxfQ.T37k5vuFQO2YUKSVPL3mnqIJTwIw7-y0uIXaUYJZgOg"

@app.route('/goods', methods=['GET'])
def get_goods():
    """
    Retrieve a list of goods.

    :raises werkzeug.exceptions.HTTPException: 500 for server errors
    :return: JSON representation of available goods with their names and prices
    :rtype: flask.Response
    """
    response = requests.get(f'{INVENTORY_PATH}/inventory')
    goods = response.json()
    response_data = [{"name": good["name"], "price": good["price"]} for good in goods]
    return jsonify(response_data)

@app.route('/good:<int:id>', methods=['GET'])
def get_good(id):
    """
    Retrieve details of a specific good by its ID.

    :param id: The ID of the good to retrieve
    :type id: int
    :raises werkzeug.exceptions.HTTPException: 404 if the good is not found, 500 for server errors
    :return: JSON representation of the good details
    :rtype: flask.Response
    """
    try:
        response = requests.get(f'{INVENTORY_PATH}/inventory:{id}')
        return jsonify(response.json())
    except:
        return jsonify({"message": "Good not found"}), 404
    
    
@app.route('/sale', methods=['POST'])
def make_sale():
    """
    Make a sale for a specific good.

    :param good_name: The name of the good to be sold
    :type good_name: str
    :raises werkzeug.exceptions.HTTPException: 400 for bad requests, 403 for unauthorized access, 404 if the good or customer is not found, 500 for server errors
    :return: JSON representation of the sale details
    :rtype: flask.Response
    """
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
        
        if customer.status_code == 500:
            return abort(500, "Server Error")
    except Exception as e:
        abort(500, "Server Error")

    data = request.get_json()
    if 'good_name' not in data:
        abort(400, "Bad request")
    good_name = data.get('good_name')
    username = customer.json()['full_name']

    try: 
        response = requests.get(f'{INVENTORY_PATH}/inventory:{good_name}')
        good = response.json()

        response = requests.get(f"{CUSTOMER_PATH}/customer:{customer_id}")
        customer = response.json()
        print(customer)
    except Exception as e:
        print(e)
        return jsonify({"message": "Good or User not found"}), 404

    if good['count'] == 0:
        return jsonify({"error": f"Item '{good_name}' is out of stock"}), 400

    if customer['balance'] < good['price']:
        return jsonify({"error": f"User '{username}' does not have enough money"}), 400
    
    count = good["count"]-1
    response = requests.put(f'{INVENTORY_PATH}/inventory:{good["inventory_id"]}', json={"count": count}, headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    response = requests.post(f'{CUSTOMER_PATH}/deduct', json={"amount": good["price"]}, headers={"Authorization": f"Bearer {token}"})

    s = Sale(inventory_id=good['inventory_id'], customer_id=customer['user_id'], quantity=1, price=good['price'])

    db.session.add(s)
    db.session.commit()
    
    requests.post(f"{LOG_PATH}/add-log", json={"message": f"New sale of item {good_name} to customer {username} for ${good['price']}"})
    
    return jsonify(sale_schema.dump(s)), 200


if __name__ == '__main__':
    app.run(debug=True, port=5350)