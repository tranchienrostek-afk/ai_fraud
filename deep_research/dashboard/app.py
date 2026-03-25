"""
AZINSU - CSI Fraud Command Center
FastAPI Backend with Neo4j Graph Database
Run: cd dashboard && uvicorn app:app --reload --port 8000
"""

from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from neo4j import GraphDatabase
import os
import time

# ── CONFIG ────────────────────────────────────────────────────
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DB = os.getenv("NEO4J_DATABASE", "neo4j")
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes

# ── APP ───────────────────────────────────────────────────────
app = FastAPI(title="AZINSU Fraud Command Center")

driver = None
_cache: dict = {}


def get_driver():
    global driver
    if driver is None:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        driver.verify_connectivity()
    return driver


def cached_query(key: str, cypher: str, transform=None):
    """Run cypher with simple TTL cache."""
    now = time.time()
    if key in _cache and now - _cache[key]["ts"] < CACHE_TTL:
        return _cache[key]["data"]

    d = get_driver()
    records, _, _ = d.execute_query(cypher, database_=NEO4J_DB)
    rows = []
    for r in records:
        row = {}
        for k in r.keys():
            v = r[k]
            if isinstance(v, list):
                v = [str(x) for x in v]
            elif isinstance(v, float):
                # Handle NaN/Inf which crash JSON encoder
                if v != v or v == float('inf') or v == float('-inf'):
                    v = None
            row[k] = v
        rows.append(row)

    data = transform(rows) if transform else rows
    _cache[key] = {"data": data, "ts": now}
    return data


# Cypher snippet: parse claim_date (handles both "M/D/YYYY H:M" and "YYYY-MM-DD H:M:S")
# Usage: replace {date_var} with claim date field, produces `year_month` as "YYYY-MM"
PARSE_MONTH = """
    CASE WHEN {date_var} CONTAINS '/'
        THEN split(split({date_var}, ' ')[0], '/')[2] + '-' +
                   CASE WHEN toInteger(split(split({date_var}, ' ')[0], '/')[0]) > 12 
                        THEN (CASE WHEN toInteger(split(split({date_var}, ' ')[0], '/')[1]) < 10 THEN '0' + toString(toInteger(split(split({date_var}, ' ')[0], '/')[1])) ELSE toString(toInteger(split(split({date_var}, ' ')[0], '/')[1])) END)
                        ELSE (CASE WHEN toInteger(split(split({date_var}, ' ')[0], '/')[0]) < 10 THEN '0' + toString(toInteger(split(split({date_var}, ' ')[0], '/')[0])) ELSE toString(toInteger(split(split({date_var}, ' ')[0], '/')[0])) END)
                   END
        ELSE substring({date_var}, 0, 7)
    END
"""

PARSE_DATE = """
    CASE WHEN {date_var} CONTAINS '/'
        THEN date({
                year: toInteger(split(split({date_var}, ' ')[0], '/')[2]),
                month: CASE WHEN toInteger(split(split({date_var}, ' ')[0], '/')[0]) > 12 
                            THEN toInteger(split(split({date_var}, ' ')[0], '/')[1]) 
                            ELSE toInteger(split(split({date_var}, ' ')[0], '/')[0]) END,
                day: CASE WHEN toInteger(split(split({date_var}, ' ')[0], '/')[0]) > 12 
                           THEN toInteger(split(split({date_var}, ' ')[0], '/')[0]) 
                           ELSE toInteger(split(split({date_var}, ' ')[0], '/')[1]) END
            })
        ELSE date(substring({date_var}, 0, 10))
    END
"""


def run_query(cypher: str):
    d = get_driver()
    records, _, _ = d.execute_query(cypher, database_=NEO4J_DB)
    rows = []
    for r in records:
        row = {}
        for k in r.keys():
            v = r[k]
            if isinstance(v, list):
                # Only stringify non-basic types to avoid breaking math on integers
                v = [str(x) if not isinstance(x, (int, float, str, bool)) and x is not None else x for x in v]
            elif isinstance(v, float):
                if v != v or v == float('inf') or v == float('-inf'):
                    v = None
            row[k] = v
        rows.append(row)
    return rows


