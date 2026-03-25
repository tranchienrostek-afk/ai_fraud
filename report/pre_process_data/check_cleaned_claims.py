import pandas as pd

path = r'D:\desktop_folder\04_Fraud_Detection\report\cleaned_data_final\DataHoSoBoiThuong_Cleaned_Final.csv'
df = pd.read_csv(path, encoding='utf-8-sig', nrows=20)

print("--- CLEANED DATA SAMPLE ---")
for i, row in df.iterrows():
    cid = str(row['claim_id'])[:8]
    req = row['claim_amount_req']
    appr = row['claim_amount_approved']
    fee = row['claim_amount_vien_phi']
    med = row['median_claim_val']
    print(f"Row {i} ({cid}...): Req={req:,.0f} | Appr={appr:,.0f} | Fee={fee:,.0f} | Med={med:,.0f}")
