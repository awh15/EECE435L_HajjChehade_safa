from shared.db import db, ma, bcrypt

class Admin(db.Model):
    """
    The Admin object represents an admin user in the system.

    :param username: The username of the admin
    :type username: str
    :param password: The password for the admin account (hashed for storage)
    :type password: str
    :ivar admin_id: The unique identifier for the admin
    :vartype admin_id: int
    :ivar username: The username of the admin
    :vartype username: str
    :ivar hashed_password: The hashed password of the admin
    :vartype hashed_password: str
    """
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    hashed_password = db.Column(db.String(128), nullable=False)
    def __init__(self, username, password):
        self.hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        super(Admin, self).__init__(username=username)


class AdminSchema(ma.Schema):
    """
    The AdminSchema object is used for serializing and deserializing admin data.

    :ivar Meta.fields: The fields to include in the schema ('admin_id' and 'username')
    :vartype Meta.fields: tuple
    """
    class Meta:
        fields = ('admin_id', 'username')

admin_schema = AdminSchema()
admins_schema = AdminSchema(many=True)