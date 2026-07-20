import unittest
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.analytics import ratios

class TestRatios(unittest.TestCase):
    # Day 08 Tests (Profitability)
    def test_npm_normal(self):
        self.assertAlmostEqual(ratios.net_profit_margin(100, 1000), 10.0)

    def test_npm_zero_sales(self):
        self.assertIsNone(ratios.net_profit_margin(100, 0))

    def test_roe_negative_equity(self):
        self.assertIsNone(ratios.return_on_equity(100, 50, -100))

    def test_opm_mismatch(self):
        with self.assertLogs(level='WARNING') as cm:
            ratios.operating_profit_margin(150, 1000, 20.0)
        self.assertIn("OPM mismatch: computed 15.00 vs source 20.00", cm.output[0])
        
    def test_roce_normal(self):
        self.assertAlmostEqual(ratios.return_on_capital_employed(200, 100, 50, 50), 100.0)

    def test_roce_benchmark(self):
        # Normal absolute benchmark (15.0)
        self.assertTrue(ratios.evaluate_roce_benchmark(16.0, is_financials=False))
        self.assertFalse(ratios.evaluate_roce_benchmark(14.0, is_financials=False))
        # Financials sector-relative benchmark (e.g. 10.0 for banks)
        self.assertTrue(ratios.evaluate_roce_benchmark(11.0, is_financials=True, sector_benchmark=10.0))
        self.assertFalse(ratios.evaluate_roce_benchmark(9.0, is_financials=True, sector_benchmark=10.0))
        
    def test_roa_normal(self):
        self.assertAlmostEqual(ratios.return_on_assets(100, 2000), 5.0)

    def test_roa_zero_assets(self):
        self.assertIsNone(ratios.return_on_assets(100, 0))

    def test_opm_normal(self):
        self.assertAlmostEqual(ratios.operating_profit_margin(150, 1000), 15.0)

    # Day 09 Tests (Leverage & Efficiency)
    def test_de_debt_free(self):
        self.assertEqual(ratios.debt_to_equity(0, 100, 50), 0.0)
        
    def test_icr_zero_interest(self):
        self.assertIsNone(ratios.interest_coverage_ratio(100, 50, 0))
        
    def test_icr_label_debt_free(self):
        self.assertEqual(ratios.get_icr_label(0), 'Debt Free')
        
    def test_high_de_flag(self):
        self.assertTrue(ratios.get_high_leverage_flag(6.0, is_financials=False))
        self.assertFalse(ratios.get_high_leverage_flag(6.0, is_financials=True))
        
    def test_icr_warning_flag(self):
        self.assertTrue(ratios.get_icr_warning_flag(1.0))
        self.assertFalse(ratios.get_icr_warning_flag(2.0))
        
    def test_net_debt_normal(self):
        self.assertEqual(ratios.net_debt(500, 200), 300)
        
    def test_asset_turnover_normal(self):
        self.assertEqual(ratios.asset_turnover(1000, 500), 2.0)
        
    def test_asset_turnover_zero_assets(self):
        self.assertIsNone(ratios.asset_turnover(1000, 0))

if __name__ == '__main__':
    unittest.main()
