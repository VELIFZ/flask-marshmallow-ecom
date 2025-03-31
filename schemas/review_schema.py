from marshmallow import fields, validates, ValidationError
from schemas import ma
from models.review_model import Review

class ReviewSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Review
        load_instance = True

    id = fields.Int(dump_only=True)
    rating = fields.Int(required=True)
    comment = fields.String()
    seller_id = fields.Int(required=True)
    buyer_id = fields.Int(required=True)
    book_id = fields.Int(allow_none=True)
    order_id = fields.Int(allow_none=True)

    @validates("rating")
    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise ValidationError("Rating must be between 1 and 5.")

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)