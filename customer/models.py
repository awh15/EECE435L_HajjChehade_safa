from shared.db import db, ma, bcrypt
from enum import Enum
from marshmallow_enum import EnumField

'''
• Customer ID
• Full name
• Username (unique)
• Password
• Balance
• Age
• Address
• Gender
• Maritalstatus
'''

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    
class MaritalStatus(Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"

class Customer(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    hashed_password = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.Enum(Gender), nullable=False)
    marital_status = db.Column(db.Enum(MaritalStatus), nullable=False)

    def __init__(self, full_name, username, password, age, address, gender, marital_status):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        balance = 0
        super(Customer, self).__init__(full_name=full_name, username=username, age=age, address=address, gender=gender, marital_status=marital_status)
    
class CustomerSchema(ma.Schema):
    gender = EnumField(Gender, by_value=True)
    marital_status = EnumField(MaritalStatus, by_value=True)
    class Meta:
        model = Customer
        fields = ('user_id', 'full_name', 'username', 'age', 'address', 'gender', 'marital_status')

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)