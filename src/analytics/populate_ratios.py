import sqlite3
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.analytics.ratios import return_on_capital_employed
from src.analytics.cagr import calculate_cagr

def populate_ratios():
    conn = sqlite3.connect('data/nifty100.db')
    
    pl_df = pd.read_sql_query("SELECT * FROM profitandloss", conn)
    bs_df = pd.read_sql_query("SELECT * FROM balancesheet", conn)
    cf_df = pd.read_sql_query("SELECT * FROM cashflow", conn)
    ratios_df = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
    
    # Identify original ratio columns
    ratio_cols = [c for c in ratios_df.columns if c != 'id']
    
    pl_df = pl_df.drop(columns=['id'], errors='ignore')
    bs_df = bs_df.drop(columns=['id'], errors='ignore')
    cf_df = cf_df.drop(columns=['id'], errors='ignore')
    ratios_df = ratios_df.drop(columns=['id'], errors='ignore')
    
    # Merge all
    df = pd.merge(pl_df, bs_df, on=['company_id', 'year'], how='outer')
    df = pd.merge(df, cf_df, on=['company_id', 'year'], how='outer')
    df = pd.merge(df, ratios_df, on=['company_id', 'year'], how='outer')
    
    # Safely convert year to int for sorting
    df['year_int'] = df['year'].astype(str).str.extract(r'(\d{4})').astype(float)
    
    df = df.sort_values(['company_id', 'year_int'])
    
    # Compute ROCE
    df['roce_pct'] = np.nan
    for idx, row in df.iterrows():
        ebit = None
        if pd.notnull(row.get('operating_profit')) and pd.notnull(row.get('depreciation')):
            ebit = row['operating_profit'] - row['depreciation']
        
        if ebit is not None and pd.notnull(row.get('equity_capital')) and pd.notnull(row.get('reserves')) and pd.notnull(row.get('borrowings')):
            val = return_on_capital_employed(ebit, row['equity_capital'], row['reserves'], row['borrowings'])
            if val is not None:
                df.at[idx, 'roce_pct'] = val
                
    # Compute CAGRs
    def compute_cagr(df, metric_col, cagr_col, years):
        df[cagr_col] = np.nan
        for company, group in df.groupby('company_id'):
            group = group.sort_values('year_int')
            for idx, row in group.iterrows():
                current_year = row['year_int']
                current_val = row.get(metric_col)
                
                past_row = group[group['year_int'] == current_year - years]
                if not past_row.empty and pd.notnull(current_val) and pd.notnull(past_row.iloc[0].get(metric_col)):
                    past_val = past_row.iloc[0][metric_col]
                    cagr_val, flag = calculate_cagr(past_val, current_val, years)
                    if cagr_val is not None:
                        df.at[idx, cagr_col] = cagr_val

    compute_cagr(df, 'sales', 'revenue_cagr_5yr', 5)
    compute_cagr(df, 'net_profit', 'pat_cagr_5yr', 5)
    compute_cagr(df, 'eps', 'eps_cagr_5yr', 5)
    compute_cagr(df, 'free_cash_flow_cr', 'fcf_cagr_5yr', 5)
    
    # Compute CFO/PAT ratio (5-year avg)
    df['cfo_pat_ratio'] = np.nan
    for company, group in df.groupby('company_id'):
        group = group.sort_values('year_int')
        for idx, row in group.iterrows():
            current_year = row['year_int']
            past_5 = group[(group['year_int'] <= current_year) & (group['year_int'] > current_year - 5)]
            if len(past_5) >= 1:
                avg_cfo = past_5['operating_activity'].mean()
                avg_pat = past_5['net_profit'].mean()
                if avg_pat and avg_pat != 0:
                    df.at[idx, 'cfo_pat_ratio'] = avg_cfo / avg_pat

    # Ensure free cash flow exists
    if 'free_cash_flow_cr' not in df.columns:
        df['free_cash_flow_cr'] = df['operating_activity'] + df['investing_activity']
        
    df['fcf_positive_flag'] = np.where(df['free_cash_flow_cr'] > 0, True, False)
    
    # Keep only the original ratio columns plus the newly computed ones
    new_cols = ['roce_pct', 'revenue_cagr_5yr', 'pat_cagr_5yr', 'eps_cagr_5yr', 'fcf_cagr_5yr', 'cfo_pat_ratio', 'fcf_positive_flag']
    final_cols = list(set(ratio_cols + new_cols))
    
    final_df = df[final_cols].copy()
    
    # Drop rows where company_id is null
    final_df = final_df.dropna(subset=['company_id', 'year'])
    
    final_df.to_sql('financial_ratios', conn, if_exists='replace', index=False)
    conn.close()
    print("Successfully populated missing KPIs in financial_ratios table.")

if __name__ == '__main__':
    populate_ratios()
