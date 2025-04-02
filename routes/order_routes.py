from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy import select, Table, MetaData, insert, update, delete
from schemas.order_schema import order_schema, orders_schema, OrderSchema
from models import db, Order
from utils.db_helpers import (
    get_table, row_to_dict, rows_to_list, paginate_results,
    handle_error, execute_query, get_by_id, create_record
)

order_bp = Blueprint('order', __name__)

@order_bp.route('/orders', methods=['POST'])
def create_order():
    try:
        # Get data from request
        order_data = request.json
        
        # Print debug info
        print(f"Attempting to create order with data: {order_data}")
        
        # Use direct SQL approach instead of ORM to avoid relationship loading issues
        metadata = MetaData()
        orders_table = Table('orders', metadata, autoload_with=db.engine)
        
        # Import datetime
        from datetime import datetime
        
        # Prepare the data for insertion - only include core fields
        insert_data = {
            'user_id': order_data.get('user_id', 1),  # Default to user 1 if not provided
            'total_amount': order_data.get('total_amount', 0),  # Default to 0 if not provided
            'status': 'Pending',  # Default status
            'payment_status': 'Unpaid',  # Default payment status
            'order_date': datetime.now(),  # Set the order date
            'created_at': datetime.now()  # Set the created_at date
        }
        
        # Add shipping_address_id only if provided to avoid null constraint issues
        if 'shipping_address_id' in order_data and order_data['shipping_address_id']:
            insert_data['shipping_address_id'] = order_data['shipping_address_id']
            
        # Insert the order
        stmt = insert(orders_table).values(**insert_data)
        result = db.session.execute(stmt)
        order_id = result.inserted_primary_key[0]
        
        # If books were provided, add them to the order_book junction table
        if 'books' in order_data and order_data['books']:
            # Create table object for order_book junction
            order_book_table = Table('order_book', metadata, autoload_with=db.engine)
            
            # Add each book to the order
            for book_id in order_data['books']:
                book_data = {
                    'order_id': order_id,
                    'book_id': book_id
                }
                book_stmt = insert(order_book_table).values(**book_data)
                db.session.execute(book_stmt)
        
        # Commit all changes
        db.session.commit()
        
        # Return success response
        insert_data['id'] = order_id
        return jsonify({
            "message": "Order created successfully",
            "order": insert_data
        }), 201
        
    except ValidationError as ve:
        return jsonify({"error": "Validation error", "details": ve.messages}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Order creation error: {str(e)}")
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500

#GET Methods
@order_bp.route('/orders', methods=['GET'])
def get_orders():
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Use direct SQL approach to avoid loading relationships
        orders_table = get_table('orders')
        
        # Build query to exclude canceled orders
        query = select(orders_table).where(orders_table.c.status != "Cancelled")
        
        # Execute query
        orders = execute_query(query)
        
        # Convert to list of dictionaries
        order_list = rows_to_list(orders, orders_table)
        
        # Paginate results
        paginated_orders = paginate_results(order_list, page, limit)
        
        return jsonify({
            "page": page,
            "total": len(order_list),
            "orders": paginated_orders
        }), 200

    except Exception as e:
        return handle_error(e, "getting orders")

@order_bp.route('/order/<int:id>', methods=['GET'])
def get_order(id):
    # Simply use our helper function
    return get_by_id('orders', id)

# PUT
@order_bp.route('/order/<int:id>', methods=['PUT'])
def update_order(id):
    try:
        # Get the orders table
        orders_table = get_table('orders')
        
        # Check if order exists
        result, _ = get_by_id('orders', id, response=False)
        
        if not result:
            return jsonify({"error": "Order not found"}), 404
            
        # Prepare update data from request
        update_data = {}
        for key, value in request.json.items():
            if hasattr(orders_table.c, key):
                update_data[key] = value
        
        # Update the order
        stmt = update(orders_table).where(orders_table.c.id == id).values(**update_data)
        db.session.execute(stmt)
        db.session.commit()
        
        # Return the updated order
        return get_by_id('orders', id)
        
    except Exception as e:
        return handle_error(e, "updating order")

# Delete but cancel
@order_bp.route('/order/<int:id>/cancel', methods=['PUT'])
def cancel_order(id):
    try:
        # Get the orders table
        orders_table = get_table('orders')
        
        # Check if order exists
        result, _ = get_by_id('orders', id, response=False)
        
        if not result:
            return jsonify({"error": "Order not found"}), 404
        
        # Set the status to cancelled (correct spelling with double l)
        stmt = update(orders_table).where(orders_table.c.id == id).values(status="Cancelled")
        db.session.execute(stmt)
        db.session.commit()
        
        return jsonify({"message": "Order cancelled successfully"}), 200
        
    except Exception as e:
        return handle_error(e, "cancelling order")