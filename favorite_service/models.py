from shared.db import db, ma, bcrypt

class Favorite(db.Model):
    """
    The Favorite object represents a customer's favorite item.

    :param customer_id: The ID of the customer who marked the item as a favorite
    :type customer_id: int
    :param inventory_id: The ID of the inventory item marked as a favorite
    :type inventory_id: int
    :ivar favorite_id: The unique identifier for the favorite record
    :vartype favorite_id: int
    :ivar customer_id: The ID of the customer who marked the item as a favorite
    :vartype customer_id: int
    :ivar inventory_id: The ID of the inventory item marked as a favorite
    :vartype inventory_id: int
    """
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

class Wishlist(db.Model):
    """
    The Wishlist object represents an item added to a customer's wishlist.

    :param customer_id: The ID of the customer who added the item to their wishlist
    :type customer_id: int
    :param inventory_id: The ID of the inventory item added to the wishlist
    :type inventory_id: int
    :ivar wishlist_id: The unique identifier for the wishlist record
    :vartype wishlist_id: int
    :ivar customer_id: The ID of the customer who added the item to their wishlist
    :vartype customer_id: int
    :ivar inventory_id: The ID of the inventory item added to the wishlist
    :vartype inventory_id: int
    """
    wishlist_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    inventory_id = db.Column(db.Integer, nullable=False)
    def __init__(self, customer_id, inventory_id):
        super(Wishlist, self).__init__(customer_id=customer_id, inventory_id=inventory_id)
        
class WishlistSchema(ma.Schema):
    """
    The WishlistSchema object is used for serializing and deserializing wishlist data.

    :cvar Meta.fields: The fields included in the schema ('wishlist_id', 'customer_id', 'inventory_id')
    :vartype Meta.fields: tuple
    :cvar Meta.model: The associated model for the schema (Wishlist)
    :vartype Meta.model: Wishlist
    """
    class Meta:
        fields = ('wishlist_id', 'customer_id', 'inventory_id') 
        model = Wishlist

wishlist_schema = WishlistSchema()
wishlists_schema = WishlistSchema(many=True)