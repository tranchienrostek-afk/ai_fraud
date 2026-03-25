from neo4j import GraphDatabase
import pandas as pd
import os

# Config
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Chien@2022"

class GraphAnalyzer:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            return pd.DataFrame([dict(record) for record in result])

    def analyze_syndicates(self):
        print("Analyzing Bank Account Syndicates...")
        query = """
        MATCH (p:Person)-[:SUBMITTED]->(c:Claim)-[:PAID_TO]->(b:Bank)
        WITH b, collect(DISTINCT p.user_id) as users, collect(DISTINCT p.full_name) as names
        WHERE size(users) > 5
        RETURN b.account_number as bank_account, b.beneficiary_name as owner_name, 
               size(users) as member_count, names[0..5] as sample_members
        ORDER BY member_count DESC
        """
        return self.run_query(query)

    def analyze_doctor_collusion(self):
        print("Analyzing Doctor-Hospital Concentrations...")
        query = """
        MATCH (d:Doctor)<-[:EXAMINED_BY]-(c:Claim)-[:TREATED_AT]->(h:Hospital)
        WITH d, h, count(c) as total_claims, sum(c.amount) as total_amount
        WHERE total_claims > 20
        RETURN d.name as doctor, h.hospital_code as hospital, total_claims, total_amount
        ORDER BY total_claims DESC
        """
        return self.run_query(query)

    def analyze_pii_sharing(self):
        print("Analyzing Shared Phone/Email Clusters...")
        # Since Phone/Email are attributes, we group by them
        query_phone = """
        MATCH (p:Person)
        WHERE p.phone_number IS NOT NULL AND p.phone_number <> '0' AND p.phone_number <> '123456789'
        WITH p.phone_number as phone, collect(p.full_name) as names, count(p) as count
        WHERE count > 2
        RETURN phone, count as shared_by_count, names[0..5] as sample_names
        ORDER BY count DESC
        """
        return self.run_query(query_phone)

if __name__ == "__main__":
    analyzer = GraphAnalyzer(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    syndicates = analyzer.analyze_syndicates()
    doctors = analyzer.analyze_doctor_collusion()
    pii = analyzer.analyze_pii_sharing()
    
    # Save results
    report_path = r'D:\desktop_folder\04_Fraud_Detection\report\graph_fraud_discovery.md'
    md = "# Báo cáo Khai phá Đồ thị (Neo4j Graph Fraud Discovery)\n\n"
    
    md += "## 1. Nhóm Dùng chung Tài khoản Ngân hàng (Bank Syndicates)\n"
    md += f"Phát hiện **{len(syndicates)} nhóm** quy mô lớn (trên 5 người/STK).\n\n"
    md += "| STK | Chủ tài khoản | Số người dùng chung | Mẫu tên hội viên |\n"
    md += "| :--- | :--- | :--- | :--- |\n"
    for _, row in syndicates.head(15).iterrows():
        md += f"| `{row['bank_account']}` | {row['owner_name']} | **{row['member_count']}** | {', '.join(row['sample_members'])}... |\n"
    
    md += "\n## 2. Các Cụm liên kết Bác sĩ - Bệnh viện nghi ngờ\n"
    md += "Truy vết các bác sĩ có tần suất ký hồ sơ bồi thường cao bất thường tại các bệnh viện cụ thể.\n\n"
    md += "| Bác sĩ | Mã Bệnh viện | Số hồ sơ | Tổng tiền (VNĐ) |\n"
    md += "| :--- | :--- | :--- | :--- |\n"
    for _, row in doctors.head(15).iterrows():
        md += f"| {row['doctor']} | {row['hospital']} | {row['total_claims']} | {row['total_amount']:,.0f} |\n"
        
    md += "\n## 3. Nhóm Dùng chung PII (Số điện thoại/Email)\n"
    md += "| Số điện thoại | Số người dùng chung | Mẫu tên |\n"
    md += "| :--- | :--- | :--- | :--- |\n"
    for _, row in pii.head(10).iterrows():
        md += f"| `{row['phone']}` | {row['shared_by_count']} | {', '.join(row['sample_names'])}... |\n"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(md)
    
    analyzer.close()
    print("Graph analysis completed.")
