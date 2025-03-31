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
            #self.fields.pop("books", None)
    
        
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True) 