# ── AUDIT RULE QUERIES (from fraud_discovery_pipeline.py) ─────
AUDIT_QUERIES = {
    "1_Petty_Fraud_Storm": {
        "title": "Trục lợi vặt (Petty Fraud Storm)",
        "description": "Hồ sơ < 200k lặp lại > 7 lần",
        "severity": "HIGH",
        "cypher": """
            MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim)
            WHERE c.claim_amount_vien_phi < 200000
            WITH p, count(c) AS so_ho_so,
                 sum(c.claim_amount_vien_phi) AS tong_tien,
                 min(c.claim_date) AS tu_ngay,
                 max(c.claim_date) AS den_ngay
            WHERE so_ho_so > 7
            RETURN p.user_id AS user_id,
                   p.full_name AS ho_ten,
                   p.phone_number AS sdt,
                   so_ho_so, round(tong_tien) AS tong_tien,
                   tu_ngay, den_ngay
            ORDER BY so_ho_so DESC LIMIT 100
        """,
    },
    "2_Facility_Loyalty": {
        "title": "Trung thành CSYT bất thường",
        "description": "Bệnh vặt khám > 2 lần tại cùng 1 cơ sở",
        "severity": "HIGH",
        "cypher": """
            MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim)-[:AT_HOSPITAL]->(h:Hospital)
            WHERE c.discharge_diagnosis =~ '(?i).*(vi\u00eam h\u1ecdng|vi\u00eam m\u0169i|c\u1ea3m c\u00fam|r\u1ed1i lo\u1ea1n ti\u00eau|vi\u00eam d\u1ea1 d\u00e0y|vi\u00eam ph\u1ebf qu\u1ea3n|vi\u00eam k\u1ebft m\u1ea1c).*'
            WITH p, h, c.discharge_diagnosis AS chan_doan,
                 count(c) AS so_lan_kham, sum(c.claim_amount_vien_phi) AS tong_tien
            WHERE so_lan_kham > 2
            RETURN p.user_id AS user_id, p.full_name AS ho_ten,
                   h.hospital_code AS ma_benh_vien, chan_doan,
                   so_lan_kham, round(tong_tien) AS tong_tien
            ORDER BY so_lan_kham DESC LIMIT 100
        """,
    },
    "3_Phone_PII_Hub": {
        "title": "Cụm dùng chung SĐT (Phone Hub)",
        "description": "Nhóm > 5 người dùng chung SĐT",
        "severity": "CRITICAL",
        "cypher": """
            MATCH (p:Person)
            WHERE p.phone_number IS NOT NULL AND p.phone_number <> 'Unknown'
            WITH p.phone_number AS phone_raw,
                 collect(DISTINCT p.full_name) AS members,
                 collect(DISTINCT p.user_id) AS user_ids
            WHERE size(members) > 5
            WITH phone_raw, members, user_ids
            UNWIND user_ids AS uid
            OPTIONAL MATCH (pp:Person {user_id: uid})-[:FILED_CLAIM]->(c:Claim)
            WITH phone_raw, members,
                 count(c) AS total_claims, sum(c.claim_amount_vien_phi) AS total_amount
            RETURN phone_raw AS sdt,
                   size(members) AS so_nguoi,
                   total_claims AS tong_ho_so,
                   round(total_amount) AS tong_tien,
                   members[0..5] AS mau_ten
            ORDER BY so_nguoi DESC LIMIT 50
        """,
    },
    "4_Bank_Syndicate": {
        "title": "Mạng lưới STK Ngân hàng",
        "description": "Nhiều người nhận tiền về cùng 1 STK",
        "severity": "CRITICAL",
        "cypher": """
            MATCH (p:Person)-[:RECEIVES_TO]->(b:BankAccount)
            OPTIONAL MATCH (p)-[:FILED_CLAIM]->(c:Claim)
            WITH b, collect(DISTINCT p.full_name) AS users,
                 collect(DISTINCT p.user_id) AS user_ids,
                 count(c) AS total_claims, sum(c.claim_amount_vien_phi) AS total_payout
            WHERE size(users) > 3
            RETURN b.account_number AS stk, b.beneficiary_name AS chu_tk,
                   size(users) AS so_nguoi, total_claims AS tong_ho_so,
                   round(total_payout) AS tong_tien_nhan,
                   users[0..5] AS mau_ten
            ORDER BY so_nguoi DESC LIMIT 50
        """,
    },
    "5_Doctor_Hospital_Hotspot": {
        "title": "Cụm Bác sĩ - Bệnh viện nghi vấn",
        "description": "Bác sĩ ký nhiều hồ sơ bất thường tại 1 BV",
        "severity": "HIGH",
        "cypher": """
            MATCH (c:Claim)-[:EXAMINED_BY]->(d:Doctor),
                  (c)-[:AT_HOSPITAL]->(h:Hospital)
            WITH d, h, count(c) AS so_ho_so, sum(c.claim_amount_vien_phi) AS tong_tien,
                 collect(DISTINCT c.discharge_diagnosis) AS danh_sach_chan_doan
            WHERE so_ho_so > 20
            RETURN d.doctor_name AS bac_si, h.hospital_code AS ma_bv,
                   so_ho_so, round(tong_tien) AS tong_tien,
                   size(danh_sach_chan_doan) AS so_loai_chan_doan,
                   danh_sach_chan_doan[0..3] AS mau_chan_doan
            ORDER BY so_ho_so DESC LIMIT 50
        """,
    },
    "6_Ghost_Clinic": {
        "title": "CSYT nghi vấn (Ghost Clinic)",
        "description": "BV có > 70% hóa đơn nhỏ (< 200k)",
        "severity": "HIGH",
        "cypher": """
            MATCH (h:Hospital)<-[:AT_HOSPITAL]-(c:Claim)
            WITH h, count(c) AS total,
                 sum(CASE WHEN c.claim_amount_vien_phi < 200000 THEN 1 ELSE 0 END) AS petty_count,
                 sum(c.claim_amount_vien_phi) AS total_amount
            WHERE total > 10
            RETURN h.hospital_code AS ma_bv, total AS tong_ho_so,
                   petty_count AS ho_so_nho,
                   round(petty_count * 100.0 / total) AS ti_le_nho_pct,
                   round(total_amount) AS tong_tien
            ORDER BY ti_le_nho_pct DESC LIMIT 30
        """,
    },
    "7_High_Freq_Claimant": {
        "title": "Người nộp hồ sơ nhiều bất thường",
        "description": "Khách hàng nộp > 10 hồ sơ",
        "severity": "HIGH",
        "cypher": """
            MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim)
            WITH p, count(c) AS so_ho_so, sum(c.claim_amount_vien_phi) AS tong_tien,
                 collect(DISTINCT c.discharge_diagnosis) AS chan_doan_list,
                 min(c.claim_date) AS tu_ngay, max(c.claim_date) AS den_ngay
            WHERE so_ho_so > 10
            RETURN p.user_id AS user_id, p.full_name AS ho_ten,
                   p.phone_number AS sdt,
                   so_ho_so, round(tong_tien) AS tong_tien,
                   size(chan_doan_list) AS so_loai_benh,
                   tu_ngay, den_ngay,
                   chan_doan_list[0..3] AS mau_chan_doan
            ORDER BY so_ho_so DESC LIMIT 50
        """,
    },
    "8_Multi_Hospital_Same_Diag": {
        "title": "Doctor Shopping (Nhiều BV)",
        "description": "Cùng 1 bệnh, khám >= 3 BV khác nhau",
        "severity": "MEDIUM",
        "cypher": """
            MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim)-[:AT_HOSPITAL]->(h:Hospital)
            WHERE c.discharge_diagnosis IS NOT NULL
            WITH p, c.discharge_diagnosis AS chan_doan,
                 collect(DISTINCT h.hospital_code) AS ds_bv,
                 count(c) AS so_ho_so, sum(c.claim_amount_vien_phi) AS tong_tien
            WHERE size(ds_bv) >= 3
            RETURN p.user_id AS user_id, p.full_name AS ho_ten,
                   chan_doan, size(ds_bv) AS so_bv_khac_nhau,
                   so_ho_so, round(tong_tien) AS tong_tien,
                   ds_bv[0..5] AS mau_bv
            ORDER BY so_bv_khac_nhau DESC LIMIT 50
        """,
    },
    "9_Diagnosis_Amount_Outlier": {
        "title": "Claim cao bất thường theo Bệnh lý",
        "description": "Hồ sơ có số tiền claim > 3x trung vị của bệnh lý đó",
        "severity": "HIGH",
        "cypher": """
            MATCH (c:Claim)
            WHERE c.discharge_diagnosis IS NOT NULL AND c.discharge_diagnosis <> ''
              AND c.claim_amount_vien_phi > 0
            WITH c.discharge_diagnosis AS diag, collect(c) AS claims,
                 percentileCont(c.claim_amount_vien_phi, 0.5) AS median_amt
            WHERE median_amt > 0
            UNWIND claims AS c
            WITH c, diag, median_amt, c.claim_amount_vien_phi / median_amt AS ratio
            WHERE ratio > 3
            MATCH (p:Person)-[:FILED_CLAIM]->(c)
            RETURN p.user_id AS user_id, p.full_name AS ho_ten,
                   diag AS chan_doan, round(c.claim_amount_vien_phi) AS so_tien_claim,
                   round(median_amt) AS trung_vi_benh_ly,
                   round(ratio * 10) / 10.0 AS he_so_vuot,
                   c.claim_id AS claim_id
            ORDER BY ratio DESC LIMIT 100
        """,
    },
    "10_Unit_Price_Outlier": {
        "title": "Đơn giá bất thường (Hồ sơ < 3tr)",
        "description": "Chi phí một danh mục thuốc/DV cao > 3x trung bình của cùng mã bệnh lý (hồ sơ < 3tr).",
        "severity": "CRITICAL",
        "cypher": """
            MATCH (c:Claim)-[:HAS_EXPENSE]->(e:ExpenseDetail)
            WHERE c.claim_amount_vien_phi < 3000000 AND e.total_amount > 0
            WITH c.discharge_diagnosis AS diagnosis, e.category AS category,
                 avg(e.total_amount) AS avg_cat_amt, count(e) AS sample_size
            WHERE sample_size >= 10
            MATCH (p:Person)-[:FILED_CLAIM]->(c2:Claim {discharge_diagnosis: diagnosis})-[:HAS_EXPENSE]->(e2:ExpenseDetail {category: category})
            WHERE c2.claim_amount_vien_phi < 3000000 AND e2.total_amount > 3 * avg_cat_amt
            OPTIONAL MATCH (e2)-[:IS_ITEM]->(ds:DrugOrService)
            RETURN p.user_id AS user_id, p.full_name AS ho_ten,
                   c2.claim_id AS claim_id, diagnosis AS chan_doan,
                   category AS danh_muc, ds.name AS ten_thuoc_dv,
                   round(e2.total_amount) AS don_gia_thuc, round(avg_cat_amt) AS trung_vi_don_gia,
                   round(e2.total_amount / avg_cat_amt, 1) AS he_so_vuot
            ORDER BY he_so_vuot DESC
            LIMIT 100
        """,
    },
    "11_Premium_Claim_Ratio": {
        "title": "Tỷ lệ Bồi thường / Phí BH (High Loss)",
        "description": "Người có tổng bồi thường > 5x tổng phí bảo hiểm đã đóng",
        "severity": "CRITICAL",
        "cypher": """
            MATCH (p:Person)-[:HAS_CONTRACT]->(cont:Contract)
            WITH p, sum(coalesce(cont.premium_paid, 0)) AS total_premium
            OPTIONAL MATCH (p)-[:FILED_CLAIM]->(c:Claim)
            WITH p, total_premium, sum(coalesce(c.claim_amount_approved, 0)) AS total_payout
            WHERE total_premium > 0 AND total_payout > 5 * total_premium
            RETURN p.user_id AS user_id, p.full_name AS ho_ten,
                   round(total_premium) AS tong_phi, 
                   round(total_payout) AS tong_boi_thuong,
                   round(total_payout * 1.0 / total_premium, 1) AS ti_le_boi_thuong
            ORDER BY ti_le_boi_thuong DESC LIMIT 100
        """,
    },
    "12_Treatment_Duration_Outlier": {
        "title": "Thời gian Điều trị bất thường",
        "description": "Số ngày nằm viện > 3x trung vị cùng bệnh lý",
        "severity": "HIGH",
        "cypher": """
            MATCH (c:Claim)-[:DIAGNOSED_WITH]->(d:Diagnosis)
            WHERE c.treatment_duration_days IS NOT NULL
            WITH d.icd_name AS pathology, collect(c.treatment_duration_days) AS durations
            WITH pathology, percentileCont(durations, 0.5) AS median_duration
            MATCH (c:Claim)-[:DIAGNOSED_WITH]->(d:Diagnosis)
            WHERE d.icd_name = pathology 
              AND c.treatment_duration_days > 3 * median_duration 
              AND c.treatment_duration_days > 2
            RETURN c.claim_id AS claim_id, pathology AS chan_doan, 
                   c.treatment_duration_days AS so_ngay_dieu_tri, 
                   round(median_duration, 1) AS median_per_diag
            ORDER BY so_ngay_dieu_tri DESC LIMIT 100
        """,
    },
    "13_High_Exclusion_Ratio": {
        "title": "Tỷ lệ Xuất toán cao",
        "description": "Hồ sơ có > 50% chi phí bị xuất toán (từ chối bồi thường)",
        "severity": "HIGH",
        "cypher": """
            MATCH (c:Claim)-[:HAS_EXPENSE]->(e:ExpenseDetail)
            WITH c, sum(coalesce(e.total_amount, 0)) AS total, 
                 sum(coalesce(e.exclusion_amount, 0)) AS excluded
            WHERE total > 0 AND (excluded * 1.0 / total) > 0.5
            RETURN c.claim_id AS claim_id, round(total) AS tong_tien, 
                   round(excluded) AS mien_thuong,
                   round((excluded * 100.0 / total), 1) AS ti_le_tu_choi_pct
            ORDER BY ti_le_tu_choi_pct DESC LIMIT 100
        """,
    },
    "14_Expired_Contract_Claim": {
        "title": "Claim trên HĐ hết hiệu lực",
        "description": "Hồ sơ nộp sau ngày HĐ hết hạn",
        "severity": "CRITICAL",
        "cypher": """
            MATCH (p:Person)-[:HAS_CONTRACT]->(cont:Contract), (p)-[:FILED_CLAIM]->(c:Claim)
            WHERE cont.contract_end_date IS NOT NULL AND c.claim_date IS NOT NULL
            WITH p, c, cont,
                 CASE WHEN c.claim_date CONTAINS '/'
                     THEN date({year: toInteger(split(split(c.claim_date, ' ')[0], '/')[2]),
                                month: toInteger(split(split(c.claim_date, ' ')[0], '/')[0]),
                                day: toInteger(split(split(c.claim_date, ' ')[0], '/')[1])})
                     ELSE date(substring(c.claim_date, 0, 10))
                 END AS d_claim,
                 CASE WHEN cont.contract_end_date CONTAINS '/'
                     THEN date({year: toInteger(split(split(cont.contract_end_date, ' ')[0], '/')[2]),
                                month: toInteger(split(split(cont.contract_end_date, ' ')[0], '/')[0]),
                                day: toInteger(split(split(cont.contract_end_date, ' ')[0], '/')[1])})
                     ELSE date(substring(cont.contract_end_date, 0, 10))
                 END AS d_end
            WHERE d_claim > d_end
            RETURN p.user_id AS user_id, p.full_name AS ho_ten,
                   c.claim_id AS claim_id, toString(d_end) AS ngay_het_han,
                   toString(d_claim) AS ngay_kham
            LIMIT 100
        """,
    },
    "15_Claim_Filing_Delay": {
        "title": "Chênh lệch Thời gian nộp Hồ sơ",
        "description": "Nộp claim > 90 ngày sau khám hoặc ngày nộp trước ngày khám",
        "severity": "HIGH",
        "cypher": """
            MATCH (c:Claim)
            WHERE c.visit_date IS NOT NULL AND c.claim_date IS NOT NULL
            WITH c,
                 CASE WHEN c.visit_date CONTAINS '/'
                     THEN date({year: toInteger(split(split(c.visit_date, ' ')[0], '/')[2]),
                                month: toInteger(split(split(c.visit_date, ' ')[0], '/')[0]),
                                day: toInteger(split(split(c.visit_date, ' ')[0], '/')[1])})
                     ELSE date(substring(c.visit_date, 0, 10))
                 END AS d_visit,
                 CASE WHEN c.claim_date CONTAINS '/'
                     THEN date({year: toInteger(split(split(c.claim_date, ' ')[0], '/')[2]),
                                month: toInteger(split(split(c.claim_date, ' ')[0], '/')[0]),
                                day: toInteger(split(split(c.claim_date, ' ')[0], '/')[1])})
                     ELSE date(substring(c.claim_date, 0, 10))
                 END AS d_claim
            WITH c, d_visit, d_claim, duration.inDays(d_visit, d_claim).days AS delay
            WHERE delay > 90 OR delay < 0
            RETURN c.claim_id AS claim_id, toString(d_visit) AS ngay_kham,
                   toString(d_claim) AS ngay_nop, delay AS so_ngay_tre
            ORDER BY delay DESC LIMIT 100
        """,
    },
    # ── PHASE 2: Graph Knowledge Mining Patterns (Rules 16-25) ──
    "16_Contract_Upgrade_Then_Claim": {
        "title": "Nâng cấp HĐ rồi Claim lớn",
        "description": "Mua/nâng gói BH rồi claim > 5 triệu trong vòng 90 ngày đầu",
        "severity": "CRITICAL",
        "cypher": """
            MATCH (p:Person)-[:HAS_CONTRACT]->(cont:Contract),
                  (p)-[:FILED_CLAIM]->(c:Claim)
            WHERE cont.contract_start_date IS NOT NULL
              AND c.claim_date IS NOT NULL
              AND cont.contract_start_date <> ""
              AND c.claim_date <> ""
              AND c.claim_amount_vien_phi > 5000000
            WITH p, cont, c,
                 date(substring(toString(cont.contract_start_date), 0, 10)) AS d_start,
                 CASE WHEN c.claim_date CONTAINS '/'
                     THEN date({{year: toInteger(split(split(c.claim_date, ' ')[0], '/')[2]),
                                month: toInteger(split(split(c.claim_date, ' ')[0], '/')[0]),
                                day: toInteger(split(split(c.claim_date, ' ')[0], '/')[1])}})
                     ELSE date(substring(c.claim_date, 0, 10))
                 END AS d_claim
            WITH p, cont, c, d_start, d_claim,
                 duration.inDays(d_start, d_claim).days AS ngay_sau_hd
            WHERE ngay_sau_hd >= 0 AND ngay_sau_hd <= 90
            RETURN p.user_id AS user_id,
                   p.full_name AS ho_ten,
                   cont.contract_id AS ma_hop_dong,
                   cont.contract_level AS goi_bh,
                   c.claim_id AS claim_id,
                   round(c.claim_amount_vien_phi) AS so_tien_claim,
                   ngay_sau_hd,
                   toString(d_start) AS ngay_bat_dau_hd,
                   toString(d_claim) AS ngay_kham
            ORDER BY so_tien_claim DESC LIMIT 100
        """,
    },
    "17_Doctor_Patient_Ring": {
        "title": "Vòng tròn Bác sĩ - Bệnh nhân",
        "description": "Nhóm >= 5 bệnh nhân luôn đi cùng 1 bác sĩ, mỗi người >= 3 lần",
        "severity": "CRITICAL",
        "cypher": """
            MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim)-[:EXAMINED_BY]->(d:Doctor)
            WITH d, p, count(c) AS so_lan
            WHERE so_lan >= 3
            WITH d, collect({{user_id: p.user_id, ho_ten: p.full_name, so_lan: so_lan}}) AS patients,
                 count(p) AS so_benh_nhan,
                 sum(so_lan) AS tong_ho_so
            WHERE so_benh_nhan >= 5
            RETURN d.doctor_id AS ma_bac_si,
                   d.name AS ten_bac_si,
                   so_benh_nhan,
                   tong_ho_so,
                   patients[0..5] AS top_benh_nhan
            ORDER BY so_benh_nhan DESC LIMIT 50
        """,
    },
    "18_Hospital_Hopping_Same_Week": {
        "title": "Nhảy BV cùng tuần",
        "description": "Cùng 1 người khám >= 2 BV khác nhau trong 7 ngày",
        "severity": "HIGH",
        "cypher": """
            MATCH (p:Person)-[:FILED_CLAIM]->(c1:Claim)-[:AT_HOSPITAL]->(h1:Hospital),
                  (p)-[:FILED_CLAIM]->(c2:Claim)-[:AT_HOSPITAL]->(h2:Hospital)
            WHERE id(c1) < id(c2) AND h1 <> h2
              AND c1.visit_date IS NOT NULL AND c2.visit_date IS NOT NULL
            WITH p, c1, c2, h1, h2,
                 CASE WHEN c1.visit_date CONTAINS '/'
                     THEN date({{year: toInteger(split(split(c1.visit_date, ' ')[0], '/')[2]),
                                month: toInteger(split(split(c1.visit_date, ' ')[0], '/')[0]),
                                day: toInteger(split(split(c1.visit_date, ' ')[0], '/')[1])}})
                     ELSE date(substring(c1.visit_date, 0, 10))
                 END AS d1,
                 CASE WHEN c2.visit_date CONTAINS '/'
                     THEN date({{year: toInteger(split(split(c2.visit_date, ' ')[0], '/')[2]),
                                month: toInteger(split(split(c2.visit_date, ' ')[0], '/')[0]),
                                day: toInteger(split(split(c2.visit_date, ' ')[0], '/')[1])}})
                     ELSE date(substring(c2.visit_date, 0, 10))
                 END AS d2
            WITH p, c1, c2, h1, h2, abs(duration.inDays(d1, d2).days) AS khoang_cach
            WHERE khoang_cach <= 7
            RETURN p.user_id AS user_id,
                   p.full_name AS ho_ten,
                   h1.hospital_code AS bv_1,
                   h2.hospital_code AS bv_2,
                   c1.claim_id AS claim_1,
                   c2.claim_id AS claim_2,
                   khoang_cach AS so_ngay_cach
            ORDER BY khoang_cach ASC LIMIT 100
        """,
    },
    "19_Expense_Category_Duplication": {
        "title": "Trùng lặp danh mục chi phí",
        "description": "Cùng 1 Claim khai > 2 chi phí trùng danh mục hoặc trùng thuốc/DV",
        "severity": "HIGH",
        "cypher": """
            MATCH (c:Claim)-[:HAS_EXPENSE]->(e:ExpenseDetail)
            WITH c, e.category AS danh_muc, count(e) AS so_dong,
                 sum(e.amount) AS tong_tien
            WHERE so_dong > 2
            RETURN c.claim_id AS claim_id,
                   danh_muc,
                   so_dong AS so_dong_trung,
                   round(tong_tien) AS tong_tien
            ORDER BY so_dong DESC LIMIT 100
        """,
    },
    "20_Bank_Account_Mismatch": {
        "title": "STK không khớp tên",
        "description": "Người nhận tiền có tên khác hẳn tên chủ hợp đồng",
        "severity": "CRITICAL",
        "cypher": """
            MATCH (p:Person)-[:RECEIVES_TO]->(b:BankAccount)
            WHERE p.full_name IS NOT NULL AND b.beneficiary_name IS NOT NULL
              AND p.full_name <> "" AND b.beneficiary_name <> ""
              AND toLower(p.full_name) <> toLower(b.beneficiary_name)
            RETURN p.user_id AS user_id,
                   p.full_name AS ho_ten,
                   b.account_number AS stk,
                   b.beneficiary_name AS ten_thu_huong,
                   b.bank_name AS ngan_hang
            ORDER BY p.full_name LIMIT 100
        """,
    },
    "21_Insurer_Doctor_Concentration": {
        "title": "Cặp Đại lý - Bác sĩ bất thường",
        "description": "1 Insurer xử lý quá nhiều hồ sơ từ 1 Doctor cụ thể (> 20 claims)",
        "severity": "HIGH",
        "cypher": """
            MATCH (ins:Insurer)<-[:INSURED_BY]-(c:Claim)-[:EXAMINED_BY]->(d:Doctor)
            WITH ins, d, count(c) AS so_ho_so,
                 sum(coalesce(c.claim_amount_approved, 0)) AS tong_duyet
            WHERE so_ho_so > 20
            RETURN ins.name AS ten_dai_ly,
                   d.doctor_id AS ma_bac_si,
                   d.name AS ten_bac_si,
                   so_ho_so,
                   round(tong_duyet) AS tong_duyet
            ORDER BY so_ho_so DESC LIMIT 50
        """,
    },
    "22_Diagnosis_Expense_Inconsistency": {
        "title": "Bệnh lý vs Chi phí không tương xứng",
        "description": "Bệnh nhẹ nhưng chi phí vượt 3x trung vị nhóm bệnh",
        "severity": "HIGH",
        "cypher": """
            MATCH (c:Claim)-[:DIAGNOSED_WITH]->(diag:Diagnosis)
            WITH diag.icd_name AS benh_ly,
                 collect(c.claim_amount_vien_phi) AS amounts,
                 count(c) AS so_claims
            WHERE so_claims >= 5
            WITH benh_ly, amounts, so_claims,
                 apoc.agg.median(amounts) AS trung_vi
            WHERE trung_vi > 0
            UNWIND amounts AS amt
            WITH benh_ly, amt, trung_vi, so_claims
            WHERE amt > trung_vi * 3
            MATCH (c2:Claim)-[:DIAGNOSED_WITH]->(d2:Diagnosis)
            WHERE d2.icd_name = benh_ly AND c2.claim_amount_vien_phi = amt
            MATCH (p:Person)-[:FILED_CLAIM]->(c2)
            RETURN p.user_id AS user_id,
                   p.full_name AS ho_ten,
                   c2.claim_id AS claim_id,
                   benh_ly,
                   round(amt) AS so_tien_claim,
                   round(trung_vi) AS trung_vi_benh_ly,
                   round(amt / trung_vi, 1) AS he_so_vuot
            ORDER BY he_so_vuot DESC LIMIT 100
        """,
    },
    "23_Circular_Money_Flow": {
        "title": "Dòng tiền vòng tròn",
        "description": ">= 3 người dùng chung STK VÀ chung bệnh viện",
        "severity": "CRITICAL",
        "cypher": """
            MATCH (p:Person)-[:RECEIVES_TO]->(b:BankAccount)
            WITH b, collect(DISTINCT p) AS persons
            WHERE size(persons) >= 3
            UNWIND persons AS p1
            MATCH (p1)-[:FILED_CLAIM]->(c:Claim)-[:AT_HOSPITAL]->(h:Hospital)
            WITH b, h, collect(DISTINCT p1.user_id) AS users_at_hospital,
                 collect(DISTINCT p1.full_name) AS ten_nguoi
            WHERE size(users_at_hospital) >= 3
            RETURN b.account_number AS stk,
                   b.bank_name AS ngan_hang,
                   h.hospital_code AS ma_bv,
                   size(users_at_hospital) AS so_nguoi,
                   ten_nguoi[0..5] AS ds_ten
            ORDER BY so_nguoi DESC LIMIT 50
        """,
    },
    "24_Weekend_Holiday_Cluster": {
        "title": "Cụm claim Cuối tuần bất thường",
        "description": "Người có > 60% claims vào cuối tuần (khi tổng >= 5 claims)",
        "severity": "MEDIUM",
        "cypher": """
            MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim)
            WHERE c.visit_date IS NOT NULL AND c.visit_date <> ""
            WITH p, c,
                 CASE WHEN c.visit_date CONTAINS '/'
                     THEN date({{year: toInteger(split(split(c.visit_date, ' ')[0], '/')[2]),
                                month: toInteger(split(split(c.visit_date, ' ')[0], '/')[0]),
                                day: toInteger(split(split(c.visit_date, ' ')[0], '/')[1])}})
                     ELSE date(substring(c.visit_date, 0, 10))
                 END AS d_visit
            WITH p, count(c) AS tong_claims,
                 sum(CASE WHEN d_visit.dayOfWeek >= 6 THEN 1 ELSE 0 END) AS claims_cuoi_tuan
            WHERE tong_claims >= 5
            WITH p, tong_claims, claims_cuoi_tuan,
                 round(claims_cuoi_tuan * 100.0 / tong_claims, 1) AS ti_le_cuoi_tuan
            WHERE ti_le_cuoi_tuan > 60
            RETURN p.user_id AS user_id,
                   p.full_name AS ho_ten,
                   tong_claims,
                   claims_cuoi_tuan,
                   ti_le_cuoi_tuan
            ORDER BY ti_le_cuoi_tuan DESC LIMIT 100
        """,
    },
    "25_Multi_Claim_Same_Day_Same_Hospital": {
        "title": "Nhiều HS cùng ngày cùng BV",
        "description": "1 người nộp >= 2 hồ sơ cùng ngày tại cùng 1 BV (bill splitting)",
        "severity": "HIGH",
        "cypher": """
            MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim)-[:AT_HOSPITAL]->(h:Hospital)
            WHERE c.visit_date IS NOT NULL AND c.visit_date <> ""
            WITH p, h, c.visit_date AS ngay_kham,
                 collect(c.claim_id) AS ds_claim,
                 count(c) AS so_ho_so,
                 sum(c.claim_amount_vien_phi) AS tong_tien
            WHERE so_ho_so >= 2
            RETURN p.user_id AS user_id,
                   p.full_name AS ho_ten,
                   h.hospital_code AS ma_bv,
                   ngay_kham,
                   so_ho_so,
                   ds_claim[0..5] AS ds_claim_id,
                   round(tong_tien) AS tong_tien
            ORDER BY so_ho_so DESC LIMIT 100
        """,
    },
}


