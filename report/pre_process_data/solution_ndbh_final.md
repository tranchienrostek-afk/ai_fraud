# Báo cáo Tổng kết Làm sạch Dữ liệu Người được Bảo hiểm (DataNDBH Final Report)

## 1. Kết quả Làm sạch (Cleaning Results)

- **Tổng số bản ghi xử lý:** 420,634 bản ghi.
- **Tình trạng nạp tiền tệ (Salary):** Áp dụng hệ số scaling 100x mặc định để bảo đảm tính nhất quán hệ thống.
- **Định danh duy nhất (Unique IDs):** Đã rà soát và chuẩn hóa khóa ngoại liên kết cho Graph Database.

## 2. Đặc trưng Nhân khẩu học (Demographics Insights)

### Biểu đồ Độ tuổi (Toàn bộ Dataset)
![Age Distribution](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts_persons/age_dist_final.png)
*Hình 1: Phân bổ tuổi chính xác sau khi quét toàn bộ 210,000+ hồ sơ.*

## 3. Quy trình Chuẩn hóa đã thực hiện

| Feature | Mô tả Thao tác |
| :--- | :--- |
| `full_name` | Quy đổi về CHỮ HOA, loại bỏ khoảng trắng rác. |
| `phone_number`| Loại bỏ toàn bộ ký tự không phải số; chuẩn hóa định dạng truy vết. |
| `date_of_birth`| Chuyển đổi về định dạng `datetime` chuẩn hóa. |
| `age` | Phái sinh độ tuổi thực tế phục vụ phân tích nhóm rủi ro. |
| `salary` | Chia 100 để đồng bộ đơn vị với bảng Chi phí và Bồi thường. |

## 4. Tệp tin Đầu ra (Deliverables)

- **Cleaned CSV:** [DataNDBH_Cleaned_Final.csv](file:///D:/desktop_folder/04_Fraud_Detection/report/cleaned_data_final/DataNDBH_Cleaned_Final.csv)
- **Charts:** Đã lưu trữ toàn bộ đồ thị phân bổ độ tuổi vào thư mục `charts_persons`.

## 5. Kết luận
Dữ liệu Người được bảo hiểm hiện đã được đồng bộ 100% với các bảng Chi phí và Hồ sơ bồi thường, sẵn sàng cho việc phân tích rủi ro đa chiều trên Dashboard và Graph Database.
