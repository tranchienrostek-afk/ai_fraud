import pandas as pd
import glob
import os

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'

def find_clones():
    # Columns to check for cloning
    cols_to_check = ['clinical_notes', 'discharge_diagnosis', 'drug_or_service_name']
    
    files = glob.glob(os.path.join(processed_dir, 'processed_*.csv'))
    
    all_rows = []
    for f in files:
        df = pd.read_csv(f)
        for col in cols_to_check:
            if col in df.columns:
                # Extract text, user, and id
                temp = df[['user_id', col]].dropna()
                temp.columns = ['user_id', 'text']
                all_rows.append(temp)
                
    if not all_rows:
        print("No text data found.")
        return

    df_text = pd.concat(all_rows)
    df_text['text_clean'] = df_text['text'].astype(str).str.strip().str.lower()
    
    # Filter short/numeric placeholders
    df_text = df_text[df_text['text_clean'].str.len() > 15]
    
    # Find Duplicates across DIFFERENT users
    stats = df_text.groupby('text_clean').agg(
        num_claims=('text_clean', 'count'),
        num_users=('user_id', 'nunique'),
        sample_users=('user_id', lambda x: list(x.unique())[:3])
    ).reset_index()

    # Suspicious if same narrative used for >= 10 claims or >= 5 users
    clones = stats[stats['num_users'] >= 5].sort_values('num_claims', ascending=False)
    
    print(f"Clusters found: {len(clones)}")
    if not clones.empty:
        clones.to_csv(r'D:\desktop_folder\04_Fraud_Detection\report\cloned_text_clusters.csv', index=False, encoding='utf-8-sig')
        
        # Report
        md = "# Báo cáo Truy vết: Nhân bản Bệnh án (Medical Cloning)\n\n"
        md += "| Nội dung nhân bản | Số hồ sơ | Số người dùng |\n"
        md += "| :--- | :--- | :--- |\n"
        for _, row in clones.head(15).iterrows():
            txt = (row['text_clean'][:100] + "...") if len(row['text_clean']) > 100 else row['text_clean']
            md += f"| \"{txt}\" | {row['num_claims']} | {row['num_users']} |\n"
            
        with open(r'D:\desktop_folder\04_Fraud_Detection\report\medical_cloning_report.md', 'w', encoding='utf-8') as f:
            f.write(md)
            
    print("Done.")

if __name__ == "__main__":
    find_clones()
