import pandas as pd
import os
import json
import sys

# Get current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, 'AI-Fraud-FeatureSchema(DataHoSoBoiThuong).csv')
report_dir = os.path.join(current_dir, 'report')

def run_analysis():
    print(f"Current Directory: {current_dir}")
    print(f"Target CSV: {csv_path}")
    print(f"Target Report Dir: {report_dir}")
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return
    
    if not os.path.exists(report_dir):
        print(f"Creating report directory at {report_dir}")
        os.makedirs(report_dir, exist_ok=True)

    print(f"Loading data...")
    try:
        # Load only 100k rows if file is too large for memory, but 11.7MB should be fine
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # 1. Summary Info
    summary = {
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": df.isnull().sum().to_dict()
    }

    # 2. Descriptive Statistics for numeric
    # Filter only numeric columns for describe
    numeric_df = df.select_dtypes(include=['number'])
    if not numeric_df.empty:
        numeric_stats = numeric_df.describe().transpose().to_dict()
        numeric_df.describe().to_csv(os.path.join(report_dir, 'numeric_stats.csv'))
    else:
        numeric_stats = {}

    # 3. Categorical distribution (Top 5 for object types)
    categorical_dist = {}
    for col in df.select_dtypes(include=['object']).columns:
        categorical_dist[col] = df[col].value_counts().head(5).to_dict()

    # Save to JSON
    with open(os.path.join(report_dir, 'data_summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

    # 4. Generate a Markdown Report
    md_content = f"# Báo cáo Khai phá Dữ liệu: AI-Fraud-FeatureSchema\n\n"
    md_content += f"## 1. Thông tin chung\n"
    md_content += f"- **Số bản ghi:** {len(df):,}\n"
    md_content += f"- **Số cột:** {len(df.columns)}\n\n"
    
    md_content += f"## 2. Danh sách cột và kiểu dữ liệu\n"
    md_content += "| Tên cột | Kiểu dữ liệu | Số giá trị thiếu |\n"
    md_content += "| :--- | :--- | :--- |\n"
    for col in df.columns:
        md_content += f"| {col} | {df[col].dtype} | {df[col].isnull().sum()} |\n"
    
    md_content += f"\n## 3. Thống kê phân phối (Top 5 giá trị phổ biến)\n"
    for col, values in categorical_dist.items():
        md_content += f"### {col}\n"
        for val, count in values.items():
            md_content += f"- {val}: {count:,}\n"
        md_content += "\n"

    with open(os.path.join(report_dir, 'analysis_report.md'), 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"Analysis complete. Reports saved in {report_dir}")

if __name__ == "__main__":
    run_analysis()
