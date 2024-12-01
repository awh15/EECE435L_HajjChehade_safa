from shared.db import db, ma
from datetime import datetime

class Review(db.Model):
    """
    The Review object represents a customer review for an inventory item.

    :param inventory_id: The ID of the inventory item being reviewed
    :type inventory_id: int
    :param customer_id: The ID of the customer who submitted the review
    :type customer_id: int
    :param rating: The rating given by the customer
    :type rating: int
    :param comment: The comment provided by the customer (optional)
    :type comment: str, optional
    :ivar review_id: The unique identifier for the review
    :vartype review_id: int
    :ivar inventory_id: The ID of the inventory item being reviewed
    :vartype inventory_id: int
    :ivar customer_id: The ID of the customer who submitted the review
    :vartype customer_id: int
    :ivar date: The date when the review was submitted
    :vartype date: str
    :ivar rating: The rating given by the customer
    :vartype rating: int
    :ivar comment: The comment provided by the customer (optional)
    :vartype comment: str
    :ivar flag: A moderation flag indicating the review's status (e.g., inappropriate or spam)
    :vartype flag: bool, optional
    """

    review_id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(30), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(80))
    flag = db.Column(db.Boolean, nullable=True)

    def __init__(self, inventory_id, customer_id, rating, comment):
        self.date = datetime.now()
        self.flag = None
        super(Review, self).__init__(inventory_id=inventory_id, customer_id=customer_id, rating=rating, comment=comment)

class ReviewSchema(ma.Schema):
    """
    The ReviewSchema object is used for serializing and deserializing review data.

    :cvar Meta.fields: The fields included in the schema ('review_id', 'inventory_id', 'customer_id', 'date', 'rating', 'comment', 'flag')
    :vartype Meta.fields: tuple
    :cvar Meta.model: The associated model for the schema (Review)
    :vartype Meta.model: Review
    """
    class Meta:
        model = Review
        fields = ('review_id', 'inventory_id', 'customer_id', 'date', 'rating', 'comment', 'flag')

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)