# ── API ENDPOINTS ─────────────────────────────────────────────

@app.get("/api/overview")
def api_overview():
    """Hero metrics for dashboard header."""
    data = cached_query("overview", """
        MATCH (c:Claim)
        WITH count(c) AS total_claims, sum(c.claim_amount_vien_phi) AS total_amount
        OPTIONAL MATCH (p:Person)-[:FILED_CLAIM]->(c2:Claim)
        WITH total_claims, total_amount,
             count(DISTINCT p.user_id) AS total_claimants
        RETURN total_claims, total_amount, total_claimants
    """)

    overview = data[0] if data else {"total_claims": 0, "total_amount": 0, "total_claimants": 0}

    # High frequency claimants
    high_freq = cached_query("high_freq_count", """
        MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim)
        WITH p, count(c) AS n WHERE n > 10
        RETURN count(p) AS cnt
    """)

    # Anomaly % (petty fraud)
    anomaly = cached_query("anomaly_pct", """
        MATCH (c:Claim)
        WITH count(c) AS total,
             sum(CASE WHEN c.claim_amount_vien_phi < 200000 AND c.claim_amount_vien_phi > 0 THEN 1 ELSE 0 END) AS petty
        RETURN CASE WHEN total > 0 THEN round(petty * 100.0 / total, 1) ELSE 0 END AS anomaly_pct
    """)

    # Syndicate count (shared bank with > 3 users)
    syndicates = cached_query("syndicate_count", """
        MATCH (p:Person)-[:RECEIVES_TO]->(b:BankAccount)
        WITH b, collect(DISTINCT p.user_id) AS users
        WHERE size(users) > 3
        RETURN count(b) AS cnt
    """)

    return {
        "total_claims": overview.get("total_claims", 0),
        "total_amount": overview.get("total_amount", 0),
        "total_claimants": overview.get("total_claimants", 0),
        "high_freq_claimants": high_freq[0]["cnt"] if (high_freq and "cnt" in high_freq[0]) else 0,
        "anomaly_pct": anomaly[0]["anomaly_pct"] if (anomaly and "anomaly_pct" in anomaly[0]) else 0,
        "syndicates": syndicates[0]["cnt"] if (syndicates and "cnt" in syndicates[0]) else 0,
    }


