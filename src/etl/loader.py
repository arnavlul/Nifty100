import pandas as pd
import sqlite3
import os
import glob
import time
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.etl.normaliser import normalize_year, normalize_ticker

def load_data():
    conn = sqlite3.connect('data/nifty100.db')
    audit_data = []

    # Load core datasets
    core_files = glob.glob('data/raw/*.xlsx')
    for file_path in core_files:
        start_time = time.time()
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        try:
            df = pd.read_excel(file_path, header=1)
            
            # Normalise columns
            for col in df.columns:
                if col.lower() == 'company_id' or (col.lower() == 'id' and table_name == 'companies'):
                    df[col] = df[col].apply(normalize_ticker)
                if col.lower() == 'year':
                    df[col] = df[col].apply(normalize_year)
                    
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            rows_in = len(df)
            audit_data.append({'table': table_name, 'rows_loaded': rows_in, 'rejections': 0, 'runtime': round(time.time() - start_time, 2)})
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    # Load supporting datasets
    supporting_files = glob.glob('data/supporting/*.xlsx')
    for file_path in supporting_files:
        start_time = time.time()
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        try:
            df = pd.read_excel(file_path, header=0)
            
            # Normalise columns
            for col in df.columns:
                if col.lower() == 'company_id':
                    df[col] = df[col].apply(normalize_ticker)
                if col.lower() == 'year':
                    df[col] = df[col].apply(normalize_year)
                    
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            rows_in = len(df)
            audit_data.append({'table': table_name, 'rows_loaded': rows_in, 'rejections': 0, 'runtime': round(time.time() - start_time, 2)})
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    pd.DataFrame(audit_data).to_csv('output/load_audit.csv', index=False)
    conn.close()
    print("Data loading complete. load_audit.csv generated.")

if __name__ == '__main__':
    load_data()
