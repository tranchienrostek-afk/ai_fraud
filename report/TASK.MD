# Làm sạch và khai phá dữ liệu

## Nhiệm vụ 1 - DataNDBH (File 1)

**Link file:** `D:\desktop_folder\04_Fraud_Detection\report\cleaned_data_final\DataNDBH_Cleaned_Final.csv`

- Cột `unit`: nếu ô giá trị rỗng thì điền là "Đơn vị"
- Cột `quantity`: nếu ô giá trị rỗng, thì lấy tổng số tiền chia cho đơn giá xem số lượng đơn vị là bao nhiêu. Công thức: `total_amount / unit_price`
- Tất cả các cột sau nếu có giá trị số lớn hơn 0 và nhỏ hơn 100 đồng thì loại bỏ bản ghi đó:
  - `unit_price`
  - `total_amount`
  - `median_price`

## Nhiệm vụ 2 - DataHoSoBoiThuong (File 2)

**Link file:** `D:\desktop_folder\04_Fraud_Detection\report\cleaned_data_final\DataHoSoBoiThuong_Cleaned_Final.csv`

- Cột `median_claim_val`, `claim_amount_approved_orig` và cột `claim_amount_approved`: chia cho 100

| median_claim_val | claim_amount_approved_orig | claim_amount_approved |
| ---------------- | -------------------------- | --------------------- |
| / 100            | / 100                      | / 100                 |

## Nhiệm vụ 3 - DataNDBH premium (File 1)

**Link file:** `D:\desktop_folder\04_Fraud_Detection\report\cleaned_data_final\DataNDBH_Cleaned_Final.csv`

- Cột `premium_paid`: chia cho 100 để xoá 2 số 0
- Các cột không có bất kỳ giá trị nào thì xoá luôn
