from shared.db import db, ma, bcrypt
from datetime import datetime

class Log(db.Model):
    """
    The Log object represents a log entry in the system.

    :param message: The log message
    :type message: str
    :param timestamp: The timestamp when the log was created (defaults to the current datetime)
    :type timestamp: str
    :ivar log_id: The unique identifier for the log
    :vartype log_id: int
    :ivar message: The content of the log message
    :vartype message: str
    :ivar timestamp: The time at which the log entry was created
    :vartype timestamp: str
    """
    log_id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False, unique=True)
    timestamp = db.Column(db.String(30), nullable=False, default=datetime.now())
    def __init__(self, message):
        super(Log, self).__init__(message=message, timestamp=datetime.now())


class LogSchema(ma.Schema):
    """
    The LogSchema object is used for serializing and deserializing log data.

    :cvar Meta.fields: The fields included in the schema ('log_id', 'message', 'timestamp')
    :vartype Meta.fields: tuple
    """
    class Meta:
        fields = ('log_id', 'message', 'timestamp')

log_schema = LogSchema()
logs_schema = LogSchema(many=True)