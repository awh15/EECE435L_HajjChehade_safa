from flask import Flask, jsonify, request
from flask_cors import CORS

from sale.models import Sale, sale_schema
from shared.db import db, ma, bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lab-project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)
ma.init_app(app)

CORS(app)

@app.route('/goods', methods=['GET'])
def get_goods():
    goods = Inventory.query.all()
    response_data = [{"name": good.name, "price": good.price} for good in goods]
    return jsonify(response_data)

@app.route('/good/<int:id>', methods=['GET'])
def get_good(id):
    try:
        good = Inventory.query.filter_by(id=id).first()
        return jsonify(inventory_schema.dump(good))
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
        good = Inventory.query.filter_by(name=good_name).first()
        customer = Customer.query.filter_by(username=username).first()
    except:
        return jsonify({"message": "Good or User not found"}), 404
    
    if good.count == 0:
        return jsonify({"error": f"Item '{good_name}' is out of stock"}), 400

    if customer.wallet < good.price:
        return jsonify({"error": f"User '{username}' does not have enough money"}), 400
    
    good.count -= 1
    customer.wallet -= good.price
    
    db.session.commit()
    
    s = Sale(inventory_id=good.id, customer_id=customer.id, quantity=1, price=good.price)
    db.session.add(s)
    db.session.commit()
    
    return jsonify(sale_schema.dump(s)), 200