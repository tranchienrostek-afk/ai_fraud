import pandas as pd
import glob
import os

input_dir = r"D:\desktop_folder\04_Fraud_Detection\report\data_splits\DataNDBH_chunks"
files = glob.glob(os.path.join(input_dir, "*.csv"))

print(f"Scanning {len(files)} files for valid data...")

total_non_null_salary = 0
total_records = 0
phone_counts = 0
identity_counts = 0

for f in files:
    # Use chunksize if files are large, but here they are around 5MB, so read_csv is fine
    df = pd.read_csv(f, encoding='utf-8-sig')
    total_records += len(df)
    if 'salary' in df.columns:
        total_non_null_salary += df['salary'].notnull().sum()
    if 'phone_number' in df.columns:
        phone_counts += df['phone_number'].notnull().sum()
    if 'identity_number' in df.columns:
        identity_counts += df['identity_number'].notnull().sum()

print(f"Total Records: {total_records}")
print(f"Total Non-null Salaries: {total_non_null_salary}")
print(f"Total Non-null Phone Numbers: {phone_counts}")
print(f"Total Non-null Identities: {identity_counts}")

if total_non_null_salary > 0:
    print("Salary data found! 100x scaling will be applicable.")
else:
    print("Salary data is entirely NULL across all chunks.")
