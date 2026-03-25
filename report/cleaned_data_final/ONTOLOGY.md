# Ontology - Hệ thống Phát hiện Trục lợi Bảo hiểm

> **Version:** 1.0
> **Ngày tạo:** 2026-03-12
> **Database:** Neo4j (Graph Database)
> **Nguồn dữ liệu:** DataNDBH, DataHoSoBoiThuong, DataChiPhi

---

## 1. Tổng quan kiến truc (Architecture Overview)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         FRAUD DETECTION GRAPH SCHEMA                            │
│                                                                                 │
│                          ┌──────────────┐                                       │
│                          │  BankAccount │                                       │
│                          └──────┬───────┘                                       │
│                                 │                                               │
│                           RECEIVES_TO                                           │
│                                 │                                               │
│  ┌──────────┐  HAS_CONTRACT  ┌──┴───────┐  FILED_CLAIM  ┌─────────────┐       │
│  │ Contract │◄──────────────│  Person  │──────────────►│   Claim     │       │
│  └──────────┘               └──────────┘               └──────┬──────┘       │
│                                                           │   │   │          │
│                              ┌─────────────────────┬──────┘   │   └───┐      │
│                              │                     │          │       │      │
│                        DIAGNOSED_WITH        AT_HOSPITAL  EXAMINED_BY │      │
│                              │                     │          │       │      │
│                        ┌─────┴─────┐      ┌───────┴──┐  ┌───┴────┐  │      │
│                        │ Diagnosis │      │ Hospital │  │ Doctor │  │      │
│                        └───────────┘      └──────────┘  └────────┘  │      │
│                                                                      │      │
│                                                              HAS_EXPENSE    │
│                                                                      │      │
│                                                             ┌────────┴───┐  │
│                                                             │  Expense   │  │
│                                                             │  Detail    │  │
│                                                             └──────┬─────┘  │
│                                                                    │        │
│                                                              IS_ITEM        │
│                                                                    │        │
│                                                          ┌─────────┴──────┐ │
│                                                          │ DrugOrService  │ │
│                                                          └────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Danh sach Node (Node Definitions)

### 2.1 `Person` — Nguoi duoc bao hiem (NDBH)

> **Nguon:** `DataNDBH_Cleaned_Final.csv`
> **Mo ta:** Dai dien cho mot ca nhan tham gia bao hiem. Day la node trung tam cua he thong, la chu the thuc hien hanh vi boi thuong.
> **Key:** `user_id`

| Thuoc tinh | Kieu du lieu | Mo ta | Vai tro trong phat hien gian lan |
|---|---|---|---|
| `user_id` | UUID (String) | Ma dinh danh duy nhat cua nguoi duoc bao hiem | **Primary Key** — Lien ket chinh giua cac bang |
| `identity_number` | String | So CMND/CCCD | Phat hien trung lap danh tinh, mot nguoi dung nhieu ho so |
| `full_name` | String | Ho va ten day du | Doi chieu voi ten tren ho so boi thuong |
| `date_of_birth` | Date | Ngay thang nam sinh | Tinh tuoi, phat hien bat thuong ve do tuoi |
| `age` | Integer | Tuoi (da tinh san) | Phan tich tuoi — nhom tuoi nao co ty le claim cao bat thuong |
| `gender` | String | Gioi tinh | Phan tich theo gioi tinh |
| `address` | String | Dia chi cu tru | Phat hien cum dia ly — nhieu nguoi cung dia chi |
| `phone_number` | String | So dien thoai | Phat hien trung so dien thoai giua nhieu nguoi |
| `email` | String | Dia chi email | Phat hien trung email |
| `salary` | Float | Muc luong | So sanh luong vs phi bao hiem vs so tien boi thuong |
| `active` | Boolean | Trang thai hop dong con hieu luc | Kiem tra claim tren hop dong het han |
| `created_at` | Datetime | Ngay tao ban ghi | Theo doi thoi gian |

