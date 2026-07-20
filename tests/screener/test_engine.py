import unittest
import pandas as pd
import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.screener.engine import ScreenerEngine

class TestScreenerEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ScreenerEngine('config/screener_config.yaml')
        self.mock_data = pd.DataFrame({
            'company': ['Company A', 'Company B (Fin)', 'Company C (Value)', 'Company D (Growth)', 'Company E (Div)', 'Company F (DebtFree)', 'Company G (Turnaround)'],
            'sector': ['IT', 'Financials', 'Manufacturing', 'Tech', 'Energy', 'FMCG', 'Telecom'],
            'roe': [20.0, 10.0, 12.0, 18.0, 16.0, 14.0, 8.0],
            'de_ratio': [0.5, 5.5, 1.5, 1.8, 0.8, 0.0, 3.0],
            'fcf': [100.0, -50.0, 20.0, 200.0, 50.0, 500.0, 10.0],
            'revenue_cagr_5yr': [12.0, 8.0, 5.0, 18.0, 11.0, 8.0, 2.0],
            'pat_cagr_5yr': [15.0, 6.0, 4.0, 25.0, 8.0, 10.0, -5.0],
            'pe_ratio': [25.0, 15.0, 12.0, 35.0, 18.0, 40.0, 10.0],
            'pb_ratio': [5.0, 1.5, 2.0, 8.0, 2.5, 6.0, 1.2],
            'dividend_yield': [0.5, 1.5, 2.5, 0.0, 3.5, 0.0, 0.0],
            'dividend_payout': [20.0, 30.0, 50.0, 0.0, 70.0, 0.0, 0.0],
            'sales': [1000.0, 2000.0, 500.0, 1500.0, 800.0, 6000.0, 300.0],
            'revenue_cagr_3yr': [15.0, 10.0, 4.0, 20.0, 12.0, 10.0, 15.0],
            'de_declining': [False, False, False, False, False, False, True],
            'icr': [10.0, 2.0, 5.0, 20.0, 8.0, np.nan, 1.5],
            'icr_label': [None, None, None, None, None, 'Debt Free', None],
            'composite_quality_score': [85, 45, 60, 80, 75, 90, 55]
        })

    def test_quality_compounder(self):
        # ROE > 15%, D/E < 1.0, FCF > 0, Revenue CAGR 5yr > 10%
        # Passes: Company A, Company E
        result = self.engine.apply_preset(self.mock_data, 'Quality Compounder')
        self.assertEqual(len(result), 2)
        self.assertIn('Company A', result['company'].values)
        self.assertIn('Company E (Div)', result['company'].values)

    def test_value_pick(self):
        # P/E < 20, P/B < 3.0, D/E < 2.0, Dividend Yield > 1%
        # Passes: Company B (Fin) [exempt from DE], Company C, Company E
        result = self.engine.apply_preset(self.mock_data, 'Value Pick')
        self.assertEqual(len(result), 3)
        self.assertIn('Company C (Value)', result['company'].values)

    def test_growth_accelerator(self):
        # PAT CAGR 5yr > 20%, Revenue CAGR 5yr > 15%, D/E < 2.0
        # Passes: Company D
        result = self.engine.apply_preset(self.mock_data, 'Growth Accelerator')
        self.assertEqual(len(result), 1)
        self.assertIn('Company D (Growth)', result['company'].values)

    def test_dividend_champion(self):
        # Dividend Yield > 2%, Dividend Payout < 80%, FCF > 0
        # Passes: Company C, Company E
        result = self.engine.apply_preset(self.mock_data, 'Dividend Champion')
        self.assertEqual(len(result), 2)
        self.assertIn('Company C (Value)', result['company'].values)
        self.assertIn('Company E (Div)', result['company'].values)

    def test_debt_free_blue_chip(self):
        # D/E = 0, ROE > 12%, Revenue > 5000 Crore
        # Passes: Company F
        result = self.engine.apply_preset(self.mock_data, 'Debt-Free Blue Chip')
        self.assertEqual(len(result), 1)
        self.assertIn('Company F (DebtFree)', result['company'].values)

    def test_turnaround_watch(self):
        # Revenue CAGR 3yr > 10%, FCF positive in latest year, D/E declining year-over-year
        # Passes: Company G
        result = self.engine.apply_preset(self.mock_data, 'Turnaround Watch')
        self.assertEqual(len(result), 1)
        self.assertIn('Company G (Turnaround)', result['company'].values)

    def test_de_financials_exemption(self):
        # D/E < 1.0, Financials are exempted
        result = self.engine.apply_filters(self.mock_data, {'de_max': 1.0})
        # Exempts: Company B (Financials) with D/E 5.5
        # Passes: Company A (0.5), Company E (0.8), Company F (0.0), and Company B (exempt)
        self.assertEqual(len(result), 4)
        self.assertIn('Company B (Fin)', result['company'].values)

    def test_icr_debt_free_exemption(self):
        # icr_min: 5.0
        # Company F has icr=NaN, icr_label='Debt Free' -> passes
        # Passes: Company A (10.0), Company D (20.0), Company E (8.0), Company F (Debt Free)
        # Note: Company C (5.0) fails because it is > 5.0 (not >=). Let's check engine logic: `row['icr'] > filters['icr_min']`.
        result = self.engine.apply_filters(self.mock_data, {'icr_min': 5.0})
        self.assertEqual(len(result), 4)
        self.assertIn('Company F (DebtFree)', result['company'].values)
        self.assertNotIn('Company C (Value)', result['company'].values)

    def test_composite_score_sort(self):
        result = self.engine.apply_preset(self.mock_data, 'Quality Compounder')
        # Company A (85), Company E (75)
        self.assertEqual(result.iloc[0]['company'], 'Company A')
        self.assertEqual(result.iloc[1]['company'], 'Company E (Div)')

if __name__ == '__main__':
    unittest.main()
