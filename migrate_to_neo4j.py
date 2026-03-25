from neo4j import GraphDatabase
import pandas as pd
import glob
import os

# Config
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"
BASE_DIR = r"D:\desktop_folder\04_Fraud_Detection\report\data_splits"

class Neo4jMigrator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            session.run(query, parameters)

    def setup_constraints(self):
        print("Setting up constraints...")
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.user_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Claim) REQUIRE c.claim_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (h:Hospital) REQUIRE h.hospital_code IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Insurer) REQUIRE i.insurer_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (b:Bank) REQUIRE b.account_number IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Doctor) REQUIRE d.name IS UNIQUE"
        ]
        for q in queries:
            try: self.run_query(q)
            except: print(f"Constraint error (likely already exists): {q}")

    def load_persons(self):
        print("Loading Persons and Contract Info...")
        files = glob.glob(os.path.join(BASE_DIR, "DataNDBH_chunks", "*.csv"))
        for f in files:
            df = pd.read_csv(f)
            # Scale salary by 100
            df['salary'] = pd.to_numeric(df['salary'], errors='coerce') / 100.0
            
            query = """
            UNWIND $rows AS row
            MERGE (p:Person {user_id: row.user_id})
            SET p.identity_number = row.identity_number,
                p.full_name = row.full_name,
                p.phone_number = row.phone_number,
                p.email = row.email,
                p.salary = row.salary,
                p.contract_level = row.contract_level
            """
            self.run_query(query, {"rows": df.where(pd.notnull(df), None).to_dict('records')})

    def load_claims_and_entities(self):
        print("Loading Claims and linking Doctors/Hospitals/Banks...")
        files = glob.glob(os.path.join(BASE_DIR, "DataHoSoBoiThuong_chunks", "*.csv"))
        for f in files:
            df = pd.read_csv(f)
            # Scale claim amounts by 100
            df['claim_amount_approved'] = pd.to_numeric(df['claim_amount_approved'], errors='coerce') / 100.0
            
            query = """
            UNWIND $rows AS row
            MERGE (c:Claim {claim_id: row.claim_id})
            SET c.claim_date = row.claim_date,
                c.amount = row.claim_amount_approved,
                c.visit_type = row.visit_type,
                c.diagnosis = row.icd_name_primary
            
            // Link to Person
            WITH c, row
            MATCH (p:Person {user_id: row.user_id})
            MERGE (p)-[:SUBMITTED]->(c)
            
            // Link to Doctor (Examining Physician)
            WITH c, row
            WHERE row.doctor_name_exam IS NOT NULL
            MERGE (d:Doctor {name: row.doctor_name_exam})
            MERGE (c)-[:EXAMINED_BY]->(d)
            
            // Link to Hospital
            WITH c, row
            WHERE row.hospital_code IS NOT NULL
            MERGE (h:Hospital {hospital_code: row.hospital_code})
            MERGE (c)-[:TREATED_AT]->(h)
            
            // Link to Insurer
            WITH c, row
            WHERE row.insurer_id IS NOT NULL
            MERGE (i:Insurer {insurer_id: row.insurer_id})
            MERGE (c)-[:HANDLED_BY]->(i)
            
            // Link to Bank
            WITH c, row
            WHERE row.beneficiary_account IS NOT NULL
            MERGE (b:Bank {account_number: row.beneficiary_account})
            ON CREATE SET b.beneficiary_name = row.beneficiary_name
            MERGE (c)-[:PAID_TO]->(b)
            """
            self.run_query(query, {"rows": df.where(pd.notnull(df), None).to_dict('records')})

    def load_expenses(self):
        print("Loading Expenses (linking to claims)...")
        files = glob.glob(os.path.join(BASE_DIR, "DataChiPhi_chunks", "*.csv"))
        for f in files:
            df = pd.read_csv(f)
            # Map CSV columns and scale
            df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce') / 100.0
            df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
            
            # Derived Unit Price Logic
            df['unit_price'] = df.apply(
                lambda row: row['total_amount'] / row['quantity'] if (pd.notnull(row['quantity']) and row['quantity'] > 0) else row['total_amount'],
                axis=1
            )
            
            query = """
            UNWIND $rows AS row
            MATCH (c:Claim {claim_id: row.claim_id})
            CREATE (e:Expense {
                item_name: row.drug_or_service_name,
                category: row.category,
                item_type: row.item_type,
                unit_price: row.unit_price,
                amount: row.total_amount,
                quantity: row.quantity,
                unit: row.unit
            })
            CREATE (c)-[:HAS_EXPENSE]->(e)
            """
            self.run_query(query, {"rows": df.where(pd.notnull(df), None).to_dict('records')})

if __name__ == "__main__":
    # Ensure Docker/Neo4j is up before running
    migrator = Neo4jMigrator(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    migrator.setup_constraints()
    migrator.load_persons()
    migrator.load_claims_and_entities()
    migrator.load_expenses()
    migrator.close()
    print("Graph migration completed successfully.")