---

### 2.2 `Contract` — Hop dong bao hiem

> **Nguon:** `DataNDBH_Cleaned_Final.csv` (tach tu bang NDBH)
> **Mo ta:** Dai dien cho mot hop dong bao hiem gan voi nguoi duoc bao hiem. Mot nguoi co the co nhieu hop dong.
> **Key:** `contract_id`

| Thuoc tinh | Kieu du lieu | Mo ta | Vai tro trong phat hien gian lan |
|---|---|---|---|
| `contract_id` | UUID (String) | Ma hop dong duy nhat | **Primary Key** |
| `so_hop_dong` | String | So hop dong nghiep vu (ma noi bo) | Doi chieu voi he thong nghiep vu |
| `contract_level` | Integer | Cap do hop dong (1, 2, 3...) | Cap do cao = quyen loi lon = rui ro cao hon |
| `contract_start_date` | Date | Ngay bat dau hieu luc | Tinh thoi gian tham gia truoc khi claim |
| `contract_end_date` | Date | Ngay het hieu luc | Phat hien claim sau khi het han |
| `premium_paid` | Float (VND) | Phi bao hiem da dong (can `/100`) | **Core** — So sanh premium vs claim amount |
| `remaining_benefit_limit` | Float (VND) | Han muc quyen loi con lai | Phat hien claim vuot han muc |

---

### 2.3 `Claim` — Ho so boi thuong

> **Nguon:** `DataHoSoBoiThuong_Cleaned_Final.csv`
> **Mo ta:** Dai dien cho mot yeu cau boi thuong bao hiem. Day la node quan trong nhat de phat hien gian lan.
> **Key:** `claim_id`

| Thuoc tinh | Kieu du lieu | Mo ta | Vai tro trong phat hien gian lan |
|---|---|---|---|
| `claim_id` | UUID (String) | Ma ho so boi thuong duy nhat | **Primary Key** |
| `claim_number` | String | So ho so nghiep vu (VD: BT/30899) | Doi chieu noi bo |
| `claim_date` | Datetime | Ngay nop ho so boi thuong | Phat hien cum thoi gian — nhieu claim cung luc |
| `claim_type` | Integer | Loai yeu cau boi thuong (1, 2) | Phan loai de phan tich theo nhom |
| `claim_status` | String | Trang thai xu ly ho so | Theo doi tien trinh |
| `approval_status` | String | Trang thai phe duyet | Phan tich ty le tu choi |
| `claim_amount_req` | Float (VND) | So tien yeu cau boi thuong | **Core** — So sanh voi so tien duyet |
| `claim_amount_req_raw` | Float (VND) | So tien yeu cau goc (truoc xu ly) | Doi chieu truoc/sau xu ly |
| `claim_amount_approved` | Float (VND) | So tien duoc phe duyet (can `/100`) | **Core** — Chenh lech voi yeu cau |
| `claim_amount_approved_orig` | Float (VND) | So tien phe duyet goc (can `/100`) | Doi chieu |
| `claim_amount_vien_phi` | Float (VND) | So tien vien phi | So sanh voi tong chi phi chi tiet |
| `denial_amount` | Float (VND) | So tien bi tu choi | Phan tich ly do tu choi |
| `median_claim_val` | Float (VND) | Gia tri trung vi claim (can `/100`) | **Core** — Benchmark de so sanh |
| `visit_date` | Date | Ngay kham/nhap vien | Phat hien ngay kham trung lap |
| `admission_date` | Date | Ngay nhap vien | Tinh thoi gian nam vien |
| `discharge_date` | Date | Ngay xuat vien | Tinh thoi gian nam vien |
| `treatment_duration_days` | Integer | So ngay dieu tri | Phat hien nam vien qua lau/ngan |
| `visit_type` | String | Ma loai kham | Phan loai |
| `visit_type_name` | String | Ten loai kham (Noi tru/Ngoai tru) | Phan tich theo hinh thuc |
| `clinical_notes` | String | Ghi chu lam sang | Phan tich van ban — NLP |
| `discharge_diagnosis` | String | Chan doan xuat vien | Doi chieu voi ma ICD |
| `actual_receipt_date` | Date | Ngay nhan chung tu thuc te | Phat hien chenh lech thoi gian |
| `insurer_id` | UUID (String) | Ma nha bao hiem | Lien ket voi he thong |

