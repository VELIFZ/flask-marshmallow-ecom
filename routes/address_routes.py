from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy import select
from schemas import address_schema, addresses_schema
from models import db, Address

address_bp = Blueprint('address', __name__)