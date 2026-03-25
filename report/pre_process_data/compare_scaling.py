import pandas as pd
import glob
import os

c_dir = r'D:\desktop_folder\04_Fraud_Detection\report\data_splits\DataHoSoBoiThuong_chunks'
e_dir = r'D:\desktop_folder\04_Fraud_Detection\report\new_data\DataChiPhi_chunks'

c_files = glob.glob(os.path.join(c_dir, "*.csv"))
e_files = glob.glob(os.path.join(e_dir, "*.csv"))

print("Loading limited data for comparison...")
df_c = pd.concat([pd.read_csv(f, nrows=5000) for f in c_files])
df_e = pd.concat([pd.read_csv(f, nrows=5000) for f in e_files])

common = set(df_c['claim_id']).intersection(set(df_e['claim_id']))

if common:
    cid = list(common)[0]
    c_row = df_c[df_c['claim_id'] == cid][['claim_id', 'claim_amount_approved']]
    e_rows = df_e[df_e['claim_id'] == cid][['drug_or_service_name', 'total_amount']]
    
    print(f"\nComparing Case ID: {cid}")
    print("--- CLAIM HEADER (Raw) ---")
    print(c_row.to_string(index=False))
    
    print("\n--- EXPENSE ITEMS (Raw) ---")
    print(e_rows.to_string(index=False))
    
    e_sum = e_rows['total_amount'].sum()
    c_val = c_row['claim_amount_approved'].iloc[0]
    
    print(f"\nExpense Sum: {e_sum:,.0f}")
    print(f"Claim Approved: {c_val:,.0f}")
    
    if abs(e_sum - c_val) < 1.0:
        print("\nMATCH: Both are in the same scale.")
    else:
        print(f"\nMISMATCH: Ratio is {max(e_sum, c_val)/min(e_sum, c_val) if min(e_sum,c_val)>0 else 'inf'}")
else:
    print("No common IDs found in samples.")
