from flask import Flask, jsonify, abort, request
from flask_cors import CORS

from admin_service.models import Admin, admin_schema, admins_schema
from shared.db import db, ma, bcrypt
from shared.token import create_token, LOG_PATH, ADMIN_PATH, extract_auth_token, decode_token

import requests
import jwt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lab-project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)
ma.init_app(app)

CORS(app)

@app.route('/create-admin', methods=['POST'])
def create_admin():
    '''
    Create new admin.

    Requires:
        username (str)
        password (str)

    Returns:
        200: Admin Schema
        400: Bad Request
        500: Server Error
    '''
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
    if 'username' not in request.json or 'password' not in request.json:
        abort(400, "Bad Request")

    username = request.json['username']
    password = request.json['password']

    try:
        new_admin = Admin(username=username, password=password)
        db.session.add(new_admin)
        db.session.commit()
        
        requests.post(f"{LOG_PATH}/add-log", json={"message": f"Admin {admin_id} created new admin: {username}"})

        return jsonify(admin_schema.dump(new_admin)), 200
    except Exception as e:
        abort(500, "Server Error")


@app.route('/authenticate', methods=['POST'])
def authenticate():
    '''
    Authenticate admin.

    Requires:
        username (str)
        password (str)

    Returns:
        200: Token
        400: Bad Request
        401: Unauthorized
        500: Server Error
    '''
    if 'password' not in request.json or 'username' not in request.json:
        abort(400, "Bad Request")

    username = request.json['username']
    password = request.json['password']
    
    try:
        admin = Admin.query.filter_by(username=username).first()

        if not admin:
            return abort(401, "Unauthorized")
        
        if not bcrypt.check_password_hash(admin.hashed_password, password):
            return abort(401, "Unauthorized")
        
        d = {"token": create_token(admin.admin_id)}

        return jsonify(d), 200
    except Exception as e:
        return abort(500, "Server Error")
    

@app.route('/admin:<int:admin_id>', methods=['GET'])
def get_admin(admin_id):
    '''
    Get admin by id.

    Requires:
        admin_id (int)

    Returns:
        200: Admin Schema
        404: Not Found
        500: Server Error
    '''
    try:
        admin = Admin.query.filter_by(admin_id=admin_id).first()

        if not admin:
            abort(404, "Admin Not Found")
        
        return jsonify(admin_schema.dump(admin)), 200
    except Exception as e:
        abort(500, "Server Error")

if __name__ == '__main__':
    app.run(debug=True, port=5050)