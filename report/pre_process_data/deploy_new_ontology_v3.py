import pandas as pd
from neo4j import GraphDatabase
import numpy as np
import time
import os

# Neo4j Config
URI = "bolt://127.0.0.1:7687"
USER = "neo4j"
PASS = "Chien@2022"
DB = "neo4j"

# Data Paths
CLEANED_DIR = r"D:\desktop_folder\04_Fraud_Detection\report\cleaned_data_final"
PERSONS_FILE = os.path.join(CLEANED_DIR, "DataNDBH_Cleaned_Final.csv")
CLAIMS_FILE = os.path.join(CLEANED_DIR, "DataHoSoBoiThuong_Cleaned_Final.csv")
EXPENSES_FILE = os.path.join(CLEANED_DIR, "DataChiPhi_Cleaned_Final.csv")
BENEFITS_FILE = os.path.join(CLEANED_DIR, "DataQuyenLoi_Cleaned_Final.csv")
HOSPITALS_FILE = os.path.join(CLEANED_DIR, "CSKCB_Cleaned_Final.csv")

def migrate():
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    
    with driver.session(database=DB) as session:
        # 1. Create Constraints and Indexes
        print("Creating Constraints and Indexes...")
        constraints = [
            "CREATE CONSTRAINT person_uid IF NOT EXISTS FOR (p:Person) REQUIRE p.user_id IS UNIQUE",
            "CREATE CONSTRAINT contract_cid IF NOT EXISTS FOR (c:Contract) REQUIRE c.contract_id IS UNIQUE",
            "CREATE CONSTRAINT claim_cid IF NOT EXISTS FOR (cl:Claim) REQUIRE cl.claim_id IS UNIQUE",
            "CREATE CONSTRAINT expense_did IF NOT EXISTS FOR (e:ExpenseDetail) REQUIRE e.detail_id IS UNIQUE",
            "CREATE CONSTRAINT hospital_code IF NOT EXISTS FOR (h:Hospital) REQUIRE h.hospital_code IS UNIQUE",
            "CREATE CONSTRAINT diagnosis_icd IF NOT EXISTS FOR (d:Diagnosis) REQUIRE d.icd_code IS UNIQUE",
            "CREATE CONSTRAINT bank_account IF NOT EXISTS FOR (b:BankAccount) REQUIRE b.account_number IS UNIQUE",
            "CREATE CONSTRAINT drug_name IF NOT EXISTS FOR (ds:DrugOrService) REQUIRE ds.name IS UNIQUE",
            "CREATE CONSTRAINT benefit_uid IF NOT EXISTS FOR (bt:Benefit) REQUIRE bt.claim_id_benefit_name IS UNIQUE"
        ]
        for c in constraints:
            session.run(c)
        
        # 2. Import Persons, Contracts, and BankAccounts (from DataNDBH)
        print("Importing Persons, Contracts, and BankAccounts...")
        ndbh = pd.read_csv(PERSONS_FILE, encoding='utf-8-sig').replace({np.nan: None})
        
        # Batch Person nodes
        person_query = """
        UNWIND $batch AS row
        MERGE (p:Person {user_id: row.user_id})
        SET p.identity_number = row.identity_number,
            p.full_name = row.full_name,
            p.date_of_birth = row.date_of_birth,
            p.age = toInteger(row.age),
            p.gender = row.gender,
            p.address = row.address,
            p.phone_number = row.phone_number,
            p.email = row.email,
            p.salary = toFloat(row.salary),
            p.active = row.active
        """
        
        # Batch Contract nodes
        contract_query = """
        UNWIND $batch AS row
        MERGE (c:Contract {contract_id: row.contract_id})
        SET c.so_hop_dong = row.so_hop_dong,
            c.contract_level = toInteger(row.contract_level),
            c.contract_start_date = row.contract_start_date,
            c.contract_end_date = row.contract_end_date,
            c.premium_paid = toFloat(row.premium_paid) / 100.0,
            c.remaining_benefit_limit = toFloat(row.remaining_benefit_limit)
        WITH c, row.user_id AS user_id
        MATCH (p:Person {user_id: user_id})
        MERGE (p)-[:HAS_CONTRACT]->(c)
        """
        
        # Batch BankAccount nodes
        bank_query = """
        UNWIND $batch AS row
        WHERE row.beneficiary_account IS NOT NULL
        MERGE (b:BankAccount {account_number: row.beneficiary_account})
        SET b.bank_code = row.bank_code,
            b.beneficiary_name = row.beneficiary_name
        WITH b, row.user_id AS user_id
        MATCH (p:Person {user_id: user_id})
        MERGE (p)-[:RECEIVES_TO]->(b)
        """
        
        batch_size = 1000
        for i in range(0, len(ndbh), batch_size):
            batch = ndbh.iloc[i:i+batch_size].to_dict('records')
            session.run(person_query, {"batch": batch})
            session.run(contract_query, {"batch": batch})
            session.run(bank_query, {"batch": batch})
            if (i // batch_size) % 10 == 0:
                print(f"  Processed NDBH batch {i//batch_size + 1}")

        # 3. Import Claims, Doctors, Hospitals, Diagnoses (from DataHoSoBoiThuong)
        print("Importing Claims and related entities...")
        claims = pd.read_csv(CLAIMS_FILE, encoding='utf-8-sig').replace({np.nan: None})
        
        # Hospital name mapping is already in Hospital nodes if we create them from CSKCB first
        hospitals_df = pd.read_csv(HOSPITALS_FILE, encoding='utf-8-sig').replace({np.nan: None})
        
        # Bulk create Hospitals first
        hosp_query = """
        UNWIND $batch AS row
        MERGE (h:Hospital {hospital_code: row.hospital_code})
        SET h.hospital_name = row.hospital_name,
            h.hospital_address = row.hospital_address
        """
        hosp_batch = hospitals_df.to_dict('records')
        session.run(hosp_query, {"batch": hosp_batch})

        claim_query = """
        UNWIND $batch AS row
        MERGE (cl:Claim {claim_id: row.claim_id})
        SET cl.claim_number = row.claim_number,
            cl.claim_date = row.claim_date,
            cl.claim_type = toInteger(row.claim_type),
            cl.claim_status = row.claim_status,
            cl.approval_status = row.approval_status,
            cl.claim_amount_req = toFloat(row.claim_amount_req),
            cl.claim_amount_approved = toFloat(row.claim_amount_approved),
            cl.claim_amount_vien_phi = toFloat(row.claim_amount_vien_phi),
            cl.denial_amount = toFloat(row.denial_amount),
            cl.median_claim_val = toFloat(row.median_claim_val),
            cl.visit_date = row.visit_date,
            cl.treatment_duration_days = toInteger(row.treatment_duration_days),
            cl.visit_type_name = row.visit_type_name,
            cl.clinical_notes = row.clinical_notes,
            cl.discharge_diagnosis = row.discharge_diagnosis
        
        // Link to Person
        WITH cl, row
        MATCH (p:Person {user_id: row.user_id})
        MERGE (p)-[:FILED_CLAIM {contract_id: row.contract_id}]->(cl)
        
        // Link to Hospital
        WITH cl, row
        WHERE row.hospital_code IS NOT NULL
        MATCH (h:Hospital {hospital_code: row.hospital_code})
        MERGE (cl)-[:AT_HOSPITAL {
            visit_type: row.visit_type_name,
            admission_date: row.admission_date,
            discharge_date: row.discharge_date
        }]->(h)
        
        // Create Diagnosis (Primary)
        WITH cl, row
        WHERE row.icd_code_primary IS NOT NULL
        MERGE (d:Diagnosis {icd_code: row.icd_code_primary})
        SET d.icd_name = row.icd_name_primary
        MERGE (cl)-[:DIAGNOSED_WITH {type: 'primary'}]->(d)
        
        // Create Doctors
        WITH cl, row
        WHERE row.doctor_name_exam IS NOT NULL
        MERGE (dr_exam:Doctor {doctor_name: row.doctor_name_exam})
        MERGE (cl)-[:EXAMINED_BY {role: 'exam'}]->(dr_exam)

        WITH cl, row
        WHERE row.doctor_name_admit IS NOT NULL
        MERGE (dr_admit:Doctor {doctor_name: row.doctor_name_admit})
        MERGE (cl)-[:EXAMINED_BY {role: 'admit'}]->(dr_admit)
        """
        
        for i in range(0, len(claims), batch_size):
            batch = claims.iloc[i:i+batch_size].to_dict('records')
            session.run(claim_query, {"batch": batch})
            if (i // batch_size) % 10 == 0:
                print(f"  Processed Claims batch {i//batch_size + 1}")

        # 4. Import Expenses and DrugOrService (from DataChiPhi)
        print("Importing Expenses and Item details...")
        expenses = pd.read_csv(EXPENSES_FILE, encoding='utf-8-sig').replace({np.nan: None})
        
        expense_query = """
        UNWIND $batch AS row
        MERGE (e:ExpenseDetail {detail_id: row.detail_id})
        SET e.quantity = toFloat(row.quantity),
            e.unit = row.unit,
            e.unit_price = toFloat(row.unit_price),
            e.total_amount = toFloat(row.total_amount),
            e.item_type = row.item_type,
            e.category = row.category,
            e.benefit_id = row.benefit_id,
            e.exclusion_amount = toFloat(row.exclusion_amount),
            e.median_price = toFloat(row.median_price)
        WITH e, row
        MATCH (cl:Claim {claim_id: row.claim_id})
        MERGE (cl)-[:HAS_EXPENSE]->(e)
        
        WITH e, row
        WHERE row.drug_or_service_name IS NOT NULL
        MERGE (ds:DrugOrService {name: row.drug_or_service_name})
        MERGE (e)-[:IS_ITEM]->(ds)
        """
        
        for i in range(0, len(expenses), batch_size):
            batch = expenses.iloc[i:i+batch_size].to_dict('records')
            session.run(expense_query, {"batch": batch})
            if (i // batch_size) % 10 == 0:
                print(f"  Processed Expenses batch {i//batch_size + 1}")

        # 5. Import Benefits (from DataQuyenLoi)
        print("Importing Benefits (Extra)...")
        benefits = pd.read_csv(BENEFITS_FILE, encoding='utf-8-sig').replace({np.nan: None})
        
        benefit_query = """
        UNWIND $batch AS row
        MERGE (bt:Benefit {claim_id_benefit_name: row.claim_id + "_" + row.benefit_name})
        SET bt.benefit_name = row.benefit_name,
            bt.requested_amount = toFloat(row.requested_amount),
            bt.approved_amount = toFloat(row.approved_amount),
            bt.status = row.status,
            bt.icd_code = row.icd_code
        WITH bt, row
        MATCH (cl:Claim {claim_id: row.claim_id})
        MERGE (cl)-[:HAS_BENEFIT]->(bt)
        """
        
        for i in range(0, len(benefits), batch_size):
            batch = benefits.iloc[i:i+batch_size].to_dict('records')
            session.run(benefit_query, {"batch": batch})
            if (i // batch_size) % 10 == 0:
                print(f"  Processed Benefits batch {i//batch_size + 1}")

    driver.close()
    print("Migration finished successfully!")

if __name__ == "__main__":
    start_time = time.time()
    try:
        migrate()
    except Exception as e:
        print(f"Error during migration: {e}")
    print(f"Total time: {time.time() - start_time:.2f} seconds")
