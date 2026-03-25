import os

input_dir = r"D:\desktop_folder\04_Fraud_Detection\report\new_data\DataChiPhi_chunks"
output_path = r"D:\desktop_folder\04_Fraud_Detection\report\pre_process_data\global_search.txt"
targets = ["44804480", "48551019", "76124990"]

with open(output_path, "w", encoding="utf-8") as out:
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            path = os.path.join(input_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                headers = f.readline()
                for line in f:
                    for t in targets:
                        if t in line:
                            out.write(f"FILE: {filename}\n")
                            out.write(f"LINE: {line.strip()}\n")
                            out.write("-" * 20 + "\n")
print(f"Global search finished. Results in {output_path}")
