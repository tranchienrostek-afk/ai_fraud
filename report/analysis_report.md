# Báo cáo Khai phá Dữ liệu: AI-Fraud-FeatureSchema

## 1. Thông tin chung
- **Số bản ghi:** 19,259
- **Số cột:** 34

## 2. Danh sách cột và kiểu dữ liệu
| Tên cột | Kiểu dữ liệu | Số giá trị thiếu |
| :--- | :--- | :--- |
| claim_id | object | 0 |
| user_id | object | 0 |
| claim_number | object | 0 |
| full_name | object | 0 |
| identity_number | object | 0 |
| date_of_birth | object | 0 |
| address | object | 12394 |
| phone_number | int64 | 0 |
| email | object | 1 |
| claim_date | object | 0 |
| claim_amount_req | float64 | 19256 |
| claim_amount_vien_phi | int64 | 0 |
| claim_amount_approved | float64 | 50 |
| claim_status | int64 | 0 |
| approval_status | int64 | 0 |
| icd_code_primary | object | 7 |
| icd_name_primary | object | 7 |
| icd_codes_secondary | object | 1 |
| visit_date | object | 1 |
| admission_date | object | 5 |
| discharge_date | object | 15642 |
| treatment_duration_days | float64 | 15642 |
| doctor_name_exam | object | 16774 |
| doctor_name_admit | object | 19246 |
| clinical_notes | float64 | 6 |
| discharge_diagnosis | object | 0 |
| hospital_code | object | 0 |
| visit_type | float64 | 1 |
| beneficiary_account | object | 0 |
| beneficiary_name | object | 0 |
| contract_id | object | 19112 |
| insurer_id | object | 0 |
| actual_receipt_date | object | 21 |
| claim_type | int64 | 0 |

## 3. Thống kê phân phối (Top 5 giá trị phổ biến)
### claim_id
- ad453c86-c315-4e1f-b19a-9a31df8b9d1d: 1
- 252d7b03-dc04-4180-810a-88b14b142079: 1
- eedb926d-5969-4527-b855-22d56af47226: 1
- 75b334e0-9741-44d2-9dab-8092aad12d8b: 1
- 7f89befb-ce31-47b7-a6fa-fc75de006894: 1

### user_id
- 27abe6c2-b194-4de7-8778-812af6840ed9: 36
- 925c1926-7d88-479d-8998-05b2f3222d8a: 30
- 8b923ab0-3b03-45fe-abd4-5af1553034d1: 24
- 5ef897c7-dd70-45b5-a4a4-5978b4b65b51: 24
- 53ef9eb5-6a5b-4cdd-9fb9-2a5404571917: 24

### claim_number
- BT/30901: 1
- BT/13416: 1
- BT/13418: 1
- BT/13419: 1
- BT/13420: 1

### full_name
- Nguyễn Minh Khôi: 41
- Kwok Vương Bảo: 36
- Nguyễn Gia Hân: 34
- Nguyễn Thị Hương: 29
- Nguyễn Khánh Linh: 28

### identity_number
- 079223035598: 36
- 079324017043: 30
- 079219000724: 27
- 001063030540: 27
- 001224042500: 27

### date_of_birth
- 8/19/2023: 43
- 7/20/2021: 37
- 11/8/2019: 31
- 6/29/2024: 30
- 7/17/2023: 29

### address
- Thành phố Hà Nội: 842
- Thành Phố HCM: 238
- Phường Từ Liêm, Thành phố Hà Nội: 47
- Vĩnh Hội, Phường Vĩnh Hội, Thành phố Hồ Chí Minh: 41
- Phường Hà Đông, Thành phố Hà Nội: 40

### email
- vint@fpts.com.vn: 63
- trinhntt1@tpb.com.vn: 53
- quangtq@fpt.com: 46
- anhtt9@fpt.com: 43
- thanhvd8@fpt.com: 40

### claim_date
- 5/29/2025 22:32: 5
- 3/25/2025 17:58: 4
- 3/9/2026 11:30: 4
- 1/20/2026 10:33: 3
- 10/2/2025 15:35: 3

