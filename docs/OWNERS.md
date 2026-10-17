# Phân công trách nhiệm các thành viên (Code Owners)

Tài liệu này quy định vai trò, nhóm kèm cặp (Pairing) và phân công trách nhiệm trực tiếp cho 6 thành viên trong nhóm đối với từng module, notebook và thư mục trong dự án.

---

## 1. Danh sách thành viên & Cơ chế ghép cặp (Pairing Mechanism)

Nhóm áp dụng mô hình ghép cặp (Pairing Mechanism) nhằm đảm bảo chất lượng kỹ thuật, chia sẻ tri thức và thực hiện cơ chế duyệt chéo PR (Peer Review):

| Mã TV | Tên thường gọi | Họ và tên | Trách nhiệm chính trong đồ án | Cặp kèm cặp & Duyệt chéo |
| :---: | :---: | :--- | :--- | :--- |
| **TV1** | **Nguyễn Đức** | Trần Nguyễn Đức (Leader) | Quản lý dự án, EDA, phân chia split và khóa tập test; chốt nhóm đặc trưng cho RQ2 (S3-06); tổng hợp báo cáo và thuyết trình | Cặp 1 (kèm cặp Hải Lý) |
| **TV2** | **Minh Thuận** | Nguyễn Trần Minh Thuận | Chạy Random Forest cố định RQ1 (S3-04); bộ phân loại và cross-validation RQ2 (S4-03) | Cặp 2 (kèm cặp Lê Minh) |
| **TV3** | **Thái Tú** | Hàng Thái Tú | Trích đặc trưng histogram, GLCM, LBP (S3-07); ứng dụng demo | Cặp 3 (kèm cặp Vũ Thương) |
| **TV4** | **Vũ Thương** | Nguyễn Vũ Thương | Trích đặc trưng HOG và nhóm ghép (S3-08); lớp nạp ảnh xám CXRDataset (S2-03) | Cặp 3 (được Thái Tú kèm cặp) |
| **TV5** | **Lê Minh** | Phạm Lê Minh | Viết lại setup_check cho CPU (S1-01); mask RQ3 và phân tích lỗi | Cặp 2 (được Minh Thuận kèm cặp) |
| **TV6** | **Hải Lý** | Lê Hải Lý | Metrics (`src/metrics.py`); tổng hợp bảng RQ1 (S3-05); bootstrap và báo cáo R1-R5 (S3-09); đánh giá test cuối | Cặp 1 (được Nguyễn Đức kèm cặp) |

---

## 2. Bảng phân công chi tiết theo Module / Notebook / Thư mục

| File / Module / Thư mục | Người phụ trách chính | Người kèm cặp & Duyệt PR | Mô tả nhiệm vụ |
| :--- | :---: | :---: | :--- |
| `notebooks/00_setup_check.ipynb` | **Lê Minh** | Minh Thuận | Kiểm tra môi trường CPU (không import torch) và in phiên bản thư viện (S1-01) |
| `notebooks/01_download_and_eda.ipynb` | **Nguyễn Đức** | Hải Lý | Tải dữ liệu, EDA, manifest dữ liệu ban đầu |
| `notebooks/02_duplicates_and_split.ipynb` | **Nguyễn Đức** | Hải Lý | Gom nhóm ảnh trùng bằng pHash, phân chia train/val/test |
| `splits/` | **Nguyễn Đức** | Hải Lý | Quản lý lưu trữ các file manifest chia tập dữ liệu |
| `src/dataset.py` | **Vũ Thương** | Thái Tú | Lớp nạp ảnh xám CXRDataset, khoá tập test (S2-03) |
| Module trích đặc trưng histogram, GLCM, LBP (S3-07; đường dẫn chốt khi tạo PR) | **Thái Tú** | Vũ Thương | Histogram 64 bin, GLCM, LBP theo threshold_v3 |
| Module trích đặc trưng HOG và nhóm ghép (S3-08; đường dẫn chốt khi tạo PR) | **Vũ Thương** | Thái Tú | HOG ô 16x16 và nhóm ghép theo threshold_v3 |
| Script bootstrap và báo cáo R1-R5 (S3-09; đường dẫn chốt khi tạo PR) | **Hải Lý** | Nguyễn Đức | Bootstrap ghép cặp 2.000 lần, bảng R1-R5 theo threshold_v3 |
| `notebooks/05_rq1_features.ipynb` | **Hải Lý** | Nguyễn Đức | Tổng hợp bảng kết quả RQ1 (so sánh 4 nhóm đặc trưng) (S3-05) |
| `notebooks/06_rq2_classifiers.ipynb` | **Minh Thuận** | Lê Minh | So sánh bộ phân loại học máy cổ điển RQ2 (S4-03) |
| `notebooks/08_rq3_masked_eval.ipynb` | **Lê Minh** | Minh Thuận | Đánh giá so sánh trên bộ ảnh gốc / chỉ phổi / ngoài phổi |
| `notebooks/09_error_analysis.ipynb` | **Lê Minh** | Minh Thuận | Phân tích các ca dự đoán sai và nguyên nhân |
| `src/metrics.py` | **Hải Lý** | Nguyễn Đức | Xây dựng module tính toán chỉ số đánh giá và ma trận nhầm lẫn |
| `notebooks/10_final_test_eval.ipynb` | **Hải Lý** | Nguyễn Đức | Thực hiện đánh giá DUY NHẤT 1 LẦN trên tập test |
| `notebooks/11_inference_demo.ipynb` | **Thái Tú** | Vũ Thương | Xây dựng notebook suy luận và ứng dụng demo |
| `demo/` | **Thái Tú** | Vũ Thương | Quản lý mã nguồn và triển khai ứng dụng demo Gradio; dùng lại đúng hàm trích đặc trưng đã đánh giá |
| `report/` | **Nguyễn Đức** (tổng hợp) | Hải Lý | Tổng hợp nội dung và hoàn thiện báo cáo bài tập lớn; mỗi thành viên viết phần của việc mình làm |

---

## 3. Nguyên tắc làm việc & Hỗ trợ trong cặp

1. **Trách nhiệm của người kèm cặp:** Hướng dẫn thành viên trong cặp tiếp cận bài toán, giải thích kiến trúc code, hỗ trợ debug khi gặp lỗi khó, và kiểm tra kỹ lưỡng (Review) trước khi phê duyệt PR.
2. **Trách nhiệm của thành viên được kèm cặp:** Tự giác học hỏi, chủ động trao đổi khi gặp vướng mắc, tuân thủ quy ước code và viết kiểm thử đầy đủ trước khi gửi yêu cầu duyệt PR.
3. **Cơ chế dự phòng:** Trong trường hợp thành viên gặp khó khăn đột xuất, người kèm cặp sẽ cùng tham gia (Pair Programming) để đảm bảo tiến độ chung của Sprint.
