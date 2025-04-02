from marshmallow import fields
from schemas import ma
from models.book_model import Book

class BookSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Book
        load_instance = True
        
    id = fields.Int(dump_only=True)
    title = fields.String(required=True)
    author = fields.String(required=True)
    price = fields.Float(required=True)
    description = fields.String()
    condition = fields.String()
    genre = fields.String()
    publication_year = fields.Int()
    isbn = fields.String()
    status = fields.String()
    image_url = fields.String()
    
    # Add relationships
    seller_id = fields.Int(required=True)
    seller = fields.Nested('UserSchema', only=('id', 'name', 'last_name', 'rating'), dump_only=True)
    reviews = fields.Nested('ReviewSchema', many=True, dump_only=True)
    
    def __init__(self, *args, **kwargs):
        include_fields = kwargs.pop('include_fields', [])
        super().__init__(*args, **kwargs)
        
        include_fields = include_fields or []
        
        # Remove nested fields unless specifically requested
        if "seller" not in include_fields:
            del self.fields["seller"]
            
        if "reviews" not in include_fields:
            del self.fields["reviews"]
    
book_schema = BookSchema()
books_schema = BookSchema(many=True)