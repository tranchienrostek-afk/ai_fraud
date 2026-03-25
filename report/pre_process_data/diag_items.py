import os

file_path = r'D:\desktop_folder\04_Fraud_Detection\report\new_data\DataChiPhi_chunks\DataChiPhi_part1.csv'
output_path = r'D:\desktop_folder\04_Fraud_Detection\report\pre_process_data\diag_final.txt'

targets = ['PEDIAKID', 'Perjeta']

with open(file_path, 'r', encoding='utf-8') as f:
    headers = f.readline().strip()
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(f"HEADERS: {headers}\n\n")
        for line in f:
            for t in targets:
                if t in line:
                    out.write(f"TARGET {t} FOUND:\n")
                    line_parts = line.strip().split(',')
                    for i, part in enumerate(line_parts):
                        out.write(f"  {i}: {part}\n")
                    out.write("-" * 20 + "\n")
                    break # Found one target in line, move to next line
print(f"Diagnostic output written to: {output_path}")
