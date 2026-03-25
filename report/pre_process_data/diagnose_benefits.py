import pandas as pd
import glob
import os
import sys

# Ensure UTF-8 output for terminal
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

input_dir = r"D:\desktop_folder\04_Fraud_Detection\report\new_data\DataQuyenLoi_chunks"
csv_files = glob.glob(os.path.join(input_dir, "DataQuyenLoi_part*.csv"))

# Correct Mapping based on raw inspection
col_map = {
    'Số hợp đồng bảo hiểm': 'policy_number',
    'ID chứng từ': 'claim_id',
    'Mã quyền lợi': 'benefit_id',
    'Tên quyền lợi': 'benefit_name',
    'Loại hạn mức': 'limit_type',
    'Hạn mức': 'benefit_limit',
    'Số tiền bồi thường': 'benefit_amount',
    'Mã phân loại ICD': 'icd_code',
    'Trạng thái hồ sơ': 'status'
}

all_dfs = []
print(f"Loading {len(csv_files)} chunks...")
for f in csv_files:
    df = pd.read_csv(f, encoding='utf-8-sig', nrows=10000)
    df = df.rename(columns=col_map)
    all_dfs.append(df)

df = pd.concat(all_dfs, ignore_index=True)

# Write output to file with explicit encoding
output_path = "diag_benefits_results.txt"
with open(output_path, "w", encoding='utf-8') as f:
    f.write("--- DataQuyenLoi Diagnostic ---\n")
    f.write(f"Sample size: {len(df)} rows\n")
    f.write("\nColumns found after mapping:\n")
    f.write(str(df.columns.tolist()) + "\n")

    f.write("\nNull Values:\n")
    f.write(str(df.isnull().sum()) + "\n")

    # Convert numeric columns
    numeric_cols = ['benefit_limit', 'benefit_amount']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            f.write(f"\n{col} Statistics:\n")
            stats = df[col].describe().apply(lambda x: format(x, 'f'))
            f.write(str(stats) + "\n")
        else:
            f.write(f"\n[ERROR] Column {col} missing!\n")

    # Check scaling for benefit_amount
    if 'benefit_amount' in df.columns:
        avg = df['benefit_amount'].mean()
        f.write(f"\nAverage Benefit Amount: {avg:,.0f} VND\n")
        if avg > 10000000: # 10M avg for a benefit is high
            f.write("[WARNING] Benefit values appear to be 100x scaled.\n")
        else:
            f.write("[OK] Benefit values appear to be in standard VND.\n")

    # Categorical distributions
    for cat_col in ['limit_type', 'status', 'benefit_name']:
        if cat_col in df.columns:
            f.write(f"\nTop 10 {cat_col}:\n")
            f.write(str(df[cat_col].value_counts().head(10)) + "\n")

print(f"Diagnostic results written to {output_path}")
