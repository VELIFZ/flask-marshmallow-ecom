from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy import select
from schemas import product_schema, products_schema
from models import db, Product

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['POST'])
def create_product():
    product = product_schema.load(request.json)
    db.session.add(product)
    db.session.commit()
    return jsonify(product_schema.dump(product)), 201

@product_bp.route('/products', methods=['GET'])
def get_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()
    return jsonify(products_schema.dump(products)), 200

@product_bp.route('/product/<int:id>', methods=['GET'])
def get_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product_schema.dump(product)), 200

@product_bp.route('/product/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    for key, value in request.json.items():
        setattr(product, key, value)
    db.session.commit()
    return jsonify(product_schema.dump(product)), 200

@product_bp.route('/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200