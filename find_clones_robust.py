import pandas as pd
import glob
import os

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'

def find_clones_robust():
    files = glob.glob(os.path.join(processed_dir, 'processed_*.csv'))
    
    all_text_records = []
    
    for f in files:
        df = pd.read_csv(f)
        # Check all string columns for each file
        for col in df.columns:
            if df[col].dtype == 'object':
                # Skip IDs
                if 'id' in col.lower() or 'code' in col.lower():
                    continue
                
                # Extract (user_id, text)
                if 'user_id' in df.columns:
                    temp = df[['user_id', col]].dropna()
                    temp.columns = ['user_id', 'text']
                    all_text_records.append(temp)
                
    if not all_text_records:
        print("No narrative data found.")
        return

    df_full = pd.concat(all_text_records)
    df_full['text_clean'] = df_full['text'].astype(str).str.strip().str.lower()
    
    # Filter short placeholders and generic values
    # Ignore values like 'nan', '2.0', '1.0', or short codes
    df_full = df_full[df_full['text_clean'].str.len() > 30]
    
    # Group and count unique users for each piece of text
    cloning_stats = df_full.groupby('text_clean').agg(
        total_claims=('user_id', 'count'),
        unique_users=('user_id', 'nunique'),
        sample_users=('user_id', lambda x: list(x.unique())[:3])
    ).reset_index()

    # Suspicious: same long text used for >= 5 different users
    clones = cloning_stats[cloning_stats['unique_users'] >= 5].sort_values(by='total_claims', ascending=False)

    print(f"Medical Cloning Clusters Found: {len(clones)}")
    
    if not clones.empty:
        clones.to_csv(r'D:\desktop_folder\04_Fraud_Detection\report\medical_cloning_clusters.csv', index=False, encoding='utf-8-sig')
        
        # Markdown Report
        md = "# Báo cáo Truy vết: Nhân bản Bệnh án (Medical Record Cloning)\n\n"
        md += f"Phân tích dựa trên 100% dữ liệu phát hiện **{len(clones)} cụm nội dung** được sao chép y hệt cho nhiều bệnh nhân.\n\n"
        md += "## 1. Các mẫu nội dung " + '"' + "Copy-Paste" + '"' + " phổ biến nhất\n"
        md += "| Nội dung Diễn biến bệnh/Dịch vụ | Tổng số hồ sơ | Số người dùng khác nhau |\n"
        md += "| :--- | :--- | :--- |\n"
        for _, row in clones.head(15).iterrows():
            txt = (row['text_clean'][:120] + "...") if len(row['text_clean']) > 120 else row['text_clean']
            md += f"| \"{txt}\" | {row['total_claims']:,} | {row['unique_users']:,} |\n"
            
        md += "\n## 2. Kết luận\n"
        md += "- **Tỷ lệ nhân bản:** Việc một đoạn văn bản dài trên 30 ký tự xuất hiện y hệt nhau cho hàng chục người dùng khác nhau là bằng chứng xác thực của việc làm giả hồ sơ bệnh án hoặc quy trình lập hồ sơ hời hợt, không ghi nhận đúng thực tế bệnh nhân.\n"
        md += "- **Khuyến nghị:** Cần đối soát danh sách hồ sơ trong tệp `medical_cloning_clusters.csv` với các Cơ sở Y tế để làm rõ tại sao có sự trùng lặp này.\n"

        with open(r'D:\desktop_folder\04_Fraud_Detection\report\medical_cloning_report.md', 'w', encoding='utf-8') as f:
            f.write(md)
            
    print("Cloning detection completed.")

if __name__ == "__main__":
    find_clones_robust()
