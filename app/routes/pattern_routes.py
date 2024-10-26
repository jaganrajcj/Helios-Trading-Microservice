from marshmallow import Schema, fields, pre_load, EXCLUDE
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services.pattern_analyzer import PatternAnalyzer
from app.utils.validators import validate_trades

class TradeSchema(Schema):
    class Meta:
        # Allow unknown fields
        unknown = EXCLUDE

    # Optional fields from MongoDB
    _id = fields.Str(required=False)
    accountId = fields.Int(required=False)  # Making this optional
    screenShotURLs = fields.List(fields.Str(), required=False)
    
    # Required fields
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
    def process_input(self, data, **kwargs):
        # Convert date if it's datetime object
        if isinstance(data.get('date'), datetime):
            data['date'] = data['date'].isoformat()
        
        # Clean pair name (remove forward slash if present)
        if 'pair' in data:
            data['pair'] = data['pair'].replace('/', '')
            
        return data

pattern_bp = Blueprint('pattern', __name__)

# Define your routes here
@pattern_bp.route('/some-route')
def some_route():
    # Your route logic here
    pass

@pattern_bp.route('/patterns', methods=['POST'])
@validate_trades
def analyze_patterns():
    trades = request.json
    analyzer = PatternAnalyzer(trades)
    
    try:
        analysis = {
            'position_size_impact': analyzer.analyze_position_size_impact(),
            'direction_bias': analyzer.analyze_pair_direction_bias(),
            'risk_reward_patterns': analyzer.analyze_risk_reward_patterns()
        }
        
        insights = analyzer.get_all_insights()
        
        return jsonify({
            'analysis': analysis,
            'insights': insights
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
