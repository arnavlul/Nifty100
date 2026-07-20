import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.etl.normaliser import normalize_year, normalize_ticker

class TestNormaliser(unittest.TestCase):
    def test_normalize_year_normal(self):
        self.assertEqual(normalize_year('Mar 2022'), 2022)
        
    def test_normalize_year_none(self):
        self.assertIsNone(normalize_year(None))
        self.assertIsNone(normalize_year('Unknown'))
        
    def test_normalize_ticker_normal(self):
        self.assertEqual(normalize_ticker(' reliance '), 'RELIANCE')
        self.assertEqual(normalize_ticker('tata motors'), 'TATA_MOTORS')
        
    def test_normalize_ticker_none(self):
        self.assertIsNone(normalize_ticker(''))
        self.assertIsNone(normalize_ticker(None))

if __name__ == '__main__':
    unittest.main()
