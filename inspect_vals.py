import pandas as pd
import glob
import os

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'

def inspect_vals(file_name, columns):
    path = os.path.join(processed_dir, file_name)
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"--- {file_name} ---")
        for col in columns:
            if col in df.columns:
                print(f"Unique values in {col}: {df[col].unique()}")

inspect_vals('processed_DataHoSoBoiThuong_part1.csv', ['claim_type', 'visit_type', 'claim_status', 'approval_status'])
inspect_vals('processed_DataChiPhi_part1.csv', ['item_type', 'category'])
