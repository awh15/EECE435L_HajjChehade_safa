from shared.db import db, ma
from enum import Enum
from marshmallow_enum import EnumField

class Category(Enum):
    FOOD = "food"
    CLOTHES = "clothes"
    ACCESSORIES = "accessories"
    ELECTRONICS = "electronics"

class Inventory(db.Model):
    inventory_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    category = db.Column(db.Enum(Category), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(128), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, name, category, price, description, count):
        super(Inventory, self).__init__(name=name, category=category, price=price, description=description, count=count)

class InventorySchema(ma.Schema):
    category = EnumField(Category, by_value=True)
    class Meta:
        model = Inventory
        fields = ('inventory_id', 'name', 'category', 'price', 'description', 'count')

inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)
