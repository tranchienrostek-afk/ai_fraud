import os

file_path = r'D:\desktop_folder\04_Fraud_Detection\report\new_data\DataChiPhi_chunks\DataChiPhi_part1.csv'
output_path = r'D:\desktop_folder\04_Fraud_Detection\report\pre_process_data\diag_output.txt'
target = 'Zinmax 500mg'

with open(file_path, 'r', encoding='utf-8') as f:
    headers = f.readline().strip()
    cols = headers.split(',')
    
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(f"HEADERS: {headers}\n\n")
        for i, col in enumerate(cols):
            out.write(f"{i}: {col}\n")
        
        out.write("\nFINDING TARGETS...\n")
        count = 0
        for line in f:
            if target in line:
                out.write(f"RAW LINE: {line.strip()}\n")
                line_parts = line.strip().split(',')
                for i, part in enumerate(line_parts):
                    out.write(f"  {i}: {part}\n")
                out.write("-" * 20 + "\n")
                count += 1
                if count >= 3:
                    break
print(f"Diagnostic output written to: {output_path}")
