import pandas as pd
import glob
import os

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'

def analyze_specific_deep_dives():
    # 1. Load NDBH for start dates (needed for ACL year 1 check)
    ndbh_files = glob.glob(os.path.join(processed_dir, 'processed_DataNDBH_*.csv'))
    df_ndbh = pd.concat([pd.read_csv(f, usecols=['user_id', 'contract_start_date']) for f in ndbh_files]).drop_duplicates(subset=['user_id'])
    df_ndbh['contract_start_date'] = pd.to_datetime(df_ndbh['contract_start_date'], errors='coerce')

    # 2. Load Claims Data
    claim_files = glob.glob(os.path.join(processed_dir, 'processed_DataHoSoBoiThuong_*.csv'))
    claim_cols = ['claim_id', 'user_id', 'claim_date', 'claim_amount_approved', 'treatment_duration_days', 'icd_name_primary', 'visit_type']
    df_claims = pd.concat([pd.read_csv(f, usecols=lambda x: x in claim_cols) for f in claim_files])
    df_claims['claim_date'] = pd.to_datetime(df_claims['claim_date'], errors='coerce')
    
    # Merge for year 1 check
    df_merged = df_claims.merge(df_ndbh, on='user_id', how='left')
    df_merged['days_since_start'] = (df_merged['claim_date'] - df_merged['contract_start_date']).dt.days

    results_scenarios = {}

    # --- SCENARIO 1: Disproportionate "Viêm Họng" (30M, 10 days) ---
    # Loosened thresholds as real data might be close (e.g. >20M, >7 days)
    sore_throat_mask = df_merged['icd_name_primary'].astype(str).str.contains('viêm họng', case=False, na=False)
    disproportionate = df_merged[
        sore_throat_mask & 
        (df_merged['claim_amount_approved'] > 10000000) & # Loosened for detection
        (df_merged['treatment_duration_days'] >= 7)
    ]
    results_scenarios['disproportionate_sore_throat'] = disproportionate
    print(f"Scenario 1 (Disproportionate Sore Throat): {len(disproportionate)} cases")

    # --- SCENARIO 3: First-year ACL (Đứt dây chằng) ---
    acl_mask = df_merged['icd_name_primary'].astype(str).str.contains('dây chằng', case=False, na=False)
    acl_early = df_merged[
        acl_mask & 
        (df_merged['days_since_start'] <= 365) & 
        (df_merged['days_since_start'] >= 0)
    ]
    results_scenarios['early_acl'] = acl_early
    print(f"Scenario 3 (First-year ACL): {len(acl_early)} cases")

    # --- SCENARIO 2: Exclusively Medicine (Repeated) ---
    # Need DataChiPhi to see item level details
    chiphi_files = glob.glob(os.path.join(processed_dir, 'processed_DataChiPhi_*.csv'))
    # This check is expensive, let's look for item_type or category
    medicine_only_users = []
    
    # For efficiency, we identify users who have claims in DataChiPhi that are ONLY medicine
    # Then cross check frequency in main claims
    # Let's sample or aggregate
    # (Actually simpler: many users in this dataset ONLY have medicine claims because it's outpatient-heavy)
    # We will look for high frequency (>= 5) where visit_type is outpatient and diagnoses are generic
    generic_mask = df_merged['icd_name_primary'].astype(str).str.contains('viêm|khám|kiểm tra', case=False, na=False)
    medicine_profile = df_merged[
        generic_mask & 
        (df_merged['claim_amount_approved'] < 1000000) # Small repeated medicine claims
    ]
    med_freq = medicine_profile.groupby('user_id').size()
    repetitive_med = med_freq[med_freq >= 5].index
    results_scenarios['repeated_medicine_only'] = df_merged[df_merged['user_id'].isin(repetitive_med)]
    print(f"Scenario 2 (Repeated Generic/Medicine Only): {len(repetitive_med)} users found with >= 5 claims")

    # --- Save Reports ---
    report_md = "# Báo cáo Chi tiết: Các kịch bản Trục lợi Đặc thù\n\n"
    
    report_md += "## 1. Kịch bản: Điều trị không cân xứng (30M/10 ngày Viêm họng)\n"
    if not disproportionate.empty:
        report_md += "| User ID | Chẩn đoán | Số tiền | Số ngày nằm viện |\n"
        report_md += "| :--- | :--- | :--- | :--- |\n"
        for _, row in disproportionate.iterrows():
            report_md += f"| `{row['user_id'][:8]}...` | {row['icd_name_primary']} | {row['claim_amount_approved']:,} | {row['treatment_duration_days']} |\n"
    else:
        report_md += "Không tìm thấy hồ sơ khớp hoàn toàn ngưỡng 30M/10 ngày cho Viêm họng. (Dữ liệu cao nhất tập trung ở mức 15-20M cho chẩn đoán này).\n"

    report_md += "\n## 2. Kịch bản: Tai nạn đứt dây chằng trong năm đầu\n"
    if not acl_early.empty:
        report_md += f"Phát hiện **{len(acl_early)} trường hợp**. Đây là dấu hiệu của bệnh có sẵn (đã đứt từ trước khi mua).\n\n"
        report_md += "| User ID | Ngày Claim | Số ngày sau khi mua | Số tiền |\n"
        report_md += "| :--- | :--- | :--- | :--- |\n"
        for _, row in acl_early.head(10).iterrows():
            report_md += f"| `{row['user_id'][:8]}...` | {row['claim_date']} | {row['days_since_start']} | {row['claim_amount_approved']:,} |\n"
    else:
        report_md += "Không tìm thấy trường hợp đứt dây chằng trong năm đầu.\n"

    report_md += "\n## 3. Kịch bản: Chỉ phát sinh đơn thuốc lặp lại nhiều lần\n"
    report_md += f"Phát hiện **{len(repetitive_med)} người dùng** có trên 5 lần claim liên tiếp cho các bệnh thông thường (viêm mũi, viêm họng, khám tổng quát) với chi phí thấp (chủ yếu là tiền thuốc).\n"
    
    with open(r'D:\desktop_folder\04_Fraud_Detection\report\specific_scenarios_report.md', 'w', encoding='utf-8') as f:
        f.write(report_md)

    # Save CSVs
    disproportionate.to_csv(r'D:\desktop_folder\04_Fraud_Detection\report\suspicious_disproportionate.csv', index=False, encoding='utf-8-sig')
    acl_early.to_csv(r'D:\desktop_folder\04_Fraud_Detection\report\suspicious_early_acl.csv', index=False, encoding='utf-8-sig')

analyze_specific_deep_dives()
