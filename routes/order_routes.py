from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy import select
from schemas import order_schema, orders_schema, OrderSchema
from models import db, Order

order_bp = Blueprint('order', __name__)

@order_bp.route('/orders', methods=['POST'])
def create_order():
    order = order_schema.load(request.json)
    db.session.add(order)
    db.session.commit()
    return jsonify(order_schema.dump(order)), 201

#GET Methods
@order_bp.route('/orders', methods=['GET'])
def get_orders():
    try:
        query = select(Order).where(Order.status != "canceled")  # no canceled orders

        orders = db.session.execute(query).scalars().all()
        return jsonify(orders_schema.dump(orders)), 200

    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500

@order_bp.route('/order/<int:id>', methods=['GET'])
def get_order(id):
    try:
        order = db.session.get(Order, id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        include = request.args.get('include', '', type=str)
        include_fields = include.split(',') if include else []

        order_schema_dynamic = OrderSchema(include_fields=include_fields)

        return jsonify(order_schema_dynamic.dump(order)), 200

    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500

# PUT
@order_bp.route('/order/<int:id>', methods=['PUT'])
def update_order(id):
    order = db.session.get(Order, id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    for key, value in request.json.items():
        setattr(order, key, value)
    db.session.commit()
    return jsonify(order_schema.dump(order)), 200

# Delete but cancel
@order_bp.route('/order/<int:id>/cancel', methods=['PUT'])
def cancel_order(id):
    try:
        order = db.session.get(Order, id)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        order.status = "canceled"
        db.session.commit()

        return jsonify({"message": "Order canceled successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500