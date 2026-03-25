# Neo4j Graph Ontology: Final Fraud Architecture

Đây là sơ đồ Ontology cuối cùng được sử dụng để xây dựng Cơ sở dữ liệu Đồ thị (Knowledge Graph) phục vụ truy vết trục lợi.

## 1. Biểu đồ Ontology (Mermaid)

```mermaid
classDiagram
    class Person {
        +String user_id (PK)
        +String identity_number
        +String full_name
        +String phone_number
        +String email
        +String address
        +Float salary
        +String contract_level
    }

    class Claim {
        +String claim_id (PK)
        +DateTime claim_date
        +Float amount
        +String visit_type
        +String diagnosis
        +Int treatment_duration_days
        +Float risk_score
    }

    class Doctor {
        +String name (PK)
    }

    class Hospital {
        +String hospital_code (PK)
        +String hospital_name
    }

    class Bank {
        +String account_number (PK)
        +String beneficiary_name
    }

    class Insurer {
        +String insurer_id (PK)
        +String name
    }

    class Expense {
        +String item_name
        +String category
        +Float amount
    }

    %% Core Relationships
    Person "1" --> "*" Claim : SUBMITTED
    Claim "*" --> "1" Hospital : TREATED_AT
    Claim "*" --> "1" Doctor : EXAMINED_BY
    Claim "*" --> "1" Insurer : HANDLED_BY
    Claim "*" --> "1" Bank : PAID_TO
    Claim "1" --> "*" Expense : HAS_EXPENSE
    
    %% Implicit Fraud-Detection Links
    Person "*" --> "*" Bank : USES_BANK_ACCOUNT
```

## 2. Chi tiết Thuộc tính quan trọng

| Node | Thuộc tính then chốt | Ý nghĩa trong Truy vết (Fraud Analysis) |
| :--- | :--- | :--- |
| **Person** | `contract_level`, `salary` | Phát hiện kịch bản "Nâng cấp gói trước khi bệnh nặng" và tính cân xứng thu nhập. |
| **Claim** | `risk_score` | Tổng hợp điểm rủi ro từ 5 lớp lọc AI để ưu tiên xử lý. |
| **Doctor** | `name` | Tìm kiếm mạng lưới bác sĩ có dấu hiệu thông đồng hoặc chẩn đoán ảo. |
| **Bank** | `account_number` | Điểm hội tụ của các nhóm trục lợi có tổ chức (Syndicates). |

## 3. Các kịch bản truy vết sẽ triển khai trên Graph
- **Mạng lưới PII:** Tìm khách hàng dùng chung Số điện thoại, Email hoặc STK Ngân hàng.
- **Vòng tròn Collusion:** Tìm mối liên hệ mật thiết giữa Đại lý (Insurer) - Bác sĩ - Bệnh viện có tỷ lệ từ chối claim cao.
- **Chuỗi sự kiện (Sequence Analysis):** Truy sát lịch sử thay đổi `contract_level` trước các `Claim` lớn.

---
**Trạng thái:** ONTOLOGY ĐÃ HOÀN THIỆN. Sẵn sàng cho quá trình Migration.
