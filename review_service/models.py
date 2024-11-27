from shared.db import db, ma
from datetime import datetime

'''
• Review ID
• Inventory ID (foreign key)
• Customer ID (foreign key)
• Date
• Rating
• Comment
'''

class Review(db.Model):
    review_id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.inventory_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.user_id'), nullable=False)
    date = db.Column(db.String(30), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(80))
    flag = db.Column(db.Boolean, nullable=True)

    def __init__(self, inventory_id, customer_id, date, rating, comment):
        self.date = datetime.now()
        self.flag = None
        super(Review, self).__init__(inventory_id=inventory_id, customer_id=customer_id, rating=rating, comment=comment)

class ReviewSchema(ma.Schema):
    class Meta:
        model = Review
        fields = ('review_id', 'inventory_id', 'customer_id', 'date', 'rating', 'comment', 'flag')

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)