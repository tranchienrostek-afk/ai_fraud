import pandas as pd
import os

path = r'D:\desktop_folder\04_Fraud_Detection\report\data_splits\DataHoSoBoiThuong_chunks\DataHoSoBoiThuong_part1.csv'
df = pd.read_csv(path, encoding='utf-8-sig')

print("--- RAW DATA MAGNITUDES (VALID REQ) ---")
valid_req = df[df['claim_amount_req'].notnull()].head(20)

for i, row in valid_req.iterrows():
    req = row['claim_amount_req']
    appr = row['claim_amount_approved']
    fee = row['claim_amount_vien_phi']
    print(f"Row {i}: Req={req:,.0f} | Appr={appr:,.0f} | Fee={fee:,.0f}")
    if appr > 0:
         print(f"  -> Req/Appr Ratio: {req/appr:.2f}")
         print(f"  -> Fee/Appr Ratio: {fee/appr:.2f}")
