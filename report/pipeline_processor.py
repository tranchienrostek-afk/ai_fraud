import pandas as pd
import numpy as np
import os
import glob
import json
from datetime import datetime

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPLITS_DIR = os.path.join(BASE_DIR, "data_splits")
OUTPUT_DIR = os.path.join(BASE_DIR, "processed")
LOG_FILE = os.path.join(BASE_DIR, "pipeline_execution.log")

class FraudDataPipeline:
    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self.stats = {}

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] {message}"
        print(msg)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    def z_score_normalize(self, df, columns):
        """Step 3: Feature Scaling (Z-score)"""
        for col in columns:
            if col in df.columns:
                mean = df[col].mean()
                std = df[col].std()
                if std > 0:
                    df[f"{col}_zscore"] = (df[col] - mean) / std
        return df

    def detect_outliers_iqr(self, df, column):
        """Step 3: Outlier Detection (IQR)"""
        if column not in df.columns:
            return df, 0
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        df[f"{column}_is_outlier"] = (df[column] < lower_bound) | (df[column] > upper_bound)
        return df, len(outliers)

    def process_chunk(self, file_path):
        """The 10-step inspired processor"""
        file_name = os.path.basename(file_path)
        self.log(f"Processing chunk: {file_name}")
        
        df = pd.read_csv(file_path)
        
        # 1. Cleaning: Fill missing numeric with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        
        # 2. Scaling & Outliers
        important_numeric = ['claim_amount_req', 'claim_amount_vien_phi', 'claim_amount_approved']
        found_numeric = [c for c in important_numeric if c in df.columns]
        
        df = self.z_score_normalize(df, found_numeric)
        
        total_outliers = 0
        for col in found_numeric:
            df, count = self.detect_outliers_iqr(df, col)
            total_outliers += count

        # 3. Export Processed Data
        output_path = os.path.join(OUTPUT_DIR, f"processed_{file_name}")
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        return {
            "rows": len(df),
            "outliers_detected": total_outliers,
            "processed_file": output_path
        }

    def run(self):
        self.log("Starting Automated Fraud Research Pipeline...")
        
        # Find all chunk files in all subfolders
        chunk_files = glob.glob(os.path.join(SPLITS_DIR, "**", "*.csv"), recursive=True)
        
        if not chunk_files:
            self.log("No chunk files found to process.")
            return

        summary_results = []
        for file in chunk_files:
            try:
                res = self.process_chunk(file)
                summary_results.append(res)
            except Exception as e:
                self.log(f"FAILED processing {file}: {str(e)}")

        # Final Summary Report
        total_rows = sum(r['rows'] for r in summary_results)
        total_outliers = sum(r['outliers_detected'] for r in summary_results)
        
        report = {
            "execution_date": datetime.now().isoformat(),
            "total_chunks_processed": len(summary_results),
            "total_rows_scanned": total_rows,
            "total_outliers_flagged": total_outliers,
            "algorithms_used": ["Z-score Scaling", "IQR Outlier Detection", "Median Imputation"]
        }
        
        with open(os.path.join(BASE_DIR, "pipeline_summary.json"), "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
            
        self.log("Pipeline Finished Successfully.")
        self.log(f"Total Rows: {total_rows}, Total Outliers Flagged: {total_outliers}")

if __name__ == "__main__":
    pipeline = FraudDataPipeline()
    pipeline.run()
