from flask import Flask, jsonify, abort, request
from flask_cors import CORS

from inventory_service.models import Inventory, inventory_schema, inventories_schema
from shared.db import db, ma, bcrypt
from shared.token import extract_auth_token, decode_token, ADMIN_PATH, LOG_PATH

import jwt
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lab-project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)
ma.init_app(app)

CORS(app)

@app.route('/inventory', methods=['POST'])
def add_inventory():
    """
    Add a new inventory item.

    :param name: The name of the inventory item
    :type name: str
    :param category: The category of the inventory item
    :type category: str
    :param price: The price of the inventory item
    :type price: float
    :param description: A description of the inventory item
    :type description: str
    :param count: The count/quantity of the inventory item
    :type count: int
    :raises werkzeug.exceptions.HTTPException: 400 for bad request, 403 for unauthorized access, 500 for server errors
    :return: JSON representation of the newly created inventory item
    :rtype: flask.Response
    """
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    admin = requests.get(f"{ADMIN_PATH}/admin:{admin_id}")
    if admin.status_code == 404:
        return abort(403, "Unauthorized")
    
    
    required_fields = ['name', 'category', 'price', 'description', 'count']

    for field in required_fields:
        if field not in request.json:
            return abort(400, "Bad Request")
        
    name = request.json['name']
    category = request.json['category'].upper()
    price = request.json['price']
    description = request.json['description']
    count = request.json['count']

    if type(name) != str or type(category) != str or type(price) != float or type(description) != str or type(count) != int:
        return abort(400, "Bad Request")
    
    try:
        dup = Inventory.query.filter_by(name=name).first()

        if dup:
            return abort(400, "Item Name Already Exists")
        
        inventory = Inventory(name=name, category=category, price=price, description=description, count=count)
        print(category)
        db.session.add(inventory)
        db.session.commit()
        
        print("here")
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Admin {admin.json()['username']} added new inventory item {name}"})

        return jsonify(inventory_schema.dump(inventory)), 200
    except Exception as e:
        print(e)
        return abort(500, "Server Error")


@app.route('/inventory:<int:inventory_id>', methods=['PUT'])
def update_inventory(inventory_id):
    """
    Update an existing inventory item.

    :param inventory_id: The ID of the inventory item to update
    :type inventory_id: int
    :param name: (Optional) The updated name of the inventory item
    :type name: str, optional
    :param category: (Optional) The updated category of the inventory item
    :type category: str, optional
    :param price: (Optional) The updated price of the inventory item
    :type price: float, optional
    :param description: (Optional) The updated description of the inventory item
    :type description: str, optional
    :param count: (Optional) The updated count/quantity of the inventory item
    :type count: int, optional
    :raises werkzeug.exceptions.HTTPException: 400 for bad request, 403 for unauthorized access, 404 if inventory item is not found, 500 for server errors
    :return: JSON representation of the updated inventory item
    :rtype: flask.Response
    """
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    admin = requests.get(f"{ADMIN_PATH}/admin:{admin_id}")
    if admin.status_code == 404:
        return abort(403, "Unauthorized")
    
    
    name = request.json.get('name')
    category = request.json.get('category')
    price = request.json.get('price')
    description = request.json.get('description')
    count = request.json.get('count')

    if name and type(name) != str:
        return abort(400, "Bad Request")
    
    if category and type(category) != str:
        return abort(400, "Bad Request")

    if price and type(price) != float:
        return abort(400, "Bad Request")

    if description and type(description) != str:
        return abort(400, "Bad Request")

    if count and type(count) != int:
        return abort(400, "Bad Request")

    try:
        inventory = Inventory.query.filter_by(inventory_id=inventory_id).first()

        if not inventory:
            return abort(404, "Item not Found")
        
        if name:
            inventory.name = name

        if category:
            inventory.category = category

        if price:
            inventory.price = price

        if description:
            inventory.description = description

        if count:
            inventory.count = count

        db.session.commit()
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Admin {admin.json()['username']} updated inventory item {inventory.name}"})

        return jsonify(inventory_schema.dump(inventory)), 200
    except Exception as e:
        print(e)
        return abort(500, "Server Error")


@app.route('/inventory:<int:inventory_id>', methods=['DELETE'])
def delete_inventory(inventory_id):
    """
    Delete an existing inventory item.

    :param inventory_id: The ID of the inventory item to delete
    :type inventory_id: int
    :raises werkzeug.exceptions.HTTPException: 403 for unauthorized access, 404 if inventory item is not found, 500 for server errors
    :return: Success message confirming the deletion
    :rtype: dict
    """
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    admin = requests.get(f"{ADMIN_PATH}/admin:{admin_id}")
    if admin.status_code == 404:
        return abort(403, "Unauthorized")
    
    
    try:
        inventory = Inventory.query.filter_by(inventory_id=inventory_id).first()

        if not inventory:
            return abort(404, "Item not Found")
        
        db.session.delete(inventory)
        db.session.commit()
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Admin {admin.json()['username']} deleted inventory item {inventory.name}"})

        return {"Message": "Item Deleted Successfully"}, 200
    except Exception as e:
        return abort(500, "Server Error")
    
    
@app.route('/inventory', methods=['GET'])
def get_inventory():
    """
    Retrieve all inventory items.

    :raises werkzeug.exceptions.HTTPException: 500 for server errors
    :return: JSON representation of all inventory items
    :rtype: flask.Response
    """
    inventories = Inventory.query.all()
    return jsonify(inventories_schema.dump(inventories)), 200


@app.route('/inventory:<string:name>', methods=['GET'])
def get_inventory_by_name(name):
    """
    Retrieve an inventory item by its name.

    :param name: The name of the inventory item to retrieve
    :type name: str
    :raises werkzeug.exceptions.HTTPException: 404 if inventory item is not found, 500 for server errors
    :return: JSON representation of the inventory item
    :rtype: flask.Response
    """
    try:
        inventory = Inventory.query.filter_by(name=name).first()

        if not inventory:
            return abort(404, "Item not Found")
        
        return jsonify(inventory_schema.dump(inventory)), 200
    except:
        return abort(500, "Server Error")
    

@app.route('/inventory:<int:inventory_id>', methods=['GET'])
def get_inventory_by_id(inventory_id):
    """
    Retrieve an inventory item by its ID.

    :param inventory_id: The ID of the inventory item to retrieve
    :type inventory_id: int
    :raises werkzeug.exceptions.HTTPException: 404 if inventory item is not found, 500 for server errors
    :return: JSON representation of the inventory item
    :rtype: flask.Response
    """
    try:
        inventory = Inventory.query.filter_by(inventory_id=inventory_id).first()

        if not inventory:
            return abort(404, "Item not Found")
        
        return jsonify(inventory_schema.dump(inventory)), 200
    except:
        return abort(500, "Server Error")


if __name__ == '__main__':
    app.run(debug=True, port=5200)