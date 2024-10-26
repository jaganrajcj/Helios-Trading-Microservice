import pandas as pd
import numpy as np
from typing import List, Dict, Any
from app.utils.helpers import calculate_trade_metrics

class BehaviorAnalyzer:
    def __init__(self, trades: List[Dict[Any, Any]]):
        self.trades_df = calculate_trade_metrics(trades)
    
    def detect_overtrading(self) -> Dict:
        """Detect potential overtrading patterns"""
        trades_per_day = self.trades_df.groupby(self.trades_df['date'].dt.date).size()
        
        return {
            'avg_trades_per_day': trades_per_day.mean(),
            'max_trades_per_day': trades_per_day.max(),
            'days_with_excessive_trading': len(trades_per_day[trades_per_day > trades_per_day.mean() + trades_per_day.std()]),
            'trading_frequency_distribution': trades_per_day.value_counts().to_dict()
        }
    
    def detect_revenge_trading(self) -> Dict:
        """Detect potential revenge trading patterns"""
        self.trades_df['time_to_next_trade'] = self.trades_df['date'].shift(-1) - self.trades_df['date']
        
        quick_trades_after_loss = self.trades_df[
            (self.trades_df['status'] == 'loss') & 
            (self.trades_df['time_to_next_trade'] < pd.Timedelta(minutes=30))
        ]
        
        return {
            'quick_trades_after_losses': len(quick_trades_after_loss),
            'quick_trades_after_losses_success_rate': (quick_trades_after_loss['status'].shift(-1) == 'win').mean(),
            'avg_pnl_after_quick_trade': quick_trades_after_loss['netPNL'].shift(-1).mean()
        }
    
    def analyze_risk_management_consistency(self) -> Dict:
        """Analyze consistency in risk management"""
        return {
            'position_size_consistency': self.trades_df['size'].std() / self.trades_df['size'].mean(),
            'stop_loss_consistency': (
                (self.trades_df['stopLoss'] - self.trades_df['entryPrice']).abs() / 
                self.trades_df['entryPrice']
            ).std(),
            'risk_per_trade_consistency': (
                self.trades_df['netPNL'].abs() / self.trades_df['accountBalance']
            ).std()
        }
    
    def get_behavior_insights(self) -> List[str]:
        insights = []
        
        # Overtrading insights
        overtrading = self.detect_overtrading()
        avg_trades = overtrading['avg_trades_per_day']
        max_trades = overtrading['max_trades_per_day']
        excessive_days = overtrading['days_with_excessive_trading']
        
        insights.append(f"On average, you make {avg_trades:.2f} trades per day, with a maximum of {max_trades} trades in a single day.")
        if excessive_days > 0:
            insights.append(f"There were {excessive_days} days with excessive trading, which might indicate overtrading tendencies.")
        
        # Revenge trading insights
        revenge = self.detect_revenge_trading()
        quick_losses = revenge['quick_trades_after_losses']
        success_rate = revenge['quick_trades_after_losses_success_rate']
        avg_pnl = revenge['avg_pnl_after_quick_trade']
        
        if quick_losses > 0:
            insights.append(f"You made {quick_losses} quick trades after losses, which could be signs of revenge trading.")
            insights.append(f"The success rate of these quick trades is {success_rate:.2%}, with an average PNL of {avg_pnl:.2f}.")
        
        # Risk management consistency insights
        risk = self.analyze_risk_management_consistency()
        position_consistency = risk['position_size_consistency']
        stop_loss_consistency = risk['stop_loss_consistency']
        risk_per_trade = risk['risk_per_trade_consistency']
        
        if position_consistency > 0.5:
            insights.append("Your position sizes vary considerably, which might indicate inconsistent risk management.")
        else:
            insights.append("Your position sizes are relatively consistent, showing good risk management practices.")
        
        if stop_loss_consistency < 0.01:
            insights.append("Your stop loss placements are very consistent, which is a positive risk management practice.")
        elif stop_loss_consistency > 0.05:
            insights.append("Your stop loss placements vary significantly, which could lead to inconsistent risk exposure.")
        
        if risk_per_trade < 0.01:
            insights.append("Your risk per trade is very consistent, indicating disciplined risk management.")
        elif risk_per_trade > 0.05:
            insights.append("Your risk per trade varies considerably, which might lead to inconsistent overall risk exposure.")
        
        return insights
    
    def calculate_loss_recovery_rate(self) -> float:
        """Calculate the average number of trades needed to recover from a loss"""
        loss_streaks = (self.trades_df['status'] != 'win').astype(int).groupby(
            (self.trades_df['status'] == 'win').astype(int).cumsum()
        ).sum()
        return loss_streaks[loss_streaks > 0].mean()

    def calculate_sharpe_ratio(self) -> float:
        """Calculate the Sharpe ratio"""
        returns = self.trades_df['accountChange']
        return (returns.mean() / returns.std()) * np.sqrt(252)  # Assuming 252 trading days in a year

    def determine_risk_level(self) -> str:
        """Determine the risk level based on various factors"""
        sharpe_ratio = self.calculate_sharpe_ratio()
        max_drawdown = (self.trades_df['accountBalance'].cummax() - self.trades_df['accountBalance']).max() / self.trades_df['accountBalance'].iloc[0]
        
        if sharpe_ratio > 1.5 and max_drawdown < 0.1:
            return "Low"
        elif sharpe_ratio > 0.5 and max_drawdown < 0.2:
            return "Moderate"
        else:
            return "High"

    def get_key_insights(self) -> str:
        """Generate a key insight about overall performance"""
        total_trades = len(self.trades_df)
        win_rate = (self.trades_df['status'] == 'win').mean()
        total_pnl = self.trades_df['netPNL'].sum()
        sharpe_ratio = self.calculate_sharpe_ratio()
        risk_level = self.determine_risk_level()
        
        return f"Over {total_trades} trades, you achieved a {win_rate:.2%} win rate with a total PNL of {total_pnl:.2f}. Your trading strategy shows a Sharpe ratio of {sharpe_ratio:.2f}, indicating a {risk_level.lower()} risk level."
