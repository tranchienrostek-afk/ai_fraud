import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'
media_dir = r'D:\desktop_folder\04_Fraud_Detection\report\media'

def analyze_jit_concentration():
    # 1. Load NDBH for start dates
    ndbh_files = glob.glob(os.path.join(processed_dir, 'processed_DataNDBH_*.csv'))
    df_ndbh = pd.concat([pd.read_csv(f, usecols=['user_id', 'contract_start_date']) for f in ndbh_files]).drop_duplicates(subset=['user_id'])
    df_ndbh['contract_start_date'] = pd.to_datetime(df_ndbh['contract_start_date'], errors='coerce')

    # 2. Load Claims Data with hospital/insurer info
    claim_files = glob.glob(os.path.join(processed_dir, 'processed_DataHoSoBoiThuong_*.csv'))
    claim_cols = ['claim_id', 'user_id', 'claim_date', 'hospital_code', 'insurer_id']
    df_claims = pd.concat([pd.read_csv(f, usecols=claim_cols) for f in claim_files])
    df_claims['claim_date'] = pd.to_datetime(df_claims['claim_date'], errors='coerce')

    # 3. Filter JIT (Just-In-Time) claims: Day 31 to 45
    df_merged = df_claims.merge(df_ndbh, on='user_id', how='left')
    df_merged['days_since_start'] = (df_merged['claim_date'] - df_merged['contract_start_date']).dt.days
    
    jit_claims = df_merged[(df_merged['days_since_start'] > 30) & (df_merged['days_since_start'] <= 45)].copy()
    
    total_jit = len(jit_claims)
    print(f"Total JIT Claims to analyze: {total_jit}")

    # 4. Aggregation by Hospital
    hosp_dist = jit_claims['hospital_code'].value_counts().reset_index()
    hosp_dist.columns = ['Hospital_Code', 'Claim_Count']
    hosp_dist['Percentage'] = (hosp_dist['Claim_Count'] / total_jit * 100).round(2)
    
    # 5. Aggregation by Insurer
    ins_dist = jit_claims['insurer_id'].value_counts().reset_index()
    ins_dist.columns = ['Insurer_ID', 'Claim_Count']
    ins_dist['Percentage'] = (ins_dist['Claim_Count'] / total_jit * 100).round(2)

    # 6. Visualization - Top 10 Hospitals
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 6))
    top_hosp = hosp_dist.head(10)
    sns.barplot(x="Hospital_Code", y="Claim_Count", data=top_hosp, palette="Blues_d", hue="Hospital_Code", legend=False)
    plt.title("Top 10 Cơ sở Y tế có tỷ lệ 'Claim sớm' cao nhất", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(media_dir, "jit_hospital_concentration.png"), dpi=300)

    # 7. Visualization - Top 10 Insurers
    plt.figure(figsize=(12, 6))
    top_ins = ins_dist.head(10)
    sns.barplot(x="Insurer_ID", y="Claim_Count", data=top_ins, palette="Reds_d", hue="Insurer_ID", legend=False)
    plt.title("Top 10 Đại lý/Công ty BR có tỷ lệ 'Claim sớm' cao nhất", fontsize=16, fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(media_dir, "jit_insurer_concentration.png"), dpi=300)

    # 8. Markdown Report
    md_content = f"# Báo cáo Tập trung: Nhóm 'Vừa hết thời gian chờ' (JIT Claims)\n\n"
    md_content += f"Phân tích tập trung vào **{total_jit:,} hồ sơ** phát sinh trong khoảng ngày 31-45 sau khi tham gia bảo hiểm.\n\n"
    
    md_content += "## 1. Tập trung theo Cơ sở Y tế (Top 5)\n"
    md_content += "![Hospital Concentration](file:///D:/desktop_folder/04_Fraud_Detection/report/media/jit_hospital_concentration.png)\n\n"
    md_content += "| Hospital Code | Số lượng hồ sơ | Tỷ lệ (%) |\n"
    md_content += "| :--- | :--- | :--- |\n"
    for _, row in hosp_dist.head(5).iterrows():
        md_content += f"| {row['Hospital_Code']} | {row['Claim_Count']} | {row['Percentage']}% |\n"
    
    md_content += "\n## 2. Tập trung theo Đại lý/Công ty (Top 5)\n"
    md_content += "![Insurer Concentration](file:///D:/desktop_folder/04_Fraud_Detection/report/media/jit_insurer_concentration.png)\n\n"
    md_content += "| Insurer ID | Số lượng hồ sơ | Tỷ lệ (%) |\n"
    md_content += "| :--- | :--- | :--- |\n"
    for _, row in ins_dist.head(5).iterrows():
        md_content += f"| {row['Insurer_ID']} | {row['Claim_Count']} | {row['Percentage']}% |\n"
    
    md_content += "\n## 3. Nhận xét\n"
    # Logic to find if top 1 has significantly more than random
    top_hosp_pct = hosp_dist.iloc[0]['Percentage']
    if top_hosp_pct > 15:
        md_content += f"- **Bất thường tại Bệnh viện:** Bệnh viện `{hosp_dist.iloc[0]['Hospital_Code']}` chiếm tận {top_hosp_pct}% lượng hồ sơ claim sớm. Cần kiểm tra xem bệnh viện này có quy trình 'khám nhanh' cho khách mới không.\n"
    else:
        md_content += "- Không có sự tập trung cực đoan tại một bệnh viện duy nhất, dữ liệu phân bổ khá đều.\n"

    top_ins_pct = ins_dist.iloc[0]['Percentage']
    if top_ins_pct > 20:
        md_content += f"- **Bất thường tại Đại lý:** Đại lý `{ins_dist.iloc[0]['Insurer_ID']}` đang có tỉ lệ claim sớm lên tới {top_ins_pct}%. Đây là dấu hiệu của việc trục lợi có tổ chức từ khâu cấp đơn.\n"
    
    with open(r'D:\desktop_folder\04_Fraud_Detection\report\jit_concentration_report.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print("JIT Concentration analysis completed.")

if __name__ == "__main__":
    analyze_jit_concentration()
