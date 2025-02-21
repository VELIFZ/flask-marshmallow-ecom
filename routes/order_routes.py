from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy import select
from schemas import order_schema, orders_schema
from models import db, Order

order_bp = Blueprint('order', __name__)