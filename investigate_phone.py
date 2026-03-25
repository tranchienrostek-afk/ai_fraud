from neo4j import GraphDatabase
import pandas as pd
import os

# Config
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Chien@2022"

def get_claims_by_phone_robust(phone_pattern):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    # Use CONTAINS to handle cases like "985048243.0" or "0985048243"
    query = """
    MATCH (p:Person)-[r:SUBMITTED]->(c:Claim)
    WHERE p.phone_number CONTAINS $phone
    OPTIONAL MATCH (c)-[:TREATED_AT]->(h:Hospital)
    OPTIONAL MATCH (c)-[:EXAMINED_BY]->(d:Doctor)
    RETURN p.full_name as user_name, p.user_id as user_id, p.phone_number as phone,
           c.claim_id as claim_id, c.claim_date as date, 
           c.amount as amount, c.diagnosis as diagnosis, 
           h.hospital_code as hospital, d.name as doctor
    ORDER BY date DESC
    """
    
    with driver.session() as session:
        result = session.run(query, {"phone": phone_pattern})
        df = pd.DataFrame([dict(record) for record in result])
    
    driver.close()
    return df

if __name__ == "__main__":
    target_phone = "985048243" # Use substring to be safe
    df_results = get_claims_by_phone_robust(target_phone)
    
    if not df_results.empty:
        output_path = r'D:\desktop_folder\04_Fraud_Detection\report\claims_by_suspicious_phone.csv'
        df_results.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        md_report = f"# Kết quả Truy vết: Các hồ sơ liên quan đến Số ĐT {target_phone}\n\n"
        md_report += f"Phát hiện **{len(df_results)} hồ sơ bồi thường** liên quan đến số điện thoại này từ **{df_results['user_id'].nunique()} khách hàng** khác nhau.\n\n"
        md_report += "## Danh sách Hồ sơ (Tổng hợp chi tiết)\n"
        md_report += "| Khách hàng | SĐT trên Hệ thống | Ngày Claim | Số tiền (VNĐ) | Chẩn đoán | Bệnh viện |\n"
        md_report += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        
        # Show more if needed, but MD has limits
        for _, row in df_results.head(50).iterrows():
            md_report += f"| {row['user_name']} | `{row['phone']}` | {row['date']} | {row['amount']:,.0f} | {row['diagnosis']} | {row['hospital']} |\n"
            
        md_report += f"\n\n*Xem toàn bộ danh sách tại: [claims_by_suspicious_phone.csv](file:///{output_path.replace(os.sep, '/')})*"
        
        with open(r'D:\desktop_folder\04_Fraud_Detection\report\phone_investigation_result.md', 'w', encoding='utf-8') as f:
            f.write(md_report)
        print(f"Investigation completed. Found {len(df_results)} claims.")
    else:
        print("No claims found for this phone number pattern.")