---

### 2.4 `Diagnosis` — Chan doan benh (ICD)

> **Nguon:** Trich xuat tu `DataHoSoBoiThuong_Cleaned_Final.csv`
> **Mo ta:** Dai dien cho ma benh theo he thong phan loai quoc te ICD-10. Mot claim co the co nhieu chan doan.
> **Key:** `icd_code`

| Thuoc tinh | Kieu du lieu | Mo ta | Vai tro trong phat hien gian lan |
|---|---|---|---|
| `icd_code` | String | Ma benh ICD-10 (VD: R25.8, E78) | **Primary Key** — Phat hien ma benh bi lam dung |
| `icd_name` | String | Ten benh tuong ung | Mo ta benh |

---

### 2.5 `Hospital` — Co so y te

> **Nguon:** Trich xuat tu `DataHoSoBoiThuong_Cleaned_Final.csv`
> **Mo ta:** Dai dien cho benh vien/phong kham noi thuc hien dieu tri. La diem nut quan trong de phat hien cau ket.
> **Key:** `hospital_code`

| Thuoc tinh | Kieu du lieu | Mo ta | Vai tro trong phat hien gian lan |
|---|---|---|---|
| `hospital_code` | String | Ma co so y te | **Primary Key** — Phat hien benh vien co ty le gian lan cao |

---

### 2.6 `Doctor` — Bac si

> **Nguon:** Trich xuat tu `DataHoSoBoiThuong_Cleaned_Final.csv`
> **Mo ta:** Dai dien cho bac si kham/dieu tri. Mot bac si co the lien quan den nhieu claim.
> **Key:** `doctor_name`

| Thuoc tinh | Kieu du lieu | Mo ta | Vai tro trong phat hien gian lan |
|---|---|---|---|
| `doctor_name` | String | Ten bac si | **Primary Key** — Phat hien bac si co nhieu claim bat thuong |
| `role` | String | Vai tro (kham/dieu tri) | Phan biet bac si kham vs bac si dieu tri |

---

### 2.7 `ExpenseDetail` — Chi tiet chi phi

> **Nguon:** `DataChiPhi_Cleaned_Final.csv`
> **Mo ta:** Dai dien cho tung dong chi phi cu the trong mot ho so boi thuong (thuoc, dich vu, vat tu...).
> **Key:** `detail_id`

| Thuoc tinh | Kieu du lieu | Mo ta | Vai tro trong phat hien gian lan |
|---|---|---|---|
| `detail_id` | UUID (String) | Ma chi tiet chi phi duy nhat | **Primary Key** |
| `quantity` | Float | So luong | Phat hien so luong bat thuong |
| `unit` | String | Don vi tinh (Vien, Chai, Tuyp...) | Kiem tra tinh hop ly |
| `unit_price` | Float (VND) | Don gia | **Core** — So sanh voi gia thi truong (median_price) |
| `total_amount` | Float (VND) | Thanh tien (quantity x unit_price) | **Core** — Kiem tra tinh toan |
| `item_type` | String | Loai hang muc (THUOC, KHAC) | Phan loai de phan tich |
| `category` | String | Danh muc | Phan loai chi tiet hon |
| `benefit_id` | String | Ma quyen loi ap dung | Lien ket voi quyen loi hop dong |
| `exclusion_amount` | Float (VND) | So tien loai tru | Phan tich so tien khong duoc chi tra |
| `median_price` | Float (VND) | Gia trung vi tham chieu | **Core** — Benchmark phat hien gia cao bat thuong |
| `created_at` | Datetime | Ngay tao ban ghi | Theo doi thoi gian |

