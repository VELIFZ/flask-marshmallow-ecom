from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy import select
from schemas import product_schema, products_schema
from models import db, Product

product_bp = Blueprint('product', __name__)