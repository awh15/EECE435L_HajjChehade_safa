from flask import Flask, jsonify, request, abort
from flask_cors import CORS

from sale.models import Sale, sale_schema
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

@app.route('/goods', methods=['GET'])
def get_goods():
    response = requests.get(f'{INVENTORY_PATH}/inventory')
    goods = response.json()
    response_data = [{"name": good.name, "price": good.price} for good in goods]
    return jsonify(response_data)

@app.route('/good/<int:id>', methods=['GET'])
def get_good(id):
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        customer_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    customer = requests.get(f"{CUSTOMER_PATH}/customer/{customer_id}")
    if customer.status_code == 404:
        return abort(403, "Unauthorized")
    try:
        response = requests.get(f'{INVENTORY_PATH}/inventory/{id}')
        return jsonify(response.json())
    except:
        return jsonify({"message": "Good not found"}), 404
    
    
@app.route('/sale', methods=['POST'])
def make_sale():
    data = request.get_json()
    good_name = data.get('good_name')
    username = data.get('username')

    # Validate inputs
    if not good_name or not username:
        return jsonify({"error": "Missing 'good_name' or 'username'"}), 400

    try: 
        response = requests.get(f'{INVENTORY_PATH}/inventory/{good_name}/')
        good = response.json()
        response = requests.get(f'{CUSTOMER_PATH}/customer/{username}/')
        customer = response.json()
    except:
        return jsonify({"message": "Good or User not found"}), 404
    
    if good['count'] == 0:
        return jsonify({"error": f"Item '{good_name}' is out of stock"}), 400

    if customer['balance'] < good['price']:
        return jsonify({"error": f"User '{username}' does not have enough money"}), 400
    
    count = good["count"]-1
    balance = customer["balance"]-good["price"]
    
    response = requests.put(f'http://localhost:5001/inventory/{good['inventory_id']}/', json={"count": count})
    response = requests.put(f'http://localhost:5000/deduct/{customer['user_id']}/', json={"amount": balance})
    
    s = Sale(inventory_id=good['inventory_id'], customer_id=customer['user_id'], quantity=1, price=good['price'])
    db.session.add(s)
    db.session.commit()
    
    requests.post(f"{LOG_PATH}/add-log", json={"message": f"New sale of item {good_name} to customer {username} for ${good['price']}"})
    
    return jsonify(sale_schema.dump(s)), 200