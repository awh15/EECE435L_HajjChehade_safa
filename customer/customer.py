from flask import Flask, jsonify, abort, request
from flask_cors import CORS

from customer.models import Customer, customer_schema, customers_schema
from shared.db import db, ma, bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lab-project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)
ma.init_app(app)

CORS(app)

'''
• Customer registration --
• Delete customer --
• Update customer information (one or many) --
• Get all customers --
• Get customer per username --
• Charge customer account/wallet in dollars --
• Deduct money from the wallet --
'''

@app.route('/customers', methods=['GET'])
def get_all_customers():
    '''
    Get all customers.

    Returns:
        200: Customers Schema
        500: Server Error
    '''
    try:
        customers = Customer.query.all()
        return jsonify(customers_schema.dump(customers)), 200
    except Exception as e:
        abort(500, "Server Error")


@app.route('/customer', methods=['GET'])
def get_customer():
    '''
    Get customer by username.

    Requires:
        name (str)

    Returns:
        200: Customer Schema
        400: Bad Request
        404: Not Found
        500: Server Error
    '''
    if 'full_name' not in request.json:
        abort(400, 'Bad Request')

    full_name = request.json['full_name']

    if type(full_name) != str:
        abort(400, "Bad Request")

    try:
        customer = Customer.query.filter_by(full_name=full_name).first()

        if not customer:
            abort(404, "Customer Not Found")
        
        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        abort(500, "Server Error")


@app.route('/customer', methods=['POST'])
def create_customer():
    '''
    Create new customer.

    Requires:
        full_name (str)
        username (str)
        password (str)
        age (int)
        address (str)
        gender (str)
        marital_status (str)

    Returns:
        200: Customer Schema
        400: Bad Request
        500: Server Error
    '''
    required_fields = ['full_name', 'username', 'password', 'age', 'address', 'gender', 'marital_status']

    for field in required_fields:
        if field not in request.json:
            abort(400, "Bad Request")

    full_name = request.json['full_name']
    username = request.json['username']
    password = request.json['password']
    age = request.json['age']
    address = request.json['address']
    gender = request.json['gender']
    marital_status = request.json['marital_status']

    if type(full_name) != str or type(username) != str or type(password) != str or type(age) != int or type(address) != str or type(gender) != str or type(marital_status) != str:
        abort(400, "Bad Request")

    try:
        dup = Customer.query.filter_by(username=username).first()

        if dup:
            abort(400, "Username is Taken")

        customer = Customer(full_name=full_name, username=username, password=password, age=age, address=address, gender=gender, marital_status=marital_status)

        db.session.add(customer)
        db.session.commit()

        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        abort(500, "Server Error")


@app.route('/customer:<int:customer_id>', methods=['POST'])
def update_customer(customer_id):
    '''
    Update customer information.

    Requires:
        customer_id (int)

    Optional:
        balance (float)
        username (str)
        password (str)
        address (str)
        marital_status (str)

    Returns:
        200: Customer Schema
        400: Bad Request
        403: Invalid Token
        404: Not Found
        500: Server Error
    '''
    balance = request.json.get('balance')
    username = request.json.get('username')
    password = request.json.get('password')
    address = request.json.get('address')
    marital_status = request.json.get('marital_status')

    if balance and type(balance) != float:
        abort(400, "Bad Request")

    if username and type(username) != str:
        abort(400, "Bad Request")

    if password and type(password) != str:
        abort(400, "Bad Request")

    if address and type(address) != str:
        abort(400, "Bad Request")

    if marital_status and type(marital_status) != str:
        abort(400, "Bad Request")

    try:
        customer = Customer.query.filter_by(customer_id=customer_id).first()

        if balance:
            customer.balance += balance

        if username:
            dup = customer.query.filter_by(username=username).first()

            if dup and dup.customer_id != customer_id:
                return abort(400, "Username already taken")
            
            customer.username = username

        if address:
            customer.address = address

        if marital_status:
            customer.marital_status = marital_status

        db.session.commit()

        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        abort(500, "Internal Server Error")


@app.route('/customer/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    '''
    Delete Customer.

    Requires:
        customer_id (int)
    
    Returns:
        200: Customer Deleted
        404: Not Found
        500: Server Error
    '''
    
    try:
        customer = Customer.query.filter_by(customer_id=customer_id).first()

        if not customer:
            abort(404, "Customer Not Found")

        db.session.delete(customer)
        db.session.commit()

        return {"Message": "Customer Deleted"}
    except Exception as e:
        abort(500, "Server Error")


@app.route('/deduct/<int:customer_id>', methods=['POST'])
def deduct(customer_id):
    '''
    Deduct from customer balance.

    Customer balance must be greater than amount to be deducted.

    Requires:
        customer_id (int)
        amount (float)

    Returns:
        200: Customer Schema
        400: Bad Request
        404: Customer Not Found
        500: Server Error
    '''
    if 'amount' not in request.json:
        abort(400, "Bad Request")

    amount = request.json['amount']

    if type(amount) != float:
        abort(400, "Bad Request")

    try:
        customer = Customer.query.filter_by(customer_id=customer_id).first()

        if not customer:
            return abort(404, "Customer Not found")
        
        if amount > customer.balance:
            return abort(400, "Cannot Deduct Amount")
        
        customer.balance -= amount

        db.session.commit()

        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        return abort(500, "Server error")
    

@app.route('/charge/<int:customer_id>', methods=['POST'])
def charge(customer_id):
    '''
    Charge customer with amount.

    Requires:
        customer_id (int)
        amount (float)

    Returns:
        200: Customer Schema
        400: Bad Request
        404: Customer Not Found
        500: Server Error
    '''
    if 'amount' not in request.json:
        abort(400, "Bad Request")

    amount = request.json['amount']

    if type(amount) != float:
        abort(400, "Bad Request")

    try:
        customer = Customer.query.filter_by(customer_id=customer_id).first()

        if not customer:
            return abort(404, "Customer Not found")
        
        customer.balance += amount

        db.session.commit()

        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        return abort(500, "Server error")


@app.route('/customer/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    '''
    Get customer by id.

    Requires:
        customer_id (int)

    Returns:
        200: Customer Schema
        404: Customer Not Found
        500: Server Error
    '''
    try:
        customer = Customer.query.filter_by(customer_id=customer_id).first()

        if not customer:
            return abort(404, "Customer Not Found")
        
        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        return abort(500, "Server Error")



