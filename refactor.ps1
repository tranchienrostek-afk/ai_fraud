$ErrorActionPreference = "SilentlyContinue"

Write-Host "Creating Directories..."
$dirs = @(
  "docs/architecture", "docs/references", "docs/reports",
  "data/raw", "data/logs", "data/processed", "data/master",
  "src", "src/core", "src/dashboard", "src/data_pipeline", 
  "src/database", "src/utils", "tests", "deploy"
)
foreach ($d in $dirs) { if (!(Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null } }

Write-Host "Moving Docs..."
Move-Item "agent_internal_architecture.md", "architecture_alignment.md", "system_architechture_multi_agent.md", "system_diagram.md", "workflow.md" -Destination "docs/architecture/"
Move-Item "1.-Phân-loại-hồ-sơ-xác-minh.pdf", "DIEM-ROI-TIEN.docx", "AI Fraud FeatureSchema.xlsx" -Destination "docs/references/"
Move-Item "report.md", "claude_code_datamining.md" -Destination "docs/reports/"

Write-Host "Moving Data..."
Move-Item "Hồ sơ nghi ngờ trục lợi*.csv", "Hồ sơ nghi ngờ trục lợi*.xlsx", "dm_duoc_BVHN.csv" -Destination "data/raw/"
Move-Item "*_matches*.txt", "cols_*.txt", "final_phone_investigation.txt", "fraud_mining_summary.txt", "suspicious_users*.txt" -Destination "data/logs/"

Write-Host "Moving Source Code..."
if (Test-Path "deep_research/dashboard") {
    Move-Item -Path "deep_research/dashboard/*" -Destination "src/dashboard/" -Force
}

Move-Item "analyze_*.py", "correlate_petty_fraud.py", "debug_narratives.py", "extract_users.py", "find_clones_final.py", "find_clones_robust.py", "investigate_phone.py", "mine_fraud_files.py", "reload_expenses.py" -Destination "src/data_pipeline/"

Move-Item "migrate_to_neo4j*.py", "verify_load.py" -Destination "src/database/"

Move-Item "check_*.py", "split_*.py", "list_cols.py", "inspect_vals.py", "search_id.py", "neo4j_cleanup_scaling.py" -Destination "src/utils/"

Write-Host "Moving Tests..."
if (Test-Path "report/pre_process_data") {
    Move-Item "report/pre_process_data/test_*.py" -Destination "tests/" -Force
}

Write-Host "Refactoring Script Complete"
