import pandas as pd
import glob
import os

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'

def analyze_upgrades_and_timing():
    # 1. Load NDBH to see contract history
    ndbh_files = glob.glob(os.path.join(processed_dir, 'processed_DataNDBH_*.csv'))
    ndbh_list = []
    for f in ndbh_files:
        df = pd.read_csv(f, usecols=['user_id', 'contract_start_date', 'contract_level', 'so_hop_dong'])
        ndbh_list.append(df)
    df_ndbh = pd.concat(ndbh_list)
    df_ndbh['contract_start_date'] = pd.to_datetime(df_ndbh['contract_start_date'], errors='coerce')
    
    # Sort to find the EARLIEST start date per user
    df_ndbh = df_ndbh.sort_values(by=['user_id', 'contract_start_date'])
    earliest_start = df_ndbh.groupby('user_id')['contract_start_date'].min().reset_index()
    earliest_start.columns = ['user_id', 'first_contract_start']

    # 2. Load Claims Data
    claim_files = glob.glob(os.path.join(processed_dir, 'processed_DataHoSoBoiThuong_*.csv'))
    claim_list = []
    for f in claim_files:
        df = pd.read_csv(f, usecols=['claim_id', 'user_id', 'claim_date', 'claim_amount_approved', 'icd_name_primary'])
        claim_list.append(df)
    df_claims = pd.concat(claim_list)
    df_claims['claim_date'] = pd.to_datetime(df_claims['claim_date'], errors='coerce')

    # 3. Merge
    df_merged = df_claims.merge(earliest_start, on='user_id', how='left')
    df_merged['days_since_first_start'] = (df_merged['claim_date'] - df_merged['first_contract_start']).dt.days

    # Pattern A: Claims > 10M within first 60 days (Wait period + small buffer)
    early_major_claims = df_merged[
        (df_merged['claim_amount_approved'] > 10000000) & 
        (df_merged['days_since_first_start'] >= 0) & 
        (df_merged['days_since_first_start'] <= 60)
    ].sort_values(by='claim_amount_approved', ascending=False)

    print(f"Early Major Claims (>10M, <60 days): {len(early_major_claims)}")

    # Pattern B: Suspicious "Wait Period" Cluster (Many claims starting exactly after 30 days)
    # We look for claims between day 31 and day 45
    wait_period_cluster = df_merged[
        (df_merged['days_since_first_start'] > 30) & 
        (df_merged['days_since_first_start'] <= 45)
    ]
    print(f"Claims occurring immediately after wait period (Days 31-45): {len(wait_period_cluster)}")

    # Pattern C: Upgrade Detection
    # Users with multiple contract_levels, where the higher level starts just before a major claim
    user_levels = df_ndbh.groupby('user_id')['contract_level'].nunique()
    upgraded_users = user_levels[user_levels > 1].index
    
    # For these users, find if they had a major claim (>20M) within 30 days of a level change
    upgrade_cases = []
    for uid in upgraded_users:
        u_contracts = df_ndbh[df_ndbh['user_id'] == uid].sort_values('contract_start_date')
        u_claims = df_claims[df_claims['user_id'] == uid]
        
        for i in range(1, len(u_contracts)):
            prev_level = u_contracts.iloc[i-1]['contract_level']
            curr_level = u_contracts.iloc[i]['contract_level']
            upgrade_date = u_contracts.iloc[i]['contract_start_date']
            
            # If current level is "higher" (assuming higher number or string sort)
            # Find claims after upgrade_date
            post_upgrade_claims = u_claims[
                (u_claims['claim_date'] >= upgrade_date) & 
                ((u_claims['claim_date'] - upgrade_date).dt.days <= 30) &
                (u_claims['claim_amount_approved'] > 10000000)
            ]
            if not post_upgrade_claims.empty:
                upgrade_cases.append(post_upgrade_claims)

    if upgrade_cases:
        df_upgrades = pd.concat(upgrade_cases)
        print(f"Claims >10M within 30 days of a contract level change: {len(df_upgrades)}")
        df_upgrades.to_csv(r'D:\desktop_folder\04_Fraud_Detection\report\suspicious_upgrades.csv', index=False, encoding='utf-8-sig')
    else:
        print("No suspicious upgrade-then-claim cases found.")

    # Save early claims
    early_major_claims.to_csv(r'D:\desktop_folder\04_Fraud_Detection\report\suspicious_early_claims.csv', index=False, encoding='utf-8-sig')

analyze_upgrades_and_timing()
