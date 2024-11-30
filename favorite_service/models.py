from shared.db import db, ma, bcrypt

'''
• Favorite ID
• Customer ID (foreign key)
• Inventory ID (foreign key)
'''

class Favorite(db.Model):
    favorite_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    inventory_id = db.Column(db.Integer, nullable=False)
    def __init__(self, customer_id, inventory_id):
        super(Favorite, self).__init__(customer_id=customer_id, inventory_id=inventory_id) 

class FavoriteSchema(ma.Schema):
    class Meta:
        fields = ('favorite_id', 'customer_id', 'inventory_id') 
        model = Favorite

favorite_schema = FavoriteSchema()
favorites_schema = FavoriteSchema(many=True)

'''
• Wishlist ID
• Customer ID (foreign key)
• Inventory ID (foreign key)
'''

class Wishlist(db.Model):
    wishlist_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    inventory_id = db.Column(db.Integer, nullable=False)
    def __init__(self, customer_id, inventory_id):
        super(Wishlist, self).__init__(customer_id=customer_id, inventory_id=inventory_id)
        
class WishlistSchema(ma.Schema):
    class Meta:
        fields = ('wishlist_id', 'customer_id', 'inventory_id') 
        model = Wishlist

wishlist_schema = WishlistSchema()
wishlists_schema = WishlistSchema(many=True)