from shared.db import db, ma
from datetime import datetime


'''
• Sale ID
• Inventory ID (foreign key)
• Customer ID (foreign key)
• Date
• Quantity
• Price
'''

class Sale(db.Model):
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
    class Meta:
        model = Sale
        fields = ('sale_id', 'inventory_id', 'customer_id', 'quantity', 'price', 'date')

sale_schema = SaleSchema()
sales_schema = SaleSchema(many=True)