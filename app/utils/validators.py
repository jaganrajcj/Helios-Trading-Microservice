from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError
from app.models.trade import TradeSchema

def validate_trades(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        schema = TradeSchema(many=True)
        try:
            schema.load(request.json)
        except ValidationError as err:
            return jsonify(err.messages), 400
        return f(*args, **kwargs)
    return decorated_function
