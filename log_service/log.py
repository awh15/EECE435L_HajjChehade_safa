from flask import Flask, jsonify, abort, request
from flask_cors import CORS

from log_service.models import Log, logs_schema, log_schema
from shared.db import db, ma, bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lab-project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)
ma.init_app(app)

CORS(app)


@app.route('/logs', methods=['GET'])
def get_logs():
    logs = Log.query.all()
    return jsonify(logs_schema.dump(logs)), 200

@app.route('/add-log', methods=['POST'])
def add_log():
    if 'message' not in request.json:
        abort(400, "Bad request")
    log = Log(message=request.json['message'])
    db.session.add(log)
    db.session.commit()
    return jsonify(log_schema.dump(log)), 200