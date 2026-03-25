import pandas as pd
import glob
import os

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'
files = glob.glob(os.path.join(processed_dir, 'processed_DataHoSoBoiThuong_*.csv'))

def analyze_types():
    all_data = []
    for f in files:
        df = pd.read_csv(f, usecols=['user_id', 'claim_amount_approved', 'visit_type', 'claim_type'])
        all_data.append(df)
    
    df_all = pd.concat(all_data)
    
    # Suspicious users (from previous analysis)
    threshold = 200000
    user_counts = df_all.groupby('user_id').size()
    user_max_amt = df_all.groupby('user_id')['claim_amount_approved'].max()
    
    suspicious_ids = user_max_amt[(user_max_amt < threshold) & (user_counts >= 3)].index
    
    suspicious_data = df_all[df_all['user_id'].isin(suspicious_ids)]
    
    print("Frequency of claim_type for suspicious users:")
    print(suspicious_data['claim_type'].value_counts(normalize=True))
    
    print("\nFrequency of visit_type for suspicious users:")
    print(suspicious_data['visit_type'].value_counts(normalize=True))
    
    print("\nFrequency of claim_type for NORMAL users (Amount >= 200k):")
    normal_data = df_all[~df_all['user_id'].isin(suspicious_ids)]
    print(normal_data['claim_type'].value_counts(normalize=True))

analyze_types()
