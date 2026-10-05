import unittest
import numpy as np
import torch
from complete_x_engine import CompleteMicrostructureAndQuantMath
from gpu_ml_engine import MarketTransformerModel
from state_persistence import SystemStateManager

class TestCapitalAIXEngine(unittest.TestCase):

    def test_math_indicators(self):
        nlvr = CompleteMicrostructureAndQuantMath.calculate_nlvr(100.0, 105.0, 95.0, 104.0)
        self.assertGreaterEqual(nlvr, 0.0)
        self.assertLessEqual(nlvr, 1.0)

    def test_bayesian_kelly(self):
        size = CompleteMicrostructureAndQuantMath.bayesian_kelly_position_size(0.6, 1.5, 50.0)
        self.assertGreater(size, 0.0)

    def test_gpu_transformer_forward(self):
        model = MarketTransformerModel(input_dim=10)
        dummy_input = torch.randn(2, 20, 10)
        output = model(dummy_input)
        self.assertEqual(output.shape, (2, 3))

    def test_database_persistence(self):
        db = SystemStateManager(db_path=":memory:")
        db.log_trade("DEAL_999", "NVDA", "BUY", 0.01, 120.5)
        trades = db.get_open_trades()
        self.assertEqual(len(trades), 1)

if __name__ == '__main__':
    unittest.main()
