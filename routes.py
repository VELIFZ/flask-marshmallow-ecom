from schemas import user_schema, order_schema, product_schema, address_schema
from models import db, User, Order, Product, Address
from app import app

from flask import request, jsonify,Blueprint
from marshmallow import ValidationError
from sqlalchemy import select


# Blueprints
