from shared.db import db, ma
from datetime import datetime

class Sale(db.Model):
    """
    The Sale object represents a sale transaction in the system.

    :param inventory_id: The ID of the inventory item sold
    :type inventory_id: int
    :param customer_id: The ID of the customer who purchased the item
    :type customer_id: int
    :param quantity: The quantity of the item sold
    :type quantity: int
    :param price: The price of the item at the time of sale
    :type price: float
    :ivar sale_id: The unique identifier for the sale
    :vartype sale_id: int
    :ivar inventory_id: The ID of the inventory item sold
    :vartype inventory_id: int
    :ivar customer_id: The ID of the customer who purchased the item
    :vartype customer_id: int
    :ivar date: The date when the sale occurred
    :vartype date: str
    :ivar quantity: The quantity of the item sold
    :vartype quantity: int
    :ivar price: The price of the item at the time of sale
    :vartype price: float
    """
    sale_id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(30), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __init__(self, inventory_id, customer_id, quantity, price):
        self.date = datetime.now()
        super(Sale, self).__init__(inventory_id=inventory_id, customer_id=customer_id, quantity=quantity, price=price)

class SaleSchema(ma.Schema):
    """
    The SaleSchema object is used for serializing and deserializing sale data.

    :cvar Meta.fields: The fields included in the schema ('sale_id', 'inventory_id', 'customer_id', 'quantity', 'price', 'date')
    :vartype Meta.fields: tuple
    :cvar Meta.model: The associated model for the schema (Sale)
    :vartype Meta.model: Sale
    """
    class Meta:
        model = Sale
        fields = ('sale_id', 'inventory_id', 'customer_id', 'quantity', 'price', 'date')

sale_schema = SaleSchema()
sales_schema = SaleSchema(many=True)