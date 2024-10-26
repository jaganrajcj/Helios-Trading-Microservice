from flask import Blueprint, request, jsonify
from app.services.behavior_analyzer import BehaviorAnalyzer
from app.models.trade import TradeSchema
from app.utils.validators import validate_trades
import numpy as np

behavior_bp = Blueprint('behavior', __name__)

@behavior_bp.route('/behavior', methods=['POST'])
@validate_trades
def analyze_behavior():
    trades = request.json
    analyzer = BehaviorAnalyzer(trades)
    
    analysis = {
        'overtrading': analyzer.detect_overtrading(),
        'revenge_trading': analyzer.detect_revenge_trading(),
        'risk_management_consistency': analyzer.analyze_risk_management_consistency()
    }
    
    insights = analyzer.get_behavior_insights()
    
    # Convert numpy types to Python native types
    def convert_to_native(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: convert_to_native(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_native(item) for item in obj]
        else:
            return obj

    analysis = convert_to_native(analysis)
    
    return jsonify({
        'analysis': analysis,
        'insights': insights
    })
