from marshmallow import fields, validate, pre_load
from schemas import ma
from models.address_model import Address, AddressType

class AddressSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Address
        load_instance = True
        include_fk = True

    id = fields.Int(dump_only=True)
    street = fields.String(required=True)
    city = fields.String(required=True)
    state = fields.String(required=True)
    postal_code = fields.String(required=True)
    country = fields.String(required=True)
    is_default = fields.Bool()
    #address_type = fields.String(validate=lambda type: type in ["Home", "Work", "Other"])
    address_type = fields.String(validate = validate.OneOf([item.value for item in AddressType]))
    user_id = fields.Int(required=True)
    
    @pre_load
    def normalize_address_type(self, data, **kwargs):
        if "address_type" in data and isinstance(data["address_type"], str):
            data["address_type"] = data["address_type"].title()
        return data

address_schema = AddressSchema()
addresses_schema = AddressSchema(many=True)