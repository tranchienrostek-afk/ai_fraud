import pandas as pd
import os

excel_path = r'D:\desktop_folder\04_Fraud_Detection\AI-Fraud-FeatureSchema.xlsx'
output_base_dir = r'D:\desktop_folder\04_Fraud_Detection\report\data_splits'

def split_excel():
    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir, exist_ok=True)
        print(f"Created output directory: {output_base_dir}")

    print(f"Loading Excel file: {excel_path} (This may take a while for ~70MB)...")
    try:
        # Load the Excel file to get all sheet names
        xl = pd.ExcelFile(excel_path, engine='openpyxl')
        sheet_names = xl.sheet_names
        print(f"Found sheets: {sheet_names}")

        for sheet in sheet_names:
            print(f"Processing sheet: {sheet}...")
            # Use chunks if memory is an issue, but 70MB should fit in RAM easily
            df = xl.parse(sheet)
            
            # Sanitize sheet name for filename
            clean_name = "".join([c if c.isalnum() else "_" for c in sheet])
            output_file = os.path.join(output_base_dir, f"{clean_name}.csv")
            
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"Exported to: {output_file}")

    except Exception as e:
        print(f"Error processing Excel: {e}")

if __name__ == "__main__":
    split_excel()
