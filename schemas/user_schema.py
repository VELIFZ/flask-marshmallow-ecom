from marshmallow import fields
from schemas import ma
from models.user_model import User

# validate incoming data

# Returns basic details by default
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User # Connects the schema to the User model (Maps to User model)
        load_instance = True # Deserializes data directly into a User instance instead of just dictionary
    
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    last_name = fields.String(required=True)
    phone_number = fields.String(required=True)
    email = fields.Email(required=True)
    # Allows NULL passwords for guests - if notrhing None since "" still a securty issue 
    password = fields.String(load_only=True, allow_none=True) 
    is_seller = fields.Bool()
    rating = fields.Float()
    total_sales = fields.Int()
    # Dynamically include nested fields only if requested    
    orders = fields.Nested('OrderSchema', many=True, dump_only=True) # read only - only basic info is included by default 
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
            
# Initialize instances
user_schema = UserSchema()
users_schema = UserSchema(many=True) #Can serialize many User objects (a list of user objects)