import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Paths
REPORT_DIR = r"D:\desktop_folder\04_Fraud_Detection\report\media"
CSV_PATH = os.path.join(r"D:\desktop_folder\04_Fraud_Detection\report", "claim_distribution.csv")

def create_charts():
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found.")
        return

    # Load data
    df = pd.read_csv(CSV_PATH)
    
    # Set visual style
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.sans-serif'] = ['Arial']
    plt.rcParams['axes.unicode_minus'] = False

    # 1. Bar Chart: Frequency by Range
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(x="Range_VND", y="Frequency", data=df, palette="viridis", hue="Range_VND", legend=False)
    
    plt.title("Phân bổ Số lượng Hồ sơ theo Khoảng Số tiền Bồi thường", fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("Khoảng Số tiền (VND)", fontsize=12)
    plt.ylabel("Số lượng Hồ sơ", fontsize=12)
    plt.xticks(rotation=45)

    # Add count labels on top of bars
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height()):,}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', 
                    xytext=(0, 9), 
                    textcoords='offset points',
                    fontsize=10,
                    fontweight='bold')

    plt.tight_layout()
    bar_chart_path = os.path.join(REPORT_DIR, "claim_distribution_bar.png")
    plt.savefig(bar_chart_path, dpi=300)
    print(f"Bar chart saved: {bar_chart_path}")

    # 2. Pie Chart: Percentage Distribution
    plt.figure(figsize=(10, 10))
    # Combine small categories for pie chart if necessary, but here we have 8, which is fine
    colors = sns.color_palette("pastel")
    plt.pie(df['Frequency'], labels=df['Range_VND'], autopct='%1.1f%%', startangle=140, colors=colors, 
            explode=[0.05 if i < 3 else 0.1 for i in range(len(df))])
    
    plt.title("Tỷ lệ % Hồ sơ theo Khoảng Số tiền", fontsize=16, fontweight='bold')
    
    pie_chart_path = os.path.join(REPORT_DIR, "claim_distribution_pie.png")
    plt.savefig(pie_chart_path, dpi=300)
    print(f"Pie chart saved: {pie_chart_path}")

if __name__ == "__main__":
    create_charts()
