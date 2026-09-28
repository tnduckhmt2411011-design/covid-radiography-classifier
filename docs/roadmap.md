# Kế hoạch thực hiện dự án (12 Tuần)

Lộ trình chi tiết 12 tuần của nhóm cho bài tập lớn môn Học máy: Phân loại 4 nhóm ảnh X-quang ngực trên tập dữ liệu COVID-19 Radiography Database.

| Tuần | Mục tiêu | Công việc chính | Sản phẩm |
| :---: | :--- | :--- | :--- |
| **1** | Học nền + dựng môi trường | Thiết lập môi trường chạy trên Kaggle (Colab dự phòng), kiểm tra GPU/CUDA, cài đặt các thư viện phụ thuộc và ghim phiên bản | Notebook `00_setup_check.ipynb`, file `requirements.txt` đã ghim phiên bản |
| **2** | Hiểu dữ liệu | Khám phá dữ liệu (EDA), phân tích phân bố nhãn, kiểm tra lung mask, phát hiện ảnh trùng lặp | Notebook `01_download_and_eda.ipynb`, manifest sơ bộ của tập dữ liệu |
| **3** | Khoá test + khung huấn luyện | Lọc trùng bằng imagehash, chia split 70/15/15 và **khoá tập test**; hoàn thiện pipeline huấn luyện có resume và module tính metrics | Notebooks `02_duplicates_and_split.ipynb`, `03_smoke_test_train.ipynb`, files trong `splits/`, `src/train.py`, `src/metrics.py` |
| **4** | Baseline + chốt ngưỡng chấp nhận + đo thời gian mỗi run | Huấn luyện mô hình cơ sở (Baseline), đo đạc thời gian huấn luyện từng run/epoch, xác lập ngưỡng hiệu năng tối thiểu chấp nhận được | Notebook `04_baseline.ipynb`, bảng kết quả benchmark baseline trong `results/` |
| **5** | RQ1 (1): DenseNet121, EfficientNet-B0 | Bắt đầu câu hỏi nghiên cứu 1: Thử nghiệm và so sánh kiến trúc DenseNet121 và EfficientNet-B0 | Notebook `05_rq1_backbones.ipynb` (giai đoạn 1) |
| **6** | RQ1 (2) + chuẩn bị RQ2/RQ3 | Hoàn tất so sánh backbones RQ1; chuẩn bị các chiến lược xử lý mất cân bằng lớp và phương pháp che ảnh | Notebook `05_rq1_backbones.ipynb` hoàn thiện, bảng tổng hợp RQ1, kế hoạch thực nghiệm RQ2 & RQ3 |
| **7** | RQ2: xử lý mất cân bằng lớp | Bắt đầu câu hỏi nghiên cứu 2: Thử nghiệm các giải pháp xử lý mất cân bằng lớp (Weighted Loss, Focal Loss, Sampler, Augmentation) | Notebook `06_rq2_imbalance.ipynb`, bảng so sánh các chiến lược RQ2 |
| **8** | Chốt cấu hình cuối, Grad-CAM, phân tích lỗi, bộ ảnh che trong/ngoài phổi | Chốt cấu hình mô hình tối ưu nhất; trực quan hóa bản đồ nhiệt Grad-CAM; phân tích các ca lỗi; tạo bộ ảnh che trong/ngoài phổi chuẩn bị cho RQ3 | Notebooks `07_gradcam_lung_attention.ipynb`, `09_error_analysis.ipynb`, module `src/gradcam.py`, bộ dữ liệu che thử nghiệm |
| **9** | RQ3: đánh giá ảnh gốc / chỉ phổi / chỉ ngoài phổi | Câu hỏi nghiên cứu 3: Đánh giá mô hình trên 3 tập (ảnh gốc / chỉ giữ vùng phổi / chỉ giữ ngoài phổi) để phát hiện shortcut learning | Notebook `08_rq3_masked_eval.ipynb`, báo cáo kết luận về độ tin cậy vùng chú ý |
| **10** | Đánh giá test MỘT lần + notebook suy luận | **Mở khoá tập test**, thực hiện đánh giá DUY NHẤT 1 LẦN trên mô hình cuối; xây dựng pipeline và notebook suy luận | Notebooks `10_final_test_eval.ipynb`, `11_inference_demo.ipynb`, bảng kết quả test chính thức |
| **11** | Báo cáo + slide + demo | Tổng hợp kết quả thực nghiệm, viết báo cáo bài tập lớn, hoàn thiện slide thuyết trình và ứng dụng demo Gradio | Báo cáo trong `report/`, slide trong `slides/`, ứng dụng trong `demo/` |
| **12** | Dự phòng, nộp, tập bảo vệ | Dành thời gian dự phòng rà soát toàn bộ sản phẩm, nộp bài tập lớn và diễn tập thuyết trình bảo vệ | Repo hoàn chỉnh, bài nộp sẵn sàng, hoàn tất diễn tập bảo vệ |