---

### 2.8 `DrugOrService` — Thuoc / Dich vu y te

> **Nguon:** Trich xuat tu `DataChiPhi_Cleaned_Final.csv`
> **Mo ta:** Dai dien cho mot loai thuoc hoac dich vu y te cu the. Dung de phan tich gia ca va tan suat su dung.
> **Key:** `drug_or_service_name`

| Thuoc tinh | Kieu du lieu | Mo ta | Vai tro trong phat hien gian lan |
|---|---|---|---|
| `drug_or_service_name` | String | Ten thuoc hoac dich vu | **Primary Key** — Phat hien thuoc bi lam dung |

---

### 2.9 `BankAccount` — Tai khoan ngan hang

> **Nguon:** Trich xuat tu `DataNDBH_Cleaned_Final.csv`
> **Mo ta:** Tai khoan nhan tien boi thuong. Nhieu nguoi dung chung tai khoan la dau hieu gian lan manh.
> **Key:** `beneficiary_account`

| Thuoc tinh | Kieu du lieu | Mo ta | Vai tro trong phat hien gian lan |
|---|---|---|---|
| `beneficiary_account` | String | So tai khoan thu huong | **Primary Key** — Phat hien nhieu nguoi chung tai khoan |
| `bank_code` | String | Ma ngan hang | Phan tich theo ngan hang |
| `beneficiary_name` | String | Ten chu tai khoan | Doi chieu voi ten NDBH |

---

## 3. Danh sach moi quan he (Relationship Definitions)

### 3.1 Relationship Diagram (Chi tiet)

```
                    ┌───────────────────────────────────────────┐
                    │            FRAUD DETECTION GRAPH          │
                    └───────────────────────────────────────────┘

  (Person)──[:HAS_CONTRACT]──►(Contract)
     │
     ├──[:RECEIVES_TO]──►(BankAccount)
     │
     └──[:FILED_CLAIM]──►(Claim)
                            │
                            ├──[:DIAGNOSED_WITH]──►(Diagnosis)
                            │       ├── type: "primary"
                            │       └── type: "secondary"
                            │
                            ├──[:AT_HOSPITAL]──►(Hospital)
                            │
                            ├──[:EXAMINED_BY]──►(Doctor)
                            │       └── role: "exam" | "admit"
                            │
                            └──[:HAS_EXPENSE]──►(ExpenseDetail)
                                                    │
                                                    └──[:IS_ITEM]──►(DrugOrService)
```

---

### 3.2 `HAS_CONTRACT` — So huu hop dong

> **Huong:** `(Person) -[:HAS_CONTRACT]-> (Contract)`
> **Mo ta:** Mot nguoi duoc bao hiem so huu mot hoac nhieu hop dong bao hiem.
> **Cardinality:** 1:N (Mot nguoi — Nhieu hop dong)

| Thuoc tinh | Kieu du lieu | Mo ta |
|---|---|---|
| *(Khong co thuoc tinh rieng)* | — | Quan he don gian, thong tin nam tren node Contract |

**Gia tri phat hien gian lan:**
- Mot nguoi co nhieu hop dong co the claim chong cheo
- Kiem tra thoi gian giua cac hop dong

---

### 3.3 `FILED_CLAIM` — Nop ho so boi thuong

> **Huong:** `(Person) -[:FILED_CLAIM]-> (Claim)`
> **Mo ta:** Nguoi duoc bao hiem nop yeu cau boi thuong. Day la moi quan he cot loi cua he thong.
> **Cardinality:** 1:N (Mot nguoi — Nhieu claim)

| Thuoc tinh | Kieu du lieu | Mo ta |
|---|---|---|
| `contract_id` | UUID (String) | Hop dong duoc su dung cho claim nay |

