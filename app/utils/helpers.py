from typing import List, Dict
import pandas as pd

def calculate_trade_metrics(trades: List[Dict]) -> pd.DataFrame:
    """Convert trades list to DataFrame and calculate basic metrics"""
    df = pd.DataFrame(trades)
    df['date'] = pd.to_datetime(df['date'])
    df['risk'] = abs(df['entryPrice'] - df['stopLoss'])
    df['reward'] = abs(df['target'] - df['entryPrice'])
    df['rr_ratio'] = df['reward'] / df['risk']
    return df.sort_values('date')