import pandas as pd
import os

files = [
    r'D:\desktop_folder\04_Fraud_Detection\Hồ sơ nghi ngờ trục lợi(List khám nhiều lần).csv',
    r'D:\desktop_folder\04_Fraud_Detection\Hồ sơ nghi ngờ trục lợi(Phát hiện trục lợi đã gặp).csv',
    r'D:\desktop_folder\04_Fraud_Detection\Hồ sơ nghi ngờ trục lợi(Sheet1).csv',
    r'D:\desktop_folder\04_Fraud_Detection\Hồ sơ nghi ngờ trục lợi.xlsx'
]

output_file = r'D:\desktop_folder\04_Fraud_Detection\fraud_mining_summary.txt'

with open(output_file, 'w', encoding='utf-8') as out:
    for f in files:
        out.write(f"\n{'='*20}\nFILE: {os.path.basename(f)}\n{'='*20}\n")
        try:
            if f.endswith('.xlsx'):
                xl = pd.ExcelFile(f)
                out.write(f"Sheets: {xl.sheet_names}\n")
                for sheet in xl.sheet_names:
                    df = pd.read_excel(f, sheet_name=sheet)
                    out.write(f"\nSheet [{sheet}] Columns: {df.columns.tolist()}\n")
                    out.write(f"Sample Data:\n{df.head(10).to_string()}\n")
            else:
                # Try common encodings
                for enc in ['utf-8', 'utf-16', 'latin-1', 'utf-8-sig']:
                    try:
                        df = pd.read_csv(f, encoding=enc)
                        out.write(f"Encoding used: {enc}\n")
                        out.write(f"Columns: {df.columns.tolist()}\n")
                        out.write(f"Sample Data:\n{df.head(20).to_string()}\n")
                        break
                    except:
                        continue
        except Exception as e:
            out.write(f"Error reading file: {str(e)}\n")

print(f"Summary written to {output_file}")
