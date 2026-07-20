import logging

def net_profit_margin(net_profit, sales):
    if sales == 0:
        return None
    return (net_profit / sales) * 100

def operating_profit_margin(operating_profit, sales, opm_percentage=None):
    if sales == 0:
        return None
    computed = (operating_profit / sales) * 100
    if opm_percentage is not None:
        if abs(computed - opm_percentage) > 1.0:
            logging.warning(f"OPM mismatch: computed {computed:.2f} vs source {opm_percentage:.2f}")
    return computed

def return_on_equity(net_profit, equity_capital, reserves):
    denominator = equity_capital + reserves
    if denominator <= 0:
        return None
    return (net_profit / denominator) * 100

def return_on_capital_employed(ebit, equity, reserves, borrowings):
    denominator = equity + reserves + borrowings
    if denominator <= 0:
        return None
    return (ebit / denominator) * 100

def evaluate_roce_benchmark(roce, is_financials=False, sector_benchmark=None, absolute_benchmark=15.0):
    if roce is None:
        return None
    if is_financials and sector_benchmark is not None:
        return roce >= sector_benchmark
    return roce >= absolute_benchmark

def return_on_assets(net_profit, total_assets):
    if total_assets == 0:
        return None
    return (net_profit / total_assets) * 100

def debt_to_equity(borrowings, equity_capital, reserves):
    if borrowings == 0:
        return 0.0
    denominator = equity_capital + reserves
    if denominator <= 0:
        return None
    return borrowings / denominator

def get_high_leverage_flag(de_ratio, is_financials=False):
    if de_ratio is None:
        return False
    if de_ratio > 5 and not is_financials:
        return True
    return False

def interest_coverage_ratio(operating_profit, other_income, interest):
    if interest == 0:
        return None
    return (operating_profit + other_income) / interest

def get_icr_label(interest):
    if interest == 0:
        return 'Debt Free'
    return None

def get_icr_warning_flag(icr):
    if icr is None:
        return False
    return icr < 1.5

def net_debt(borrowings, investments):
    return borrowings - investments

def asset_turnover(sales, total_assets):
    if total_assets == 0:
        return None
    return sales / total_assets
