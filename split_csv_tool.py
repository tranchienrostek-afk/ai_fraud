import pandas as pd
import os
import math

# Paths
source_dir = r"D:\desktop_folder\04_Fraud_Detection\report\data_splits"
MAX_SIZE_MB = 5
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

def split_csv_file(file_path):
    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]
    file_size = os.path.getsize(file_path)
    
    if file_size <= MAX_SIZE_BYTES:
        return

    print(f"Splitting {file_name} ({file_size / (1024*1024):.2f} MB)...")
    
    # Create subfolder for chunks
    subfolder = os.path.join(source_dir, f"{base_name}_chunks")
    os.makedirs(subfolder, exist_ok=True)

    # Read the file
    df = pd.read_csv(file_path)
    
    # Estimate rows per 5MB
    num_rows = len(df)
    bytes_per_row = file_size / num_rows
    rows_per_chunk = math.floor(MAX_SIZE_BYTES / bytes_per_row)
    
    # Adjust rows_per_chunk down slightly to be safe with header size
    rows_per_chunk = max(1, int(rows_per_chunk * 0.95))
    
    num_chunks = math.ceil(num_rows / rows_per_chunk)
    print(f"Planned chunks: {num_chunks} (approx {rows_per_chunk} rows each)")

    for i in range(num_chunks):
        start_row = i * rows_per_chunk
        end_row = min((i + 1) * rows_per_chunk, num_rows)
        chunk_df = df.iloc[start_row:end_row]
        
        chunk_name = f"{base_name}_part{i+1}.csv"
        chunk_path = os.path.join(subfolder, chunk_name)
        
        # Save chunk
        chunk_df.to_csv(chunk_path, index=False, encoding='utf-8-sig')
        actual_size = os.path.getsize(chunk_path)
        print(f"  Created {chunk_name} - {actual_size / (1024*1024):.2f} MB")

def main():
    files = [f for f in os.listdir(source_dir) if f.endswith('.csv') and os.path.isfile(os.path.join(source_dir, f))]
    for f in files:
        split_csv_file(os.path.join(source_dir, f))
    print("All tasks completed.")

if __name__ == "__main__":
    main()
