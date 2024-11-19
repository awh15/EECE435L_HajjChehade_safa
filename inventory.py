from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from .models.inventory import Inventory, inventory_schema, inventories_schema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lab-project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)
CORS(app)

'''
• Adding goods
• Deducting goods
• Updating goods
'''

@app.route('/inventory', methods=['POST'])
def add_inventory():
    '''
    Add Inventory.

    Requires:
        name (str)
        category (str)
        price (float)
        description (str)
        count (int)

    Returns:
        200: Inventory Schema
        400: Bad Request
        500: Server Error
    '''
    required_fields = ['name', 'category', 'price', 'description', 'count']

    for field in required_fields:
        if field not in request.json:
            return abort(400, "Bad Request")
        
    name = request.json['name']
    category = request.json['category']
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

        db.session.add(inventory)
        db.session.commit()

        return jsonify(inventory_schema.dump(inventory)), 200
    except Exception as e:
        return abort(500, "Server Error")


@app.route('/inventory/<int:inventory_id>', methods=['POST'])
def update_inventory(inventory_id):
    '''
    Update existing inventory.

    Requires:
        inventory_id (int)

    Optional:
        name (str)
        category (str)
        price (float)
        description (str)
        count (str)

    Returns:
        200: Inventory Schema
        404: Inventory Not Found
        400: Bad Request
        500: Server Error
    '''
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

        return jsonify(inventory_schema.dump(inventory)), 200
    except Exception as e:
        return abort(500, "Server Error")


@app.route('/inventory/<int:inventory_id>', methods=['DELETE'])
def delete_inventory(inventory_id):
    '''
    Delete existing inventory.

    Requires:
        inventory_id (int)

    Returns:
        200: Inventory Deleted
        404: Inventory Not Found
        500: Server Error
    '''
    try:
        inventory = Inventory.query.filter_by(inventory_id=inventory_id).first()

        if not inventory:
            return abort(404, "Item not Found")
        
        db.session.delete(inventory)

        return {"Message": "Item Deleted Successfully"}, 200
    except Exception as e:
        return abort(500, "Server Error")