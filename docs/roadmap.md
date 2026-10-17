# Kế hoạch và Bảng theo dõi tiến độ đồ án (Scrum rút gọn)

Tài liệu theo dõi tiến độ thực hiện đồ án môn Học máy trong 12 tuần, áp dụng mô hình Scrum rút gọn dành cho nhóm 6 sinh viên beginner. Toàn bộ tiến độ được đồng bộ với trạng thái thực tế trên GitHub repository.

---

## Mục 1. Cách đọc tài liệu

### 1.1. Hệ thống 6 trạng thái công việc

Mỗi công việc trong backlog chỉ nhận đúng 1 trong 6 trạng thái sau, gắn chặt với hoạt động trên GitHub:

- **Chưa làm:** Mặc định cho tất cả các công việc chưa bắt đầu hoặc chưa tìm thấy bằng chứng xác thực trên GitHub/repo.
- **Đang làm:** Có nhánh tính năng `feat/<ten>-<viec>` đang mở trên repo, đang được phát triển và chưa tạo Pull Request.
- **Chờ duyệt:** Đã mở Pull Request trên GitHub, đang trong quá trình kiểm tra và chờ thành viên trong cặp duyệt (Approve), chưa merge vào `main`.
- **Xong:** Pull Request đã được merge vào nhánh `main` VÀ đạt đầy đủ tiêu chí nghiệm thu của việc đó. Đối với các việc không qua Pull Request (ví dụ: gửi câu hỏi cho giảng viên), bắt buộc cần Leader (Nguyễn Đức) xác nhận bằng văn bản.
- **Bị chặn:** Công việc không thể tiếp tục do vướng mắc về kỹ thuật, thiếu thông tin, hoặc phụ thuộc chưa hoàn thành. Bắt buộc phải có dòng giải thích nguyên nhân tại Mục 5.
- **Hủy – ngoài phạm vi:** việc không còn trong phạm vi theo quy định của giảng viên; không tính vào mẫu số; bằng chứng cũ lưu ở tag archive-dl-ngoai-pham-vi.

### 1.2. Quy ước ước lượng độ lớn (Size)

Độ lớn công việc được ước lượng thô theo giờ làm việc thực tế để nhóm sinh viên dễ phân bổ thời gian (nhóm có thể tinh chỉnh ở buổi Sprint Planning):

- **S (Small):** Nhỏ hơn hoặc bằng 2 giờ làm việc.
- **M (Medium):** Từ 3 đến 5 giờ làm việc.
- **L (Large):** Từ 6 đến 10 giờ làm việc.

### 1.3. Cột Bằng chứng

