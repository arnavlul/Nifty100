import sqlite3
import pandas as pd
import numpy as np

def winsorise_and_scale(series):
    if len(series.dropna()) == 0:
        return series
    p10 = series.quantile(0.10)
    p90 = series.quantile(0.90)
    
    if p90 == p10:
        # Avoid division by zero
        return series.apply(lambda x: 50.0 if pd.notnull(x) else np.nan)
        
    clipped = series.clip(lower=p10, upper=p90)
    scaled = (clipped - p10) / (p90 - p10) * 100
    return scaled

def compute_de_score(de):
    if pd.isnull(de):
        return np.nan
    if de <= 0: return 100.0
    if de <= 0.5: return 85.0
    if de <= 1.0: return 70.0
    if de <= 2.0: return 50.0
    if de > 5.0: return 0.0
    # Linear interpolation for values between the explicit breakpoints
    if de > 2.0 and de <= 5.0:
        return 50.0 - ((de - 2.0) / 3.0) * 50.0
    return 0.0

def compute_icr_score(icr, label):
    if label == 'Debt Free':
        return 100.0
    if pd.isnull(icr):
        return np.nan
    if icr >= 10: return 100.0
    if icr >= 5: return 75.0
    if icr >= 3: return 50.0
    if icr < 1.5: return 0.0
    # Interpolation
    if icr >= 5 and icr < 10:
        return 75.0 + ((icr - 5.0) / 5.0) * 25.0
    if icr >= 3 and icr < 5:
        return 50.0 + ((icr - 3.0) / 2.0) * 25.0
    if icr >= 1.5 and icr < 3:
        return 0.0 + ((icr - 1.5) / 1.5) * 50.0
    return 0.0

def compute_composite_scores():
    conn = sqlite3.connect('data/nifty100.db')
    
    ratios = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
    sectors = pd.read_sql_query("SELECT * FROM sectors", conn)
    
    df = pd.merge(ratios, sectors[['company_id', 'broad_sector']], on='company_id', how='left')
    
    # We will compute the score for each year, or just the latest year? 
    # Usually composite score is computed across all available years.
    
    df['composite_quality_score'] = np.nan
    
    # Define metric mapping to weight
    metrics_p10p90 = [
        'return_on_equity_pct', 'roce_pct', 'net_profit_margin_pct',
        'fcf_cagr_5yr', 'cfo_pat_ratio', 'revenue_cagr_5yr', 'pat_cagr_5yr'
    ]
    
    # Iterate over sector and year to normalise
    for (sector, year), group in df.groupby(['broad_sector', 'year']):
        idx = group.index
        scores = pd.DataFrame(index=idx)
        
        # Profitability (35%)
        scores['roe_score'] = winsorise_and_scale(group['return_on_equity_pct']) * 0.15
        scores['roce_score'] = winsorise_and_scale(group['roce_pct']) * 0.10
        scores['npm_score'] = winsorise_and_scale(group['net_profit_margin_pct']) * 0.10
        
        # Cash Quality (30%)
        scores['fcf_cagr_score'] = winsorise_and_scale(group['fcf_cagr_5yr']) * 0.15
        scores['cfo_pat_score'] = winsorise_and_scale(group['cfo_pat_ratio']) * 0.10
        fcf_flag = group.get('fcf_positive_flag', group.get('free_cash_flow_cr', 0) > 0)
        scores['fcf_flag_score'] = np.where(fcf_flag == True, 100.0, 0.0) * 0.05
        
        # Growth (20%)
        scores['rev_cagr_score'] = winsorise_and_scale(group['revenue_cagr_5yr']) * 0.10
        scores['pat_cagr_score'] = winsorise_and_scale(group['pat_cagr_5yr']) * 0.10
        
        # Leverage (15%)
        scores['de_score'] = group['debt_to_equity'].apply(compute_de_score) * 0.10
        
        # ICR requires icr_label which we don't have stored, but we can assume 'Debt Free' if debt_to_equity == 0
        icr_labels = np.where(group['debt_to_equity'] == 0, 'Debt Free', None)
        scores['icr_score'] = [compute_icr_score(row['interest_coverage'], lbl) * 0.05 for (_, row), lbl in zip(group.iterrows(), icr_labels)]
        
        # Sum ignoring NAs, but if all are NA, keep NA
        total_score = scores.sum(axis=1, min_count=1)
        
        # However, if some metrics are missing, the sum will be out of less than 100.
        # So we should scale it back up by the sum of weights of non-missing metrics.
        weights_sum = scores.notnull() * [15, 10, 10, 15, 10, 5, 10, 10, 10, 5]
        valid_weights = weights_sum.sum(axis=1)
        
        final_scaled_score = (total_score / valid_weights) * 100
        
        df.loc[idx, 'composite_quality_score'] = final_scaled_score
        
    df.drop(columns=['broad_sector'], inplace=True)
    df.to_sql('financial_ratios', conn, if_exists='replace', index=False)
    conn.close()
    print("Composite scores computed and saved.")

if __name__ == '__main__':
    compute_composite_scores()
