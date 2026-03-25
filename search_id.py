import pandas as pd
import glob
import os
import json

TARGET_ID = "1f9a218e-9866-4453-9449-e25e88a70bd5"
PROCESSED_DIR = r"D:\desktop_folder\04_Fraud_Detection\report\processed"

def extract_record():
    files = glob.glob(os.path.join(PROCESSED_DIR, "processed_*.csv"))
    results = {}

    for f in files:
        basename = os.path.basename(f)
        module_name = basename.replace("processed_", "").split("_part")[0]
        
        try:
            # Check for matches in ANY column
            # Reading in chunks or searching manually is faster for search but let's use pandas for small results
            df = pd.read_csv(f)
            # Find rows where any column contains the ID
            mask = df.apply(lambda row: row.astype(str).str.contains(TARGET_ID).any(), axis=1)
            matches = df[mask]
            
            if not matches.empty:
                if module_name not in results:
                    results[module_name] = []
                results[module_name].append(matches)
        except Exception as e:
            print(f"Error reading {f}: {e}")

    # Process and present results
    if not results:
        print(f"No records found for ID: {TARGET_ID}")
        return

    print(f"--- Results for ID: {TARGET_ID} ---")
    final_output = {}
    for module, dfs in results.items():
        combined = pd.concat(dfs)
        final_output[module] = combined.to_dict(orient='records')
        print(f"\nModule: {module} ({len(combined)} records found)")
        # Print a clean summary
        for _, row in combined.iterrows():
            print("-" * 30)
            for col, val in row.items():
                if pd.notna(val):
                    print(f"{col}: {val}")

    # Save to JSON for report
    with open(r"D:\desktop_folder\04_Fraud_Detection\report\specific_search_result.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    extract_record()