Mỗi công việc ở trạng thái "Xong" hoặc "Chờ duyệt" bắt buộc phải ghi rõ nguồn xác thực:
- Đường dẫn hoặc mã số Pull Request trên GitHub (ví dụ: PR #1, PR #2).
- Mã commit, đường dẫn file trong repository (ví dụ: `splits/manifest.csv`).
- Tên kernel và run id trên Kaggle (đối với kernel chạy private).
- Hoặc dòng chữ "leader xác nhận" đối với công việc ngoại lệ không có code trên Git.

### 1.4. Bảng thuật ngữ rút gọn cho người mới

| Thuật ngữ | Ý nghĩa đơn giản trong đồ án |
| :--- | :--- |
| **Sprint** | Chu kỳ làm việc cố định dài 2 tuần để hoàn thành một nhóm mục tiêu nhất định. |
| **Sprint Goal** | Mục tiêu cốt lõi nhất mà cả nhóm phải đạt được khi kết thúc một sprint. |
| **Backlog** | Danh sách tất cả các công việc cần làm trong dự án, được chia nhỏ theo từng sprint. |
| **Definition of Done** | Bộ tiêu chuẩn bắt buộc để một công việc được công nhận là hoàn thành thực sự. |
| **Sprint Review** | Buổi họp ngắn cuối sprint để trình bày và kiểm tra các sản phẩm đã hoàn thành. |
| **Retrospective** | Buổi họp rút kinh nghiệm cuối sprint để cải tiến cách phối hợp và sửa lỗi cho sprint tiếp theo. |

### 1.5. Nhịp làm việc đề xuất cho nhóm

- **Sprint Planning (Đầu sprint, khoảng 30 phút):** Nhóm họp online/offline, Leader (Nguyễn Đức) giao việc theo phân công trong `docs/OWNERS.md`, các cặp ước lượng lại Size nếu cần.
- **Cập nhật tiến độ hàng tuần (Cuối tuần):** Người phụ trách cập nhật trạng thái công việc của mình ngay trong chính Pull Request hoặc commit của việc đó.
- **Sprint Review và Retrospective (Cuối sprint, khoảng 45 phút):** Đánh giá sản phẩm sprint, ghi nhận vào Mục 7 và chốt kế hoạch sprint tiếp theo.

---

## Mục 2. Tổng quan tiến độ

Cập nhật lần cuối: 16/10/2026

| Sprint | Tuần | Mục tiêu sprint | Số việc Xong/Mẫu số | Trạng thái sprint | Ghi chú |
| :---: | :---: | :--- | :---: | :---: | :--- |
| **S1** | T1-2 | Môi trường chạy được và hiểu dữ liệu | 3/7 | Đang làm | Đã xong EDA và manifest; S1-01 và S1-02 chuyển Chưa làm để viết lại cho CPU; chờ xác nhận S1-03 và S1-04 (7 việc, 0 hủy, mẫu số 7) |
| **S2** | T3-4 | Khóa test, nạp dữ liệu ảnh xám, baseline và tiêu chí chấp nhận | 3/4 | Đang làm | Đã xong lọc trùng pHash, chia split 70/15/15 khóa test, lớp CXRDataset ảnh xám (PR #16); 4 việc DL đã hủy; S2-08 đang làm tại PR #17 (8 việc, 4 hủy, mẫu số 4) |
| **S3** | T5-6 | RQ1: so sánh nhóm đặc trưng thủ công | 0/6 | Chưa làm | Trích đặc trưng và so sánh 4 nhóm đặc trưng với Random Forest cố định trên 3 seed; chốt nhóm đặc trưng cho RQ2 (9 việc, 3 hủy, mẫu số 6) |
| **S4** | T7-8 | RQ2: so sánh bộ phân loại và chuẩn bị RQ3 | 0/4 | Chưa làm | So sánh 6 bộ phân loại trên nhóm đặc trưng tốt nhất của RQ1, chốt cấu hình, chuẩn bị bộ ảnh che cho RQ3 (7 việc, 3 hủy, mẫu số 4) |
| **S5** | T9-10 | RQ3 (shortcut learning), đánh giá test MỘT lần, notebook suy luận | 0/6 | Chưa làm | Đánh giá ảnh che và mở khóa tập test duy nhất một lần (6 việc, 0 hủy, mẫu số 6) |
| **S6** | T11-12 | Báo cáo, slide, demo, dự phòng, nộp, tập bảo vệ | 0/6 | Chưa làm | Hoàn thiện báo cáo tổng kết, ứng dụng Gradio và slide bảo vệ (6 việc, 0 hủy, mẫu số 6) |
| **Tổng** | **T1-12** | **Toàn bộ 6 sprint của đồ án** | **6/33** | **Đang triển khai** | **Đạt 18.2% Xong (6/33 việc), 1 việc Đang làm (S2-08), 26 việc Chưa làm, 10 việc Hủy – ngoài phạm vi (Tổng 43 việc, 10 hủy, mẫu số 33)** |

---

## Mục 3. Backlog chi tiết theo sprint

### Sprint 1 (Tuần 1 - 2): Môi trường chạy được và hiểu dữ liệu
**Sprint Goal:** Chứng minh môi trường chạy CPU (Kaggle hoặc máy cá nhân) hoạt động ổn định, xác minh tập dữ liệu 21.165 ảnh trên 4 lớp, xuất file `manifest.csv` đầy đủ mask và phân tích nguy cơ shortcut learning.

| ID | Tuần | Công việc | Gắn với | Phụ trách | Size | Trạng thái | Bằng chứng | Tiêu chí nghiệm thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S1-01 | T1 | Kiểm tra môi trường chạy (Kaggle CPU hoặc máy cá nhân), ghi chép cấu hình | Hạ tầng | Lê Minh (duyệt Minh Thuận) | M | Chưa làm | Chưa có PR | notebooks/00_setup_check.ipynb viết lại cho CPU (không import torch), in được phiên bản numpy, pandas, scikit-learn, scikit-image, opencv, pillow, gradio và kiểm tra được đường dẫn dữ liệu; cấu hình ghi trong docs/kaggle_setup_notes.md |
| S1-02 | T1 | Ghim phiên bản thư viện thực tế vào `requirements.txt` | Hạ tầng | Cả nhóm | S | Chưa làm | Chưa có PR | requirements.txt có scikit-image và phiên bản đã ghim của numpy, pandas, scikit-learn, scikit-image, opencv-python-headless, pillow, gradio (lấy từ kết quả setup_check); không còn chú thích '# chưa đo' cho thư viện đã ghim |
| S1-03 | T1 | 6/6 thành viên clone repo về máy và kiểm tra môi trường cục bộ | Hạ tầng | Cả nhóm | S | Chưa làm | Chưa có bằng chứng, cần Leader (Nguyễn Đức) xác nhận | 6/6 thành viên chạy notebooks/00_setup_check.ipynb (bản CPU) trên máy cục bộ và ghi lại kết quả; phụ thuộc S1-01 |
| S1-04 | T1 | Gửi danh sách câu hỏi làm rõ đề tài cho giảng viên | Báo cáo | Nguyễn Đức (Leader) | S | Chưa làm | Chưa có bằng chứng, cần Leader (Nguyễn Đức) xác nhận | Câu hỏi cho giảng viên đã gửi bằng văn bản hoặc email |
| S1-05 | T2 | Xây dựng notebook `01_download_and_eda.ipynb` đọc dữ liệu từ Kaggle | Hạ tầng | Nguyễn Đức | M | Xong | PR #1 đã merge, `notebooks/01_download_and_eda.ipynb`, kernel `cxr-eda-manifest` | Notebook tự động tìm dataset, đọc dữ liệu, không có lỗi lập trình |
| S1-06 | T2 | Tạo file `manifest.csv`, đối chiếu số lượng ảnh và mask 4 lớp | Chống rò rỉ | Nguyễn Đức | M | Xong | PR #1 đã merge, `splits/manifest.csv`, `outputs/eda_manifest/manifest.csv` | Số ảnh mỗi lớp khớp chính xác số biết (21.165 ảnh), báo cáo mask khớp 100% |
| S1-07 | T2 | Thống kê độ sáng, lưới ảnh mẫu và phát hiện 54 hash trùng lặp | Chống rò rỉ | Nguyễn Đức | S | Xong | PR #1 đã merge, `results/eda/brightness_distribution.png`, `results/eda/samples_grid.png` | Có danh sách nhóm ảnh trùng lặp, phân tích nghi vấn shortcut learning về độ sáng |

---

### Sprint 2 (Tuần 3 - 4): Khóa test, nạp dữ liệu ảnh xám, baseline và tiêu chí chấp nhận
**Sprint Goal:** Hoàn thành gom nhóm trùng pHash và chia train/val/test 70/15/15, khóa nghiêm ngặt tập test; xây dựng lớp nạp ảnh xám CXRDataset; xác lập tiêu chí chấp nhận threshold_v3.

| ID | Tuần | Công việc | Gắn với | Phụ trách | Size | Trạng thái | Bằng chứng | Tiêu chí nghiệm thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S2-01 | T3 | Gom nhóm ảnh trùng pHash (Hamming 0) trong 02_duplicates_and_split.ipynb: 178 nhóm, 401 ảnh; không loại ảnh nào khỏi bộ 21.165 ảnh | Chống rò rỉ | Nguyễn Đức | M | Xong | PR #4 đã merge (commit `83531cc`), `notebooks/02_duplicates_and_split.ipynb`, kernel `cxr-duplicates-and-split`, `splits/README.md` | Lọc nhóm trùng pHash ngưỡng T=0 (178 nhóm, 401 ảnh), 0 cặp trùng khác nhãn, không rò rỉ nhóm giữa các split |
| S2-02 | T3 | Chia tập train/val/test theo tỉ lệ 70/15/15 và gắn tag `test-locked` | Chống rò rỉ | Nguyễn Đức | M | Xong | PR #4 đã merge, `splits/split_v1.csv`, `splits/split_v1.sha256`, tag `test-locked` trỏ commit `e7c0993b`, `tests/test_split.py` pass | Tỉ lệ 70/15/15 chuẩn (độ lệch < 0.1%), khóa test set v1 bằng SHA256 và tag `test-locked` |
| S2-03 | T3 | Xây dựng lớp nạp ảnh xám CXRDataset trong src/dataset.py | Hạ tầng | Vũ Thương | M | Xong | PR #16; tests/test_dataset_grayscale.py | đọc ảnh xám 8-bit 299x299 theo manifest, không resize; khoá tập test (allow_test=False); tests/test_dataset_grayscale.py pass |
| S2-04 | T3 | Xây dựng pipeline huấn luyện `src/train.py` có hỗ trợ resume | Hạ tầng | Minh Thuận | L | Hủy – ngoài phạm vi | Hủy – ngoài phạm vi; bằng chứng cũ lưu ở tag archive-dl-ngoai-pham-vi | Pipeline mixed precision AMP, lưu `last.pt` và `best.pt` (macro-F1), hỗ trợ resume tự động, tên run chuẩn `<rq>_<backbone>_<strategy>_<imb>_s<seed>` |
| S2-05 | T3 | Chạy smoke test trên `03_smoke_test_train.ipynb` | Hạ tầng | Minh Thuận | S | Hủy – ngoài phạm vi | Hủy – ngoài phạm vi; bằng chứng cũ lưu ở tag archive-dl-ngoai-pham-vi | 12/12 pytest pass, giả lập ngắt phiên và resume thành công epoch 1 -> 2 trên Kaggle GPU trong 49s |
| S2-06 | T4 | Huấn luyện mô hình cơ sở Baseline trên `04_baseline.ipynb` | Hạ tầng | Minh Thuận | L | Hủy – ngoài phạm vi | Hủy – ngoài phạm vi; bằng chứng cũ lưu ở tag archive-dl-ngoai-pham-vi | Bảng baseline có macro-F1 và recall từng lớp trên tập validation |
| S2-07 | T4 | Đo đạc thời gian chạy thực tế mỗi run và ước tính tổng GPU-giờ | Hạ tầng | Minh Thuận | S | Hủy – ngoài phạm vi | Hủy – ngoài phạm vi; bằng chứng cũ lưu ở tag archive-dl-ngoai-pham-vi | Có số liệu thời gian từng epoch và bảng ước tính tổng GPU-giờ cho các tuần sau |
| S2-08 | T4 | Xác lập tiêu chí chấp nhận bằng văn bản (threshold_v3) | Báo cáo | Nguyễn Đức (Leader) | S | Đang làm | PR #17 (Draft) | results/threshold_v3.md được nhóm chốt (ngày chốt 16/10/2026), PR được duyệt chéo và merge |

---

### Sprint 3 (Tuần 5 - 6): RQ1: so sánh nhóm đặc trưng thủ công
**Sprint Goal:** trích đặc trưng và so sánh 4 nhóm đặc trưng với Random Forest cố định trên 3 seed; chốt nhóm đặc trưng cho RQ2.

| ID | Tuần | Công việc | Gắn với | Phụ trách | Size | Trạng thái | Bằng chứng | Tiêu chí nghiệm thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S3-01 | T5 | Cài đặt các kiến trúc DenseNet121 và EfficientNet-B0 trong `src/models.py` | RQ1 | Thái Tú | M | Hủy – ngoài phạm vi | Hủy – ngoài phạm vi; bằng chứng cũ lưu ở tag archive-dl-ngoai-pham-vi | Khởi tạo đúng kiến trúc, nạp đúng pretrained weights ImageNet |
| S3-02 | T5 | Thực hiện các run huấn luyện chiến lược frozen backbone | RQ1 | Thái Tú | L | Hủy – ngoài phạm vi | Hủy – ngoài phạm vi; bằng chứng cũ lưu ở tag archive-dl-ngoai-pham-vi | Ít nhất 50% run RQ1 hoàn tất, mỗi run có đầy đủ config, log và file `best.pt` |
| S3-03 | T5 | Thực hiện các run huấn luyện chiến lược full fine-tuning | RQ1 | Thái Tú | L | Hủy – ngoài phạm vi | Hủy – ngoài phạm vi; bằng chứng cũ lưu ở tag archive-dl-ngoai-pham-vi | Hoàn tất các run fine-tune trên cả 2 backbone với log và checkpoint |
| S3-04 | T6 | Chạy Random Forest cố định trên 4 nhóm đặc trưng, 3 seed (42, 43, 44) | RQ1 | Minh Thuận (duyệt Lê Minh) | L | Chưa làm | Chưa có nhánh/PR | RandomForestClassifier 500 cây, class_weight="balanced_subsample", không tinh chỉnh; 4 nhóm (histogram; GLCM + LBP; HOG; ghép) x 3 seed = 12 run; mỗi run có results/<run_id>/{config.yaml, metrics.json, log, preds_val.csv} theo cổng H1 của threshold_v3 |
| S3-05 | T6 | Tổng hợp bảng kết quả RQ1 (so sánh 4 nhóm đặc trưng) trong notebooks/05_rq1_backbones.ipynb | RQ1 | Hải Lý (duyệt Đức) | M | Chưa làm | Chưa có nhánh/PR | bảng macro-F1 và recall từng lớp của 4 nhóm đặc trưng (trung bình ± độ lệch chuẩn mẫu của 3 seed), kèm khoảng tin cậy bootstrap theo mục 5 threshold_v3 |
| S3-06 | T6 | Chốt nhóm đặc trưng tốt nhất trên validation cho RQ2 | RQ1 | Nguyễn Đức (duyệt Hải Lý) | S | Chưa làm | Chưa có nhánh/PR | theo mục 5 threshold_v3: nhóm khác histogram chỉ thay tham chiếu khi chênh macro-F1 trung bình >= 0,005 và khoảng tin cậy 95% của hiệu số không chứa 0; ghi vào biên bản trước khi xem kết quả |
| S3-07 | T5 | Trích đặc trưng histogram, GLCM, LBP | RQ1 | Thái Tú (duyệt Vũ Thương) | M | Chưa làm | Chưa có nhánh/PR | module trích đặc trưng chạy trên ảnh xám 299x299 không resize, đúng tham số mục 1 threshold_v3 (histogram 64 bin; GLCM 32 mức, khoảng cách [1, 3, 5], 4 góc, 5 thuộc tính; LBP uniform (8,1) và (16,2)); có test đơn vị; ghi số ảnh có correlation NaN vào log |
| S3-08 | T5 | Trích đặc trưng HOG và tạo nhóm ghép | RQ1 | Vũ Thương (duyệt Thái Tú) | M | Chưa làm | Chưa có nhánh/PR | HOG ô 16x16, khối 2x2, 9 hướng, L2-Hys; ghép = histogram + GLCM + LBP; đo thời gian trích (giây CPU) của từng nhóm |
| S3-09 | T6 | Script bootstrap ghép cặp và bảng báo cáo R1-R5 | RQ1 | Hải Lý (duyệt Đức) | M | Chưa làm | Chưa có nhánh/PR | bootstrap 2.000 lần: mỗi lần rút cùng một mẫu ảnh cho hai cấu hình, macro-F1 trung bình 3 seed, hiệu số A - B, khoảng tin cậy 95% theo phân vị 2,5-97,5; có test trên dữ liệu giả có đáp án biết trước; xuất R1, R2, R4, R5 (phải xong trước S3-06) |

---

### Sprint 4 (Tuần 7 - 8): RQ2: so sánh bộ phân loại và chuẩn bị RQ3
**Sprint Goal:** so sánh 6 bộ phân loại trên nhóm đặc trưng tốt nhất của RQ1, chốt cấu hình, chuẩn bị bộ ảnh che cho RQ3.

| ID | Tuần | Công việc | Gắn với | Phụ trách | Size | Trạng thái | Bằng chứng | Tiêu chí nghiệm thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S4-01 | T7 | Cài đặt Weighted Cross-Entropy và Focal Loss trong `src/train.py` | RQ2 | Vũ Thương | M | Hủy – ngoài phạm vi | Hủy – ngoài phạm vi; bằng chứng cũ lưu ở tag archive-dl-ngoai-pham-vi | Hàm mất mát tính đúng đạo hàm, hỗ trợ truyền trọng số lớp |
| S4-02 | T7 | Thử nghiệm WeightedRandomSampler và Data Augmentation bổ sung | RQ2 | Vũ Thương | M | Hủy – ngoài phạm vi | Hủy – ngoài phạm vi; bằng chứng cũ lưu ở tag archive-dl-ngoai-pham-vi | Sampler cân bằng tỉ lệ lấy mẫu giữa lớp ít (Viral Pneumonia) và lớp nhiều (Normal) |
| S4-03 | T7 | So sánh các bộ phân loại học máy cổ điển (RQ2) trong notebooks/06_rq2_imbalance.ipynb | RQ2 | Minh Thuận (duyệt Lê Minh) | L | Chưa làm | Chưa có nhánh/PR | Logistic Regression, k-NN, Decision Tree, Random Forest, SVM, Gradient Boosting trên nhóm đặc trưng tốt nhất của RQ1; siêu tham số chọn bằng StratifiedGroupKFold 5 fold theo group_id; trọng số lớp theo H3 của threshold_v3 |
| S4-04 | T8 | Chốt cấu hình mô hình tối ưu nhất và đóng băng tham số thực nghiệm | Hạ tầng | Cả nhóm | S | Chưa làm | Chưa có nhánh/PR | Cấu hình cuối cùng được ghi nhận văn bản và khóa chặt chẽ |
| S4-05 | T8 | Cài đặt module Grad-CAM trong `src/gradcam.py` và `07_gradcam_lung_attention.ipynb` | RQ3 | Lê Minh | L | Hủy – ngoài phạm vi | Hủy – ngoài phạm vi; bằng chứng cũ lưu ở tag archive-dl-ngoai-pham-vi | Xuất được bản đồ nhiệt Grad-CAM phủ trên ảnh X-quang, đối chiếu trực quan với mask |
| S4-06 | T8 | Phân tích chi tiết các ca dự đoán sai trên `09_error_analysis.ipynb` | Báo cáo | Lê Minh | M | Chưa làm | Chưa có nhánh/PR | Lập danh sách các ca nhầm lẫn điển hình giữa COVID, Lung Opacity và Pneumonia |
| S4-07 | T8 | Tạo bộ ảnh che thử nghiệm (chỉ giữ phổi / che ngoài phổi) | RQ3 | Lê Minh (duyệt Minh Thuận) | M | Chưa làm | Chưa có nhánh/PR | Bộ ảnh che được kiểm tra bằng mắt trên ít nhất 20 ảnh mỗi lớp không bị lệch mask |

---

### Sprint 5 (Tuần 9 - 10): RQ3 (Shortcut Learning), đánh giá test MỘT lần, suy luận
**Sprint Goal:** Đánh giá mô hình trên bộ ảnh che để đo lường độ lệ thuộc vào vùng ngoài phổi (RQ3); mở khóa tập test để đánh giá duy nhất một lần; hoàn thiện notebook suy luận độc lập.

*Ghi chú kỹ thuật RQ3:* manifest ghi mask_match_size = False cho 21165 ảnh (cột image_width = 299, image_height = 299; manifest không có cột kích thước mask); mask cần đổi kích thước về kích thước ảnh (nội suy gần nhất) trước khi che; kích thước mask thực tế: chưa đo.

| ID | Tuần | Công việc | Gắn với | Phụ trách | Size | Trạng thái | Bằng chứng | Tiêu chí nghiệm thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S5-01 | T9 | Đánh giá mô hình trên 3 tập (ảnh gốc, chỉ phổi, ngoài phổi) trong `08_rq3_masked_eval.ipynb` | RQ3 | Lê Minh | L | Chưa làm | Chưa có nhánh/PR | Bảng RQ3 trên tập validation thể hiện đầy đủ sự thay đổi độ chính xác trên 3 kiểu che |
| S5-02 | T9 | Tính permutation importance và so sánh đặc trưng trong phổi với ngoài phổi | RQ3 | Lê Minh | M | Chưa làm | Chưa có nhánh/PR | permutation importance và so sánh macro-F1 của đặc trưng chỉ trong phổi với chỉ ngoài phổi theo R3 của threshold_v3 |
| S5-03 | T9 | Soạn thảo kết luận nghiên cứu về nguy cơ shortcut learning | RQ3 | Lê Minh | M | Chưa làm | Chưa có nhánh/PR | Kết luận sơ bộ về mức độ shortcut learning dù kết quả có đẹp hay không |
| S5-04 | T10 | Mở khóa tập test và thực hiện đánh giá DUY NHẤT 1 LẦN trong `10_final_test_eval.ipynb` | Chống rò rỉ | Hải Lý | M | Chưa làm | Chưa có nhánh/PR | Kết quả test ghi đúng 1 lần duy nhất kèm mã hash file split để đảm bảo tính khách quan |
| S5-05 | T10 | Xuất ma trận nhầm lẫn (Confusion Matrix) và bảng chỉ số trên test | Báo cáo | Hải Lý | S | Chưa làm | Chưa có nhánh/PR | Bảng kết quả test đầy đủ accuracy, macro-F1 và recall từng lớp |
| S5-06 | T10 | Xây dựng notebook suy luận độc lập `11_inference_demo.ipynb` | Hạ tầng | Hải Lý | M | Chưa làm | Chưa có nhánh/PR | Notebook suy luận chạy lại được từ đầu trên một phiên Kaggle mới tinh |

---

### Sprint 6 (Tuần 11 - 12): Báo cáo, Demo, Bảo vệ và Hoàn tất
**Sprint Goal:** Hoàn thiện toàn diện báo cáo bài tập lớn, ứng dụng demo Gradio, slide thuyết trình; diễn tập bảo vệ và nộp sản phẩm đúng hạn.

| ID | Tuần | Công việc | Gắn với | Phụ trách | Size | Trạng thái | Bằng chứng | Tiêu chí nghiệm thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S6-01 | T11 | Soạn thảo báo cáo bài tập lớn trong thư mục `report/` | Báo cáo | Đức | L | Chưa làm | Chưa có nhánh/PR | Báo cáo trình bày đầy đủ RQ1-3, giới hạn nghiên cứu và cảnh báo y khoa |
| S6-02 | T11 | Xây dựng ứng dụng demo Gradio tương tác trong `demo/` | Hạ tầng | Thái Tú (duyệt Vũ Thương) | M | Chưa làm | Chưa có nhánh/PR | Một thành viên không phụ trách phần đó chạy lại được app và suy luận thành công |
| S6-03 | T11 | Hoàn thiện slide thuyết trình bảo vệ đề tài trong `slides/` | Báo cáo | Đức | M | Chưa làm | Chưa có nhánh/PR | Slide ngắn gọn, đầy đủ biểu đồ thực nghiệm và cấu trúc đề cương |
| S6-04 | T12 | Rà soát toàn bộ sản phẩm, code và định dạng theo yêu cầu giảng viên | Báo cáo | Cả nhóm | S | Chưa làm | Chưa có nhánh/PR | Đúng định dạng file, tiêu chuẩn kỹ thuật mà giảng viên yêu cầu |
| S6-05 | T12 | Tổ chức diễn tập thuyết trình và trả lời câu hỏi phản biện | Báo cáo | Cả nhóm | M | Chưa làm | Chưa có nhánh/PR | Diễn tập thuyết trình hoàn chỉnh ít nhất 1 lần trước buổi bảo vệ chính thức |
| S6-06 | T12 | Đóng gói sản phẩm cuối kỳ và nộp bài tập lớn | Báo cáo | Nguyễn Đức (Leader) | S | Chưa làm | Chưa có nhánh/PR | Nộp bài đúng hạn quy định, repo sạch sẽ và đồng bộ |

---

## Mục 4. Definition of Done chung

Một công việc chỉ được phép đánh dấu là **Xong** khi và chỉ khi thỏa mãn đầy đủ 6 điều kiện nghiêm ngặt sau đây:

1. **Pull Request được duyệt chéo:** Pull Request đã được ít nhất một thành viên trong cặp xem xét, kiểm tra và phê duyệt (Approve), sau đó được merge vào nhánh `main`.
2. **Notebook chạy lại được:** Tất cả notebook phải chạy lại thành công từ đầu đến cuối (`Run All`) trên môi trường sạch không phát sinh lỗi.
3. **Kết quả lưu đúng vị trí:** Bảng số liệu, log, tệp kết quả của run hoặc biểu đồ phải được lưu đúng thư mục quy định (`results/`, `splits/`, `report/`).
4. **Bảo mật và sạch repo:** Tuyệt đối không có dữ liệu ảnh thô, tệp mô hình đã huấn luyện (ví dụ `*.pkl`, `*.joblib`), token bí mật (`kaggle.json`, `.env`) bị commit vào Git.
5. **Đồng bộ tiến độ trên roadmap:** Dòng công việc tương ứng trong `docs/roadmap.md` đã được cập nhật trạng thái thành `Xong` kèm link Pull Request hoặc bằng chứng cụ thể.
6. **Tuân thủ khóa test:** Tuyệt đối không dùng tập test trong bất kỳ bước huấn luyện, chọn mô hình hay tinh chỉnh nào; tập test chỉ được mở ra đúng một lần tại Tuần 10.

---

## Mục 5. Vướng mắc và quyết định đang mở

Bảng tổng hợp các vấn đề cần giải quyết hoặc quyết định để tránh bị chặn tiến độ:

| Mục | Loại | Người quyết | Trạng thái | Ghi chú |
| :--- | :---: | :---: | :---: | :--- |
| Phương án tải trọng số ImageNet cho kernel huấn luyện | Quyết định | Leader (Nguyễn Đức) | Đóng – ngoài phạm vi (16/10/2026) | Không còn áp dụng sau khi chuyển sang Machine Learning cổ điển |
| Phân công chủ sở hữu module `src/models.py` | Quyết định | Leader (Nguyễn Đức) | Đã giải quyết | Đã phân công Thái Tú (Hàng Thái Tú) làm chủ sở hữu `src/models.py`, kèm cặp bởi Vũ Thương (Nguyễn Vũ Thương) |
| Quyết định giữ `split_v1` hay tạo `split_v2` | Quyết định | Leader (Nguyễn Đức) | Mở | `split_v1` đã khóa với ngưỡng T=0 (178 nhóm, 401 ảnh). Đã thống kê 735 cặp gần trùng (Hamming 1-4) khác split (325 Train-Test, 335 Train-Val, 75 Val-Test; 229 khác nhãn, 506 cùng nhãn). Mở cho tới khi Leader (Nguyễn Đức) đánh giá có cần sửa ngưỡng hay không (735 cặp gần trùng là giới hạn đã biết). |
| Rubric chấm điểm chi tiết của giảng viên | Rủi ro | Giảng viên / Leader (Nguyễn Đức) | Đang chờ | Chưa có rubric chấm điểm chính thức; nhóm cần liên hệ hỏi giảng viên để bám sát trọng số điểm. |
| Hình thức sản phẩm nộp cuối kỳ | Quyết định | Giảng viên / Leader (Nguyễn Đức) | Đang chờ | Giảng viên đã nêu: sản phẩm nộp gồm ứng dụng demo hoàn chỉnh, kèm báo cáo và bài thuyết trình bảo vệ. Còn chờ giảng viên: định nghĩa "hoàn chỉnh" (chạy trên máy, triển khai trực tuyến hay video demo), hạn nộp, và có bắt buộc dùng Gradio hay không. |
| Thông tin nguồn gốc của bộ dữ liệu CXR (Shortcut Learning) | Rủi ro | Cả nhóm | Mở | Dataset tổng hợp từ nhiều nguồn, thiếu metadata bệnh nhân (`patient_id`) và thiết bị chụp; độ lệch độ sáng lớp COVID cao hơn rõ rệt; cần ghi rõ giới hạn này trong báo cáo và đánh giá tại RQ3. |
| Quyết định 1 (chuẩn hóa B2 head-only) | Quyết định | Leader / Cả nhóm | Đóng – ngoài phạm vi (16/10/2026) | Không còn áp dụng sau khi gỡ bỏ toàn bộ baseline Deep Learning B2/B3 |
| Quyết định 2 (quy tắc chọn cấu hình RQ1 sang RQ2) | Quyết định | Leader / Cả nhóm | Đã chốt | Chấp nhận: chênh macro-F1 trung bình >= 0,005 VÀ khoảng tin cậy 95% bootstrap theo ảnh (ghép cặp, trung bình qua 3 seed, 2.000 lần lấy mẫu) không chứa 0; một phép so sánh chính (ứng viên tốt nhất với B3); quy tắc đóng băng trước khi xem kết quả RQ1 |
| Quyết định 3 (triển khai baseline lối tắt A1) | Quyết định | Leader / Cả nhóm | Đã chốt | Triển khai A1 (histogram độ xám + trung bình và độ lệch chuẩn; CPU) |
| Quyết định 4 (đo thử nghiệm ngân sách hai kiến trúc RQ1) | Quyết định | Leader / Cả nhóm | Đóng – ngoài phạm vi (16/10/2026) | Không còn áp dụng do không sử dụng DenseNet121, EfficientNet-B0 và GPU |
| Tiêu chí chấp nhận Threshold v2 | Quyết định | Leader / Cả nhóm | Mở | Đề xuất đã merge (PR #12); đang được thay thế bằng threshold_v3 (PR #17) |
| Hạn nộp, tiêu chí chấm, hình thức nộp | Quyết định | Giảng viên / Leader (Nguyễn Đức) | Đang chờ | Chờ giảng viên phản hồi danh sách câu hỏi làm rõ đề tài (S1-04) |
| Chuyển repo sang private | Quyết định | Leader (Nguyễn Đức) | Mở | Chuyển repo sang private sau khi PR tài liệu merge và trước Tuần 7 |
| Xác minh lưới ảnh mẫu | Rủi ro | Cả nhóm | Mở | `results/eda/samples_grid.png` chưa xác minh có chứa ảnh X-quang hay không |

---

## Mục 6. Quy tắc khi trễ tiến độ

Trong quá trình thực hiện, nếu tiến độ thực tế bị trễ hơn 1 tuần so với kế hoạch Sprint, nhóm sẽ áp dụng quy tắc cắt giảm phạm vi công việc theo thứ tự ưu tiên sau đây:

1. **Cắt giảm 1:** Cắt bỏ phần RQ3-C (phần mở rộng: huấn luyện lại mô hình từ đầu trên tập ảnh chỉ chứa vùng phổi).
2. **Cắt giảm 2:** Cắt bỏ thử nghiệm Focal Loss trong RQ2 (chỉ giữ lại Weighted Cross-Entropy Loss).
3. **Cắt giảm 3:** Bớt đi một nhóm đặc trưng trong RQ1 (bỏ nhóm ghép, chỉ giữ histogram, GLCM + LBP và HOG).
4. **Cắt giảm 4:** Giảm số lượng seed ngẫu nhiên chạy lặp lại từ 3 seed xuống còn 2 seed để tiết kiệm thời gian tính toán.
5. **Cắt giảm 5:** Cắt bỏ phần ứng dụng demo giao diện (Gradio app), chỉ giữ lại notebook suy luận `11_inference_demo.ipynb`.

**Các phần tuyệt đối KHÔNG được phép cắt giảm:**
- Quy tắc khóa tập test và cách ly dữ liệu.
- Mô hình cơ sở Baseline và ngưỡng chấp nhận tối thiểu.
- Đánh giá Macro-F1 và Recall trên từng lớp bệnh riêng biệt.
- RQ3-A và RQ3-B (đánh giá trên ảnh che phổi và trực quan hóa permutation importance).
- Phần giới hạn nghiên cứu và cảnh báo y khoa trong báo cáo bài tập lớn.

---

## Mục 7. Sprint Review và Retrospective

Khung theo dõi đánh giá và rút kinh nghiệm cuối mỗi sprint (điền nội dung thực tế ở buổi họp cuối sprint, không tự ý bịa đặt):

### Sprint 1 (Tuần 1 - 2)
- **Đã làm được:** sprint đã kết thúc; chưa có biên bản review/retro trong repo
- **Chưa xong và vì sao:** sprint đã kết thúc; chưa có biên bản review/retro trong repo
- **Đổi gì ở sprint sau:** sprint đã kết thúc; chưa có biên bản review/retro trong repo

### Sprint 2 (Tuần 3 - 4)
- **Đã làm được:** sprint đã kết thúc; chưa có biên bản review/retro trong repo
- **Chưa xong và vì sao:** sprint đã kết thúc; chưa có biên bản review/retro trong repo
- **Đổi gì ở sprint sau:** sprint đã kết thúc; chưa có biên bản review/retro trong repo

### Sprint 3 (Tuần 5 - 6)
- **Đã làm được:** Chưa diễn ra
- **Chưa xong và vì sao:** Chưa diễn ra
- **Đổi gì ở sprint sau:** Chưa diễn ra

### Sprint 4 (Tuần 7 - 8)
- **Đã làm được:** Chưa diễn ra
- **Chưa xong và vì sao:** Chưa diễn ra
- **Đổi gì ở sprint sau:** Chưa diễn ra

### Sprint 5 (Tuần 9 - 10)
- **Đã làm được:** Chưa diễn ra
- **Chưa xong và vì sao:** Chưa diễn ra
- **Đổi gì ở sprint sau:** Chưa diễn ra

### Sprint 6 (Tuần 11 - 12)
- **Đã làm được:** Chưa diễn ra
- **Chưa xong và vì sao:** Chưa diễn ra
- **Đổi gì ở sprint sau:** Chưa diễn ra

---

## Mục 8. Lịch sử thay đổi

| Phiên bản | Ngày | Người sửa | Nội dung thay đổi |
| :---: | :---: | :---: | :--- |
| **v1.0** | 28/09/2026 | Cả nhóm | Khởi tạo khung lộ trình 12 tuần ban đầu |
| **v2.0** | 02/10/2026 | Leader và nhóm | Nâng cấp lộ trình sang bảng theo dõi tiến độ Scrum rút gọn 6 sprint có trạng thái và bằng chứng |
| **v2.1** | 03/10/2026 | Kỹ sư ML & Nhóm | Đồng bộ tiến độ Sprint 2 (hoàn tất Tuần 3 Track A & Track B, khóa test, GPU smoke test pass) và mở lại các quyết định của Leader |
| **v2.2** | 04/10/2026 | Nguyễn Đức (Leader) & Nhóm | Chuẩn hóa toàn bộ nội dung sang tiếng Việt có dấu chuẩn UTF-8, đồng bộ tên các thành viên (Nguyễn Đức, Minh Thuận, Thái Tú, Vũ Thương, Lê Minh, Hải Lý) thay cho mã định danh TV1-TV6 |
| **v2.3** | 13/10/2026 | Trợ lý theo dõi tiến độ | Đồng bộ tiến độ Sprint 2 sau khi PR #11 merge (S2-06, S2-07, S2-08 chuyển Xong), ghi nhận 4 quyết định nhóm đã chốt tại Mục 5 |
| **v2.4** | 14/10/2026 | Kỹ sư ML & Nhóm | Đồng bộ sau kiểm toán V1: cập nhật merge commit PR #2 cho S1-02, cập nhật Mục 5 (trọng số ImageNet & Threshold v2), Mục 7 (Sprint 1-2 retro), bổ sung ghi chú mask RQ3 |
| **v3.0** | 16/10/2026 | Kỹ sư ML & Nhóm | Chuyển hướng ML cổ điển theo quy định giảng viên: 10 việc Hủy, 11 việc sửa, 3 việc mới, mẫu số mới 33 việc; cập nhật tiêu chí nghiệm thu cho các việc ML cổ điển và ngưỡng threshold_v3 (quyết định ngày 16/10/2026) |
