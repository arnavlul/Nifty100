def calculate_cagr(start_val, end_val, years, available_years=None):
    """
    Computes Compound Annual Growth Rate (CAGR) and returns a tuple (value, flag).
    Edge cases handled:
    - Positive+Positive: compute normally (Flag: NORMAL)
    - Positive+Negative: return None with flag DECLINE_TO_LOSS
    - Negative+Positive: return None with flag TURNAROUND
    - Negative+Negative: return None with flag BOTH_NEGATIVE
    - Zero base: return None with flag ZERO_BASE
    - Less than n years of data: return None with flag INSUFFICIENT
    """
    # 1. Check for insufficient data
    if available_years is not None and available_years < years:
        return None, "INSUFFICIENT"
        
    if years <= 0:
        return None, "INSUFFICIENT"
        
    # 2. Check for zero base
    if start_val == 0:
        return None, "ZERO_BASE"
        
    # 3. Handle Negative Start Cases
    if start_val < 0:
        if end_val > 0:
            return None, "TURNAROUND"
        else:
            return None, "BOTH_NEGATIVE"
            
    # 4. Handle Positive Start Cases
    if start_val > 0:
        if end_val < 0:
            return None, "DECLINE_TO_LOSS"
        
        # 5. Normal Positive+Positive Case
        # Formula: ((end/start)^(1/n) - 1) * 100
        cagr = ((end_val / start_val) ** (1 / years) - 1) * 100
        return cagr, "NORMAL"
        
    return None, "UNKNOWN"

def compute_cagr_windows(prefix, current_val, val_3yr_ago=None, val_5yr_ago=None, val_10yr_ago=None):
    """
    Computes 3-year, 5-year, and 10-year CAGR windows for a given metric prefix.
    Returns a dictionary suitable for directly updating a database row with separate flag columns.
    """
    results = {}
    
    # 3-Year Window
    if val_3yr_ago is not None:
        val, flag = calculate_cagr(val_3yr_ago, current_val, 3)
        results[f"{prefix}_cagr_3yr"] = val
        results[f"{prefix}_cagr_3yr_flag"] = flag
        
    # 5-Year Window
    if val_5yr_ago is not None:
        val, flag = calculate_cagr(val_5yr_ago, current_val, 5)
        results[f"{prefix}_cagr_5yr"] = val
        results[f"{prefix}_cagr_5yr_flag"] = flag
        
    # 10-Year Window
    if val_10yr_ago is not None:
        val, flag = calculate_cagr(val_10yr_ago, current_val, 10)
        results[f"{prefix}_cagr_10yr"] = val
        results[f"{prefix}_cagr_10yr_flag"] = flag
        
    return results

def compute_revenue_cagrs(current_rev, rev_3yr_ago=None, rev_5yr_ago=None, rev_10yr_ago=None):
    return compute_cagr_windows("revenue", current_rev, rev_3yr_ago, rev_5yr_ago, rev_10yr_ago)

def compute_pat_cagrs(current_pat, pat_3yr_ago=None, pat_5yr_ago=None, pat_10yr_ago=None):
    return compute_cagr_windows("pat", current_pat, pat_3yr_ago, pat_5yr_ago, pat_10yr_ago)

def compute_eps_cagrs(current_eps, eps_3yr_ago=None, eps_5yr_ago=None, eps_10yr_ago=None):
    return compute_cagr_windows("eps", current_eps, eps_3yr_ago, eps_5yr_ago, eps_10yr_ago)
