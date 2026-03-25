import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'
media_dir = r'D:\desktop_folder\04_Fraud_Detection\report\media'

def analyze_hfm_distribution():
    # 1. Load Claims Data
    claim_files = glob.glob(os.path.join(processed_dir, 'processed_DataHoSoBoiThuong_*.csv'))
    df_list = []
    for f in claim_files:
        df = pd.read_csv(f, usecols=['claim_id', 'claim_amount_approved', 'icd_name_primary', 'visit_type', 'treatment_duration_days'])
        df_list.append(df)
    df_claims = pd.concat(df_list)

    # 2. Filter for "Tay chân miệng"
    hfm_mask = df_claims['icd_name_primary'].astype(str).str.contains('tay chân miệng', case=False, na=False)
    df_hfm = df_claims[hfm_mask].copy()
    
    if df_hfm.empty:
        print("No HFM claims found.")
        return

    # 3. Basic Stats
    stats = df_hfm['claim_amount_approved'].describe()
    print("HFM Stats:")
    print(stats)

    # 4. Visualization
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 7))
    
    # Histogram with KDE
    sns.histplot(df_hfm['claim_amount_approved'], kde=True, bins=30, color='teal')
    plt.title("Phân phối Số tiền Bồi thường: Bệnh Tay Chân Miệng", fontsize=16, fontweight='bold')
    plt.xlabel("Số tiền được duyệt (VNĐ)", fontsize=12)
    plt.ylabel("Số lượng hồ sơ", fontsize=12)
    
    # Add vertical lines for mean/median
    plt.axvline(stats['mean'], color='red', linestyle='--', label=f"Trung bình: {stats['mean']:,.0f}")
    plt.axvline(stats['50%'], color='orange', linestyle='-', label=f"Trung vị: {stats['50%']:,.0f}")
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(media_dir, "hfm_distribution.png"), dpi=300)

    # 5. Segment analysis (Inpatient vs Outpatient)
    # 1.0 usually outpatient, 2.0 inpatient (standard in this dataset based on previous views)
    seg_stats = df_hfm.groupby('visit_type')['claim_amount_approved'].agg(['count', 'mean', 'median', 'max'])
    print("\nSegment analysis (Outpatient vs Inpatient):")
    print(seg_stats)

    # 6. Markdown Report
    md_content = "# Phân tích Mật độ: Bệnh Tay chân miệng (HFM)\n\n"
    md_content += f"Phân tích dựa trên **{len(df_hfm):,} hồ sơ** được xác định là Tay chân miệng.\n\n"
    
    md_content += "## 1. Biểu đồ Phân phối số tiền\n"
    md_content += "![HFM Distribution](file:///D:/desktop_folder/04_Fraud_Detection/report/media/hfm_distribution.png)\n\n"
    
    md_content += "## 2. Thống kê Chi tiết\n"
    md_content += "| Chỉ số | Giá trị (VNĐ) |\n"
    md_content += "| :--- | :--- |\n"
    md_content += f"| Số lượng hồ sơ | {len(df_hfm):,} |\n"
    md_content += f"| Giá trị Trung bình | {stats['mean']:,.0f} |\n"
    md_content += f"| Giá trị Trung vị (Median) | {stats['50%']:,.0f} |\n"
    md_content += f"| Giá trị Cao nhất (Max) | {stats['max']:,.0f} |\n"
    md_content += f"| Giá trị Thấp nhất (Min) | {stats['min']:,.0f} |\n\n"
    
    md_content += "## 3. Phân khúc theo Loại hình khám\n"
    md_content += "| Loại hình | Số lượng | Trung bình (VNĐ) | Cao nhất (VNĐ) |\n"
    md_content += "| :--- | :--- | :--- | :--- |\n"
    for idx, row in seg_stats.iterrows():
        label = "Nội trú" if idx == 2.0 else "Ngoại trú"
        md_content += f"| {label} | {int(row['count'])} | {row['mean']:,.0f} | {row['max']:,.0f} |\n"
    
    md_content += "\n## 4. Nhận xét\n"
    md_content += f"- Đa số hồ sơ tập trung ở ngưỡng **{stats['50%']:,.0f} - {stats['mean']:,.0f} VNĐ**.\n"
    if stats['max'] > 10000000:
        md_content += f"- Phát hiện một số hồ sơ **Outlier** lên tới {stats['max']:,.0f} VNĐ, cần kiểm tra lại thời gian nằm viện của các trường hợp này để xác minh tính cân xứng.\n"

    with open(r'D:\desktop_folder\04_Fraud_Detection\report\hfm_distribution_report.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print("HFM distribution analysis completed.")

if __name__ == "__main__":
    analyze_hfm_distribution()
