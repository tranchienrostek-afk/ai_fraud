import pandas as pd

raw_path = r'D:\desktop_folder\04_Fraud_Detection\report\data_splits\DataHoSoBoiThuong_chunks\DataHoSoBoiThuong_part1.csv'
clean_path = r'D:\desktop_folder\04_Fraud_Detection\report\cleaned_data_final\DataHoSoBoiThuong_Cleaned_Final.csv'

raw = pd.read_csv(raw_path, encoding='utf-8-sig')
clean = pd.read_csv(clean_path, encoding='utf-8-sig')

# Find a claim with non-null values for all fields
sub = raw[raw['claim_amount_approved'].notnull() & (raw['claim_amount_approved'] > 0)]
if sub.empty:
    print("No valid claims found.")
else:
    cid = sub.iloc[0]['claim_id']
    r = raw[raw['claim_id'] == cid].iloc[0]
    c = clean[clean['claim_id'] == cid].iloc[0]
    
    print(f"VERIFYING CLAIM ID: {cid}")
    print(f"  Field           | Raw Value      | Cleaned Value  | Ratio (Raw/Clean)")
    print(f"  ----------------|----------------|----------------|------------------")
    
    fields = ['claim_amount_req', 'claim_amount_approved', 'claim_amount_vien_phi']
    for f in fields:
        rv = r[f] if f in r else 0
        cv = c[f] if f in c else 0
        ratio = rv / cv if cv != 0 else 0
        print(f"  {f[:15]:<15} | {rv:>14,.0f} | {cv:>14,.0f} | {ratio:>16.2f}")
