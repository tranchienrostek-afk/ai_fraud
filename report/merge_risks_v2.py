import pandas as pd
import glob
import os

report_dir = r'D:\desktop_folder\04_Fraud_Detection\report'
processed_dir = os.path.join(report_dir, 'processed')

def merge_all_risks_v2():
    # 1. Load All Claims (Base)
    claim_files = glob.glob(os.path.join(processed_dir, 'processed_DataHoSoBoiThuong_*.csv'))
    df_base = pd.concat([pd.read_csv(f) for f in claim_files])
    df_base['risk_score'] = 0
    df_base['risk_indicators'] = ""

    # 2. User-level Risks (Petty Fraud)
    petty_file = os.path.join(report_dir, 'suspicious_petty_claims.csv')
    if os.path.exists(petty_file):
        petty_users = pd.read_csv(petty_file)['user_id'].tolist()
        mask_petty = df_base['user_id'].isin(petty_users)
        df_base.loc[mask_petty, 'risk_score'] += 3
        df_base.loc[mask_petty, 'risk_indicators'] += "Petty Invoice Only (<200k); "

    # 3. Claim-level Risks (Sensitive Timing)
    timing_file = os.path.join(report_dir, 'suspicious_early_claims.csv')
    if os.path.exists(timing_file):
        timing_claims = pd.read_csv(timing_file)['claim_id'].tolist()
        mask_timing = df_base['claim_id'].isin(timing_claims)
        df_base.loc[mask_timing, 'risk_score'] += 5
        df_base.loc[mask_timing, 'risk_indicators'] += "Sensitive Timing (Early Major); "

    # 4. Special Disease (Waiting Period)
    disease_file = os.path.join(report_dir, 'suspicious_special_diseases.csv')
    if os.path.exists(disease_file):
        disease_claims = pd.read_csv(disease_file)['claim_id'].tolist()
        mask_disease = df_base['claim_id'].isin(disease_claims)
        df_base.loc[mask_disease, 'risk_score'] += 4
        df_base.loc[mask_disease, 'risk_indicators'] += "Waiting Period Violation; "

    # 5. Medical Cloning (Text Similarity)
    clones_file = os.path.join(report_dir, 'medical_cloning_clusters.csv')
    if os.path.exists(clones_file):
        clones = pd.read_csv(clones_file)
        top_texts = set(clones['text_clean'].astype(str).tolist())
        for col in ['clinical_notes', 'discharge_diagnosis']:
            if col in df_base.columns:
                mask_clone = df_base[col].astype(str).str.strip().str.lower().isin(top_texts)
                df_base.loc[mask_clone, 'risk_score'] += 3
                df_base.loc[mask_clone, 'risk_indicators'] += "Medical Record Cloning; "

    # 6. Syndicates (Shared Bank/Phone)
    phone_file = os.path.join(report_dir, 'syndicate_by_phone_number.csv')
    if os.path.exists(phone_file):
        shared_phone = pd.read_csv(phone_file)
        bad_phones = set(shared_phone['phone_number'].astype(str).tolist())
        mask_phone = df_base['phone_number'].astype(str).str.strip().isin(bad_phones)
        df_base.loc[mask_phone, 'risk_score'] += 3
        df_base.loc[mask_phone, 'risk_indicators'] += "Syndicate (Shared Phone); "
    
    acc_file = os.path.join(report_dir, 'syndicate_by_beneficiary_account.csv')
    if os.path.exists(acc_file):
        shared_acc = pd.read_csv(acc_file)
        # Extreme Risk: accounts with >= 10 users
        extreme_accs = set(shared_acc[shared_acc['num_people'] >= 10]['beneficiary_account'].astype(str).tolist())
        mask_ext = df_base['beneficiary_account'].astype(str).str.strip().isin(extreme_accs)
        df_base.loc[mask_ext, 'risk_score'] += 10
        df_base.loc[mask_ext, 'risk_indicators'] += "EXTREME Syndicate (Shared Bank Acc >= 10 users); "

    # 7. Financial Outlier
    mask_outlier = df_base['claim_amount_approved_is_outlier'] == True
    df_base.loc[mask_outlier, 'risk_score'] += 2
    df_base.loc[mask_outlier, 'risk_indicators'] += "Financial Outlier; "

    # 8. Sort and Save
    df_base = df_base.sort_values(by='risk_score', ascending=False)
    df_base.to_csv(os.path.join(report_dir, 'master_fraud_risk_list.csv'), index=False, encoding='utf-8-sig')

    total_claims = len(df_base)
    high_risk = len(df_base[df_base['risk_score'] >= 10])
    med_risk = len(df_base[(df_base['risk_score'] >= 5) & (df_base['risk_score'] < 10)])
    
    print(f"Total Claims Analyzed: {total_claims:,}")
    print(f"High Risk (Score >= 10): {high_risk:,}")
    print(f"Medium Risk (Score 5-9): {med_risk:,}")

if __name__ == "__main__":
    merge_all_risks_v2()
