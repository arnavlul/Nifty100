import re

def normalize_year(year_str):
    if year_str is None:
        return None
    year_str = str(year_str).strip()
    match = re.search(r'\b(20\d{2})\b', year_str)
    if match:
        return int(match.group(1))
    return None

def normalize_ticker(ticker_str):
    if not ticker_str:
        return None
    return str(ticker_str).strip().upper().replace(' ', '_')
