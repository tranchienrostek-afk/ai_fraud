from neo4j import GraphDatabase
import pandas as pd
import glob
import os

# Config from USER
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"  # Default user
NEO4J_PASSWORD = "Chien@2022"
NEO4J_DB = "neo4j" # Default db, user mentioned name=ai_fraud, might be the db name
BASE_DIR = r"D:\desktop_folder\04_Fraud_Detection\report\data_splits"

class Neo4jMigrator:
    def __init__(self, uri, user, password, database="neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.db = database

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session(database=self.db) as session:
            session.run(query, parameters)

    def setup_constraints(self):
        print(f"Setting up constraints in database '{self.db}'...")
        queries = [
            "CREATE CONSTRAINT p_uid IF NOT EXISTS FOR (p:Person) REQUIRE p.user_id IS UNIQUE",
            "CREATE CONSTRAINT c_cid IF NOT EXISTS FOR (c:Claim) REQUIRE c.claim_id IS UNIQUE",
            "CREATE CONSTRAINT h_hcode IF NOT EXISTS FOR (h:Hospital) REQUIRE h.hospital_code IS UNIQUE",
            "CREATE CONSTRAINT i_iid IF NOT EXISTS FOR (i:Insurer) REQUIRE i.insurer_id IS UNIQUE",
            "CREATE CONSTRAINT b_acc IF NOT EXISTS FOR (b:Bank) REQUIRE b.account_number IS UNIQUE",
            "CREATE CONSTRAINT d_name IF NOT EXISTS FOR (d:Doctor) REQUIRE d.name IS UNIQUE"
        ]
        for q in queries:
            try:
                self.run_query(q)
            except Exception as e:
                print(f"Constraint info: {e}")

    def load_persons(self):
        print("Loading Persons...")
        files = glob.glob(os.path.join(BASE_DIR, "DataNDBH_chunks", "*.csv"))
        for f in files:
            print(f"Processing {os.path.basename(f)}...")
            df = pd.read_csv(f)
            # Ensure salary is numeric and scale by 100
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
        print("Loading Claims and linking entities...")
        files = glob.glob(os.path.join(BASE_DIR, "DataHoSoBoiThuong_chunks", "*.csv"))
        for f in files:
            print(f"Processing {os.path.basename(f)}...")
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
            
            // Link to Doctor
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
        print("Loading Expenses...")
        files = glob.glob(os.path.join(BASE_DIR, "DataChiPhi_chunks", "*.csv"))
        for f in files:
            print(f"Processing {os.path.basename(f)}...")
            df = pd.read_csv(f)
            # Map CSV columns to Neo4j properties
            df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce') / 100.0
            df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
            
            # Derived Unit Price Logic (Total / Qty)
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
    # The user said name=ai_fraud, pass=Chien@2022. 
    # Usually username is neo4j. I will try neo4j/Chien@2022 first.
    # If the user meant username is ai_fraud, I will try that if it fails.
    
    # Trying with db='neo4j' as primary, but if user specifically has a db named 'ai_fraud'
    # I'll check common names.
    
    db_name = "neo4j" # Default
    # If user meant 'ai_fraud' is the database name
    # migrator = Neo4jMigrator(NEO4J_URI, "neo4j", "Chien@2022", database="ai_fraud")
    
    migrator = Neo4jMigrator(NEO4J_URI, "neo4j", "Chien@2022", database=db_name)
    try:
        migrator.setup_constraints()
        migrator.load_persons()
        migrator.load_claims_and_entities()
        migrator.load_expenses()
    except Exception as e:
        print(f"Migration error: {e}")
        print("Retrying with username 'ai_fraud'...")
        migrator.close()
        migrator = Neo4jMigrator(NEO4J_URI, "ai_fraud", "Chien@2022", database="neo4j")
        migrator.setup_constraints()
        migrator.load_persons()
        migrator.load_claims_and_entities()
        migrator.load_expenses()
    
    migrator.close()
    print("Graph migration completed.")
