import pandas as pd
import numpy as np
from typing import List, Dict, Any, Union
from app.utils.helpers import calculate_trade_metrics

class PatternAnalyzer:
    def __init__(self, trades: Union[List[Dict[Any, Any]], Dict[Any, Any]]):
        # Convert single trade to list if necessary
        trades_list = [trades] if isinstance(trades, dict) else trades
        self.trades_df = calculate_trade_metrics(trades_list)
    
    def analyze_position_size_impact(self) -> Dict:
        """Analyze how position size affects win rate"""
        if len(self.trades_df) < 4:
            # Handle small number of trades
            size_groups = pd.qcut(self.trades_df['size'], 
                                min(len(self.trades_df), 4), 
                                labels=['Small', 'Medium', 'Large', 'Very Large'][:len(self.trades_df)],
                                duplicates='drop')
        else:
            size_groups = pd.qcut(self.trades_df['size'], 4, 
                                labels=['Small', 'Medium', 'Large', 'Very Large'])
            
        self.trades_df['size_quartile'] = size_groups
        
        size_analysis = self.trades_df.groupby('size_quartile', observed=True).agg({
            'status': lambda x: (x == 'win').mean(),
            'netPNL': ['mean', 'std'],
            'accountChange': ['mean', 'std']
        }).round(4)
        
        # Convert the multi-index DataFrame to a nested dictionary with string keys
        result = {}
        for size_group in size_analysis.index:
            result[str(size_group)] = {
                'win_rate': float(size_analysis.loc[size_group, 'status']),
                'netPNL': {
                    'mean': float(size_analysis.loc[size_group, ('netPNL', 'mean')]),
                    'std': float(size_analysis.loc[size_group, ('netPNL', 'std')])
                },
                'accountChange': {
                    'mean': float(size_analysis.loc[size_group, ('accountChange', 'mean')]),
                    'std': float(size_analysis.loc[size_group, ('accountChange', 'std')])
                }
            }
        
        return result
    
    def analyze_pair_direction_bias(self) -> Dict:
        """Analyze win rates and profitability by direction for each pair"""
        direction_analysis = self.trades_df.groupby(['pair', 'direction']).agg({
            'status': lambda x: (x == 'win').mean(),
            'netPNL': 'mean',
            'accountChange': 'mean'
        }).round(4)
        
        # Convert the multi-index DataFrame to a nested dictionary with string keys
        result = {}
        for (pair, direction), row in direction_analysis.iterrows():
            if pair not in result:
                result[pair] = {}
            result[pair][direction] = {
                'win_rate': float(row['status']),
                'avg_netPNL': float(row['netPNL']),
                'avg_accountChange': float(row['accountChange'])
            }
        
        return result
    
    def analyze_risk_reward_patterns(self) -> Dict:
        """Analyze risk/reward ratio effectiveness"""
        if len(self.trades_df) < 4:
            # For small number of trades, use fewer groups
            rr_groups = pd.qcut(self.trades_df['rr_ratio'], 
                              min(len(self.trades_df), 4), 
                              duplicates='drop')
        else:
            rr_groups = pd.qcut(self.trades_df['rr_ratio'], 4)
            
        rr_analysis = self.trades_df.groupby(rr_groups).agg({
            'status': lambda x: (x == 'win').mean(),
            'netPNL': 'mean'
        }).round(4)
        
        # Convert the index to strings and then to a dictionary
        result = {}
        for rr_range, row in rr_analysis.iterrows():
            key = f"{rr_range.left:.2f}-{rr_range.right:.2f}"
            result[key] = {
                'win_rate': float(row['status']),  # Convert to float
                'avg_netPNL': float(row['netPNL'])  # Convert to float
            }
        
        return result

    def get_position_size_insights(self) -> List[str]:
        analysis = self.analyze_position_size_impact()
        insights = []
        
        size_categories = sorted(analysis.keys())
        win_rates = [analysis[size]['win_rate'] for size in size_categories]
        
        if win_rates[-1] > win_rates[0]:
            insights.append(f"Larger position sizes tend to have higher win rates, with {size_categories[-1]} positions having a {win_rates[-1]:.2%} win rate compared to {win_rates[0]:.2%} for {size_categories[0]} positions.")
        elif win_rates[0] > win_rates[-1]:
            insights.append(f"Smaller position sizes tend to have higher win rates, with {size_categories[0]} positions having a {win_rates[0]:.2%} win rate compared to {win_rates[-1]:.2%} for {size_categories[-1]} positions.")
        
        avg_pnl = [analysis[size]['netPNL']['mean'] for size in size_categories]
        if avg_pnl[-1] > avg_pnl[0]:
            insights.append(f"Larger positions tend to be more profitable, with an average PNL of {avg_pnl[-1]:.2f} for {size_categories[-1]} positions compared to {avg_pnl[0]:.2f} for {size_categories[0]} positions.")
        elif avg_pnl[0] > avg_pnl[-1]:
            insights.append(f"Smaller positions tend to be more profitable, with an average PNL of {avg_pnl[0]:.2f} for {size_categories[0]} positions compared to {avg_pnl[-1]:.2f} for {size_categories[-1]} positions.")
        
        return insights

    def get_pair_direction_insights(self) -> List[str]:
        analysis = self.analyze_pair_direction_bias()
        insights = []
        
        for pair, directions in analysis.items():
            if 'long' in directions and 'short' in directions:
                long_win_rate = directions['long']['win_rate']
                short_win_rate = directions['short']['win_rate']
                
                if abs(long_win_rate - short_win_rate) > 0.1:  # 10% difference threshold
                    better_direction = 'long' if long_win_rate > short_win_rate else 'short'
                    worse_direction = 'short' if better_direction == 'long' else 'long'
                    insights.append(f"For {pair}, {better_direction} trades have a significantly higher win rate ({directions[better_direction]['win_rate']:.2%}) compared to {worse_direction} trades ({directions[worse_direction]['win_rate']:.2%}).")
            elif 'long' in directions:
                insights.append(f"For {pair}, only long trades were found with a win rate of {directions['long']['win_rate']:.2%}.")
            elif 'short' in directions:
                insights.append(f"For {pair}, only short trades were found with a win rate of {directions['short']['win_rate']:.2%}.")
        
        if not insights:
            insights.append("No significant directional bias was found for any currency pair.")
        
        return insights

    def get_risk_reward_insights(self) -> List[str]:
        analysis = self.analyze_risk_reward_patterns()
        insights = []
        
        rr_categories = sorted(analysis.keys(), key=lambda x: float(x.split('-')[0]))
        win_rates = [analysis[rr]['win_rate'] for rr in rr_categories]
        
        if win_rates[-1] > win_rates[0]:
            insights.append(f"Trades with higher risk-reward ratios tend to have better win rates, with {rr_categories[-1]} R:R trades having a {win_rates[-1]:.2%} win rate compared to {win_rates[0]:.2%} for {rr_categories[0]} R:R trades.")
        elif win_rates[0] > win_rates[-1]:
            insights.append(f"Trades with lower risk-reward ratios tend to have better win rates, with {rr_categories[0]} R:R trades having a {win_rates[0]:.2%} win rate compared to {win_rates[-1]:.2%} for {rr_categories[-1]} R:R trades.")
        
        avg_pnl = [analysis[rr]['avg_netPNL'] for rr in rr_categories]
        if avg_pnl[-1] > avg_pnl[0]:
            insights.append(f"Trades with higher risk-reward ratios tend to be more profitable, with an average PNL of {avg_pnl[-1]:.2f} for {rr_categories[-1]} R:R trades compared to {avg_pnl[0]:.2f} for {rr_categories[0]} R:R trades.")
        elif avg_pnl[0] > avg_pnl[-1]:
            insights.append(f"Trades with lower risk-reward ratios tend to be more profitable, with an average PNL of {avg_pnl[0]:.2f} for {rr_categories[0]} R:R trades compared to {avg_pnl[-1]:.2f} for {rr_categories[-1]} R:R trades.")
        
        return insights

    def get_all_insights(self) -> Dict[str, List[str]]:
        return {
            "position_size_insights": self.get_position_size_insights(),
            "pair_direction_insights": self.get_pair_direction_insights(),
            "risk_reward_insights": self.get_risk_reward_insights()
        }

    def get_key_trading_insights(self) -> List[str]:
        insights = []
        
        # Pair Direction Insight
        direction_analysis = self.analyze_pair_direction_bias()
        best_pairs = []
        for pair, directions in direction_analysis.items():
            for direction in ['long', 'short']:
                if direction in directions and directions[direction]['win_rate'] == 1.0:
                    best_pairs.append(f"{pair} {direction}")
        if best_pairs:
            insights.append(f"Pair Direction: {' and '.join(best_pairs[:2])} show 100% win rates.")
        
        # Position Size Insight
        size_analysis = self.analyze_position_size_impact()
        size_categories = sorted(size_analysis.keys())
        best_size = max(size_categories, key=lambda x: size_analysis[x]['win_rate'])
        insights.append(f"Position Size: {best_size} positions have higher win rates ({size_analysis[best_size]['win_rate']:.2%}) and profitability.")
        
        # Risk-Reward Insight
        rr_analysis = self.analyze_risk_reward_patterns()
        rr_categories = sorted(rr_analysis.keys(), key=lambda x: float(x.split('-')[0]))
        best_rr = max(rr_categories, key=lambda x: rr_analysis[x]['win_rate'])
        insights.append(f"Risk-Reward: Higher R:R ratios ({best_rr}) yield better win rates ({rr_analysis[best_rr]['win_rate']:.2%}) and profitability.")
        
        return insights
