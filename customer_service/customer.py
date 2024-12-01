from flask import Flask, jsonify, abort, request
from flask_cors import CORS

import requests

from customer_service.models import Customer, customer_schema, customers_schema
from shared.db import db, ma, bcrypt
from shared.token import create_token, ADMIN_PATH, extract_auth_token, decode_token, jwt, LOG_PATH, CUSTOMER_PATH

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lab-project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)
ma.init_app(app)

CORS(app)

@app.route('/customers', methods=['GET'])
def get_all_customers():
    '''
    Get all customers.
    Must be an Admin.

    Returns:
        200: Customers Schema
        401: Unauthorized
        403: Invalid Token
        500: Server Error
    '''
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        user_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    try:
        admin = requests.get(f"{ADMIN_PATH}/admin:{user_id}")

        if admin.status_code == 404:
            return abort(401, "Unauthorized")
        
        if admin.status_code == 500:
            return abort(500, "Server Error")
        
        customers = Customer.query.all()
        return jsonify(customers_schema.dump(customers)), 200
    except Exception as e:
        print(e)
        abort(500, "Server Error")


@app.route('/customer:<string:full_name>', methods=['GET'])
def get_customer_by_name(full_name):
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

    try:
        customer = Customer.query.filter_by(full_name=full_name).first()
        print(customer)
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
    gender = request.json['gender'].upper()
    marital_status = request.json['marital_status'].upper()

    if type(full_name) != str or type(username) != str or type(password) != str or type(age) != int or type(address) != str or type(gender) != str or type(marital_status) != str:
        abort(400, "Bad Request")

    try:
        dup = Customer.query.filter_by(username=username).first()

        if dup:
            abort(400, "Username is Taken")

        customer = Customer(full_name=full_name, username=username, password=password, age=age, address=address, gender=gender, marital_status=marital_status)

        db.session.add(customer)
        db.session.commit()
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"New customer: {full_name}"})

        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        print(e)
        abort(500, "Server Error")


@app.route('/customer', methods=['PUT'])
def update_customer():
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
    
    
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        customer_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    try:
        customer = Customer.query.filter_by(user_id=customer_id).first()
        
        if not customer:
            abort(404, "Customer Not Found")
    except Exception as e:
        abort(500, "Server Error")
    
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
        customer = Customer.query.filter_by(user_id=customer_id).first()

        if balance:
            customer.balance += balance

        if username:
            dup = customer.query.filter_by(username=username).first()

            if dup and dup.user_id != customer_id:
                return abort(400, "Username already taken")
            
            customer.username = username

        if address:
            customer.address = address

        if marital_status:
            customer.marital_status = marital_status.upper()

        db.session.commit()
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Updated customer information: {customer.username}"})
        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        print(e)
        abort(500, "Internal Server Error")


@app.route('/customer', methods=['DELETE'])
def delete_customer():
    '''
    Delete Customer.

    Requires:
        customer_id (int)
    
    Returns:
        200: Customer Deleted
        404: Not Found
        500: Server Error
    '''
    
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
        customer_id = response1.json()['user_id']
        try:
            customer = Customer.query.filter_by(user_id=customer_id).first()

            if not customer:
                abort(404, "Customer Not Found")

            db.session.delete(customer)
            db.session.commit()
            
            requests.post(f"{LOG_PATH}/add-log", json={"message": f"Deleted customer: {customer.username}"})

            return {"Message": "Customer Deleted"}
        except Exception as e:
            abort(500, "Server Error")
            
    elif response2.status_code == 200:
        if "customer_id" not in request.json():
            abort(400, "Bad Request")
        customer_id = request.json()['customer_id']
        
        try:
            admin_id = response2.json()['admin_id']
            customer = Customer.query.filter_by(user_id=customer_id).first()

            if not customer:
                abort(404, "Customer Not Found")

            db.session.delete(customer)
            db.session.commit()
            
            requests.post(f"{LOG_PATH}/add-log", json={"message": f"Admin {admin_id} Deleted customer: {customer.username}"})

            return {"Message": "Customer Deleted"}
        except Exception as e:
            abort(500, "Server Error")
    
    else:
        abort(403, "Unauthorized")
        

@app.route('/deduct', methods=['POST'])
def deduct():
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
    
    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        customer_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    try:
        admin = requests.get(f"{CUSTOMER_PATH}/customer:{customer_id}")

        if admin.status_code == 404:
            return abort(401, "Unauthorized")
        
        if admin.status_code == 500:
            return abort(500, "Server Error")
    except:
        abort(500, "Server Error")
    
    if 'amount' not in request.json:
        abort(400, "Bad Request")

    amount = request.json['amount']

    if type(amount) != float:
        abort(400, "Bad Request")

    try:
        customer = Customer.query.filter_by(user_id=customer_id).first()

        if not customer:
            return abort(404, "Customer Not found")
        
        if amount > customer.balance:
            return abort(400, "Cannot Deduct Amount")
        
        customer.balance -= amount

        db.session.commit()
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Deducted {amount} from customer {customer.username}"})

        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        return abort(500, "Server error")
    

@app.route('/charge', methods=['POST'])
def charge():
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
    except:
        abort(500, "Server Error")
    
    if 'amount' not in request.json:
        abort(400, "Bad Request")

    amount = request.json['amount']

    if type(amount) != float:
        abort(400, "Bad Request")

    try:
        customer = Customer.query.filter_by(user_id=customer_id).first()

        if not customer:
            return abort(404, "Customer Not found")
        
        customer.balance += amount

        db.session.commit()
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Increased wallet balance of customer {customer.username} by {amount}"})

        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        return abort(500, "Server error")


@app.route('/customer:<int:customer_id>', methods=['GET'])
def get_customer_by_id(customer_id):
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
        customer = Customer.query.filter_by(user_id=customer_id).first()
        
        if not customer:
            return abort(404, "Customer Not Found")
        
        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        return abort(500, "Server Error")


@app.route('/authenticate', methods=['POST'])
def authenticate():
    if 'username' not in request.json or 'password' not in request.json:
        abort(400, "Bad Request")
    username = request.json['username']
    password = request.json['password']
    
    try:
        customer = Customer.query.filter_by(username=username).first()

        if not customer:
            return abort(401, "Unauthorized")
        
        if not bcrypt.check_password_hash(customer.hashed_password, password):
            return abort(401, "Unauthorized")
        
        d = {"token": create_token(customer.user_id)}

        return jsonify(d), 200
    except Exception as e:
        return abort(500, "Server Error")    


if __name__ == "__main__":
    app.run(debug=True, port=5100)