@app.get("/api/audit-rules")
def api_audit_rules():
    """All audit rule results."""
    results = []
    for key, cfg in AUDIT_QUERIES.items():
        try:
            rows = cached_query(f"audit_{key}", cfg["cypher"])
        except Exception as e:
            print(f"[AUDIT] Rule {key} failed: {e}")
            rows = []
        results.append({
            "rule_id": key,
            "title": cfg["title"],
            "description": cfg["description"],
            "severity": cfg["severity"],
            "count": len(rows),
            "records": rows[:20],  # top 20 per rule
        })
    return results


@app.get("/api/top-suspects")
def api_top_suspects(limit: int = Query(default=50, le=200)):
    """Risk-scored persons with composite risk formula."""
    rows = cached_query("risk_raw_v2", """
        MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim)
        WITH p,
             count(c) AS num_claims,
             sum(coalesce(c.claim_amount_approved, 0)) AS total_approved,
             sum(CASE WHEN c.claim_amount_vien_phi < 200000 AND c.claim_amount_vien_phi > 0 THEN 1 ELSE 0 END) AS petty_claims,
             sum(CASE WHEN c.treatment_duration_days > 5 THEN 1 ELSE 0 END) AS long_stays,
             collect(DISTINCT c.discharge_diagnosis) AS unique_diag
        OPTIONAL MATCH (p)-[:HAS_CONTRACT]->(ct:Contract)
        WITH p, num_claims, total_approved, petty_claims, long_stays, unique_diag,
             sum(coalesce(ct.premium_paid, 0)) AS total_premium,
             max(ct.contract_level) AS contract_level
        RETURN p.user_id AS user_id,
               p.full_name AS full_name,
               p.phone_number AS phone,
               contract_level,
               num_claims, round(total_approved) AS total_approved,
               petty_claims, long_stays,
               size(unique_diag) AS unique_diagnoses,
               round(total_premium) AS total_premium
        ORDER BY num_claims DESC
    """)

    # Compute composite risk in Python
    for r in rows:
        nc = r.get("num_claims", 0) or 0
        pc = r.get("petty_claims", 0) or 0
        ta = r.get("total_approved", 0) or 0
        tp = r.get("total_premium", 0) or 0
        ls = r.get("long_stays", 0) or 0
        ud = r.get("unique_diagnoses", 1) or 1

        # Axis scoring
        freq_score = min(nc / 5.0, 10.0) # 0-10
        petty_ratio = pc / nc if nc > 0 else 0
        petty_score = petty_ratio * 10
        
        loss_ratio = ta / (tp + 1.0)
        loss_score = min(loss_ratio * 2.0, 10.0) # 5x payout = 10 pts
        
        duration_score = min(ls * 2.0, 10.0) # 5 long stays = 10 pts
        diversity_score = max(0, min(1, 1 - ud / (nc + 1.0))) * 10

        r["composite_risk"] = round(
            freq_score * 0.20 +
            petty_score * 0.15 +
            loss_score * 0.35 +
            duration_score * 0.15 +
            diversity_score * 0.15, 2
        )

    rows.sort(key=lambda x: x.get("composite_risk", 0), reverse=True)
    return rows[:limit]


