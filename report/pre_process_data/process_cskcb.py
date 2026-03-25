import json
import pandas as pd
import os

# Paths
input_path = r"D:\desktop_folder\04_Fraud_Detection\report\data_splits\cskcb.json"
export_dir = r"D:\desktop_folder\04_Fraud_Detection\report\cleaned_data_final"
output_csv = os.path.join(export_dir, "CSKCB_Cleaned_Final.csv")

if not os.path.exists(export_dir):
    os.makedirs(export_dir)

print(f"Loading {input_path}...")
with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract relevant fields
records = []
for item in data:
    records.append({
        'hospital_code': str(item.get('maCskcb') or '').strip(),
        'hospital_name': str(item.get('label') or '').strip(),
        'hospital_address': str(item.get('diachi') or '').strip(),
        'hospital_id': str(item.get('id') or '').strip()
    })

df = pd.DataFrame(records)

# 1. Basic Cleaning
# Remove entries with empty codes
initial_count = len(df)
df = df[df['hospital_code'] != '']
dropped_empty = initial_count - len(df)

# Drop duplicates based on code (keep first)
df = df.drop_duplicates(subset=['hospital_code'], keep='first')
final_count = len(df)

print(f"Initial records: {initial_count}")
print(f"Dropped empty codes: {dropped_empty}")
print(f"Unique hospital codes: {final_count}")

# 2. Export
df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"Exported cleaned mapping to {output_csv}")

# 3. Quick Stats for Report
with open(os.path.join(r"D:\desktop_folder\04_Fraud_Detection\report\pre_process_data", "solution_cskcb.md"), "w", encoding='utf-8-sig') as f:
    f.write("# Báo cáo Chuẩn hóa Danh mục Cơ sở Y tế (CSKCB Mapping)\n\n")
    f.write(f"Dữ liệu này được trích xuất từ `cskcb.json` để phục vụ việc giải mã các mã cơ sở y tế trong các báo cáo bồi thường và chi phí.\n\n")
    f.write(f"## 1. Kết quả xử lý\n\n")
    f.write(f"- **Tổng số cơ sở y tế:** {final_count:,} cơ sở.\n")
    f.write(f"- **Định dạng đầu ra:** CSV (UTF-8 with BOM) để đọc trực tiếp trên Excel.\n")
    f.write(f"- **Các trường thông tin:** `hospital_code`, `hospital_name`, `hospital_address`.\n\n")
    f.write(f"## 2. Mẫu dữ liệu (Top 5)\n\n")
    
    sample = df.head(5)
    f.write("| Mã CSKCB | Tên Cơ sở | Địa chỉ |\n")
    f.write("| :--- | :--- | :--- |\n")
    for _, row in sample.iterrows():
        f.write(f"| {row['hospital_code']} | {row['hospital_name']} | {row['hospital_address']} |\n")

print("Diagnostic document created.")
