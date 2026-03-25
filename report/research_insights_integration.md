# Tổng hợp Kiến thức từ Báo cáo Nghiên cứu chuyên sâu (Research Insights)

Tôi đã phân tích tài liệu `deep-research-report.md` và rút ra các bài học quan trọng để tối ưu hóa hệ thống Phát hiện Trục lợi Bảo hiểm hiện tại.

## 1. Nâng cấp Quy trình Xử lý Dữ liệu (Pipeline)
Báo cáo nhấn mạnh quy trình 10 bước chuẩn chỉ. Tôi sẽ áp dụng các kỹ thuật sau vào 5 Agent của chúng ta:

*   **Tiền xử lý (Pre-processing):** Áp dụng **Z-score Normalization** và **Missing Value Imputation** (thay vì chỉ xóa bỏ) để giữ lại tối đa thông tin cho Agent 03 và 04.
*   **Phát hiện Ngoại lệ (Outliers):** Kết hợp thêm phương pháp **IQR (Interquartile Range)** bên cạnh Isolation Forest hiện có để tăng độ nhạy với các ca trục lợi số tiền lớn.

## 2. Tối ưu hóa các Agent
Dựa trên triết lý từ báo cáo, các Agent sẽ được nâng cấp logic:

| Agent | Cải tiến từ Nghiên cứu | Ứng dụng thực tế |
| :--- | :--- | :--- |
| **02. Graph** | **Clustering (Phân cụm)** | Sử dụng thêm DBSCAN để phát hiện các "cụm mật độ" người dùng bất thường mà không cần biết trước số lượng nhóm. |
| **03. Anomaly** | **PCA (Giảm chiều)** | Dùng PCA để trích xuất các thành phần quan trọng nhất từ bệnh án, giúp Agent 03 tập trung vào các đặc điểm gây xao nhãng ít hơn. |
| **04. Scoring** | **Calibration (Hiệu chuẩn)** | Sử dụng Brier Score để đảm bảo điểm số Fraud Score (0-100) phản ánh đúng xác suất thực tế, không bị quá tự tin (overconfident). |
| **05. Narrator** | **XAI (Explainable AI)** | Tích hợp sâu hơn phương pháp SHAP để giải thích chính xác biến số nào (Tuổi, Bệnh viện, hay Số tiền) đóng góp nhiều nhất vào rủi ro. |

## 3. Hệ thống Giám sát và Drift
Báo cáo nhắc nhở về tính chất thay đổi của dữ liệu theo thời gian (Concept Drift).
*   **Hành động:** Thiết kế cơ chế giám sát độ lệch phân phối dữ liệu (KL-divergence) để biết khi nào cần tái huấn luyện (Retrain) các mô hình ML trong Agent 03 và 04.

## 4. Đạo đức và Công bằng (Fairness)
*   **Hành động:** Đảm bảo Agent 05 không sử dụng các thông tin nhạy cảm (như giới tính, tôn giáo) làm lý do giải thích trừ khi có liên quan trực tiếp đến rủi ro bệnh lý, tuân thủ tinh thần GDPR và Privacy by Design.

---
**Kết luận:** Những kiến thức này giúp hệ thống của chúng ta chuyển từ một mô hình thực nghiệm sang một hệ thống chuẩn doanh nghiệp (Enterprise-ready), có khả năng xử lý hàng triệu hồ sơ với độ tin cậy và minh bạch cao.