**Gia tri phat hien gian lan:**
- Tan suat claim cao bat thuong cua mot nguoi
- Nhieu claim trong thoi gian ngan
- Claim tren hop dong da het han

---

### 3.4 `RECEIVES_TO` — Nhan tien vao tai khoan

> **Huong:** `(Person) -[:RECEIVES_TO]-> (BankAccount)`
> **Mo ta:** Nguoi duoc bao hiem nhan tien boi thuong vao tai khoan ngan hang.
> **Cardinality:** N:1 (Nhieu nguoi co the cung mot tai khoan)

| Thuoc tinh | Kieu du lieu | Mo ta |
|---|---|---|
| *(Khong co thuoc tinh rieng)* | — | — |

**Gia tri phat hien gian lan:**
- **CRITICAL** — Nhieu `Person` cung `RECEIVES_TO` mot `BankAccount` la dau hieu gian lan manh
- Ten `beneficiary_name` khac voi `full_name` cua Person

---

### 3.5 `AT_HOSPITAL` — Kham/dieu tri tai benh vien

> **Huong:** `(Claim) -[:AT_HOSPITAL]-> (Hospital)`
> **Mo ta:** Ho so boi thuong duoc thuc hien tai mot co so y te cu the.
> **Cardinality:** N:1 (Nhieu claim — Mot benh vien)

| Thuoc tinh | Kieu du lieu | Mo ta |
|---|---|---|
| `visit_type` | String | Hinh thuc kham (Noi tru / Ngoai tru) |
| `admission_date` | Date | Ngay nhap vien |
| `discharge_date` | Date | Ngay xuat vien |

**Gia tri phat hien gian lan:**
- Benh vien co ty le claim cao bat thuong
- Benh vien co ty le phe duyet 100%
- Nhieu benh nhan cung benh vien cung thoi diem

---

### 3.6 `DIAGNOSED_WITH` — Duoc chan doan benh

> **Huong:** `(Claim) -[:DIAGNOSED_WITH]-> (Diagnosis)`
> **Mo ta:** Ho so boi thuong gan voi mot hoac nhieu ma benh ICD-10.
> **Cardinality:** N:M (Mot claim nhieu ma benh, mot ma benh nhieu claim)

| Thuoc tinh | Kieu du lieu | Mo ta |
|---|---|---|
| `type` | String | `"primary"` hoac `"secondary"` — Phan biet chan doan chinh / phu |

**Gia tri phat hien gian lan:**
- Ma benh pho bien bat thuong tai mot benh vien
- Mot nguoi bi chan doan lap di lap lai cung ma benh
- Ma benh khong tuong thich voi loai thuoc/dich vu

---

### 3.7 `EXAMINED_BY` — Duoc kham/dieu tri boi bac si

> **Huong:** `(Claim) -[:EXAMINED_BY]-> (Doctor)`
> **Mo ta:** Ho so boi thuong co lien quan den bac si kham hoac bac si dieu tri.
> **Cardinality:** N:M (Mot claim co the co nhieu bac si)

| Thuoc tinh | Kieu du lieu | Mo ta |
|---|---|---|
| `role` | String | `"exam"` (bac si kham) hoac `"admit"` (bac si dieu tri) |

**Gia tri phat hien gian lan:**
- Bac si co so luong claim qua cao
- Bac si lien tuc ke don thuoc dat tien
- Mang luoi bac si — benh vien — benh nhan bat thuong

---

### 3.8 `HAS_EXPENSE` — Bao gom chi phi

> **Huong:** `(Claim) -[:HAS_EXPENSE]-> (ExpenseDetail)`
> **Mo ta:** Mot ho so boi thuong bao gom nhieu dong chi phi chi tiet (thuoc, dich vu, vat tu).
> **Cardinality:** 1:N (Mot claim — Nhieu dong chi phi)

