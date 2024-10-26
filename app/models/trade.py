from marshmallow import Schema, fields, pre_load
from datetime import datetime

class TradeSchema(Schema):
    accountId = fields.Int(required=True)
    pair = fields.Str(required=True)
    direction = fields.Str(required=True)
    status = fields.Str(required=True)
    strategy = fields.Str(allow_none=True)
    date = fields.DateTime(required=True)
    accountBalance = fields.Float(required=True)
    entryPrice = fields.Float(required=True)
    size = fields.Float(required=True)
    stopLoss = fields.Float(required=True)
    target = fields.Float(required=True)
    exitPrice = fields.Float(required=True)
    netPNL = fields.Float(required=True)
    accountChange = fields.Float(required=True)

    @pre_load
    def process_date(self, data, **kwargs):
        if isinstance(data.get('date'), datetime):
            data['date'] = data['date'].isoformat()
        return data