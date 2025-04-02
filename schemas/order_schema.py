from marshmallow import fields
from schemas import ma
from models.order_model import Order

# Includes Books if Requested
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True
        load_instance = True
        
    # Only include these by default
    id = fields.Int(dump_only=True)
    order_date = fields.DateTime(dump_only=True)
    total_amount = fields.Float(dump_only=True, required=True)
    status = fields.String(dump_only=True)
    payment_status = fields.String(dump_only=True)
    tracking_number = fields.String(dump_only=True)
        
    # Serialize books within an order (Dynamically include books only if requested)
    # Relationships
    customer = fields.Nested('UserSchema', only=('id', 'name', 'last_name', 'email'), dump_only=True)
    shipping_address = fields.Nested('AddressSchema', dump_only=True)
    books = fields.Nested('BookSchema', many=True, only=('id', 'title', 'author', 'price'), dump_only=True)
    
    def __init__(self, *args, **kwargs):
        include_fields = kwargs.pop('include_fields', [])
        super().__init__(*args, **kwargs)
        
        include_fields = include_fields or []
        
        # Remove nested fields unless specifically requested
        if 'books' not in include_fields:
            del self.fields['books']
            
        if 'customer' not in include_fields:
            del self.fields['customer']
            
        if 'shipping_address' not in include_fields:
            del self.fields['shipping_address']
        
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True) 