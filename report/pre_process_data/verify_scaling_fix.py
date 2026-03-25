import pandas as pd
import glob
import os

claims_file = r'D:\desktop_folder\04_Fraud_Detection\report\data_splits\DataHoSoBoiThuong_chunks\DataHoSoBoiThuong_part1.csv'
expenses_file = r'D:\desktop_folder\04_Fraud_Detection\report\data_splits\DataChiPhi_chunks\DataChiPhi_part1.csv'

claims = pd.read_csv(claims_file, encoding='utf-8-sig', nrows=1000)
expenses = pd.read_csv(expenses_file, encoding='utf-8-sig', nrows=10000)

common_ids = set(claims['claim_id']).intersection(set(expenses['claim_id']))

if not common_ids:
    print("No common claim_ids found in initial samples.")
else:
    cid = list(common_ids)[0]
    c_row = claims[claims['claim_id'] == cid].iloc[0]
    e_rows = expenses[expenses['claim_id'] == cid]
    e_sum = e_rows['total_amount'].sum()
    
    print(f"Checking Claim ID: {cid}")
    print(f"Raw claim_amount_req:      {c_row['claim_amount_req']:,.0f}")
    print(f"Raw claim_amount_approved: {c_row['claim_amount_approved']:,.0f}")
    print(f"Raw claim_amount_vien_phi: {c_row['claim_amount_vien_phi']:,.0f}")
    print(f"Raw total_amount (Exp):    {e_sum:,.0f}")
    
    if e_sum > 0:
        print(f"Ratio Exp Sum / Approved: {e_sum / c_row['claim_amount_approved']:.2f}")
        print(f"Ratio Exp Sum / Req:      {e_sum / c_row['claim_amount_req']:.2f}")

    print("\n--- Summary of Verification ---")
    if abs((e_sum / 100.0) - c_row['claim_amount_approved']) < 100:
        print("CONFIRMED: Expenses are 100x larger than Approved. Approved is ALREADY scaled.")
    elif abs(e_sum - c_row['claim_amount_approved']) < 100:
        print("MATCH: Expenses and Approved have the same scale.")
    else:
        print("Scaling relationship is complex.")
