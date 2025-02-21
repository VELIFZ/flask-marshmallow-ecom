from flask_marshmallow import Marshmallow
from marshmallow import fields

from models import User, Address, Order, Product
from app import app

# Marshmallow is initialized (with flask) for serialization, deserialization, and validation.
ma = Marshmallow(app)

## validate incoming data

# Returns basic details by default
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password',) # Exclude password from responses
        
    password = fields.String(load_only=True, allow_none=True)  # Allows NULL passwords for guests - if notrhing None since "" still a securty issue   
    # Dynamically include nested fields only if requested    
    orders = fields.Nested('OrderSchema', many=True, dump_only=True) # read only - only order_date is included by default 
    addresses = fields.Nested('AddressSchema', many=True)
    
    
    def __init__(self, *args, **kwargs):
        # Get optional 'include' parameter from context 
        include_fields = kwargs.pop("include_fields", [])
        super().__init__(*args, **kwargs)
        
        # Remove addresses and orders unless requested
        if "addresses" not in include_fields:
            del self.fields["addresses"]

        if "orders" not in include_fields:
            del self.fields["orders"]

# Returns only 'order_date' by default
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True
        load_instance = True
        
    # Only include 'order_date' by default
    order_date = fields.DateTime(dump_only=True)
        
    # Serialize products within an order - optional inclusion of products
    products = fields.Nested('ProductSchema', many=True, dump_only=True)
    
    def __init__(self, *args, **kwargs):
        include_fields = kwargs.pop('include_fields', [])
        super().__init__(*args, **kwargs)
        
        if 'products' not in include_fields:
            del self.fields['products']
    
class AddressSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Address
        load_instance = True    

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
       
       
# Initialize Schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True) #Can serialize many User objects (a list of user objects)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True) 
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
address_schema = AddressSchema()
addresses_schema = AddressSchema(many=True)

