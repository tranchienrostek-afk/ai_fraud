import pandas as pd
import glob
import os

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'

def perform_link_analysis():
    # 1. Load Claims Data with all identifiers
    claim_files = glob.glob(os.path.join(processed_dir, 'processed_DataHoSoBoiThuong_*.csv'))
    cols = ['user_id', 'full_name', 'identity_number', 'phone_number', 'email', 'beneficiary_account', 'beneficiary_name']
    df_list = []
    for f in claim_files:
        df = pd.read_csv(f, usecols=lambda x: x in cols)
        df_list.append(df)
    df_all = pd.concat(df_list).drop_duplicates()

    results = {}

    # Define identifiers to check for sharing
    identifiers = {
        'Số điện thoại': 'phone_number',
        'Email': 'email',
        'Số tài khoản thụ hưởng': 'beneficiary_account'
    }

    linked_report = "# Báo cáo Liên kết (Link Analysis): Nhóm Trục lợi (Syndicates)\n\n"
    linked_report += "Phân tích tìm kiếm các trường hợp nhiều khách hàng khác nhau nhưng sử dụng chung thông tin liên lạc hoặc tài khoản ngân hàng.\n\n"

    for label, col in identifiers.items():
        if col not in df_all.columns:
            continue
            
        # Group by identifier and find unique identity_numbers
        # Ensure we filter out NaNs and generic placeholders
        df_valid = df_all.dropna(subset=[col, 'identity_number'])
        df_valid[col] = df_valid[col].astype(str).str.strip().str.lower()
        
        counts = df_valid.groupby(col).agg(
            num_people=('identity_number', 'nunique'),
            people_names=('full_name', lambda x: list(x.unique())),
            ids=('identity_number', lambda x: list(x.unique()))
        ).reset_index()

        syndicates = counts[counts['num_people'] > 1].sort_values(by='num_people', ascending=False)
        
        linked_report += f"## 1. Dùng chung {label}\n"
        if not syndicates.empty:
            linked_report += f"Phát hiện **{len(syndicates)} {label}** được sử dụng bởi từ 2 người trở lên.\n\n"
            linked_report += f"| {label} | Số người dùng | Danh sách Họ tên |\n"
            linked_report += "| :--- | :--- | :--- |\n"
            for _, row in syndicates.head(10).iterrows():
                linked_report += f"| `{row[col]}` | {row['num_people']} | {', '.join(row['people_names'])} |\n"
            linked_report += "\n"
            # Save full list
            syndicates.to_csv(os.path.join(r'D:\desktop_folder\04_Fraud_Detection\report', f'syndicate_by_{col}.csv'), index=False, encoding='utf-8-sig')
        else:
            linked_report += "Không phát hiện trường hợp dùng chung.\n\n"

    # 2. Save Final Linked Report
    with open(r'D:\desktop_folder\04_Fraud_Detection\report\syndicate_report.md', 'w', encoding='utf-8') as f:
        f.write(linked_report)
    
    print("Link analysis completed.")

if __name__ == "__main__":
    perform_link_analysis()
