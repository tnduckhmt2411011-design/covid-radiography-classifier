# Mục lục và danh mục

Tệp này gộm ba mục đầu cuối của phần mở đầu quyển: mục lục, danh mục bảng biểu và
danh mục hình ảnh. Nội dung sinh tự động từ sáu chương, tài liệu tham khảo và phụ lục
bằng `scripts/report_frontmatter.py`, nên không lệch khi chương thêm tiểu mục hoặc bảng mới.
Số trang để trống; khi dựng bản Word, dùng *References → Table of Contents* của Word
để sinh số trang thật, rồi dán hai danh mục dưới dạng bảng hai cột (đề mục – trang).

## 1. Mục lục

**Phần mở đầu (đánh số La Mã)**

- i. Trang bìa chính
- ii. Trang bìa phụ
- iii. Lời cảm ơn
- iv. Lời cam đoan
- v. Tóm tắt tiếng Việt và Abstract
- vi. Danh mục ký hiệu và chữ viết tắt
- vii. Mục lục
- viii. Danh mục bảng biểu
- ix. Danh mục hình ảnh

**Phần nội dung chính (đánh số Ả Rập)**

- CHƯƠNG 1. GIỚI THIỆU VÀ TỔNG QUAN ĐỀ TÀI
  - 1.1. Bối cảnh và lý do chọn đề tài
  - 1.2. Mục tiêu và ba câu hỏi nghiên cứu
  - 1.3. Phạm vi nghiên cứu và ranh giới kỹ thuật
  - 1.4. Đóng góp của đề tài
  - 1.5. Cấu trúc báo cáo
  - Tài liệu tham khảo phát sinh trong chương
- CHƯƠNG 2. DỮ LIỆU VÀ PHƯƠNG PHÁP NGHIÊN CỨU
  - 2.1. Nguồn gốc bộ dữ liệu và độ tin cậy thông tin
  - 2.2. Phân tích khám phá dữ liệu và nguy cơ học lối tắt từ độ sáng và metadata tệp
  - 2.3. Gom nhóm ảnh trùng bằng pHash ngưỡng T = 0
  - 2.4. Phân chia train/val/test 70/15/15 và cơ chế khóa tập test
  - 2.5. Giới hạn còn lại của dữ liệu
  - 2.6. Trích xuất đặc trưng thủ công trên ảnh xám 299 × 299
    - 2.6.1. Đặc trưng histogram cường độ sáng, 64 chiều
    - 2.6.2. Đặc trưng kết cấu GLCM 60 chiều và LBP 28 chiều
    - 2.6.3. Đặc trưng hướng biên HOG, 10.404 chiều
    - 2.6.4. Nhóm đặc trưng ghép 152 chiều
  - 2.7. Chuẩn hóa dữ liệu, StandardScaler chỉ fit trên train
  - 2.8. Sáu thuật toán phân loại và không gian siêu tham số
  - 2.9. Phương pháp đánh giá thống kê và bootstrap ghép cặp
- CHƯƠNG 3. KẾT QUẢ RQ1 VÀ RQ2 TRÊN TẬP VALIDATION
  - 3.1. RQ1: bốn nhóm đặc trưng trên Random Forest
  - 3.2. Kiểm định thống kê và quyết định chọn nhóm ghép
  - 3.3. RQ2: sáu bộ phân loại trên nhóm ghép
  - 3.4. Đánh giá SVM RBF trên validation
- CHƯƠNG 4. MỨC PHỤ THUỘC VÀO VÙNG NGOÀI PHỔI (RQ3)
  - 4.1. Năm kịch bản che mặt nạ phổi
  - 4.2. Tầm quan trọng đặc trưng theo 10 khối
  - 4.3. Các giả thuyết chưa kiểm chứng về vùng ngoài mặt nạ phổi
- CHƯƠNG 5. KẾT QUẢ KIỂM TRA ĐỘC LẬP VÀ TRIỂN KHAI
  - 5.1. Kết quả trên tập test độc lập, mở khóa một lần
  - 5.2. Chênh lệch validation và test
  - 5.3. Phân tích lỗi sai và cặp nhầm lẫn Normal – Lung_Opacity
  - 5.4. Tính độc lập và khả năng tái lập của thực nghiệm
  - 5.5. Triển khai ứng dụng
    - 5.5.1. Pipeline suy luận từ ảnh xám 299×299 đến xác suất dự đoán
    - 5.5.2. Giao diện Streamlit và các thành phần tương tác
    - 5.5.3. Cảnh báo y khoa tích hợp trong ứng dụng
    - 5.5.4. Độ trễ suy luận thực tế
  - Tài liệu tham khảo phát sinh trong chương
- CHƯƠNG 6. THẢO LUẬN, GIỚI HẠN VÀ HƯỚNG PHÁT TRIỂN
  - 6.1. Thảo luận kết quả đạt được
  - 6.2. Giới hạn nghiên cứu
  - 6.3. Cảnh báo y khoa và đạo đức nghiên cứu
  - 6.4. Hướng phát triển
  - 6.5. Kết luận

**Phần cuối quyển (đánh số tiếp)**

