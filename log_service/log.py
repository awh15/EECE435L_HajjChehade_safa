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
    """
    Retrieve all logs.

    :raises werkzeug.exceptions.HTTPException: 500 for server errors
    :return: JSON representation of all logs
    :rtype: flask.Response
    """
    logs = Log.query.all()
    return jsonify(logs_schema.dump(logs)), 200

@app.route('/add-log', methods=['POST'])
def add_log():
    """
    Add a new log message.

    :param message: The log message to be added
    :type message: str
    :raises werkzeug.exceptions.HTTPException: 400 for bad request, 500 for server errors
    :return: JSON representation of the newly created log
    :rtype: flask.Response
    """
    if 'message' not in request.json:
        abort(400, "Bad request")
    log = Log(message=request.json['message'])
    db.session.add(log)
    db.session.commit()
    return jsonify(log_schema.dump(log)), 200


if __name__ == '__main__':
    app.run(debug=True, port=5250)