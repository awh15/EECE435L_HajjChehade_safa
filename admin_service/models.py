from shared.db import db, ma, bcrypt

'''
• Admin ID
• Username
• Password
'''

class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    hashed_password = db.Column(db.String(128), nullable=False)
    def __init__(self, username, password):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        super(Admin, self).__init__(username=username)


class AdminSchema(ma.Schema):
    class Meta:
        fields = ('admin_id', 'username')

admin_schema = AdminSchema()
admins_schema = AdminSchema(many=True)