| Thuoc tinh | Kieu du lieu | Mo ta |
|---|---|---|
| *(Khong co thuoc tinh rieng)* | — | Thong tin chi tiet nam tren node ExpenseDetail |

**Gia tri phat hien gian lan:**
- Tong chi phi chi tiet khac voi `claim_amount_req`
- So luong dong chi phi bat thuong (qua nhieu hoac qua it)
- Gia chi phi cao hon nhieu so voi `median_price`

---

### 3.9 `IS_ITEM` — La thuoc/dich vu

> **Huong:** `(ExpenseDetail) -[:IS_ITEM]-> (DrugOrService)`
> **Mo ta:** Chi tiet chi phi tuong ung voi mot loai thuoc hoac dich vu y te cu the.
> **Cardinality:** N:1 (Nhieu chi tiet — Mot thuoc/dich vu)

| Thuoc tinh | Kieu du lieu | Mo ta |
|---|---|---|
| *(Khong co thuoc tinh rieng)* | — | — |

**Gia tri phat hien gian lan:**
- Thuoc/dich vu co gia dao dong lon giua cac claim
- Thuoc dat tien xuat hien voi tan suat cao bat thuong
- Thuoc khong phu hop voi chan doan (ICD)

---

## 4. Mapping tu CSV sang Graph

### 4.1 Nguon goc du lieu cho tung Node

```
┌──────────────────────┬─────────────────────────────────────────┬──────────────┐
│ Node                 │ Nguon CSV                               │ Cach tao     │
├──────────────────────┼─────────────────────────────────────────┼──────────────┤
│ Person               │ DataNDBH_Cleaned_Final.csv              │ Truc tiep    │
│ Contract             │ DataNDBH_Cleaned_Final.csv              │ Tach ra      │
│ Claim                │ DataHoSoBoiThuong_Cleaned_Final.csv     │ Truc tiep    │
│ Diagnosis            │ DataHoSoBoiThuong (icd_code_primary,    │ Trich xuat   │
│                      │   icd_codes_secondary, icd_name_primary)│              │
│ Hospital             │ DataHoSoBoiThuong (hospital_code)       │ Trich xuat   │
│ Doctor               │ DataHoSoBoiThuong (doctor_name_exam,    │ Trich xuat   │
│                      │   doctor_name_admit)                    │              │
│ ExpenseDetail        │ DataChiPhi_Cleaned_Final.csv            │ Truc tiep    │
│ DrugOrService        │ DataChiPhi (drug_or_service_name)       │ Trich xuat   │
│ BankAccount          │ DataNDBH (beneficiary_account,          │ Trich xuat   │
│                      │   bank_code, beneficiary_name)          │              │
└──────────────────────┴─────────────────────────────────────────┴──────────────┘
```

### 4.2 Khoa lien ket giua cac bang CSV

```
DataNDBH.user_id ──────────────► DataHoSoBoiThuong.user_id
DataNDBH.contract_id ──────────► DataHoSoBoiThuong.contract_id
DataHoSoBoiThuong.claim_id ────► DataChiPhi.claim_id
```

---

## 5. Cac mau gian lan co the phat hien (Fraud Patterns)

### 5.1 Tu Graph Topology

| # | Mau gian lan | Truy van Graph | Mo ta |
|---|---|---|---|
| 1 | **Shared Bank Account** | Nhieu `Person` → cung `BankAccount` | Nhieu nguoi nhan tien vao cung tai khoan |
| 2 | **Doctor Ring** | `Doctor` ← nhieu `Claim` ← nhieu `Person` cung `Hospital` | Mang luoi bac si — benh nhan |
| 3 | **Hospital Cluster** | `Hospital` ← nhieu `Claim` co cung `Diagnosis` | Benh vien co cum benh bat thuong |
| 4 | **Duplicate Identity** | Nhieu `Person` cung `identity_number` hoac `phone_number` | Mot nguoi nhieu ho so |
| 5 | **Expired Contract Claim** | `Person` → `Contract`(het han) nhung van co `Claim` moi | Claim tren hop dong da het |

