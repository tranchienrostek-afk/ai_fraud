import pandas as pd
import glob
import os

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'

def analyze_sensitive_timing():
    # 1. Load NDBH (Insured Person) Data - only need user_id and contract_start_date
    ndbh_files = glob.glob(os.path.join(processed_dir, 'processed_DataNDBH_*.csv'))
    ndbh_list = []
    for f in ndbh_files:
        df = pd.read_csv(f, usecols=['user_id', 'contract_start_date', 'contract_level'])
        ndbh_list.append(df)
    df_ndbh = pd.concat(ndbh_list).drop_duplicates(subset=['user_id'])
    df_ndbh['contract_start_date'] = pd.to_datetime(df_ndbh['contract_start_date'], errors='coerce')

    # 2. Load Claims Data
    claim_files = glob.glob(os.path.join(processed_dir, 'processed_DataHoSoBoiThuong_*.csv'))
    claim_list = []
    for f in claim_files:
        df = pd.read_csv(f, usecols=['claim_id', 'user_id', 'claim_date', 'claim_amount_approved', 'visit_date', 'icd_name_primary'])
        claim_list.append(df)
    df_claims = pd.concat(claim_list)
    df_claims['claim_date'] = pd.to_datetime(df_claims['claim_date'], errors='coerce')

    # 3. Join
    df_merged = df_claims.merge(df_ndbh, on='user_id', how='left')
    
    # 4. Filter 1: Large claim (> 50M) within 30 days of contract start
    df_merged['days_since_start'] = (df_merged['claim_date'] - df_merged['contract_start_date']).dt.days
    
    large_claim_threshold = 50000000
    waiting_period_days = 30
    
    suspicious_timing = df_merged[
        (df_merged['claim_amount_approved'] > large_claim_threshold) & 
        (df_merged['days_since_start'] >= 0) & 
        (df_merged['days_since_start'] <= waiting_period_days)
    ]
    
    print(f"Total Sensitive Timing Cases (Claim > 50M within 30 days): {len(suspicious_timing)}")
    
    # 5. Filter 2: Policy Upgrades (Year 1 major injuries)
    # We define year 1 as < 365 days
    major_injury_keywords = ['dây chằng', 'gãy', 'chấn thương', 'phẫu thuật', 'ung thư']
    pattern = '|'.join(major_injury_keywords)
    
    year_one_major = df_merged[
        (df_merged['days_since_start'] >= 0) & 
        (df_merged['days_since_start'] <= 365) & 
        (df_merged['icd_name_primary'].astype(str).str.contains(pattern, case=False, na=False)) &
        (df_merged['claim_amount_approved'] > 20000000) # Significant amount
    ]
    
    print(f"Total Year 1 Major Claims: {len(year_one_major)}")

    # 6. Save Results
    output_timing = r'D:\desktop_folder\04_Fraud_Detection\report\suspicious_sensitive_timing.csv'
    suspicious_timing.to_csv(output_timing, index=False, encoding='utf-8-sig')
    
    output_year1 = r'D:\desktop_folder\04_Fraud_Detection\report\suspicious_year1_major.csv'
    year_one_major.to_csv(output_year1, index=False, encoding='utf-8-sig')
    
    # 7. Descriptive Stats for Report
    report_data = {
        "sensitive_count": len(suspicious_timing),
        "year1_major_count": len(year_one_major),
        "max_amount_early": suspicious_timing['claim_amount_approved'].max() if not suspicious_timing.empty else 0
    }
    
    print("\nSuspicious Cases Sample:")
    print(suspicious_timing[['user_id', 'claim_date', 'contract_start_date', 'days_since_start', 'claim_amount_approved']].head())

analyze_sensitive_timing()
