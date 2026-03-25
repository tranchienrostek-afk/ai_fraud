import pandas as pd
import glob
import os

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'
files = glob.glob(os.path.join(processed_dir, 'processed_DataHoSoBoiThuong_*.csv'))

def analyze_petty_claims():
    all_data = []
    for f in files:
        df = pd.read_csv(f, usecols=['user_id', 'claim_amount_approved', 'visit_type', 'claim_type', 'clinical_notes'])
        all_data.append(df)
    
    df_all = pd.concat(all_data)
    
    # Threshold for petty claims
    threshold = 200000
    
    # 1. Total claims per user
    user_summary = df_all.groupby('user_id').agg(
        total_claims=('user_id', 'count'),
        petty_claims=('claim_amount_approved', lambda x: (x < threshold).sum()),
        avg_amount=('claim_amount_approved', 'mean')
    )
    
    # 2. Users who ONLY have petty claims and have more than 3 claims
    suspicious_users = user_summary[
        (user_summary['petty_claims'] == user_summary['total_claims']) & 
        (user_summary['total_claims'] >= 3)
    ].sort_values(by='total_claims', ascending=False)
    
    print(f"Total Suspicious Users (Only claims < 200k, >= 3 claims): {len(suspicious_users)}")
    print("\nTop suspicious users by claim count:")
    print(suspicious_users.head(10))
    
    # Save the list
    output_path = r'D:\desktop_folder\04_Fraud_Detection\report\suspicious_petty_claims.csv'
    suspicious_users.to_csv(output_path, encoding='utf-8-sig')
    
    # 3. Look for "Bán lẻ" in clinical_notes
    petty_with_notes = df_all[df_all['claim_amount_approved'] < threshold]
    if 'clinical_notes' in petty_with_notes.columns:
        # Since clinical_notes was seen as numeric in stats, let's check it
        retail_mentions = petty_with_notes[petty_with_notes['clinical_notes'].astype(str).str.contains('bán lẻ', case=False, na=False)]
        print(f"\nClaims < 200k mentioning 'bán lẻ' in notes: {len(retail_mentions)}")

analyze_petty_claims()
