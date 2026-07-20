def free_cash_flow(operating_activity, investing_activity):
    """
    Computes Free Cash Flow. Negative values are allowed.
    FCF = CFO + CFI (since investing activity is usually negative outflow)
    """
    return operating_activity + investing_activity

def cfo_quality_score(cfo_5yr_avg, pat_5yr_avg):
    """
    Computes CFO Quality Score based on 5-year averages.
    >1.0 = High Quality, 0.5-1.0 = Moderate, <0.5 = Accrual Risk
    Returns a tuple (score_value, label).
    """
    if pat_5yr_avg == 0:
        return None, None
        
    ratio = cfo_5yr_avg / pat_5yr_avg
    
    if ratio > 1.0:
        label = "High Quality"
    elif ratio >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"
        
    return ratio, label

def capex_intensity(investing_activity, sales):
    """
    Computes CapEx Intensity: abs(investing_activity) / sales x 100
    <3% = Asset Light, 3-8% = Moderate, >8% = Capital Intensive
    Returns a tuple (intensity_value, label).
    """
    if sales == 0:
        return None, None
        
    intensity = (abs(investing_activity) / sales) * 100
    
    if intensity < 3.0:
        label = "Asset Light"
    elif intensity <= 8.0:
        label = "Moderate"
    else:
        label = "Capital Intensive"
        
    return intensity, label

def fcf_conversion_rate(fcf, operating_profit):
    """
    Computes FCF Conversion Rate: FCF / operating_profit x 100
    """
    if operating_profit == 0:
        return None
    return (fcf / operating_profit) * 100

def get_capital_allocation_pattern(cfo, cfi, cff, cfo_pat_ratio=0.0):
    """
    8-pattern classifier based on signs of (CFO, CFI, CFF).
    + means >= 0, - means < 0.
    """
    cfo_sign = '+' if cfo >= 0 else '-'
    cfi_sign = '+' if cfi >= 0 else '-'
    cff_sign = '+' if cff >= 0 else '-'
    
    pattern = (cfo_sign, cfi_sign, cff_sign)
    
    if pattern == ('+', '-', '-'):
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1.0:
            return "Shareholder Returns"
        else:
            return "Reinvestor"
            
    elif pattern == ('+', '+', '-'):
        return "Liquidating Assets"
    elif pattern == ('-', '+', '+'):
        return "Distress Signal"
    elif pattern == ('-', '-', '+'):
        return "Growth Funded by Debt"
    elif pattern == ('+', '+', '+'):
        return "Cash Accumulator"
    elif pattern == ('-', '-', '-'):
        return "Pre-Revenue"
    elif pattern == ('+', '-', '+'):
        return "Mixed"
    
    return "Unknown"
