import pandas as pd
import glob
import os

processed_dir = r'D:\desktop_folder\04_Fraud_Detection\report\processed'

def debug_notes_content():
    files = glob.glob(os.path.join(processed_dir, 'processed_*.csv'))
    for f in files:
        df = pd.read_csv(f, nrows=100)
        basename = os.path.basename(f)
        print(f"--- File: {basename} ---")
        
        # Check all string columns for potentially long text
        for col in df.columns:
            if df[col].dtype == 'object':
                avg_len = df[col].astype(str).str.len().mean()
                if avg_len > 10:
                    print(f"Potential Narrative Column: {col} (Avg Len: {avg_len:.1f})")
                    print(f"Sample: {df[col].dropna().iloc[0:2].tolist()}\n")

if __name__ == "__main__":
    debug_notes_content()
