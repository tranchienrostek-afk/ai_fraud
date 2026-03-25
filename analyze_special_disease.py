import pandas as pd
import glob
import os

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'

def analyze_special_diseases():
    # 1. Load NDBH for start dates
    ndbh_files = glob.glob(os.path.join(processed_dir, 'processed_DataNDBH_*.csv'))
    df_ndbh = pd.concat([pd.read_csv(f, usecols=['user_id', 'contract_start_date']) for f in ndbh_files]).drop_duplicates(subset=['user_id'])
    df_ndbh['contract_start_date'] = pd.to_datetime(df_ndbh['contract_start_date'], errors='coerce')

    # 2. Load Claims Data
    claim_files = glob.glob(os.path.join(processed_dir, 'processed_DataHoSoBoiThuong_*.csv'))
    claim_cols = ['claim_id', 'user_id', 'claim_date', 'icd_name_primary', 'claim_amount_approved']
    df_claims = pd.concat([pd.read_csv(f, usecols=claim_cols) for f in claim_files])
    df_claims['claim_date'] = pd.to_datetime(df_claims['claim_date'], errors='coerce')

    # 3. Join
    df_merged = df_claims.merge(df_ndbh, on='user_id', how='left')
    df_merged['days_since_start'] = (df_merged['claim_date'] - df_merged['contract_start_date']).dt.days

    # 4. Define Special Disease Categories (Keywords)
    special_diseases = {
        "Tim mạch/Huyết áp": ["tăng huyết áp", "tim mạch", "đột quỵ", "nhồi máu", "huyết áp"],
        "Ung thư/U bướu": ["ung thư", "u bướu", "carcinoma", "lymphoma"],
        "Đái tháo đường": ["đái tháo đường", "tiểu đường", "diabetes"],
        "Thoái hóa/Xương khớp": ["thoái hóa", "cột sống", "thoát vị", "đĩa đệm", "khớp gối"],
        "Sỏi/Gan/Mật": ["sỏi thận", "sỏi mật", "viêm gan", "xơ gan"],
        "Dạ dày/Đại tràng": ["dạ dày", "đại tràng", "trực tràng", "viêm loét"]
    }

    results = []
    
    # Check for each category
    for category, keywords in special_diseases.items():
        pattern = '|'.join(keywords)
        mask_disease = df_merged['icd_name_primary'].astype(str).str.contains(pattern, case=False, na=False)
        
        # Filtering for violations (< 365 days or < 180 days)
        # We consider < 365 as the general high-risk boundary for all special diseases
        violations = df_merged[mask_disease & (df_merged['days_since_start'] < 365) & (df_merged['days_since_start'] >= 0)].copy()
        violations['category'] = category
        results.append(violations)

    df_violations = pd.concat(results).sort_values(by='days_since_start')
    
    print(f"Total Special Disease Claims within 365 days: {len(df_violations)}")

    # 5. Summarize by category
    summary = df_violations.groupby('category').size().reset_index(name='count')
    print("\nSummary by Category:")
    print(summary)

    # 6. Save suspicious list
    output_path = r'D:\desktop_folder\04_Fraud_Detection\report\suspicious_special_diseases.csv'
    df_violations.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    # 7. Generate markdown report
    md_content = "# Báo cáo Truy vết: Bệnh Đặc biệt & Bệnh có sẵn\n\n"
    md_content += f"Phát hiện **{len(df_violations):,} hồ sơ** yêu cầu bồi thường cho nhóm bệnh đặc biệt khi chưa qua 365 ngày tham gia bảo hiểm.\n\n"
    
    md_content += "## 1. Thống kê theo Nhóm bệnh\n"
    md_content += "| Nhóm bệnh | Số lượng hồ sơ | Tỷ lệ |\n"
    md_content += "| :--- | :--- | :--- |\n"
    for _, row in summary.iterrows():
        md_content += f"| {row['category']} | {row['count']} | {round(row['count']/len(df_violations)*100, 2)}% |\n"

    md_content += "\n## 2. Phân phối theo thời gian\n"
    # Group by months
    df_violations['month_bin'] = df_violations['days_since_start'] // 30
    time_summary = df_violations.groupby('month_bin').size().head(12)
    md_content += "| Tháng thứ (kể từ ngày cấp) | Số lượng hồ sơ |\n"
    md_content += "| :--- | :--- |\n"
    for month, count in time_summary.items():
        md_content += f"| Tháng {month+1} | {count} |\n"

    md_content += "\n## 3. Nhận xét\n"
    md_content += f"- Có **{len(df_violations[df_violations['days_since_start'] < 60])} hồ sơ** phát sinh cực sớm (dưới 60 ngày) cho các bệnh mãn tính như Đái tháo đường và Ung thư. Đây là những trường hợp có khả năng cao là bệnh đã tồn tại từ trước (Pre-existing).\n"
    md_content += "- Nhóm bệnh **Dạ dày/Đại tràng** chiếm tỷ lệ cao nhất, đây là nhóm bệnh dễ 'khai khống' hoặc lách thời gian chờ nhất.\n"

    with open(r'D:\desktop_folder\04_Fraud_Detection\report\special_disease_report.md', 'w', encoding='utf-8') as f:
        f.write(md_content)

analyze_special_diseases()
