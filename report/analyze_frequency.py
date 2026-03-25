import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# Paths
PROCESSED_DIR = r"D:\desktop_folder\04_Fraud_Detection\report\processed"
REPORT_DIR = r"D:\desktop_folder\04_Fraud_Detection\report"
MEDIA_DIR = r"D:\desktop_folder\04_Fraud_Detection\report\media"

def analyze_frequency():
    files = glob.glob(os.path.join(PROCESSED_DIR, "processed_*.csv"))
    if not files:
        print("No processed files found.")
        return

    print(f"Aggregating user frequencies from {len(files)} files...")
    all_user_ids = []
    
    for f in files:
        try:
            df_head = pd.read_csv(f, nrows=0)
            col_to_use = None
            if 'user_id' in df_head.columns:
                col_to_use = 'user_id'
            elif 'identity_number' in df_head.columns:
                col_to_use = 'identity_number'
                
            if col_to_use:
                df = pd.read_csv(f, usecols=[col_to_use])
                all_user_ids.append(df[col_to_use])
        except Exception as e:
            print(f"Error reading {f}: {e}")

    if not all_user_ids:
        print("No user data found.")
        return

    combined_users = pd.concat(all_user_ids)
    # Step 1: count claims per user_id
    user_counts_series = combined_users.value_counts()
    
    # Step 2: count frequencies of those counts (Clustering)
    # This gives: index = number of claims, value = number of users
    freq_series = user_counts_series.value_counts().sort_index()
    
    # Create DataFrame manually to avoid reset_index() naming issues
    freq_dist = pd.DataFrame({
        'Claims_per_User': freq_series.index,
        'Num_Users': freq_series.values
    })
    
    # Save CSV
    freq_dist.to_csv(os.path.join(REPORT_DIR, "claim_frequency_stats.csv"), index=False, encoding='utf-8-sig')
    
    # Charts
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 6))
    
    viz_df = freq_dist.copy()
    max_threshold = 10
    mask = viz_df['Claims_per_User'] > max_threshold
    
    if mask.any():
        plus_count = viz_df.loc[mask, 'Num_Users'].sum()
        viz_df = viz_df[viz_df['Claims_per_User'] <= max_threshold].copy()
        viz_df['Claims_per_User_Str'] = viz_df['Claims_per_User'].astype(str)
        # Add new row using explicit column list
        final_viz = pd.concat([
            viz_df[['Claims_per_User_Str', 'Num_Users']], 
            pd.DataFrame([{'Claims_per_User_Str': f'{max_threshold}+', 'Num_Users': plus_count}])
        ], ignore_index=True)
    else:
        viz_df['Claims_per_User_Str'] = viz_df['Claims_per_User'].astype(str)
        final_viz = viz_df[['Claims_per_User_Str', 'Num_Users']]

    ax = sns.barplot(x="Claims_per_User_Str", y="Num_Users", data=final_viz, palette="magma", hue="Claims_per_User_Str", legend=False)
    plt.title("Phân loại Người dùng theo Tần suất Bồi thường (Frequency Clusters)", fontsize=16, fontweight='bold')
    plt.xlabel("Số lần bồi thường (Claims)", fontsize=12)
    plt.ylabel("Số lượng Người dùng (Number of Users)", fontsize=12)
    
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height()):,}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', xytext=(0, 9), textcoords='offset points')

    plt.tight_layout()
    chart_filename = "claim_frequency_chart.png"
    chart_path = os.path.join(MEDIA_DIR, chart_filename)
    plt.savefig(chart_path, dpi=300)
    
    # Markdown Report
    image_uri = f"file:///D:/desktop_folder/04_Fraud_Detection/report/media/{chart_filename}"
    md_content = "# Báo cáo Tần suất Bồi thường (Claim Frequency Report)\n\n"
    md_content += f"![Biểu đồ tần suất]({image_uri})\n\n"
    md_content += "## Phân loại Cụm (Clusters)\n"
    md_content += "| Tần suất (Số lần/Người) | Số lượng Người | Tỷ lệ (%) |\n"
    md_content += "| :--- | :--- | :--- |\n"
    
    total_users = freq_dist['Num_Users'].sum()
    for _, row in freq_dist.iterrows():
        pct = (row['Num_Users'] / total_users * 100).round(2)
        md_content += f"| **{row['Claims_per_User']} lần** | {row['Num_Users']:,} | {pct}% |\n"
    
    md_content += f"\n**Tổng số định danh duy nhất:** {total_users:,} người dùng.\n"
    
    with open(os.path.join(REPORT_DIR, "claim_frequency_report.md"), "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print("Frequency clusters analysis completed.")

if __name__ == "__main__":
    analyze_frequency()