@app.get("/api/person-risk-radar/{user_id}")
def api_person_risk_radar(user_id: str):
    """Personalized risk radar chart data."""
    # Use PARSE_DATE snippets for safety
    parse_visit = PARSE_DATE.replace("{date_var}", "c.visit_date")
    parse_claim = PARSE_DATE.replace("{date_var}", "c.claim_date")
    
    cypher = """
        MATCH (p:Person {user_id: '$USER_ID$'})
        OPTIONAL MATCH (p)-[:HAS_CONTRACT]->(cont:Contract)
        WITH p, sum(coalesce(cont.premium_paid, 0)) AS total_premium
        OPTIONAL MATCH (p)-[:FILED_CLAIM]->(c:Claim)
        WITH p, total_premium, c, 
             $PARSE_VISIT$ AS d_visit, 
             $PARSE_CLAIM$ AS d_claim
        WITH p, total_premium, count(c) AS num_claims, 
             sum(coalesce(c.claim_amount_approved, 0)) AS total_payout,
             sum(CASE WHEN c.claim_amount_vien_phi < 200000 AND c.claim_amount_vien_phi > 0 THEN 1 ELSE 0 END) AS petty_count,
             avg(c.treatment_duration_days) AS avg_dur,
             avg(duration.inDays(d_visit, d_claim).days) AS avg_delay
        RETURN num_claims, total_payout, total_premium, petty_count, 
               coalesce(avg_dur, 0) AS avg_dur, coalesce(avg_delay, 0) AS avg_delay
    """.replace("$USER_ID$", user_id).replace("$PARSE_VISIT$", parse_visit).replace("$PARSE_CLAIM$", parse_claim)
    data = run_query(cypher)
    if not data:
        return {"data": [0,0,0,0,0]}
    
    r = data[0]
    nc = r.get("num_claims", 0)
    pc = r.get("petty_count", 0)
    payout = r.get("total_payout", 0)
    premium = r.get("total_premium", 0)
    dur = r.get("avg_dur", 0)
    delay = r.get("avg_delay", 0)
    
    # Normalization [0-100]
    freq = max(0, min(100, (nc / 15.0) * 100))
    petty = 0 if nc == 0 else max(0, min(100, (pc / nc) * 100))
    loss = max(0, min(100, (payout / (premium + 1.0)) * 20)) # 5x = 100
    duration = max(0, min(100, (dur / 5.0) * 33)) # 3x (15 days) approx 100
    delay_score = max(0, min(100, (delay / 90.0) * 100))
    
    return {
        "data": [
            round(freq, 1), 
            round(petty, 1), 
            round(loss, 1), 
            round(duration, 1), 
            round(delay_score, 1)
        ],
        "labels": ["Tần suất", "Hồ sơ nhỏ", "Tỉ lệ bồi thường", "Thời gian đ.trị", "Độ trễ nộp HS"]
    }


@app.get("/api/hospital-risk-radar/{hospital_code}")
def api_hospital_risk_radar(hospital_code: str):
    """Risk radar for a hospital."""
    cypher = f"""
        MATCH (h:Hospital {{hospital_code: '{hospital_code}'}})<-[:AT_HOSPITAL]-(c:Claim)
        WITH h,
             count(c) AS total_claims,
             sum(coalesce(c.claim_amount_approved, 0)) AS total_approved,
             sum(CASE WHEN c.claim_amount_vien_phi < 200000 AND c.claim_amount_vien_phi > 0 THEN 1 ELSE 0 END) AS petty_count,
             avg(c.treatment_duration_days) AS avg_dur,
             collect(DISTINCT c.discharge_diagnosis) AS unique_diag
        OPTIONAL MATCH (h)<-[:AT_HOSPITAL]-(c2:Claim)<-[:FILED_CLAIM]-(p:Person)
        WITH total_claims, total_approved, petty_count, avg_dur, unique_diag,
             count(DISTINCT p.user_id) AS unique_patients
        RETURN total_claims, total_approved, petty_count,
               coalesce(avg_dur, 0) AS avg_dur,
               size(unique_diag) AS diag_diversity,
               unique_patients
    """
    data = run_query(cypher)
    if not data:
        return {"data": [0, 0, 0, 0, 0]}

    r = data[0]
    tc = r.get("total_claims", 0) or 0
    pc = r.get("petty_count", 0) or 0
    ta = r.get("total_approved", 0) or 0
    dur = r.get("avg_dur", 0) or 0
    dd = r.get("diag_diversity", 0) or 0
    up = r.get("unique_patients", 1) or 1

    volume = max(0, min(100, (tc / 200.0) * 100))
    petty_ratio = 0 if tc == 0 else max(0, min(100, (pc / tc) * 100))
    avg_cost = max(0, min(100, (ta / (tc + 1)) / 50000.0))  # 5M per claim = 100
    duration_score = max(0, min(100, (dur / 5.0) * 33))
    concentration = max(0, min(100, (tc / (up + 1)) / 3.0 * 100))  # 3 claims/patient = 100

    return {
        "data": [round(volume, 1), round(petty_ratio, 1), round(avg_cost, 1),
                 round(duration_score, 1), round(concentration, 1)],
        "labels": ["Lưu lượng HS", "Tỷ lệ HS vụn", "Chi phí TB", "Thời gian đ.trị", "Tập trung BN"]
    }


@app.get("/api/doctor-risk-radar/{doctor_name}")
def api_doctor_risk_radar(doctor_name: str):
    """Risk radar for a doctor."""
    cypher = f"""
        MATCH (d:Doctor {{doctor_name: '{doctor_name}'}})<-[:EXAMINED_BY]-(c:Claim)
        WITH d,
             count(c) AS total_claims,
             sum(coalesce(c.claim_amount_approved, 0)) AS total_approved,
             sum(CASE WHEN c.claim_amount_vien_phi < 200000 AND c.claim_amount_vien_phi > 0 THEN 1 ELSE 0 END) AS petty_count,
             avg(c.treatment_duration_days) AS avg_dur,
             collect(DISTINCT c.discharge_diagnosis) AS unique_diag
        OPTIONAL MATCH (d)<-[:EXAMINED_BY]-(c2:Claim)<-[:FILED_CLAIM]-(p:Person)
        WITH total_claims, total_approved, petty_count, avg_dur, unique_diag,
             count(DISTINCT p.user_id) AS unique_patients
        RETURN total_claims, total_approved, petty_count,
               coalesce(avg_dur, 0) AS avg_dur,
               size(unique_diag) AS diag_diversity,
               unique_patients
    """
    data = run_query(cypher)
    if not data:
        return {"data": [0, 0, 0, 0, 0]}

    r = data[0]
    tc = r.get("total_claims", 0) or 0
    pc = r.get("petty_count", 0) or 0
    ta = r.get("total_approved", 0) or 0
    dur = r.get("avg_dur", 0) or 0
    dd = r.get("diag_diversity", 0) or 0
    up = r.get("unique_patients", 1) or 1

    volume = max(0, min(100, (tc / 100.0) * 100))
    petty_ratio = 0 if tc == 0 else max(0, min(100, (pc / tc) * 100))
    avg_cost = max(0, min(100, (ta / (tc + 1)) / 50000.0))
    duration_score = max(0, min(100, (dur / 5.0) * 33))
    diag_narrow = max(0, min(100, (1 - dd / (tc + 1)) * 100))  # fewer diagnoses = more suspicious

    return {
        "data": [round(volume, 1), round(petty_ratio, 1), round(avg_cost, 1),
                 round(duration_score, 1), round(diag_narrow, 1)],
        "labels": ["Lưu lượng HS", "Tỷ lệ HS vụn", "Chi phí TB", "Thời gian đ.trị", "Đơn điệu bệnh lý"]
    }