### icd_code_primary
- J00: 1,239
- J20: 697
- J02: 637
- K02: 476
- J01: 338

### icd_name_primary
- Viêm mũi họng cấp [cảm thường]: 1,239
- Viêm phế quản cấp: 697
- Viêm họng cấp: 637
- Sâu răng: 476
- Viêm mũi xoang cấp tính: 299

### icd_codes_secondary
- {}: 11,103
- {"adeca53e-5b2f-4fb9-87cf-df084288b5ff": {"id": "adeca53e-5b2f-4fb9-87cf-df084288b5ff", "ma": "J00", "ten": "Viêm mũi họng cấp [cảm thường]"}}: 387
- {"38183afe-3d82-41ab-b19b-2cf100dd0726": {"id": "38183afe-3d82-41ab-b19b-2cf100dd0726", "ma": "K21", "ten": "Bệnh trào ngược dạ dày- thực quản"}}: 210
- {"32361dcf-b118-471c-97aa-178110c63789": {"id": "32361dcf-b118-471c-97aa-178110c63789", "ma": "J02", "ten": "Viêm họng cấp"}}: 173
- {"14aff052-8fe3-4ec4-acc9-6d36b385954a": {"id": "14aff052-8fe3-4ec4-acc9-6d36b385954a", "ma": "J20", "ten": "Viêm phế quản cấp"}}: 125

### visit_date
- 17/01/2026: 125
- 10/01/2026: 115
- 20/01/2026: 115
- 13/01/2026: 112
- 16/01/2026: 109

### admission_date
- 17/01/2026: 125
- 20/01/2026: 114
- 10/01/2026: 114
- 14/01/2026: 112
- 13/01/2026: 111

### discharge_date
- 26/01/2026: 28
- 31/12/2025: 27
- 09/02/2026: 26
- 23/01/2026: 25
- 02/02/2026: 23

### doctor_name_exam
- Lê Anh Tuấn: 8
- Nguyễn Thị Xuân: 8
- BS.CKI. Lâm Thị Mai Liên: 8
- Hoàng Thị Cúc: 8
- Nguyễn Thị Thảo: 7

### doctor_name_admit
- Trần Minh Trí : 1
- Lê Thị Hồng: 1
- Đoàn Thị Kim Châu: 1
- Tôn Minh Trí: 1
- Nguyễn Minh Thu: 1

### discharge_diagnosis
- Viêm mũi họng cấp: 166
- Viêm họng cấp: 150
- Bị chó cắn, đả thương: 143
- Viêm phế quản cấp: 126
- Viêm mũi họng: 95

### hospital_code
- 01288: 1,210
- 01915: 849
- 01934: 550
- 48072: 439
- 48195: 423

### beneficiary_account
- 1: 204
- 1048306057: 142
- 03566628701: 60
- 1290153594: 54
- 00355868002: 53

### beneficiary_name
- 1: 165
- CT TNHH BV DKTN AN SINH-PHUC TRUONG MINH: 154
- BVDK PHUONG DONG - CN CT TNHH TO HOP Y T: 60
- NGUYỄN THỊ VI: 55
- CONG TY CO PHAN BENH VIEN DA KHOA HOAN M: 50

### contract_id
- 7ebb5cbe-b88e-4829-9fa9-43fddace09de: 27
- 99de5479-3480-4def-9666-ea2018a7950a: 24
- eca36466-e06c-4235-a3b8-a87ec406bbfd: 18
- 9921f1d4-c92d-4ca0-921a-af2b4ceccea1: 10
- 49acb65f-96f2-4e62-bfaa-6b318c8fa4f0: 9

### insurer_id
- 0367a073-ce98-4652-8c91-533dbf2ea003: 19,259

### actual_receipt_date
- 2/9/2026: 238
- 3/2/2026: 238
- 2/2/2026: 237
- 1/19/2026: 233
- 1/26/2026: 224

