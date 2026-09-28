# Phân công trách nhiệm các thành viên (Code Owners)

Dưới đây là bảng phân công trách nhiệm trực tiếp cho từng module, notebook và thư mục trong dự án (sử dụng định danh thành viên từ TV1 đến TV6).

| File / Module / Thư mục | Người phụ trách | Mô tả nhiệm vụ |
| :--- | :---: | :--- |
| `notebooks/00_setup_check.ipynb` | **Cả nhóm** | Kiểm tra môi trường chung, GPU và ghim thư viện |
| `notebooks/01_download_and_eda.ipynb` | **TV1** | Tải dữ liệu, EDA, manifest dữ liệu ban đầu |
| `notebooks/02_duplicates_and_split.ipynb` | **TV1** | Lọc ảnh trùng bằng imagehash, phân chia train/val/test |
| `splits/` | **TV1** | Quản lý lưu trữ các file manifest chia tập dữ liệu |
| `src/train.py` | **TV2** | Xây dựng pipeline huấn luyện, kiểm định và checkpoint resume |
| `notebooks/03_smoke_test_train.ipynb` | **TV2** | Chạy thử nghiệm nhanh vòng lặp train và kiểm tra resume |
| `notebooks/04_baseline.ipynb` | **TV2** | Huấn luyện mô hình baseline, đo thời gian run |
| `notebooks/05_rq1_backbones.ipynb` | **TV3** | Nghiên cứu và so sánh các backbone (DenseNet121 vs EfficientNet-B0) |
| Augmentation trong `src/dataset.py` | **TV4** | Cài đặt các kỹ thuật tăng cường dữ liệu ảnh |
| `notebooks/06_rq2_imbalance.ipynb` | **TV4** | Nghiên cứu và thử nghiệm xử lý mất cân bằng lớp |
| `src/gradcam.py` | **TV5** | Cài đặt hàm trích xuất Grad-CAM và phủ nhiệt |
| `notebooks/07_gradcam_lung_attention.ipynb` | **TV5** | Trực quan hóa Grad-CAM và đo vùng chú ý phổi |
| `notebooks/08_rq3_masked_eval.ipynb` | **TV5** | Đánh giá so sánh trên bộ ảnh gốc / chỉ phổi / ngoài phổi |
| `notebooks/09_error_analysis.ipynb` | **TV5** | Phân tích các ca dự đoán sai và nguyên nhân |
| `src/metrics.py` | **TV6** | Xây dựng module tính toán chỉ số đánh giá và ma trận nhầm lẫn |
| `notebooks/10_final_test_eval.ipynb` | **TV6** | Thực hiện đánh giá DUY NHẤT 1 LẦN trên tập test |
| `notebooks/11_inference_demo.ipynb` | **TV6** | Xây dựng notebook suy luận và ứng dụng demo |
| `demo/` | **TV6** | Quản lý mã nguồn và triển khai ứng dụng demo Gradio |
| `report/` | **TV6** | Tổng hợp nội dung và hoàn thiện báo cáo bài tập lớn |
| `src/models.py` | *(Chưa phân công, nhóm quyết)* | Định nghĩa các kiến trúc mô hình |