### 5.2 Tu Statistical Analysis

| # | Mau gian lan | Metric | Mo ta |
|---|---|---|---|
| 6 | **Price Inflation** | `unit_price` >> `median_price` | Don gia cao bat thuong so voi trung vi |
| 7 | **Claim vs Premium** | `claim_amount_approved` >> `premium_paid` | So tien boi thuong vuot xa phi dong |
| 8 | **Frequency Abuse** | Count `FILED_CLAIM` per `Person` per month | Tan suat claim cao bat thuong |
| 9 | **Duration Anomaly** | `treatment_duration_days` outlier | Thoi gian dieu tri bat thuong |
| 10 | **Amount Mismatch** | SUM(`total_amount`) != `claim_amount_req` | Tong chi tiet khong khop voi yeu cau |

---

## 6. Cypher Query mau (Neo4j)

### 6.1 Tao Node

```cypher
// Person
LOAD CSV WITH HEADERS FROM 'file:///DataNDBH_Cleaned_Final.csv' AS row
CREATE (p:Person {
  user_id: row.user_id,
  identity_number: row.identity_number,
  full_name: row.full_name,
  date_of_birth: date(row.date_of_birth),
  age: toInteger(row.age),
  gender: row.gender,
  address: row.address,
  phone_number: row.phone_number,
  email: row.email,
  salary: toFloat(row.salary),
  active: row.active,
  created_at: row.created_at
});

// Contract
LOAD CSV WITH HEADERS FROM 'file:///DataNDBH_Cleaned_Final.csv' AS row
CREATE (c:Contract {
  contract_id: row.contract_id,
  so_hop_dong: row.so_hop_dong,
  contract_level: toInteger(row.contract_level),
  contract_start_date: date(row.contract_start_date),
  contract_end_date: date(row.contract_end_date),
  premium_paid: toFloat(row.premium_paid) / 100.0,
  remaining_benefit_limit: toFloat(row.remaining_benefit_limit)
});

// Claim
LOAD CSV WITH HEADERS FROM 'file:///DataHoSoBoiThuong_Cleaned_Final.csv' AS row
CREATE (cl:Claim {
  claim_id: row.claim_id,
  claim_number: row.claim_number,
  claim_date: row.claim_date,
  claim_type: row.claim_type,
  claim_status: row.claim_status,
  approval_status: row.approval_status,
  claim_amount_req: toFloat(row.claim_amount_req),
  claim_amount_approved: toFloat(row.claim_amount_approved) / 100.0,
  claim_amount_vien_phi: toFloat(row.claim_amount_vien_phi),
  denial_amount: toFloat(row.denial_amount),
  median_claim_val: toFloat(row.median_claim_val) / 100.0,
  visit_date: row.visit_date,
  treatment_duration_days: toInteger(row.treatment_duration_days),
  visit_type_name: row.visit_type_name,
  clinical_notes: row.clinical_notes,
  discharge_diagnosis: row.discharge_diagnosis
});

// ExpenseDetail
LOAD CSV WITH HEADERS FROM 'file:///DataChiPhi_Cleaned_Final.csv' AS row
CREATE (e:ExpenseDetail {
  detail_id: row.detail_id,
  quantity: toFloat(row.quantity),
  unit: row.unit,
  unit_price: toFloat(row.unit_price),
  total_amount: toFloat(row.total_amount),
  item_type: row.item_type,
  category: row.category,
  benefit_id: row.benefit_id,
  exclusion_amount: toFloat(row.exclusion_amount),
  median_price: toFloat(row.median_price),
  created_at: row.created_at
});
```

### 6.2 Tao Relationship

