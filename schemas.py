from flask_marshmallow import Marshmallow
from marshmallow import fields

from models import User, Address, Order, Product
from app import app

# Marshmallow is initialized (with flask) for serialization, deserialization, and validation.
ma = Marshmallow(app)

# validate incoming data

# Returns basic details by default
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        
    password = fields.String(load_only=True, allow_none=True) 
    # Allows NULL passwords for guests - if notrhing None since "" still a securty issue   
    # Dynamically include nested fields only if requested    
    orders = fields.Nested('OrderSchema', many=True, dump_only=True) # read only - only order_date is included by default 
    addresses = fields.Nested('AddressSchema', many=True)
    
    
    def __init__(self, *args, **kwargs):
        # Get 'include' parameter in endpoints 
        include_fields = kwargs.pop("include_fields", [])
        super().__init__(*args, **kwargs)
        
        # bunsuz user_routes'de kullaninca error verdi. 
        include_fields = include_fields or []
        
        # Remove addresses and orders unless requested
        if "addresses" not in include_fields:
            del self.fields["addresses"]

        if "orders" not in include_fields:
            del self.fields["orders"]

# MARK: Order Schema
# Includes Books if Requested
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True
        load_instance = True
        
    # Only include these by default
    id = fields.Int(dump_only=True)
    order_date = fields.DateTime(dump_only=True)
    total_amount = fields.Float(dump_only=True)
    status = fields.String(dump_only=True)
    payment_status = fields.String(dump_only=True)
        
    # Serialize books within an order (Dynamically include products only if requested)
    books = fields.Nested('BookSchema', many=True, dump_only=True)
    
    def __init__(self, *args, **kwargs):
        include_fields = kwargs.pop('include_fields', [])
        super().__init__(*args, **kwargs)
        
        if 'books' not in include_fields:
            del self.fields['books']
    
class AddressSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Address
        load_instance = True
        include_fk = True  

    user_id = fields.Int(required=True)

class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
       
       
# Initialize Schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True) #Can serialize many User objects (a list of user objects)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True) 
product_schema = BookSchema()
products_schema = BookSchema(many=True)
address_schema = AddressSchema()
addresses_schema = AddressSchema(many=True)


# class ReviewSchema(Schema):
#     rating = fields.Int(required=True)

#     @validates("rating")
#     def validate_rating(self, value):
#         if value < 1 or value > 5:
#             raise ValidationError("Rating must be between 1 and 5.")