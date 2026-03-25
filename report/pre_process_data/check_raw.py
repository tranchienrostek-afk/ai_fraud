import os
import glob

target = 'Zinmax 500mg'
input_dir = r'D:\desktop_folder\04_Fraud_Detection\report\new_data\DataChiPhi_chunks'

csv_files = glob.glob(os.path.join(input_dir, '*.csv'))
for path in csv_files:
    try:
        with open(path, 'r', encoding='utf-8') as file:
            headers = next(file).strip()
            for line in file:
                if target in line:
                    print(f'File: {os.path.basename(path)}')
                    print(f'Headers: {headers}')
                    print(f'Content: {line.strip()}')
                    # Print one more for variety
                    continue
    except Exception as e:
        print(f"Error reading {path}: {e}")
