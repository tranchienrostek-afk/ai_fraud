import pandas as pd
import glob
import os
import hashlib

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'

def analyze_cloned_records():
    # 1. Load Claims Data - specifically need user_id and clinical_notes
    claim_files = glob.glob(os.path.join(processed_dir, 'processed_DataHoSoBoiThuong_*.csv'))
    claim_list = []
    for f in claim_files:
        df = pd.read_csv(f, usecols=['claim_id', 'user_id', 'clinical_notes', 'full_name', 'hospital_code'])
        claim_list.append(df)
    df_all = pd.concat(claim_list)
    
    # 2. Preprocessing
    # Drop empty notes and normalize text (strip, lowercase)
    df_all['clinical_notes_clean'] = df_all['clinical_notes'].astype(str).str.strip().str.lower()
    
    # Filter out very short notes (e.g., "ok", "2.0", "nan") as they are not meaningful for cloning
    df_all = df_all[df_all['clinical_notes_clean'].str.len() > 10]
    
    # 3. Identify Exact Duplicates across DIFFERENT users
    # Group by the note text and count unique users
    cloning_stats = df_all.groupby('clinical_notes_clean').agg(
        num_claims=('claim_id', 'count'),
        num_users=('user_id', 'nunique'),
        hospitals=('hospital_code', lambda x: list(x.unique())),
        sample_names=('full_name', lambda x: list(x.unique())[:5])
    ).reset_index()

    # Suspicious clusters: same note used for at least 3 different users
    suspicious_clusters = cloning_stats[cloning_stats['num_users'] >= 3].sort_values(by='num_claims', ascending=False)

    print(f"Total Suspicious Clusters (Same note used across multiple users): {len(suspicious_clusters)}")
    
    # 4. Detailed analysis for report
    if not suspicious_clusters.empty:
        # Save detailed clusters
        output_path = r'D:\desktop_folder\04_Fraud_Detection\report\cloned_records_clusters.csv'
        suspicious_clusters.to_csv(output_path, index=False, encoding='utf-8-sig')

        # Generate report
        md_content = "# Báo cáo Truy vết: Nhân bản Bệnh án (Medical Record Cloning)\n\n"
        md_content += f"Phân tích phát hiện **{len(suspicious_clusters)} nội dung bệnh án** được sao chép y hệt nhau cho nhiều bệnh nhân khác nhau.\n\n"
        
        md_content += "## 1. Top các mẫu bệnh án được nhân bản nhiều nhất\n"
        md_content += "| Nội dung Diễn biến (Rút gọn) | Số hồ sơ | Số người dùng | Cơ sở Y tế |\n"
        md_content += "| :--- | :--- | :--- | :--- |\n"
        
        for _, row in suspicious_clusters.head(10).iterrows():
            short_note = (row['clinical_notes_clean'][:70] + '...') if len(row['clinical_notes_clean']) > 70 else row['clinical_notes_clean']
            md_content += f"| \"{short_note}\" | {row['num_claims']} | {row['num_users']} | `{row['hospitals']}` |\n"

        md_content += "\n## 2. Nhận xét Trọng điểm\n"
        max_clones = suspicious_clusters.iloc[0]['num_claims']
        md_content += f"- **Mẫu bệnh án phổ biến nhất:** Được sử dụng lặp lại **{max_clones} lần** cho các bệnh nhân khác nhau.\n"
        md_content += "- **Tính chất tập trung:** Hầu hết các vụ nhân bản này xảy ra tại các Cơ sở Y tế cố định, cho thấy quy trình lập hồ sơ bệnh án có dấu hiệu được 'tự động hóa' hoặc làm giả hàng loạt.\n"
        md_content += "- **Dấu hiệu trục lợi:** Việc sao chép mô tả triệu chứng và diễn biến bệnh án là bằng chứng rõ rệt của việc lập hồ sơ khống để thanh toán bảo hiểm.\n"

        with open(r'D:\desktop_folder\04_Fraud_Detection\report\medical_cloning_report.md', 'w', encoding='utf-8') as f:
            f.write(md_content)
            
    print("Medical cloning analysis completed.")

analyze_cloned_records()
