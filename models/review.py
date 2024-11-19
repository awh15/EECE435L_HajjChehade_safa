from app import db, ma, datetime

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
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    date = db.Column(db.Datetime, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(80))

    def __init__(self, inventory_id, customer_id, date, rating, comment):
        date = datetime.now()
        super(Review, self).__init__(inventory_id=inventory_id, customer_id=customer_id, rating=rating, comment=comment)

class ReviewSchema(ma.Schema):
    class Meta:
        model = Review
        fields = ('review_id', 'inventory_id', 'customer_id', 'date', 'rating', 'comment')

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)