```cypher
// Person -[:HAS_CONTRACT]-> Contract
MATCH (p:Person), (c:Contract)
WHERE p.user_id = c.user_id
CREATE (p)-[:HAS_CONTRACT]->(c);

// Person -[:FILED_CLAIM]-> Claim
MATCH (p:Person), (cl:Claim)
WHERE p.user_id = cl.user_id
CREATE (p)-[:FILED_CLAIM {contract_id: cl.contract_id}]->(cl);

// Person -[:RECEIVES_TO]-> BankAccount
MATCH (p:Person), (b:BankAccount)
WHERE p.beneficiary_account = b.beneficiary_account
CREATE (p)-[:RECEIVES_TO]->(b);

// Claim -[:AT_HOSPITAL]-> Hospital
MATCH (cl:Claim), (h:Hospital)
WHERE cl.hospital_code = h.hospital_code
CREATE (cl)-[:AT_HOSPITAL {
  visit_type: cl.visit_type_name,
  admission_date: cl.admission_date,
  discharge_date: cl.discharge_date
}]->(h);

// Claim -[:DIAGNOSED_WITH]-> Diagnosis (primary)
MATCH (cl:Claim), (d:Diagnosis)
WHERE cl.icd_code_primary = d.icd_code
CREATE (cl)-[:DIAGNOSED_WITH {type: "primary"}]->(d);

// Claim -[:HAS_EXPENSE]-> ExpenseDetail
MATCH (cl:Claim), (e:ExpenseDetail)
WHERE cl.claim_id = e.claim_id
CREATE (cl)-[:HAS_EXPENSE]->(e);

// ExpenseDetail -[:IS_ITEM]-> DrugOrService
MATCH (e:ExpenseDetail), (ds:DrugOrService)
WHERE e.drug_or_service_name = ds.drug_or_service_name
CREATE (e)-[:IS_ITEM]->(ds);
```

### 6.3 Truy van phat hien gian lan

```cypher
// Tim nhung nguoi dung chung tai khoan ngan hang
MATCH (p1:Person)-[:RECEIVES_TO]->(b:BankAccount)<-[:RECEIVES_TO]-(p2:Person)
WHERE p1.user_id <> p2.user_id
RETURN b.beneficiary_account, collect(DISTINCT p1.full_name) AS shared_users,
       count(DISTINCT p1) AS user_count
ORDER BY user_count DESC;

// Tim benh vien co nhieu claim bat thuong
MATCH (cl:Claim)-[:AT_HOSPITAL]->(h:Hospital)
WITH h, count(cl) AS claim_count, avg(cl.claim_amount_approved) AS avg_approved
WHERE claim_count > 50
RETURN h.hospital_code, claim_count, avg_approved
ORDER BY claim_count DESC;

// Tim chi phi co don gia cao hon 3x gia trung vi
MATCH (e:ExpenseDetail)-[:IS_ITEM]->(ds:DrugOrService)
WHERE e.median_price > 0 AND e.unit_price > e.median_price * 3
RETURN ds.drug_or_service_name, e.unit_price, e.median_price,
       e.unit_price / e.median_price AS price_ratio
ORDER BY price_ratio DESC
LIMIT 100;
```

---

## 7. Index khuyen nghi cho Neo4j

```cypher
CREATE INDEX person_uid FOR (p:Person) ON (p.user_id);
CREATE INDEX person_id_number FOR (p:Person) ON (p.identity_number);
CREATE INDEX contract_cid FOR (c:Contract) ON (c.contract_id);
CREATE INDEX claim_cid FOR (cl:Claim) ON (cl.claim_id);
CREATE INDEX expense_did FOR (e:ExpenseDetail) ON (e.detail_id);
CREATE INDEX hospital_code FOR (h:Hospital) ON (h.hospital_code);
CREATE INDEX diagnosis_icd FOR (d:Diagnosis) ON (d.icd_code);
CREATE INDEX bank_account FOR (b:BankAccount) ON (b.beneficiary_account);
CREATE INDEX drug_name FOR (ds:DrugOrService) ON (ds.drug_or_service_name);
```
