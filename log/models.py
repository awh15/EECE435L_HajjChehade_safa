from shared.db import db, ma, bcrypt
from datetime import datetime

class Log(db.Model):
    log_id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False, unique=True)
    timestamp = db.Column(db.Datetime, nullable=False, default=datetime.now())
    def __init__(self, message):
        super(Log, self).__init__(message=message, timestamp=datetime.now())


class LogSchema(ma.Schema):
    class Meta:
        fields = ('log_id', 'message', 'timestamp')

log_schema = LogSchema()
logs_schema = LogSchema(many=True)