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
    """
    Create a new admin.

    :param request: HTTP request containing 'username' and 'password' in JSON, defaults to None
    :type request: flask.Request
    :raises jwt.ExpiredSignatureError: If the token has expired
    :raises jwt.InvalidTokenError: If the token is invalid
    :raises werkzeug.exceptions.HTTPException: 403 if unauthorized or token issues, 400 for bad request, 500 for server error
    :return: JSON representation of the created admin
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
        print(e)
        abort(500, "Server Error")


@app.route('/authenticate', methods=['POST'])
def authenticate():
    """
    Authenticate an admin.

    :param request: HTTP request containing 'username' and 'password' in JSON, defaults to None
    :type request: flask.Request
    :raises werkzeug.exceptions.HTTPException: 400 if bad request, 401 if unauthorized, 500 for server error
    :return: JSON containing the authentication token
    :rtype: flask.Response
    """
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
    """
    Get an admin by their ID.

    :param admin_id: The ID of the admin
    :type admin_id: int
    :raises werkzeug.exceptions.HTTPException: 404 if admin not found, 500 for server error
    :return: JSON representation of the admin
    :rtype: flask.Response
    """

    try:
        admin = Admin.query.filter_by(admin_id=admin_id).first()

        if not admin:
            abort(404, "Admin Not Found")
        
        return jsonify(admin_schema.dump(admin)), 200
    except Exception as e:
        abort(500, "Server Error")

if __name__ == '__main__':
    app.run(debug=True, port=5050)