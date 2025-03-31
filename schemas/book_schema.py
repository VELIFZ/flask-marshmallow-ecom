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
    
book_schema = BookSchema()
books_schema = BookSchema(many=True)