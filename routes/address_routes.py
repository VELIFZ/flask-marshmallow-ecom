from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy import select
from schemas import address_schema, addresses_schema
from models import db, Address

address_bp = Blueprint('address', __name__)

@address_bp.route('/addresses', methods=['POST'])
def create_address():
    try:
        data = request.json
        new_address = address_schema.load(data)
        db.session.add(new_address)
        db.session.commit()
        return jsonify(address_schema.dump(new_address)), 201
    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500

@address_bp.route('/addresses', methods=['GET'])
def get_addresses():
    query = select(Address)
    addresses = db.session.execute(query).scalars().all()
    return jsonify(addresses_schema.dump(addresses)), 200

@address_bp.route('/address/<int:id>', methods=['GET'])
def get_address(id):
    address = db.session.get(Address, id)
    if not address:
        return jsonify({"error": "Address not found"}), 404
    return jsonify(address_schema.dump(address)), 200

@address_bp.route('/address/<int:id>', methods=['PUT'])
def update_address(id):
    address = db.session.get(Address, id)
    if not address:
        return jsonify({"error": "Address not found"}), 404
    for key, value in request.json.items():
        setattr(address, key, value)
    db.session.commit()
    return jsonify(address_schema.dump(address)), 200

@address_bp.route('/address/<int:id>', methods=['DELETE'])
def delete_address(id):
    address = db.session.get(Address, id)
    if not address:
        return jsonify({"error": "Address not found"}), 404
    db.session.delete(address)
    db.session.commit()
    return jsonify({"message": "Address deleted"}), 200
