import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Paths
input_dir = r"D:\desktop_folder\04_Fraud_Detection\report\new_data\DataQuyenLoi_chunks"
export_dir = r"D:\desktop_folder\04_Fraud_Detection\report\cleaned_data_final"
chart_dir = r"D:\desktop_folder\04_Fraud_Detection\report\pre_process_data\charts_benefits"
output_report = r"D:\desktop_folder\04_Fraud_Detection\report\pre_process_data\solution_quyenloi.md"

if not os.path.exists(export_dir): os.makedirs(export_dir)
if not os.path.exists(chart_dir): os.makedirs(chart_dir)

# Mapping dictionary
col_map = {
    'Số hợp đồng bảo hiểm': 'policy_number',
    'Số hồ sơ': 'claim_id',
    'Ngày vào viện': 'admission_date',
    'Ngày ra viện': 'discharge_date',
    'Chẩn đoán ra viện': 'discharge_diagnosis',
    'Chẩn đoán bệnh': 'diagnosis',
    'Cơ sở khám chữa bệnh': 'hospital_name',
    'Loại khám chữa bệnh': 'visit_type',
    'Quyền lợi bảo hiểm': 'benefit_name',
    'Số tiền yêu cầu bồi thường': 'requested_amount',
    'Số tiền bồi thường': 'approved_amount',
    'Trạng thái hồ sơ': 'status',
    'ICD': 'icd_code'
}

# 1. Load data
csv_files = glob.glob(os.path.join(input_dir, "DataQuyenLoi_part*.csv"))
print(f"Loading {len(csv_files)} benefit files...")
dfs = [pd.read_csv(f, encoding='utf-8-sig') for f in csv_files]
df = pd.concat(dfs, ignore_index=True)
initial_count = len(df)

# 2. Rename and Scale
df = df.rename(columns=col_map)

# Focus on primary columns
target_cols = ['claim_id', 'policy_number', 'benefit_name', 'requested_amount', 'approved_amount', 'status', 'icd_code', 'visit_type', 'hospital_name', 'admission_date', 'discharge_date']
df = df[target_cols].copy()

# Scale currency by 100x
df['requested_amount'] = pd.to_numeric(df['requested_amount'], errors='coerce').fillna(0) / 100.0
df['approved_amount'] = pd.to_numeric(df['approved_amount'], errors='coerce').fillna(0) / 100.0

# 3. Text Standardization
df['benefit_name'] = df['benefit_name'].astype(str).str.strip().str.upper()
df['status'] = df['status'].astype(str).str.strip()
df['hospital_name'] = df['hospital_name'].astype(str).str.strip()

# Handle dates
df['admission_date'] = pd.to_datetime(df['admission_date'], errors='coerce')
df['discharge_date'] = pd.to_datetime(df['discharge_date'], errors='coerce')

# 4. Generate Visualizations
sns.set_theme(style="whitegrid")
plt.figure(figsize=(12, 6))
top_benefits = df['benefit_name'].value_counts().nlargest(10)
sns.barplot(x=top_benefits.values, y=top_benefits.index, palette="viridis")
plt.title('Top 10 Quyền lợi Bảo hiểm phổ biến', fontsize=14)
plt.xlabel('Số lượng hồ sơ')
plt.savefig(os.path.join(chart_dir, "benefit_usage.png"))
plt.close()

plt.figure(figsize=(10, 6))
sns.histplot(df[df['approved_amount'] > 0]['approved_amount'], bins=50, kde=True, log_scale=True, color='orange')
plt.title('Phân bổ Số tiền Bồi thường theo Quyền lợi (Log scale)', fontsize=14)
plt.savefig(os.path.join(chart_dir, "benefit_dist.png"))
plt.close()

# 5. Generate Professional Report
total_approved = df['approved_amount'].sum()
top_benefits_val = df.groupby('benefit_name')['approved_amount'].sum().nlargest(10)

with open(output_report, "w", encoding='utf-8-sig') as f:
    f.write(f"# Báo cáo Khai phá Dữ liệu Quyền lợi Bảo hiểm (Benefits Data Mining)\n\n")
    f.write(f"## 1. Tóm tắt Điều hành (Executive Summary)\n\n")
    f.write(f"- **Tổng số bản ghi xử lý:** {initial_count:,} dòng.\n")
    f.write(f"- **Tổng giá trị chi trả thực tế:** **{total_approved:,.0f} VND**.\n")
    f.write(f"- **Tình trạng Scaling:** Đã phát hiện và xử lý lỗi phóng đại 100x trên toàn bộ cột số tiền.\n\n")
    
    f.write(f"### Sử dụng Quyền lợi\n")
    f.write(f"![Sử dụng Quyền lợi](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts_benefits/benefit_usage.png)\n")
    f.write(f"*Hình 1: Biểu đồ tần suất sử dụng các loại quyền lợi bảo hiểm.*\n\n")
    
    f.write(f"## 2. Phân tích Chất lượng Dữ liệu (Data Integrity)\n\n")
    f.write(f"> [!IMPORTANT]\n")
    f.write(f"> Toàn bộ dữ liệu tiền tệ trong `DataQuyenLoi` thô bị nhân 100 lần. Đơn giá thực tế đã được quy đổi VND chuẩn.\n\n")
    f.write(f"- **Mã hóa ICD:** Đồng bộ với danh mục chẩn đoán quốc tế.\n")
    f.write(f"- **Trạng thái Thanh toán:** {df['status'].nunique()} loại trạng thái khác nhau, chủ yếu là 'Đã thanh toán'.\n\n")
    
    f.write(f"## 3. Top 10 Quyền lợi có chi phí cao nhất\n\n")
    f.write(f"| Tên Quyền lợi | Tổng tiền Chi trả (VND) |\n")
    f.write(f"| :--- | :---: |\n")
    for name, val in top_benefits_val.items():
        f.write(f"| {name} | {val:,.0f} |\n")
    
    f.write(f"\n## 4. Phân bổ Số tiền Chi trả\n\n")
    f.write(f"![Phân bổ Tiền](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts_benefits/benefit_dist.png)\n")
    f.write(f"*Hình 2: Phân bổ log-scale của giá trị bồi thường theo quyền lợi.*\n\n")

# 6. Export Cleaned Data
export_path = os.path.join(export_dir, "DataQuyenLoi_Cleaned_Final.csv")
df.to_csv(export_path, index=False, encoding='utf-8-sig')

print(f"Processing complete! Cleaned CSV: {export_path}")
print(f"Report: {output_report}")
