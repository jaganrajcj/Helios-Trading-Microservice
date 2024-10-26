import unittest
import json
import requests
from datetime import datetime

BASE_URL = 'http://localhost:5000/api/v1/analyze'

class TestTradeAnalysisAPI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        with open('tests/test_data/sample_trades.json', 'r') as f:
            cls.sample_trades = json.load(f)
        
        # Convert date strings to datetime objects for internal use
        for trade in cls.sample_trades:
            trade['date'] = datetime.fromisoformat(trade['date'].rstrip('Z'))
        
        # Add missing required fields
        for trade in cls.sample_trades:
            trade['accountId'] = 1  # Assuming all trades belong to the same account

    def get_json_serializable_trades(self):
        # Create a copy of sample_trades and convert datetime back to ISO format string
        serializable_trades = []
        for trade in self.sample_trades:
            trade_copy = trade.copy()
            trade_copy['date'] = trade_copy['date'].isoformat()
            serializable_trades.append(trade_copy)
        return serializable_trades

    def test_pattern_analysis(self):
        response = requests.post(f'{BASE_URL}/patterns', json=self.get_json_serializable_trades())
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('position_size_impact', data)
        self.assertIn('direction_bias', data)
        self.assertIn('risk_reward_patterns', data)

    def test_behavior_analysis(self):
        response = requests.post(f'{BASE_URL}/behavior', json=self.get_json_serializable_trades())
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('overtrading', data)
        self.assertIn('revenge_trading', data)
        self.assertIn('risk_management_consistency', data)

    def test_invalid_data(self):
        invalid_data = [{"invalid": "data"}]
        response = requests.post(f'{BASE_URL}/patterns', json=invalid_data)
        self.assertEqual(response.status_code, 400)

        response = requests.post(f'{BASE_URL}/behavior', json=invalid_data)
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()

# tests/test_data/sample_trades.json
[
    {
        "pair": "EUR/AUD",
        "direction": "short",
        "status": "loss",
        "strategy": "none",
        "date": "2024-01-30T14:15:00.000Z",
        "accountBalance": 1354.5,
        "entryPrice": 1.6234,
        "size": 0.15,
        "stopLoss": 1.627,
        "target": 1.618,
        "exitPrice": 1.6265,
        "netPNL": -46.5,
        "accountChange": -3.43
    },
    {
        "pair": "AUD/USD",
        "direction": "short",
        "status": "loss",
        "strategy": "none",
        "date": "2023-12-30T13:30:00.000Z",
        "accountBalance": 1076.0,
        "entryPrice": 0.6789,
        "size": 0.3,
        "stopLoss": 0.681,
        "target": 0.675,
        "exitPrice": 0.6805,
        "netPNL": -48.0,
        "accountChange": -4.46
    },
    {
        "pair": "USD/JPY",
        "direction": "long",
        "status": "win",
        "strategy": "none",
        "date": "2023-12-27T08:15:00.000Z",
        "accountBalance": 1001.0,
        "entryPrice": 131.45,
        "size": 0.15,
        "stopLoss": 131.2,
        "target": 132.0,
        "exitPrice": 131.95,
        "netPNL": 75.0,
        "accountChange": 7.49
    }
]
