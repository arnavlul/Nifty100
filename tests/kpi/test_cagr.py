import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.analytics import cagr

class TestCAGR(unittest.TestCase):
    def test_cagr_normal(self):
        # 100 to 133.1 over 3 years is exactly 10% CAGR
        val, flag = cagr.calculate_cagr(100, 133.1, 3, available_years=3)
        self.assertAlmostEqual(val, 10.0, places=1)
        self.assertEqual(flag, "NORMAL")
        
    def test_cagr_turnaround(self):
        # Negative to Positive
        val, flag = cagr.calculate_cagr(-50, 100, 3)
        self.assertIsNone(val)
        self.assertEqual(flag, "TURNAROUND")
        
    def test_cagr_decline_to_loss(self):
        # Positive to Negative
        val, flag = cagr.calculate_cagr(100, -20, 5)
        self.assertIsNone(val)
        self.assertEqual(flag, "DECLINE_TO_LOSS")
        
    def test_cagr_both_negative(self):
        # Negative to Negative
        val, flag = cagr.calculate_cagr(-50, -10, 3)
        self.assertIsNone(val)
        self.assertEqual(flag, "BOTH_NEGATIVE")
        
    def test_cagr_zero_base(self):
        # Zero to Positive
        val, flag = cagr.calculate_cagr(0, 100, 5)
        self.assertIsNone(val)
        self.assertEqual(flag, "ZERO_BASE")
        
    def test_cagr_insufficient_data(self):
        # Only 2 years of data available, but requested 3 year CAGR
        val, flag = cagr.calculate_cagr(100, 150, 3, available_years=2)
        self.assertIsNone(val)
        self.assertEqual(flag, "INSUFFICIENT")
        
    def test_cagr_zero_years(self):
        # Invalid years
        val, flag = cagr.calculate_cagr(100, 150, 0)
        self.assertIsNone(val)
        self.assertEqual(flag, "INSUFFICIENT")

    def test_cagr_large_numbers(self):
        # Testing billion-dollar figures
        val, flag = cagr.calculate_cagr(1_000_000_000, 2_000_000_000, 5)
        self.assertAlmostEqual(val, 14.87, places=2)
        self.assertEqual(flag, "NORMAL")
        
    def test_cagr_fractional_values(self):
        # EPS values are often fractional
        val, flag = cagr.calculate_cagr(1.25, 2.50, 4)
        self.assertAlmostEqual(val, 18.92, places=2)
        self.assertEqual(flag, "NORMAL")
        
    def test_cagr_wrappers(self):
        # Testing the new specific wrapper functions that return dictionaries
        rev_dict = cagr.compute_revenue_cagrs(current_rev=121, rev_3yr_ago=None, rev_5yr_ago=None, rev_10yr_ago=None)
        # Should be empty if no past values provided
        self.assertEqual(rev_dict, {})
        
        rev_dict = cagr.compute_revenue_cagrs(current_rev=133.1, rev_3yr_ago=100)
        self.assertAlmostEqual(rev_dict["revenue_cagr_3yr"], 10.0, places=1)
        self.assertEqual(rev_dict["revenue_cagr_3yr_flag"], "NORMAL")
        self.assertNotIn("revenue_cagr_5yr", rev_dict)
        
        pat_dict = cagr.compute_pat_cagrs(current_pat=-10, pat_3yr_ago=50)
        self.assertIsNone(pat_dict["pat_cagr_3yr"])
        self.assertEqual(pat_dict["pat_cagr_3yr_flag"], "DECLINE_TO_LOSS")
        
        eps_dict = cagr.compute_eps_cagrs(current_eps=5, eps_3yr_ago=0, eps_5yr_ago=10)
        self.assertIsNone(eps_dict["eps_cagr_3yr"])
        self.assertEqual(eps_dict["eps_cagr_3yr_flag"], "ZERO_BASE")
        # 5 year EPS: 10 down to 5 -> Negative growth but normal calc
        self.assertAlmostEqual(eps_dict["eps_cagr_5yr"], -12.94, places=1)
        self.assertEqual(eps_dict["eps_cagr_5yr_flag"], "NORMAL")

if __name__ == '__main__':
    unittest.main()
