import pandas as pd
import yaml
import numpy as np

class ScreenerEngine:
    def __init__(self, config_path):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
            
    def apply_preset(self, df, preset_name):
        if preset_name not in self.config['presets']:
            raise ValueError(f"Preset {preset_name} not found in configuration.")
            
        filters = self.config['presets'][preset_name]
        return self.apply_filters(df, filters)
        
    def apply_filters(self, df, filters):
        result = df.copy()
        
        # 15 supported metrics and custom flags
        if 'roe_min' in filters:
            result = result[result['roe'] > filters['roe_min']]
            
        if 'de_max' in filters:
            # Skip companies in Financials sector when applying D/E max
            de_max = filters['de_max']
            # If D/E max is exactly 0, it means Debt-Free. 
            if de_max == 0:
                result = result[(result['de_ratio'] <= 0) | (result['sector'] == 'Financials')]
            else:
                result = result[(result['de_ratio'] < de_max) | (result['sector'] == 'Financials')]
                
        if 'fcf_min' in filters:
            result = result[result['fcf'] > filters['fcf_min']]
            
        if 'revenue_cagr_5yr_min' in filters:
            result = result[result['revenue_cagr_5yr'] > filters['revenue_cagr_5yr_min']]
            
        if 'pat_cagr_5yr_min' in filters:
            result = result[result['pat_cagr_5yr'] > filters['pat_cagr_5yr_min']]
            
        if 'opm_min' in filters:
            result = result[result['opm'] > filters['opm_min']]
            
        if 'pe_max' in filters:
            result = result[result['pe_ratio'] < filters['pe_max']]
            
        if 'pb_max' in filters:
            result = result[result['pb_ratio'] < filters['pb_max']]
            
        if 'dividend_yield_min' in filters:
            result = result[result['dividend_yield'] > filters['dividend_yield_min']]
            
        if 'icr_min' in filters:
            # treat 'Debt Free' label as ICR = infinity
            def check_icr(row):
                if row.get('icr_label') == 'Debt Free':
                    return True
                return pd.notnull(row['icr']) and row['icr'] > filters['icr_min']
            result = result[result.apply(check_icr, axis=1)]
            
        if 'market_cap_min' in filters:
            result = result[result['market_cap'] > filters['market_cap_min']]
            
        if 'net_profit_min' in filters:
            result = result[result['net_profit'] > filters['net_profit_min']]
            
        if 'eps_cagr_5yr_min' in filters:
            result = result[result['eps_cagr_5yr'] > filters['eps_cagr_5yr_min']]
            
        if 'asset_turnover_min' in filters:
            result = result[result['asset_turnover'] > filters['asset_turnover_min']]
            
        if 'sales_min' in filters:
            result = result[result['sales'] > filters['sales_min']]
            
        if 'revenue_cagr_3yr_min' in filters:
            result = result[result['revenue_cagr_3yr'] > filters['revenue_cagr_3yr_min']]
            
        if 'dividend_payout_max' in filters:
            result = result[result['dividend_payout'] < filters['dividend_payout_max']]
            
        if 'de_declining' in filters and filters['de_declining']:
            # Expecting a boolean column 'de_declining'
            result = result[result['de_declining'] == True]
            
        # Return sorted DataFrame with composite_quality_score
        if 'composite_quality_score' in result.columns:
            result = result.sort_values(by='composite_quality_score', ascending=False)
            
        return result
