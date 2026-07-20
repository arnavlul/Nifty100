import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.analytics import cashflow_kpis

class TestCashflowKPIs(unittest.TestCase):
    def test_free_cash_flow(self):
        self.assertEqual(cashflow_kpis.free_cash_flow(100, -40), 60)
        # Negative allowed
        self.assertEqual(cashflow_kpis.free_cash_flow(50, -100), -50)
        
    def test_cfo_quality_score(self):
        # > 1.0
        val, label = cashflow_kpis.cfo_quality_score(150, 100)
        self.assertEqual(label, "High Quality")
        
        # 0.5 - 1.0
        val, label = cashflow_kpis.cfo_quality_score(75, 100)
        self.assertEqual(label, "Moderate")
        
        # < 0.5
        val, label = cashflow_kpis.cfo_quality_score(40, 100)
        self.assertEqual(label, "Accrual Risk")
        
        # Zero PAT
        val, label = cashflow_kpis.cfo_quality_score(100, 0)
        self.assertIsNone(val)
        
    def test_capex_intensity(self):
        # < 3%
        val, label = cashflow_kpis.capex_intensity(-20, 1000)
        self.assertEqual(label, "Asset Light")
        
        # 3 - 8%
        val, label = cashflow_kpis.capex_intensity(-50, 1000)
        self.assertEqual(label, "Moderate")
        
        # > 8%
        val, label = cashflow_kpis.capex_intensity(-100, 1000)
        self.assertEqual(label, "Capital Intensive")
        
        # Zero sales
        val, label = cashflow_kpis.capex_intensity(-100, 0)
        self.assertIsNone(val)
        
    def test_fcf_conversion(self):
        self.assertEqual(cashflow_kpis.fcf_conversion_rate(50, 100), 50.0)
        self.assertIsNone(cashflow_kpis.fcf_conversion_rate(50, 0))
        
    def test_capital_allocation_patterns(self):
        # (+, -, -) High CFO/PAT -> Shareholder Returns
        self.assertEqual(cashflow_kpis.get_capital_allocation_pattern(100, -50, -50, 1.5), "Shareholder Returns")
        
        # (+, -, -) Normal -> Reinvestor
        self.assertEqual(cashflow_kpis.get_capital_allocation_pattern(100, -50, -50, 0.8), "Reinvestor")
        
        # (+, +, -) -> Liquidating Assets
        self.assertEqual(cashflow_kpis.get_capital_allocation_pattern(100, 50, -100), "Liquidating Assets")
        
        # (-, +, +) -> Distress Signal
        self.assertEqual(cashflow_kpis.get_capital_allocation_pattern(-100, 50, 50), "Distress Signal")
        
        # (-, -, +) -> Growth Funded by Debt
        self.assertEqual(cashflow_kpis.get_capital_allocation_pattern(-50, -50, 100), "Growth Funded by Debt")
        
        # (+, +, +) -> Cash Accumulator
        self.assertEqual(cashflow_kpis.get_capital_allocation_pattern(50, 50, 50), "Cash Accumulator")
        
        # (-, -, -) -> Pre-Revenue
        self.assertEqual(cashflow_kpis.get_capital_allocation_pattern(-50, -50, -50), "Pre-Revenue")
        
        # (+, -, +) -> Mixed
        self.assertEqual(cashflow_kpis.get_capital_allocation_pattern(100, -150, 50), "Mixed")

if __name__ == '__main__':
    unittest.main()
