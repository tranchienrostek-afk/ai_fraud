import pandas as pd
import glob
import os
import sys

# Set encoding for stdout to handle Vietnamese characters if needed (for direct printing)
# sys.stdout.reconfigure(encoding='utf-8')

# Paths
input_dir = r"D:\desktop_folder\04_Fraud_Detection\report\data_splits\DataHoSoBoiThuong_chunks"
output_report = r"D:\desktop_folder\04_Fraud_Detection\report\pre_process_data\diag_claims_results.txt"
csv_files = glob.glob(os.path.join(input_dir, "DataHoSoBoiThuong_part*.csv"))

results = []

def log(msg):
    print(msg)
    results.append(msg)

log(f"Loading {len(csv_files)} files...")
# Use utf-8-sig to handle BOM and Vietnamese characters correctly
dfs = [pd.read_csv(f, encoding='utf-8-sig') for f in csv_files]
df = pd.concat(dfs, ignore_index=True)

log(f"Total Records: {len(df)}")

# Financial Stats
log("\n--- Financial Stats (Raw) ---")
stats = df[['claim_amount_req', 'claim_amount_approved']].describe()
log(str(stats))

log("\n--- Top 10 High-Value Claims (Approved) ---")
cols = ['claim_id', 'icd_name_primary', 'claim_amount_approved']
top_claims = df.nlargest(10, 'claim_amount_approved')[cols]
log(top_claims.to_string())

# Check for ICD Issues
log("\n--- Top 10 ICD Names ---")
top_icd = df['icd_name_primary'].value_counts().head(10)
log(str(top_icd))

# Check for Nulls
log("\n--- Null Counts ---")
nulls = df.isnull().sum()
log(str(nulls[nulls > 0]))

# Categories distribution
log("\n--- Claim Type Distribution ---")
log(str(df['claim_type'].value_counts()))

log("\n--- Claim Status Distribution ---")
log(str(df['claim_status'].value_counts()))

# Write all results to file with correct encoding
with open(output_report, "w", encoding='utf-8-sig') as f:
    f.write("\n".join(results))

log(f"\nDiagnostic results written to: {output_report}")
