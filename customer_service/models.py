from shared.db import db, ma, bcrypt
from enum import Enum
from marshmallow_enum import EnumField

class Gender(Enum):
    """
    The Gender enumeration represents the gender of a customer.

    :cvar MALE: Represents male gender
    :vartype MALE: str
    :cvar FEMALE: Represents female gender
    :vartype FEMALE: str
    """
    MALE = "male"
    FEMALE = "female"
    
class MaritalStatus(Enum):
    """
    The MaritalStatus enumeration represents the marital status of a customer.

    :cvar SINGLE: Indicates the customer is single
    :vartype SINGLE: str
    :cvar MARRIED: Indicates the customer is married
    :vartype MARRIED: str
    :cvar DIVORCED: Indicates the customer is divorced
    :vartype DIVORCED: str
    :cvar WIDOWED: Indicates the customer is widowed
    :vartype WIDOWED: str
    """
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"

class Customer(db.Model):
    """
    The Customer object represents a customer in the system.

    :param full_name: The full name of the customer
    :type full_name: str
    :param username: The username of the customer (must be unique)
    :type username: str
    :param password: The plain-text password for the customer (hashed for storage)
    :type password: str
    :param age: The age of the customer
    :type age: int
    :param address: The address of the customer
    :type address: str
    :param gender: The gender of the customer
    :type gender: Gender
    :param marital_status: The marital status of the customer
    :type marital_status: MaritalStatus
    :ivar user_id: The unique identifier for the customer
    :vartype user_id: int
    :ivar balance: The current balance of the customer (default is 0)
    :vartype balance: float
    :ivar hashed_password: The hashed password of the customer
    :vartype hashed_password: str
    """
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
        self.hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.balance = 0
        super(Customer, self).__init__(full_name=full_name, username=username, age=age, address=address, gender=gender, marital_status=marital_status)
    
class CustomerSchema(ma.Schema):
    """
    The CustomerSchema object is used for serializing and deserializing customer data.

    :ivar gender: The gender of the customer serialized using EnumField
    :vartype gender: Gender
    :ivar marital_status: The marital status of the customer serialized using EnumField
    :vartype marital_status: MaritalStatus
    :cvar Meta.fields: The fields included in the schema
    :vartype Meta.fields: tuple
    """
    gender = EnumField(Gender, by_value=True)
    marital_status = EnumField(MaritalStatus, by_value=True)
    class Meta:
        model = Customer
        fields = ('user_id', 'full_name', 'username', 'age', 'address', 'gender', 'marital_status', 'balance')

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)