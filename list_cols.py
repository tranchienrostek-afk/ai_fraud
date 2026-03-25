import pandas as pd
import glob
import os

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'
files = glob.glob(os.path.join(processed_dir, 'processed_*_part1.csv'))

for f in files:
    try:
        df = pd.read_csv(f, nrows=0)
        print(f"File: {os.path.basename(f)}")
        print(f"Columns: {list(df.columns)}\n")
    except Exception as e:
        print(f"Error reading {f}: {e}")
