import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Paths
cleaned_csv = r"D:\desktop_folder\04_Fraud_Detection\report\cleaned_data_final\DataChiPhi_Cleaned_Final.csv"
output_dir = r"D:\desktop_folder\04_Fraud_Detection\report\pre_process_data\charts"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load data
df = pd.read_csv(cleaned_csv)

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans' # Safe for most environments

# 1. Unit Price Distribution (Log Scale)
plt.figure(figsize=(10, 6))
sns.histplot(df['unit_price'], kde=True, bins=50, log_scale=True, color='skyblue')
plt.title('Phân bổ Đơn giá (Unit Price Distribution - Log Scale)', fontsize=14)
plt.xlabel('Đơn giá (VND - Log Scale)', fontsize=12)
plt.ylabel('Tần suất (Count)', fontsize=12)
plt.tight_layout()
price_dist_path = os.path.join(output_dir, "unit_price_distribution.png")
plt.savefig(price_dist_path)
plt.close()

# 2. Total Amount Distribution (Log Scale)
plt.figure(figsize=(10, 6))
sns.histplot(df['total_amount'], kde=True, bins=50, log_scale=True, color='salmon')
plt.title('Phân bổ Tổng tiền (Total Amount Distribution - Log Scale)', fontsize=14)
plt.xlabel('Tổng tiền (VND - Log Scale)', fontsize=12)
plt.ylabel('Tần suất (Count)', fontsize=12)
plt.tight_layout()
total_dist_path = os.path.join(output_dir, "total_amount_distribution.png")
plt.savefig(total_dist_path)
plt.close()

# 3. Boxplot by Item Type (Top 8 types to avoid clutter)
top_types = df['item_type'].value_counts().nlargest(8).index
df_top = df[df['item_type'].isin(top_types)]

plt.figure(figsize=(12, 8))
sns.boxplot(data=df_top, x='item_type', y='unit_price', palette='viridis', hue='item_type', legend=False)
plt.yscale('log')
plt.title('So sánh dải giá theo Phân loại (Unit Price by Item Type - Log Scale)', fontsize=14)
plt.xticks(rotation=45)
plt.xlabel('Phân loại', fontsize=12)
plt.ylabel('Đơn giá (VND - Log Scale)', fontsize=12)
plt.tight_layout()
box_dist_path = os.path.join(output_dir, "category_boxplot.png")
plt.savefig(box_dist_path)
plt.close()

print(f"Charts generated successfully in: {output_dir}")
print(f"1. {price_dist_path}")
print(f"2. {total_dist_path}")
print(f"3. {box_dist_path}")
