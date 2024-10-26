from flask import Blueprint, request, jsonify
from app.services.pattern_analyzer import PatternAnalyzer
from app.services.behavior_analyzer import BehaviorAnalyzer
from app.utils.validators import validate_trades
import numpy as np

combined_bp = Blueprint('combined', __name__)

@combined_bp.route('/combined-analysis', methods=['POST'])
@validate_trades
def combined_analysis():
    trades = request.json
    pattern_analyzer = PatternAnalyzer(trades)
    behavior_analyzer = BehaviorAnalyzer(trades)
    
    try:
        pattern_analysis = {
            'position_size_impact': pattern_analyzer.analyze_position_size_impact(),
            'direction_bias': pattern_analyzer.analyze_pair_direction_bias(),
            'risk_reward_patterns': pattern_analyzer.analyze_risk_reward_patterns()
        }
        pattern_insights = pattern_analyzer.get_all_insights()
        
        behavior_analysis = {
            'overtrading': behavior_analyzer.detect_overtrading(),
            'revenge_trading': behavior_analyzer.detect_revenge_trading(),
            'risk_management_consistency': behavior_analyzer.analyze_risk_management_consistency(),
            'loss_recovery_rate': behavior_analyzer.calculate_loss_recovery_rate(),
            'sharpe_ratio': behavior_analyzer.calculate_sharpe_ratio(),
            'risk_level': behavior_analyzer.determine_risk_level()
        }
        behavior_insights = behavior_analyzer.get_behavior_insights()
        key_insights = behavior_analyzer.get_key_insights()
        
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

        pattern_analysis = convert_to_native(pattern_analysis)
        behavior_analysis = convert_to_native(behavior_analysis)
        
        key_trading_insights = pattern_analyzer.get_key_trading_insights()
        
        return jsonify({
            'pattern_analysis': pattern_analysis,
            'pattern_insights': pattern_insights,
            'behavior_analysis': behavior_analysis,
            'behavior_insights': behavior_insights,
            'key_insights': key_insights,
            'key_trading_insights': key_trading_insights
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

