import pandas as pd
import glob
import os

report_dir = r'D:\desktop_folder\04_Fraud_Detection\report'
processed_dir = os.path.join(report_dir, 'processed')

def merge_all_risks():
    # 1. Load All Claims (Base)
    claim_files = glob.glob(os.path.join(processed_dir, 'processed_DataHoSoBoiThuong_*.csv'))
    df_base = pd.concat([pd.read_csv(f) for f in claim_files])
    df_base['risk_score'] = 0
    df_base['risk_indicators'] = ""

    def add_risk(df, filtered_ids, score, label):
        mask = df['claim_id'].isin(filtered_ids)
        df.loc[mask, 'risk_score'] += score
        df.loc[mask, 'risk_indicators'] += label + "; "

    # 2. Petty Fraud (<200k)
    petty = pd.read_csv(os.path.join(report_dir, 'suspicious_petty_claims.csv'))
    add_risk(df_base, petty['claim_id'], 2, "Petty Invoice (<200k)")

    # 3. Sensitive Timing (Early claims)
    timing = pd.read_csv(os.path.join(report_dir, 'suspicious_early_claims.csv'))
    add_risk(df_base, timing['claim_id'], 5, "Sensitive Timing (Early Major)")

    # 4. Special Disease (Waiting Period)
    disease = pd.read_csv(os.path.join(report_dir, 'suspicious_special_diseases.csv'))
    add_risk(df_base, disease['claim_id'], 4, "Waiting Period Violation")

    # 5. Medical Cloning (Text Similarity)
    # This report is at text level, let's load the clusters and map back
    clones = pd.read_csv(os.path.join(report_dir, 'medical_cloning_clusters.csv'))
    # Re-run a simple match for the top clones to tag base
    # For now, we'll tag if the text is in the top clone list
    top_texts = set(clones['text_clean'].tolist())
    # We check multiple columns
    for col in ['clinical_notes', 'discharge_diagnosis']:
        if col in df_base.columns:
            mask_clone = df_base[col].astype(str).str.strip().str.lower().isin(top_texts)
            df_base.loc[mask_clone, 'risk_score'] += 3
            df_base.loc[mask_clone, 'risk_indicators'] += "Medical Record Cloning; "

    # 6. Syndicates (Shared Bank/Phone)
    # Load the phone and account CSVs
    try:
        shared_phone = pd.read_csv(os.path.join(report_dir, 'syndicate_by_phone_number.csv'))
        bad_phones = set(shared_phone['phone_number'].astype(str).tolist())
        mask_phone = df_base['phone_number'].astype(str).str.strip().isin(bad_phones)
        df_base.loc[mask_phone, 'risk_score'] += 3
        df_base.loc[mask_phone, 'risk_indicators'] += "Syndicate (Shared Phone); "
    except: pass
    
    try:
        shared_acc = pd.read_csv(os.path.join(report_dir, 'syndicate_by_beneficiary_account.csv'))
        # Specific filter: accounts with >= 10 users are extreme risk
        extreme_accs = set(shared_acc[shared_acc['num_people'] >= 10]['beneficiary_account'].astype(str).tolist())
        mask_ext = df_base['beneficiary_account'].astype(str).str.strip().isin(extreme_accs)
        df_base.loc[mask_ext, 'risk_score'] += 10
        df_base.loc[mask_ext, 'risk_indicators'] += "EXTREME Syndicate (Shared Bank Acc >= 10 users); "
    except: pass

    # 7. Outliers from first step
    mask_outlier = df_base['claim_amount_approved_is_outlier'] == True
    df_base.loc[mask_outlier, 'risk_score'] += 2
    df_base.loc[mask_outlier, 'risk_indicators'] += "Financial Outlier; "

    # Output Master Result
    df_base = df_base.sort_values(by='risk_score', ascending=False)
    df_base.to_csv(os.path.join(report_dir, 'master_fraud_risk_list.csv'), index=False, encoding='utf-8-sig')

    # Summary Stats
    total_high_risk = len(df_base[df_base['risk_score'] >= 10])
    print(f"Total High Risk Claims (Score >= 10): {total_high_risk}")
    print(f"Top Score Detected: {df_base['risk_score'].max()}")

merge_all_risks()