@app.get("/api/syndicates")
def api_syndicates():
    """Cytoscape.js-ready nodes/edges for shared bank/phone clusters (top clusters only)."""

    d = get_driver()

    # Shared bank edges — only top 30 largest clusters
    bank_records, _, _ = d.execute_query("""
        MATCH (p:Person)-[:RECEIVES_TO]->(b:BankAccount)
        WITH b, collect(p) AS all_members
        WHERE size(all_members) > 3
        WITH b, all_members ORDER BY size(all_members) DESC LIMIT 10
        WITH b, all_members[0..10] AS members
        UNWIND members AS p1
        UNWIND members AS p2
        WITH p1, p2, b
        WHERE p1.user_id < p2.user_id
        RETURN DISTINCT p1.user_id AS source, p1.full_name AS source_name,
               p2.user_id AS target, p2.full_name AS target_name,
               b.account_number AS shared_bank, b.beneficiary_name AS bank_owner
    """, database_=NEO4J_DB)

    # Shared phone edges — only top 30 largest clusters
    phone_records, _, _ = d.execute_query("""
        MATCH (p:Person)
        WHERE p.phone_number IS NOT NULL AND p.phone_number <> 'Unknown'
        WITH p.phone_number AS phone, collect(p) AS all_members
        WHERE size(all_members) > 5
        WITH phone, all_members ORDER BY size(all_members) DESC LIMIT 10
        WITH phone, all_members[0..10] AS members
        UNWIND members AS p1
        UNWIND members AS p2
        WITH p1, p2, phone
        WHERE p1.user_id < p2.user_id
        RETURN DISTINCT p1.user_id AS source, p1.full_name AS source_name,
               p2.user_id AS target, p2.full_name AS target_name,
               phone AS shared_phone
    """, database_=NEO4J_DB)

    nodes = {}
    edges = []

    for r in bank_records:
        src, tgt = r["source"], r["target"]
        nodes[src] = {"id": src, "label": r["source_name"], "type": "Person"}
        nodes[tgt] = {"id": tgt, "label": r["target_name"], "type": "Person"}
        bank_id = f"B:{r['shared_bank']}"
        nodes[bank_id] = {"id": bank_id, "label": r["bank_owner"] or r["shared_bank"], "type": "Bank"}
        edges.append({"source": src, "target": bank_id, "type": "SHARED_BANK"})
        edges.append({"source": tgt, "target": bank_id, "type": "SHARED_BANK"})

    for r in phone_records:
        src, tgt = r["source"], r["target"]
        nodes[src] = {"id": src, "label": r["source_name"], "type": "Person"}
        nodes[tgt] = {"id": tgt, "label": r["target_name"], "type": "Person"}
        phone_id = f"PH:{r['shared_phone']}"
        nodes[phone_id] = {"id": phone_id, "label": r["shared_phone"], "type": "Phone"}
        edges.append({"source": src, "target": phone_id, "type": "SHARED_PHONE"})
        edges.append({"source": tgt, "target": phone_id, "type": "SHARED_PHONE"})

    # Deduplicate edges
    seen = set()
    unique_edges = []
    for e in edges:
        key = (e["source"], e["target"], e["type"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)

    return {
        "nodes": list(nodes.values()),
        "edges": unique_edges,
    }


@app.get("/api/diagnosis-stats")
def api_diagnosis_stats():
    """Thống kê toàn bộ bệnh lý: count, avg, median, min, max, max_vs_median."""
    rows = cached_query("diagnosis_stats", """
        MATCH (c:Claim)
        WHERE c.discharge_diagnosis IS NOT NULL AND c.discharge_diagnosis <> ''
          AND c.claim_amount_vien_phi > 0
        WITH c.discharge_diagnosis AS diagnosis,
             count(c) AS cnt,
             avg(c.claim_amount_vien_phi) AS avg_amt,
             percentileCont(c.claim_amount_vien_phi, 0.5) AS median_amt,
             min(c.claim_amount_vien_phi) AS min_amt,
             max(c.claim_amount_vien_phi) AS max_amt
        RETURN diagnosis, cnt, round(avg_amt) AS avg_amt,
               round(median_amt) AS median_amt,
               round(min_amt) AS min_amt, round(max_amt) AS max_amt
        ORDER BY cnt DESC
    """)
    result = []
    for r in rows:
        median = r.get("median_amt") or 0
        max_amt = r.get("max_amt") or 0
        r["max_vs_median"] = round(max_amt / median, 1) if median > 0 else 0
        if r["max_vs_median"] >= 3:
            result.append(r)
    return result


@app.get("/api/diagnosis-detail/{diagnosis}")
def api_diagnosis_detail(diagnosis: str):
    """Chi tiết từng hồ sơ của 1 bệnh lý."""
    rows = run_query(f"""
        MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim)
        WHERE c.discharge_diagnosis = '{diagnosis}' AND c.claim_amount_vien_phi > 0
        OPTIONAL MATCH (c)-[:AT_HOSPITAL]->(h:Hospital)
        RETURN p.user_id AS user_id, p.full_name AS ho_ten,
               c.claim_id AS claim_id, round(c.claim_amount_vien_phi) AS so_tien,
               c.claim_date AS ngay_claim,
               h.hospital_code AS benh_vien
        ORDER BY c.claim_amount_vien_phi DESC LIMIT 200
    """)
    return rows


@app.get("/api/network/phone/{phone}")
def api_network_phone(phone: str):
    """Explode all connections for a shared phone number."""
    rows = run_query(f"""
        MATCH (p:Person {{phone_number: '{phone}'}})
        OPTIONAL MATCH (p)-[:FILED_CLAIM]->(c:Claim)
        OPTIONAL MATCH (c)-[:AT_HOSPITAL]->(h:Hospital)
        OPTIONAL MATCH (p)-[:RECEIVES_TO]->(b:BankAccount)
        RETURN p.user_id AS person_id, p.full_name AS person_name,
               c.claim_id AS claim_id, c.claim_amount_vien_phi AS amount,
               c.discharge_diagnosis AS diagnosis, c.claim_date AS claim_date,
               h.hospital_code AS hospital, b.account_number AS bank
    """)

    nodes = {}
    edges = []

    # Central Phone node
    phone_id = f"PH:{phone}"
    nodes[phone_id] = {"id": phone_id, "label": phone, "type": "Phone"}

    for r in rows:
        pid = r.get("person_id")
        if pid:
            nodes[pid] = {"id": pid, "label": r.get("person_name", pid), "type": "Person"}
            edges.append({"source": pid, "target": phone_id, "type": "SHARED_PHONE"})

            cid = r.get("claim_id")
            if cid:
                nodes[cid] = {
                    "id": cid, "label": f"{cid}\n{r.get('amount', 0)}",
                    "type": "Claim", "amount": r.get("amount", 0)
                }
                edges.append({"source": pid, "target": cid, "type": "FILED_CLAIM"})

                hosp = r.get("hospital")
                if hosp:
                    hid = f"H:{hosp}"
                    nodes[hid] = {"id": hid, "label": hosp, "type": "Hospital"}
                    edges.append({"source": cid, "target": hid, "type": "AT_HOSPITAL"})

            bank = r.get("bank")
            if bank:
                bid = f"B:{bank}"
                nodes[bid] = {"id": bid, "label": bank, "type": "Bank"}
                edges.append({"source": pid, "target": bid, "type": "RECEIVES_TO"})

    return {"nodes": list(nodes.values()), "edges": edges}


@app.get("/api/network/{user_id}")
def api_network(user_id: str):
    """Ego-network drill-down — full ontology: Hospital, BankAccount, Doctor, Expense."""
    rows = run_query(f"""
        MATCH (p:Person {{user_id: '{user_id}'}})-[:FILED_CLAIM]->(c:Claim)
        OPTIONAL MATCH (c)-[:AT_HOSPITAL]->(h:Hospital)
        OPTIONAL MATCH (c)-[:EXAMINED_BY]->(d:Doctor)
        RETURN p.user_id AS person_id, p.full_name AS person_name,
               c.claim_id AS claim_id, c.claim_amount_vien_phi AS amount,
               c.discharge_diagnosis AS diagnosis, c.claim_date AS claim_date,
               h.hospital_code AS hospital,
               d.doctor_name AS doctor
    """)

    # Fetch bank separately (linked to Person, not Claim)
    bank_rows = run_query(f"""
        MATCH (p:Person {{user_id: '{user_id}'}})-[:RECEIVES_TO]->(b:BankAccount)
        RETURN b.account_number AS bank, b.beneficiary_name AS bank_owner
    """)

    nodes = {}
    edges = []

    if not rows:
        return {"nodes": [], "edges": []}

    person_name = rows[0].get("person_name", user_id)
    nodes[user_id] = {"id": user_id, "label": person_name, "type": "Person"}

    # Add bank nodes (Person -> BankAccount)
    for br in bank_rows:
        bank = br.get("bank")
        if bank:
            bid = f"B:{bank}"
            nodes[bid] = {"id": bid, "label": br.get("bank_owner", bank), "type": "Bank"}
            edges.append({"source": user_id, "target": bid, "type": "RECEIVES_TO"})

    claim_ids = set()
    for r in rows:
        cid = r.get("claim_id")
        if cid:
            nodes[cid] = {
                "id": cid, "label": f"{cid}\n{r.get('amount', 0)}",
                "type": "Claim", "amount": r.get("amount", 0),
                "diagnosis": r.get("diagnosis", ""),
                "claim_date": r.get("claim_date", ""),
            }
            edges.append({"source": user_id, "target": cid, "type": "FILED_CLAIM"})
            claim_ids.add(cid)

            hosp = r.get("hospital")
            if hosp:
                hid = f"H:{hosp}"
                nodes[hid] = {"id": hid, "label": hosp, "type": "Hospital"}
                edges.append({"source": cid, "target": hid, "type": "AT_HOSPITAL"})

            doctor = r.get("doctor")
            if doctor:
                did = f"D:{doctor}"
                nodes[did] = {"id": did, "label": doctor, "type": "Doctor"}
                edges.append({"source": cid, "target": did, "type": "EXAMINED_BY"})

    # Fetch top Expenses per claim (limit to avoid graph overload)
    if claim_ids:
        cid_list = "', '".join(claim_ids)
        exp_rows = run_query(f"""
            MATCH (c:Claim)-[:HAS_EXPENSE]->(e:ExpenseDetail)
            WHERE c.claim_id IN ['{cid_list}']
            OPTIONAL MATCH (e)-[:IS_ITEM]->(ds:DrugOrService)
            WITH c, e, ds ORDER BY e.total_amount DESC
            WITH c, collect({{e: e, ds: ds}})[0..10] AS top_expenses
            UNWIND top_expenses AS item
            RETURN c.claim_id AS claim_id,
                   id(item.e) AS eid,
                   item.ds.name AS item_name,
                   item.e.category AS category,
                   item.e.total_amount AS amount,
                   item.e.unit_price AS unit_price,
                   item.e.quantity AS quantity,
                   item.e.unit AS unit
        """)
        for er in exp_rows:
            eid = f"E:{er['eid']}"
            name = er.get("item_name") or er.get("category") or "Chi phí"
            amt = er.get("amount")
            label = f"{name[:30]}"
            if amt:
                label += f"\n{amt:,.0f}đ"
            nodes[eid] = {
                "id": eid, "label": label, "type": "Expense",
                "item_name": er.get("item_name"),
                "category": er.get("category"),
                "amount": amt,
                "unit_price": er.get("unit_price"),
                "quantity": er.get("quantity"),
                "unit": er.get("unit"),
            }
            edges.append({"source": er["claim_id"], "target": eid, "type": "HAS_EXPENSE"})

    # Deduplicate edges
    seen = set()
    unique_edges = []
    for e in edges:
        key = (e["source"], e["target"], e["type"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)

    return {"nodes": list(nodes.values()), "edges": unique_edges}


@app.get("/api/person-story/{user_id}")
def api_person_story(user_id: str):
    """Monthly stats, financials, and doctor/hospital distribution."""
    month_expr = PARSE_MONTH.replace("{date_var}", "c.claim_date")
    timeline = run_query(f"""
        MATCH (p:Person {{user_id: '{user_id}'}})-[:FILED_CLAIM]->(c:Claim)
        WHERE c.claim_date IS NOT NULL
        WITH c, {month_expr} AS month
        WITH month, count(c) AS claim_count,
             sum(c.claim_amount_vien_phi) AS req_amount,
             sum(c.claim_amount_approved) AS approved_amount
        RETURN month, claim_count,
               round(req_amount) AS req_amount,
               round(approved_amount) AS approved_amount
        ORDER BY month
    """)

    diagnoses = run_query(f"""
        MATCH (p:Person {{user_id: '{user_id}'}})-[:FILED_CLAIM]->(c:Claim)-[:DIAGNOSED_WITH]->(d:Diagnosis)
        RETURN d.icd_name AS name, count(c) AS value
        ORDER BY value DESC LIMIT 5
    """)

    hospitals = run_query(f"""
        MATCH (p:Person {{user_id: '{user_id}'}})-[:FILED_CLAIM]->(c:Claim)-[:AT_HOSPITAL]->(h:Hospital)
        RETURN h.hospital_name AS name, count(c) AS value
        ORDER BY value DESC LIMIT 5
    """)

    doctors = run_query(f"""
        MATCH (p:Person {{user_id: '{user_id}'}})-[:FILED_CLAIM]->(c:Claim)-[:EXAMINED_BY]->(dr:Doctor)
        RETURN dr.doctor_name AS name, count(c) AS value
        ORDER BY value DESC LIMIT 5
    """)

    claims = run_query(f"""
        MATCH (p:Person {{user_id: '{user_id}'}})-[:FILED_CLAIM]->(c:Claim)
        OPTIONAL MATCH (c)-[:AT_HOSPITAL]->(h:Hospital)
        RETURN c.claim_id AS claim_id, 
               toString(c.claim_date) AS date,
               c.discharge_diagnosis AS diagnosis,
               round(c.claim_amount_approved) AS amount,
               h.hospital_name AS hospital
        ORDER BY c.claim_date DESC LIMIT 20
    """)

    return {
        "timeline": timeline,
        "diagnoses": diagnoses,
        "hospitals": hospitals,
        "doctors": doctors,
        "claims": claims
    }


@app.get("/api/claim-detail/{claim_id}")
def api_claim_detail(claim_id: str):
    """Deep dive into a specific claim's expenses."""
    meta = run_query(f"""
        MATCH (c:Claim {{claim_id: '{claim_id}'}})
        OPTIONAL MATCH (p:Person)-[:FILED_CLAIM]->(c)
        OPTIONAL MATCH (c)-[:AT_HOSPITAL]->(h:Hospital)
        OPTIONAL MATCH (c)-[:EXAMINED_BY]->(dr:Doctor)
        OPTIONAL MATCH (c)-[:DIAGNOSED_WITH]->(d:Diagnosis)
        RETURN c.claim_id AS id, c.claim_date AS date,
               round(c.claim_amount_req) AS req,
               round(c.claim_amount_approved) AS approved,
               p.full_name AS person, h.hospital_name AS hospital,
               dr.doctor_name AS doctor, d.icd_name AS diagnosis
    """)

    expenses = run_query(f"""
        MATCH (c:Claim {{claim_id: '{claim_id}'}})-[:HAS_EXPENSE]->(e:ExpenseDetail)
        OPTIONAL MATCH (e)-[:IS_ITEM]->(ds:DrugOrService)
        RETURN ds.name AS item, e.category AS category,
               e.quantity AS qty, round(e.unit_price) AS price,
               round(e.median_price) AS median,
               round(e.total_amount) AS total,
               CASE WHEN e.median_price > 0 AND e.unit_price > 3 * e.median_price THEN true ELSE false END AS is_outlier
        ORDER BY is_outlier DESC, total DESC
    """)

    return {
        "meta": meta[0] if meta else {},
        "expenses": expenses
    }


@app.get("/api/waiting-period-stats")
def api_waiting_period_stats():
    """Distribution of claims by month since contract start."""
    date_expr = PARSE_DATE.replace("{date_var}", "c.claim_date")
    cypher = (
        "MATCH (p:Person)-[:HAS_CONTRACT]->(cont:Contract), "
        "(p)-[:FILED_CLAIM]->(c:Claim) "
        "WHERE cont.contract_start_date IS NOT NULL AND c.claim_date IS NOT NULL "
        "WITH c, date(cont.contract_start_date) AS start_d, "
        + date_expr + " AS claim_d "
        "WITH c, duration.between(start_d, claim_d).months AS month_offset "
        "WHERE month_offset >= 0 AND month_offset < 12 "
        "RETURN month_offset, "
        "count(c) AS claim_count, "
        "round(sum(coalesce(c.claim_amount_approved, 0))) AS total_approved "
        "ORDER BY month_offset"
    )
    return run_query(cypher)


@app.get("/api/waiting-period-detail/{month_index}")
def api_waiting_period_detail(month_index: int):
    """Deep dive into diseases for a specific month since contract start."""
    date_expr = PARSE_DATE.replace("{date_var}", "c.claim_date")
    # List of keywords for chronic/pre-existing diseases
    CHRONIC_KEYWORDS = [
        "ung thư", "cancer", "u ác", "neoplasm",
        "tiểu đường", "diabetes", "mãn tính", "chronic",
        "tim mạch", "cardio", "huyết áp", "hypertension",
        "thận", "renal", "gan", "hepatic", "xơ gan",
        "khớp", "arthritis", "thoát vị", "hernia",
        "dây chằng", "acl", "meniscus"
    ]
    
    # We use a regex for the chronic filter in Cypher
    chronic_regex = "(?i).*(" + "|".join(CHRONIC_KEYWORDS) + ").*"
    
    cypher = (
        "MATCH (p:Person)-[:HAS_CONTRACT]->(cont:Contract), "
        "(p)-[:FILED_CLAIM]->(c:Claim)-[:DIAGNOSED_WITH]->(d:Diagnosis) "
        "WHERE cont.contract_start_date IS NOT NULL AND c.claim_date IS NOT NULL "
        "WITH p, c, d, date(cont.contract_start_date) AS start_d, "
        + date_expr + " AS claim_d "
        "WITH p, c, d, "
        "duration.between(start_d, claim_d).months AS month_offset "
        "WHERE month_offset = " + str(month_index) + " "
        "RETURN d.icd_name AS disease, "
        "p.user_id AS user_id, "
        "p.full_name AS person_name, "
        "c.claim_id AS claim_id, "
        "round(c.claim_amount_approved) AS amount, "
        "toString(c.claim_date) AS date, "
        "CASE WHEN d.icd_name =~ '" + chronic_regex + "' THEN true ELSE false END AS is_chronic "
        "ORDER BY is_chronic DESC, amount DESC "
        "LIMIT 200"
    )
    return run_query(cypher)


@app.get("/api/reports/top-hospitals")
def api_report_hospitals():
    """Top 20 Hospitals by various metrics."""
    cypher = """
        MATCH (h:Hospital)<-[:AT_HOSPITAL]-(c:Claim)
        RETURN h.hospital_name AS name,
               count(c) AS frequency,
               round(sum(c.claim_amount_vien_phi)) AS total_req,
               round(sum(c.claim_amount_approved)) AS total_approved,
               round(avg(c.claim_amount_approved)) AS avg_approved
        ORDER BY frequency DESC LIMIT 20
    """
    return run_query(cypher)


@app.get("/api/reports/top-diagnoses")
def api_report_diagnoses():
    """Top 20 Diagnoses with monthly distribution."""
    # Use the PARSE_MONTH snippet for robust date handling
    parse_month_cypher = PARSE_MONTH.format(date_var="c.claim_date")
    cypher = f"""
        MATCH (d:Diagnosis)<-[:DIAGNOSED_WITH]-(c:Claim)
        WHERE c.claim_date IS NOT NULL AND c.claim_date <> ""
        WITH d, c, {parse_month_cypher} AS yyyy_mm
        WITH d, count(c) AS cases,
             round(sum(c.claim_amount_vien_phi)) AS total_req,
             round(sum(c.claim_amount_approved)) AS total_approved,
             collect(toInteger(split(yyyy_mm, '-')[1])) AS months
        RETURN d.icd_name AS name, d.icd_code AS code,
               cases, total_req, total_approved,
               months
        ORDER BY cases DESC LIMIT 20
    """
    rows = run_query(cypher)
    
    for r in rows:
        dist = [0] * 12
        for m in r.get('months', []):
            try:
                m_int = int(m)
                if 1 <= m_int <= 12:
                    dist[m_int - 1] += 1
            except (ValueError, TypeError):
                continue
        r['seasonality'] = dist
        del r['months']
    return rows


@app.get("/api/reports/waiting-anomalies")
def api_waiting_anomalies():
    """Identify users who claim immediately after registration."""
    # Use PARSE_DATE for both to ensure they are Neo4j Date objects
    parse_start = PARSE_DATE.replace("{date_var}", "cont.contract_start_date")
    parse_claim = PARSE_DATE.replace("{date_var}", "c.claim_date")
    
    cypher = """
        MATCH (p:Person)-[:HAS_CONTRACT]->(cont:Contract),
              (p)-[:FILED_CLAIM]->(c:Claim)
        WHERE cont.contract_start_date IS NOT NULL AND c.claim_date IS NOT NULL
          AND cont.contract_start_date <> "" AND c.claim_date <> ""
        WITH p, c, cont, PARSE_START AS d_start, PARSE_CLAIM AS d_claim
        WITH p, c, cont, duration.between(d_start, d_claim).days AS days_diff
        WHERE days_diff >= 0 AND days_diff <= 7
        RETURN p.user_id AS user_id, p.full_name AS person,
               c.claim_id AS claim_id, toString(c.claim_date) AS claim_date,
               toString(cont.contract_start_date) AS start_date,
               days_diff, round(c.claim_amount_approved) AS amount
        ORDER BY days_diff ASC, amount DESC
        LIMIT 100
    """.replace("PARSE_START", parse_start).replace("PARSE_CLAIM", parse_claim)
    return run_query(cypher)


@app.get("/api/timeline")
def api_timeline():
    """Monthly claim aggregation for ECharts."""
    month_expr = PARSE_MONTH.replace("{date_var}", "c.claim_date")
    rows = cached_query("timeline", f"""
        MATCH (c:Claim)
        WHERE c.claim_date IS NOT NULL
        WITH c, {month_expr} AS month
        WITH month, count(c) AS claim_count,
             sum(c.claim_amount_vien_phi) AS total_amount,
             avg(c.claim_amount_vien_phi) AS avg_amount
        RETURN month, claim_count, round(total_amount) AS total_amount,
               round(avg_amount) AS avg_amount
        ORDER BY month
    """)
    return rows


@app.get("/api/heatmap")
def api_heatmap():
    """Day-of-month x month matrix for ECharts heatmap."""
    month_expr = PARSE_MONTH.replace("{date_var}", "c.claim_date")
    rows = cached_query("heatmap", f"""
        MATCH (c:Claim)
        WHERE c.claim_date IS NOT NULL
        WITH c, {month_expr} AS month,
             CASE WHEN c.claim_date CONTAINS '/'
                  THEN toInteger(split(split(c.claim_date, ' ')[0], '/')[1])
                  ELSE toInteger(substring(c.claim_date, 8, 2))
             END AS day_of_month
        WITH month, day_of_month, count(*) AS cnt
        RETURN month, day_of_month, cnt
        ORDER BY month, day_of_month
    """)
    return rows


# ── STATIC FILES & STARTUP ───────────────────────────────────

app.mount("/static", StaticFiles(directory="static"), name="static")



# ── GRAPH INTERACTION API ────────────────────────────────────

@app.get("/api/node-neighbors/{node_id:path}")
def api_node_neighbors_advanced(node_id: str):
    """Fetch direct neighbors of a node for expansion."""
    # Split type prefix if exists (e.g., B:123 -> type=BankAccount, id=123)
    parts = node_id.split(':', 1)
    if len(parts) > 1:
        prefix, val = parts[0], parts[1]
        # Map label prefix to Neo4j Label
        label_map = {"B": "BankAccount", "H": "Hospital", "PH": "Phone", "D": "Doctor"}
        neo_label = label_map.get(prefix, "Person")
        ident_key = "account_number" if prefix == "B" else \
                    "hospital_code" if prefix == "H" else \
                    "phone_number" if prefix == "PH" else \
                    "doctor_name" if prefix == "D" else "user_id"

        if prefix == "PH":
            match_clause = f"MATCH (n:Person {{{ident_key}: '{val}'}})"
        else:
            match_clause = f"MATCH (n:{neo_label} {{{ident_key}: '{val}'}})"
    else:
        match_clause = f"MATCH (n:Person {{user_id: '{node_id}'}})"

    cypher = f"""
        {match_clause}
        MATCH (n)-[r]-(m)
        RETURN n, r, m LIMIT 50
    """

    records = run_query(cypher)
    nodes = {}
    edges = []

    for r in records:
        # Target node (m)
        m_node = r['m']
        m_labels = list(m_node.labels)
        m_type = m_labels[0] if m_labels else "Unknown"

        # Determine human-readable label and unique ID
        m_props = dict(m_node)
        m_id = m_props.get("user_id") or m_props.get("claim_id") or \
               m_props.get("account_number") or m_props.get("hospital_code") or \
               m_props.get("doctor_name") or str(m_props.get("phone_number"))

        nodes[m_id] = {
            "id": m_id,
            "label": str(m_props.get("full_name") or m_props.get("doctor_name") or m_id),
            "type": m_type,
            "properties": m_props
        }

        edges.append({
            "source": node_id,
            "target": m_id,
            "type": r['r'].type
        })

    return {"nodes": list(nodes.values()), "edges": edges}


@app.get("/api/phone-story/{phone}")
def api_phone_story(phone: str):
    """Aggregate statistics for a shared phone hub."""
    month_expr = PARSE_MONTH.replace("{date_var}", "c.claim_date")
    stats = run_query(f"""
        MATCH (p:Person {{phone_number: '{phone}'}})
        OPTIONAL MATCH (p)-[:FILED_CLAIM]->(c:Claim)
        RETURN count(DISTINCT p) AS num_people,
               count(c) AS num_claims,
               sum(c.claim_amount_vien_phi) AS total_amount,
               collect(DISTINCT p.full_name)[0..5] AS member_preview
    """)

    timeline = run_query(f"""
        MATCH (p:Person {{phone_number: '{phone}'}})-[:FILED_CLAIM]->(c:Claim)
        WHERE c.claim_date IS NOT NULL
        WITH c, {month_expr} AS month
        WITH month, count(c) AS claim_count, sum(c.claim_amount_vien_phi) AS total_amount
        RETURN month, claim_count, round(total_amount) AS total_amount
        ORDER BY month
    """)

    diagnoses = run_query(f"""
        MATCH (p:Person {{phone_number: '{phone}'}})-[:FILED_CLAIM]->(c:Claim)
        WHERE c.discharge_diagnosis IS NOT NULL
        RETURN c.discharge_diagnosis AS name, count(c) AS value
        ORDER BY value DESC LIMIT 5
    """)

    return {
        "stats": stats[0] if stats else {},
        "timeline": timeline,
        "diagnoses": diagnoses
    }



@app.get("/api/reports/anti-selection-diagnoses")
def api_report_anti_selection_diag():
    """Top 10 Diagnoses for claims within first 90 days of insurance."""
    parse_start = PARSE_DATE.replace("{date_var}", "cont.contract_start_date")
    parse_claim = PARSE_DATE.replace("{date_var}", "c.claim_date")
    
    cypher = """
        MATCH (cont:Contract)<-[:HAS_CONTRACT]-(p:Person)-[:FILED_CLAIM]->(c:Claim)-[:DIAGNOSED_WITH]->(d:Diagnosis)
        WHERE cont.contract_start_date IS NOT NULL AND c.claim_date IS NOT NULL
          AND cont.contract_start_date <> "" AND c.claim_date <> ""
        WITH d, duration.between(PARSE_START, PARSE_CLAIM).days AS diff
        WHERE diff >= 0 AND diff <= 90
        RETURN d.icd_name AS name, count(*) AS value
        ORDER BY value DESC LIMIT 10
    """.replace("PARSE_START", parse_start).replace("PARSE_CLAIM", parse_claim)
    return run_query(cypher)


@app.get("/api/reports/diagnosis-hospitals/{icd}")
def api_report_diag_hospitals(icd: str):
    """Top 10 Hospitals for a specific Diagnosis."""
    cypher = f"""
        MATCH (d:Diagnosis {{icd_code: '{icd}'}})<-[:DIAGNOSED_WITH]-(c:Claim)-[:AT_HOSPITAL]->(h:Hospital)
        RETURN h.hospital_name AS name,
               count(c) AS frequency,
               round(avg(c.claim_amount_approved)) AS avg_approved
        ORDER BY frequency DESC LIMIT 10
    """
    return run_query(cypher)


# ── WEB ROUTES ────────────────────────────────────────────────

@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")

@app.on_event("shutdown")
def shutdown():
    global driver
    if driver:
        driver.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
