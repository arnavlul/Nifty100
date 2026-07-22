import sqlite3
import pandas as pd

def compute_peer_percentiles():
    conn = sqlite3.connect('data/nifty100.db')
    
    # Load data
    peer_df = pd.read_sql_query("SELECT * FROM peer_groups", conn)
    ratios_df = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
    
    # Metrics to rank
    metrics = [
        'return_on_equity_pct', 'roce_pct', 'net_profit_margin_pct',
        'debt_to_equity', 'free_cash_flow_cr', 'pat_cagr_5yr', 
        'revenue_cagr_5yr', 'eps_cagr_5yr', 'interest_coverage', 'asset_turnover'
    ]
    
    # Merge peers with ratios
    df = pd.merge(ratios_df, peer_df, on='company_id', how='left')
    
    results = []
    
    # For companies without peer groups
    no_peer = df[df['peer_group_name'].isnull()]['company_id'].unique()
    for company in no_peer:
        print(f"{company}: No peer group assigned")
        
    # Drop rows without peer group
    df = df.dropna(subset=['peer_group_name'])
    
    for metric in metrics:
        if metric not in df.columns:
            continue
            
        for (peer_group, year), group in df.groupby(['peer_group_name', 'year']):
            # Filter out NaNs for ranking
            valid_group = group.dropna(subset=[metric]).copy()
            if len(valid_group) == 0:
                continue
                
            # rank pct
            # method='average' is default, ascending=True means lower values get lower pct.
            # So a high value gets high percentile_rank.
            valid_group['percentile_rank'] = valid_group[metric].rank(pct=True)
            
            if metric == 'debt_to_equity':
                valid_group['percentile_rank'] = 1.0 - valid_group['percentile_rank']
                
            for _, row in valid_group.iterrows():
                results.append({
                    'company_id': row['company_id'],
                    'peer_group_name': peer_group,
                    'metric': metric,
                    'value': row[metric],
                    'percentile_rank': row['percentile_rank'],
                    'year': year
                })
                
    if results:
        result_df = pd.DataFrame(results)
        result_df.to_sql('peer_percentiles', conn, if_exists='replace', index=False)
        print("Populated peer_percentiles table.")
    else:
        print("No valid data to populate peer_percentiles.")
    conn.close()

if __name__ == '__main__':
    compute_peer_percentiles()
