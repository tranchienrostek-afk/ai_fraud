import pandas as pd
import glob
import os

# Paths
input_dir = r"D:\desktop_folder\04_Fraud_Detection\report\data_splits\DataNDBH_chunks"
output_report = r"D:\desktop_folder\04_Fraud_Detection\report\pre_process_data\diag_persons_results.txt"
csv_files = glob.glob(os.path.join(input_dir, "DataNDBH_part*.csv"))

results = []

def log(msg):
    print(msg)
    results.append(msg)

log(f"Loading {len(csv_files)} person files (DataNDBH)...")
# Using sample of files if too many, but 21 files is manageable for loading headers/samples
dfs = [pd.read_csv(f, encoding='utf-8-sig', nrows=10000) for f in csv_files]
df = pd.concat(dfs, ignore_index=True)

log(f"Total Records in sample: {len(df)}")

# Diagnostic on Salary
log("\n--- Salary Stats (Raw Sample) ---")
if 'salary' in df.columns:
    log(str(df['salary'].describe()))
    log("\n--- Top 10 High-Salary Persons ---")
    log(df.nlargest(10, 'salary')[['user_id', 'full_name', 'salary']].to_string())
else:
    log("Column 'salary' not found!")

# Check for Nulls
log("\n--- Null Counts (Sample) ---")
log(str(df.isnull().sum()))

# Phone and ID checks
log("\n--- ID/Phone Integrity ---")
log(f"Unique identities: {df['identity_number'].nunique()}")
log(f"Unique phones: {df['phone_number'].nunique()}")

# Gender distribution
log("\n--- Gender Distribution ---")
if 'gender' in df.columns:
    log(str(df['gender'].value_counts()))

# Write to file
with open(output_report, "w", encoding='utf-8-sig') as f:
    f.write("\n".join(results))

log(f"\nDiagnostic results written to: {output_report}")
