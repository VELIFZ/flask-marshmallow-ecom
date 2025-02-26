from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy import select
from schemas import product_schema, products_schema
from models import db, Product

product_bp = Blueprint('product', __name__)

# # ✅ PAGINATED GET /products
# @bp.route('/products', methods=['GET'])
# def get_products():
#     page = request.args.get('page', 1, type=int)
#     limit = request.args.get('limit', 10, type=int)

#     products = Product.query.paginate(page=page, per_page=limit, error_out=False)

#     return jsonify({
#         "page": page,
#         "total_pages": products.pages,
#         "total_products": products.total,
#         "products": products_schema.dump(products.items)
#     }), 200

# 🛠 Test Pagination in Postman

# 1️⃣ Get First Page of Users
# GET http://127.0.0.1:5000/users?page=1&limit=5