- Tài liệu tham khảo
- Phụ lục
  - Phụ lục A. Cài đặt, tải mô hình và vận hành ứng dụng demo
    - A.1. Môi trường và cài đặt
    - A.2. Mô hình đóng băng và kiểm tra tính toàn vẹn
    - A.3. Biến môi trường
    - A.4. Vận hành và triển khai
    - A.5. Kiểm thử liên quan
    - A.6. Giới hạn và an toàn
  - Phụ lục B. Cấu trúc kho mã nguồn và danh sách bài kiểm thử
    - B.1. Cấu trúc kho
    - B.2. Danh sách bài kiểm thử
  - Phụ lục C. Lưới siêu tham số và tham số chọn của sáu bộ phân loại
    - C.1. Lưới siêu tham số
    - C.2. Tham số chọn và kết quả trên tập validation
    - C.3. Thứ hạng chi phí huấn luyện


## 2. Danh mục bảng biểu

- **Bảng 1.1:** Ba câu hỏi nghiên cứu, thước đo và quy tắc ra quyết định
- **Bảng 1.2:** Ràng buộc kỹ thuật và cơ chế kiểm soát
- **Bảng 2.1:** Thành phần bốn lớp theo nguồn gốc
- **Bảng 2.2:** Độ sáng trung bình theo lớp (thang 0–255)
- **Bảng 2.3:** Phân bố bốn lớp theo tập train, validation và test
- **Bảng 2.4:** 735 cặp gần trùng nằm ở hai tập khác nhau
- **Bảng 2.5:** Bốn nhóm đặc trưng và số chiều
- **Bảng 2.6:** Sáu bộ phân loại và không gian siêu tham số
- **Bảng 3.1:** Macro-F1 bốn nhóm đặc trưng trên validation, trung bình 3 seed
- **Bảng 3.2:** Phép so sánh của RQ1 với histogram làm mốc
- **Bảng 3.3:** Macro-F1 sáu bộ phân loại trên validation
- **Bảng 3.4:** Precision, Recall và F1 theo lớp của SVM trên validation
- **Bảng 3.5:** Ma trận nhầm lẫn của SVM trên validation
- **Bảng 3.6:** Tỷ lệ lỗi của từng cặp lớp trên tập validation
- **Bảng 4.1:** Macro-F1, khoảng tin cậy và accuracy của năm kịch bản trên 3.174 ảnh validation
- **Bảng 4.2:** Phép so sánh ghép cặp giữa các kịch bản (bootstrap 2.000 lần, n = 3.174)
- **Bảng 4.3:** Cặp nhầm lẫn Normal ↔ Lung_Opacity theo ba kịch bản cùng chế độ
- **Bảng 4.4:** Phép tách theo nguồn ảnh trên ba kịch bản cùng chế độ
- **Bảng 4.5:** Mức sụt macro-F1 khi hoán vị từng khối (10 lần xáo trộn, trên 3.174 ảnh validation)
- **Bảng 5.1:** Các chỉ số tổng thể của mô hình trên 3.176 ảnh tập test
- **Bảng 5.2:** Precision, Recall và F1 theo lớp của mô hình trên tập test
- **Bảng 5.3:** Recall từng lớp trên validation và trên tập test
- **Bảng 5.4:** Ma trận nhầm lẫn trên 3.176 ảnh tập test
- **Bảng 5.5:** Độ trễ đầu-cuối và theo từng chặng, thống kê trên trung vị ba lượt của 200 ảnh (seed 42)
- **Bảng 6.1:** Tóm tắt macro-F1 của các cấu hình chính và khoảng tin cậy 95%
- **Bảng A.1:** Biến môi trường của ứng dụng demo
- **Bảng A.2:** Thông số mô hình đóng băng
- **Bảng B.1:** Cấu trúc thư mục cấp một của kho
- **Bảng B.2:** 28 module kiểm thử và số phép kiểm thử (344 phép)
- **Bảng C.1:** Lưới siêu tham số của sáu bộ phân loại
- **Bảng C.2:** Siêu tham số chọn qua 5-fold CV và Macro-F1 validation của sáu bộ phân loại
- **Bảng C.3:** Chi phí huấn luyện của sáu bộ phân loại (giây CPU)
- Tổng cộng: 32 bảng.

## 3. Danh mục hình ảnh

- **Hình 2.1:** Phân bố độ sáng trung bình của bốn lớp — tệp nguồn `results/eda/brightness_distribution.png`
- **Hình 3.1:** Ma trận nhầm lẫn của SVM chuẩn hóa theo hàng (nhãn thực), trên 3.174 ảnh validation — tệp nguồn `report/figures/03_ma_tran_nham_lon_svm_val.png`
- **Hình 4.1:** Macro-F1 năm kịch bản RQ3 trên 3.174 ảnh validation, cột là điểm ước lượng và que chỉ khoảng tin cậy 95% — tệp nguồn `report/figures/04_macro_f1_kich_ban_rq3.png`
- **Hình 5.1:** Ma trận nhầm lẫn của mô hình SVM trên 3.176 ảnh tập kiểm tra độc lập, chuẩn hóa theo hàng — tệp nguồn `report/figures/05_ma_tran_nham_lon_test.png`
- Tổng cộng: 4 hình.

## Ghi chú kỹ thuật

- Nguồn: tiêu đề đọc từ sáu tệp `report/0*.md` (cấp `#`, `##`, `###`), bỏ hạng mục 
  "Ghi chú kỹ thuật" không thuộc nội dung báo cáo; bảng và hình đọc từ dòng chú thích in đậm.
- Sinh lại bằng `python scripts/report_frontmatter.py` (ghi đè tệp này).
- Hình 2.1 nằm ở `results/eda/` do notebook EDA sinh, không nằm trong `report/figures/`;
  khi chuyển Word, chèn ảnh từ đúng đường dẫn đó rồi đặt chú thích Hình 2.1 bên dưới.
