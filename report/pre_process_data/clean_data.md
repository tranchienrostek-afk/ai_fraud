Dựa trên cấu trúc của cả 4 tập dữ liệu (Chi phí, Hồ sơ bồi thường, Người được bảo hiểm, Quyền lợi), chiến thuật tổng thể để xử lý các trường dữ liệu lỗi, bất thường và sai định dạng bao gồm các nhóm hành động cốt lõi sau:

**1. Chiến thuật xử lý nhóm dữ liệu Tiền tệ (Bắt buộc & Đồng loạt)**

- **Chia tỷ lệ chuẩn:** Xuyên suốt tất cả các bảng, mọi giá trị tiền tệ đều đang bị phóng đại 100 lần. Bạn bắt buộc phải chia cho 100 đối với: `unit_price`, `total_amount`, `exclusion_amount` (bảng Chi phí), `claim_amount_requested`, `claim_amount_approved` (bảng Bồi thường), `salary` (bảng Người được bảo hiểm), và `limit_amount`, `remaining_benefit_limit` (bảng Quyền lợi).
- **Kiểm tra chéo logic (Sanity Checks):**
  - Bảng Chi phí: Đảm bảo `total_amount` bằng đúng `unit_price` nhân với `quantity`.
  - Bảng Quyền lợi: Đảm bảo `remaining_benefit_limit` (hạn mức còn lại) không vượt quá `limit_amount` (hạn mức tối đa), đồng thời sử dụng trường này để ngăn chặn các khoản chi trả quá hạn mức.

**2. Chiến thuật xử lý Khóa liên kết (UUID) và Định danh**

- **Toàn vẹn khóa liên kết:** Các cột khóa chính và khóa ngoại mang định dạng UUID (`detail_id`, `claim_id`, `user_id`, `benefit_id`) có vai trò nối liền các bảng. Phải xóa hoặc làm sạch các dòng chứa UUID bị Null hoặc sai định dạng để không làm đứt gãy dữ liệu khi Join.
- **Làm sạch dữ liệu định danh để chống trục lợi:** Sử dụng `identity_number` để đối chiếu, phát hiện và gộp các bản ghi người dùng trùng lặp. Cột `phone` (số điện thoại) cần được chuẩn hóa định dạng để làm cơ sở nhận diện các cụm trục lợi thông qua việc dùng chung SĐT.

**3. Chiến thuật xử lý dữ liệu Phân loại (Categorical) và Mã hóa (Text)**

- **Mã bệnh y khoa (ICD):** Cột `ICD` được đánh giá là cực kỳ quan trọng để phát hiện trục lợi. Cần chuẩn hóa, loại bỏ mã không hợp lệ và có thể gom nhóm để phân tích chẩn đoán bất thường.
- **Chuẩn hóa văn bản:** Làm sạch văn bản (khoảng trắng, viết hoa/thường) cho `drug_or_service_name` để thuật toán dễ dàng phân tích hành vi lạm dụng.
- **Đồng nhất các nhóm phân loại:** Cần chuẩn hóa các giá trị tại cột `claim_type`, `Trạng thái hồ sơ`, `item_type`, `category`, và `benefit_type` để áp dụng chính xác các bộ quy tắc kiểm soát hoặc lọc dữ liệu. Giới tính (`gender`) cũng cần đưa về các chuẩn chung.
- **Biến trạng thái (Boolean):** Cột `active` trong bảng Quyền lợi cần được xác minh là True/False chuẩn xác để dùng làm bộ lọc xác định hồ sơ có được chi trả không.

**4. Chiến thuật phát hiện Dữ liệu ngoại lai (Outlier) & Bất thường**

- **Rà soát gian lận chi phí:** Khảo sát sự phân bố của `unit_price` để phát hiện các trường hợp kê giá cao bất thường.
- **Giám sát số lượng:** Cột `quantity` phải được đánh giá tính hợp lý; các giá trị vô lý cần được gắn cờ (flag).

**5. Chiến thuật chuyển đổi dữ liệu Thời gian (Temporal Data)**

- **Chuyển đổi ngày sinh thành nhóm rủi ro:** Định dạng lại cột `dob` (ngày sinh) về chuẩn Date, từ đó tính ra "Tuổi" để phân tích rủi ro theo từng nhóm tuổi.
- **Tính toán hiệu suất (SLA):** Đưa `actual_receipt_date` về chuẩn Date để đo lường chính xác thời gian xử lý hồ sơ, có thể bổ trợ trong việc phát hiện các hồ sơ được duyệt nhanh/chậm bất thường. Các trường `created_at` ở các bảng cũng cần chuẩn hóa để theo dõi lịch sử.
