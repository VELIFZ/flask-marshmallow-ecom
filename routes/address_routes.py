from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy import select, insert, update, delete, Table, MetaData
from schemas.address_schema import address_schema, addresses_schema
from models import db, Address
from utils.db_helpers import (
    get_table, row_to_dict, rows_to_list, paginate_results,
    handle_error, execute_query, get_by_id, create_record
)

address_bp = Blueprint('address', __name__)

@address_bp.route('/addresses', methods=['POST'])
def create_address():
    try:
        # Get address data from request
        address_data = request.json
        
        # Create the address using our helper function
        return create_record('addresses', address_data)
        
    except ValidationError as ve:
        return jsonify({"error": "Validation error", "details": ve.messages}), 400
    except Exception as e:
        return handle_error(e, "creating address")

@address_bp.route('/addresses', methods=['GET'])
def get_addresses():
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Use direct SQL approach to avoid loading relationships
        addresses_table = get_table('addresses')
        
        # Build the query
        query = select(addresses_table)
        
        # Execute query
        addresses = execute_query(query)
        
        # Convert to list of dictionaries
        address_list = rows_to_list(addresses, addresses_table)
        
        # Paginate results
        paginated_addresses = paginate_results(address_list, page, limit)
        
        return jsonify({
            "page": page,
            "total": len(address_list),
            "addresses": paginated_addresses
        }), 200
        
    except Exception as e:
        return handle_error(e, "getting addresses")

@address_bp.route('/user/<int:user_id>/addresses', methods=['GET'])
def get_user_addresses(user_id):
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Use direct SQL approach to avoid loading relationships
        addresses_table = get_table('addresses')
        
        # Build the query to get addresses for a specific user
        query = select(addresses_table).where(addresses_table.c.user_id == user_id)
        
        # Execute query
        addresses = execute_query(query)
        
        # Convert to list of dictionaries
        address_list = rows_to_list(addresses, addresses_table)
        
        # Paginate results
        paginated_addresses = paginate_results(address_list, page, limit)
        
        return jsonify({
            "page": page,
            "total": len(address_list),
            "addresses": paginated_addresses
        }), 200
        
    except Exception as e:
        return handle_error(e, f"getting addresses for user {user_id}")

@address_bp.route('/address/<int:id>', methods=['GET'])
def get_address(id):
    # Simply use our helper function
    return get_by_id('addresses', id)

@address_bp.route('/address/<int:id>', methods=['PUT'])
def update_address(id):
    try:
        addresses_table = get_table('addresses')
        
        # First check if the address exists
        result, _ = get_by_id('addresses', id, response=False)
        
        if not result:
            return jsonify({"error": "Address not found"}), 404
        
        # Prepare update data from request
        update_data = {}
        for key, value in request.json.items():
            if hasattr(addresses_table.c, key):
                update_data[key] = value
        
        # Update the address
        stmt = update(addresses_table).where(addresses_table.c.id == id).values(**update_data)
        db.session.execute(stmt)
        db.session.commit()
        
        # Get the updated address
        return get_by_id('addresses', id)
        
    except ValidationError as ve:
        return jsonify({"error": "Validation error", "details": ve.messages}), 400
    except Exception as e:
        return handle_error(e, "updating address")

@address_bp.route('/address/<int:id>', methods=['DELETE'])
def delete_address(id):
    try:
        addresses_table = get_table('addresses')
        
        # First check if the address exists
        result, _ = get_by_id('addresses', id, response=False)
        
        if not result:
            return jsonify({"error": "Address not found"}), 404
        
        # Delete the address
        stmt = delete(addresses_table).where(addresses_table.c.id == id)
        db.session.execute(stmt)
        db.session.commit()
        
        return jsonify({"message": "Address deleted successfully"}), 200
    except Exception as e:
        return handle_error(e, "deleting address")

@address_bp.route('/user/<int:user_id>/addresses/default-shipping/<int:address_id>', methods=['PUT'])
def set_default_shipping(user_id, address_id):
    try:
        # Get addresses table
        addresses_table = get_table('addresses')
        
        # First check if the address exists and belongs to the user
        query = select(addresses_table).where(
            (addresses_table.c.id == address_id) & 
            (addresses_table.c.user_id == user_id)
        )
        address = db.session.execute(query).first()
        
        if not address:
            return jsonify({"error": "Address not found or does not belong to user"}), 404
        
        # First, reset all is_default flags for this user's addresses
        stmt = update(addresses_table).where(
            addresses_table.c.user_id == user_id
        ).values(
            is_default=False
        )
        db.session.execute(stmt)
        
        # Then set this address as the default shipping address
        stmt = update(addresses_table).where(
            addresses_table.c.id == address_id
        ).values(
            is_default=True
        )
        db.session.execute(stmt)
        db.session.commit()
        
        return jsonify({"message": "Default shipping address updated successfully"}), 200
        
    except Exception as e:
        return handle_error(e, "setting default shipping address")

@address_bp.route('/user/<int:user_id>/addresses/default-billing/<int:address_id>', methods=['PUT'])
def set_default_billing(user_id, address_id):
    try:
        # Since we only have a single is_default field, this endpoint will function 
        # the same as the default shipping endpoint for now
        return set_default_shipping(user_id, address_id)
        
    except Exception as e:
        return handle_error(e, "setting default billing address")

@address_bp.route('/user/<int:user_id>/addresses/defaults', methods=['GET'])
def get_default_addresses(user_id):
    try:
        # Get addresses table
        addresses_table = get_table('addresses')
        
        # Initialize result
        defaults = {
            "default_address": None
        }
        
        # Get default address
        address_query = select(addresses_table).where(
            (addresses_table.c.user_id == user_id) & 
            (addresses_table.c.is_default == True)
        )
        default_address = db.session.execute(address_query).first()
        if default_address:
            defaults["default_address"] = row_to_dict(default_address, addresses_table)
        
        return jsonify(defaults), 200
        
    except Exception as e:
        return handle_error(e, "getting default address")
