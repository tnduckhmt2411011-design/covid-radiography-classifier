# Phân công trách nhiệm các thành viên (Code Owners)

Tài liệu này quy định vai trò, nhóm kèm cặp (Pairing) và phân công trách nhiệm trực tiếp cho 6 thành viên trong nhóm đối với từng module, notebook và thư mục trong dự án.

---

## 1. Danh sách thành viên & Cơ chế ghép cặp (Pairing Mechanism)

Nhóm áp dụng mô hình ghép cặp (Pairing Mechanism) nhằm đảm bảo chất lượng kỹ thuật, chia sẻ tri thức và thực hiện cơ chế duyệt chéo PR (Peer Review):

| Mã TV | Tên thường gọi | Họ và tên | Mã sinh viên | Trách nhiệm chính trong đồ án | Cặp kèm cặp & Duyệt chéo |
| :---: | :---: | :--- | :---: | :--- | :--- |
| **TV1** | **Nguyễn Đức** | Trần Nguyễn Đức (Leader) | KHMT2411011 | Quản lý dự án, EDA, phân chia split và khóa tập test | Cặp 1 (kèm cặp Hải Lý) |
| **TV2** | **Minh Thuận** | Nguyễn Trần Minh Thuận | KHMT2411014 | Pipeline huấn luyện PyTorch AMP, resume, baseline mô hình | Cặp 2 (kèm cặp Lê Minh) |
| **TV3** | **Thái Tú** | Hàng Thái Tú | KHMT2411046 | Kiến trúc mô hình (`src/models.py`), nghiên cứu RQ1 (Backbones) | Cặp 3 (kèm cặp Vũ Thương) |
| **TV4** | **Vũ Thương** | Nguyễn Vũ Thương | KHMT2411022 | Data Augmentation, nghiên cứu RQ2 (Mất cân bằng lớp) | Cặp 3 (được Thái Tú kèm cặp) |
| **TV5** | **Lê Minh** | Phạm Lê Minh | KHMT2411003 | Grad-CAM (`src/gradcam.py`), phân tích lỗi, nghiên cứu RQ3 (Ảnh che) | Cặp 2 (được Minh Thuận kèm cặp) |
| **TV6** | **Hải Lý** | Lê Hải Lý | KHMT2411021 | Metrics (`src/metrics.py`), đánh giá test cuối, demo Gradio & báo cáo | Cặp 1 (được Nguyễn Đức kèm cặp) |

---

## 2. Bảng phân công chi tiết theo Module / Notebook / Thư mục

| File / Module / Thư mục | Người phụ trách chính | Người kèm cặp & Duyệt PR | Mô tả nhiệm vụ |
| :--- | :---: | :---: | :--- |
| `notebooks/00_setup_check.ipynb` | **Cả nhóm** | **Nguyễn Đức (Leader)** | Kiểm tra môi trường chung, GPU và ghim thư viện |
| `notebooks/01_download_and_eda.ipynb` | **Nguyễn Đức** | Hải Lý | Tải dữ liệu, EDA, manifest dữ liệu ban đầu |
| `notebooks/02_duplicates_and_split.ipynb` | **Nguyễn Đức** | Hải Lý | Lọc ảnh trùng bằng imagehash, phân chia train/val/test |
| `splits/` | **Nguyễn Đức** | Hải Lý | Quản lý lưu trữ các file manifest chia tập dữ liệu |
| `src/train.py` | **Minh Thuận** | Lê Minh | Xây dựng pipeline huấn luyện, kiểm định và checkpoint resume |
| `notebooks/03_smoke_test_train.ipynb` | **Minh Thuận** | Lê Minh | Chạy thử nghiệm nhanh vòng lặp train và kiểm tra resume |
| `notebooks/04_baseline.ipynb` | **Minh Thuận** | Lê Minh | Huấn luyện mô hình baseline, đo thời gian run |
| `src/models.py` | **Thái Tú** | Vũ Thương | Xây dựng và quản lý các kiến trúc mô hình (ResNet18, DenseNet121, EfficientNet-B0) |
| `notebooks/05_rq1_backbones.ipynb` | **Thái Tú** | Vũ Thương | Nghiên cứu và so sánh các backbone (DenseNet121 vs EfficientNet-B0) |
| Augmentation trong `src/dataset.py` | **Vũ Thương** | Thái Tú | Cài đặt các kỹ thuật tăng cường dữ liệu ảnh |
| `notebooks/06_rq2_imbalance.ipynb` | **Vũ Thương** | Thái Tú | Nghiên cứu và thử nghiệm xử lý mất cân bằng lớp (Weighted Loss, Focal Loss) |
| `src/gradcam.py` | **Lê Minh** | Minh Thuận | Cài đặt hàm trích xuất Grad-CAM và phủ nhiệt |
| `notebooks/07_gradcam_lung_attention.ipynb` | **Lê Minh** | Minh Thuận | Trực quan hóa Grad-CAM và đo vùng chú ý phổi |
| `notebooks/08_rq3_masked_eval.ipynb` | **Lê Minh** | Minh Thuận | Đánh giá so sánh trên bộ ảnh gốc / chỉ phổi / ngoài phổi |
| `notebooks/09_error_analysis.ipynb` | **Lê Minh** | Minh Thuận | Phân tích các ca dự đoán sai và nguyên nhân |
| `src/metrics.py` | **Hải Lý** | Nguyễn Đức | Xây dựng module tính toán chỉ số đánh giá và ma trận nhầm lẫn |
| `notebooks/10_final_test_eval.ipynb` | **Hải Lý** | Nguyễn Đức | Thực hiện đánh giá DUY NHẤT 1 LẦN trên tập test |
| `notebooks/11_inference_demo.ipynb` | **Hải Lý** | Nguyễn Đức | Xây dựng notebook suy luận và ứng dụng demo |
| `demo/` | **Hải Lý** | Nguyễn Đức | Quản lý mã nguồn và triển khai ứng dụng demo Gradio |
| `report/` | **Hải Lý** | **Cả nhóm** | Tổng hợp nội dung và hoàn thiện báo cáo bài tập lớn |

---

## 3. Nguyên tắc làm việc & Hỗ trợ trong cặp

1. **Trách nhiệm của người kèm cặp:** Hướng dẫn thành viên trong cặp tiếp cận bài toán, giải thích kiến trúc code, hỗ trợ debug khi gặp lỗi khó, và kiểm tra kỹ lưỡng (Review) trước khi phê duyệt PR.
2. **Trách nhiệm của thành viên được kèm cặp:** Tự giác học hỏi, chủ động trao đổi khi gặp vướng mắc, tuân thủ quy ước code và viết kiểm thử đầy đủ trước khi gửi yêu cầu duyệt PR.
3. **Cơ chế dự phòng:** Trong trường hợp thành viên gặp khó khăn đột xuất, người kèm cặp sẽ cùng tham gia (Pair Programming) để đảm bảo tiến độ chung của Sprint.
