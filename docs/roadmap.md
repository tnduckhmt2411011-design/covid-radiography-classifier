# Kế hoạch và Bảng theo dõi tiến độ đồ án (Scrum rút gọn)

Tài liệu theo dõi tiến độ thực hiện đồ án môn Học máy trong 12 tuần, áp dụng mô hình Scrum rút gọn dành cho nhóm 6 sinh viên beginner. Toàn bộ tiến độ được đồng bộ với trạng thái thực tế trên GitHub repository.

---

## Mục 1. Cách đọc tài liệu

### 1.1. Hệ thống 5 trạng thái công việc

Mỗi công việc trong backlog chỉ nhận đúng 1 trong 5 trạng thái sau, gắn chặt với hoạt động trên GitHub:

- **Chưa làm:** Mặc định cho tất cả các công việc chưa bắt đầu hoặc chưa tìm thấy bằng chứng xác thực trên GitHub/repo.
- **Đang làm:** Có nhánh tính năng `feat/<ten>-<viec>` đang mở trên repo, đang được phát triển và chưa tạo Pull Request.
- **Chờ duyệt:** Đã mở Pull Request trên GitHub, đang trong quá trình kiểm tra và chờ thành viên trong cặp duyệt (Approve), chưa merge vào `main`.
- **Xong:** Pull Request đã được merge vào nhánh `main` VÀ đạt đầy đủ tiêu chí nghiệm thu của việc đó. Đối với các việc không qua Pull Request (ví dụ: gửi câu hỏi cho giảng viên), bắt buộc cần Leader (Nguyễn Đức) xác nhận bằng văn bản.
- **Bị chặn:** Công việc không thể tiếp tục do vướng mắc về kỹ thuật, thiếu thông tin, hoặc phụ thuộc chưa hoàn thành. Bắt buộc phải có dòng giải thích nguyên nhân tại Mục 5.

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

Cập nhật lần cuối: 03/10/2026

| Sprint | Tuần | Mục tiêu sprint | Số việc Xong/Tổng | Trạng thái sprint | Ghi chú |
| :---: | :---: | :--- | :---: | :---: | :--- |
| **S1** | T1-2 | Môi trường chạy được và hiểu dữ liệu | 5/7 | Đang làm | Đã xong setup Kaggle, EDA và manifest; chờ Leader (Nguyễn Đức) xác nhận T1-03 và T1-04 |
| **S2** | T3-4 | Khóa test, khung huấn luyện chạy được, có baseline và ngưỡng chấp nhận | 5/8 | Đang làm | Hoàn tất 100% Tuần 3 (Track A & Track B, khóa test, GPU smoke test pass); chuẩn bị Tuần 4 baseline |
| **S3** | T5-6 | Hoàn tất RQ1 (so sánh backbone và chiến lược fine-tune) | 0/6 | Chưa làm | So sánh DenseNet121 và EfficientNet-B0 |
| **S4** | T7-8 | Hoàn tất RQ2 (mất cân bằng lớp), chốt cấu hình cuối, Grad-CAM, phân tích lỗi, bộ ảnh che | 0/7 | Chưa làm | Thử nghiệm Weighted Loss, Focal Loss, tạo mask ảnh |
| **S5** | T9-10 | RQ3 (shortcut learning), đánh giá test MỘT lần, notebook suy luận | 0/6 | Chưa làm | Đánh giá ảnh che và mở khóa tập test duy nhất một lần |
| **S6** | T11-12 | Báo cáo, slide, demo, dự phòng, nộp, tập bảo vệ | 0/6 | Chưa làm | Hoàn thiện báo cáo tổng kết và ứng dụng Gradio |
| **Tổng** | **T1-12** | **Toàn bộ 6 sprint của đồ án** | **10/40** | **Đang triển khai** | **Đạt 25.0% tổng khối lượng công việc** |

---

## Mục 3. Backlog chi tiết theo sprint

### Sprint 1 (Tuần 1 - 2): Môi trường chạy được và hiểu dữ liệu
**Sprint Goal:** Chứng minh môi trường tính toán Kaggle GPU hoạt động ổn định, xác minh tập dữ liệu 21.165 ảnh trên 4 lớp, xuất file `manifest.csv` đầy đủ mask và phân tích nguy cơ shortcut learning.

| ID | Tuần | Công việc | Gắn với | Phụ trách | Size | Trạng thái | Bằng chứng | Tiêu chí nghiệm thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S1-01 | T1 | Kiểm tra môi trường Kaggle GPU, ghi chép cấu hình phần cứng | Hạ tầng | Cả nhóm | M | Xong | PR #2 đã merge, `docs/kaggle_setup_notes.md`, kernel `cxr-setup-check` | Chạy thành công trên 2x Tesla T4, xác định torch 2.10.0+cu128 và CUDA 12.8 không lỗi |
| S1-02 | T1 | Ghim phiên bản thư viện thực tế vào `requirements.txt` | Hạ tầng | Cả nhóm | S | Xong | PR #2 đã merge, commit `e7c88b0`, `docs/kaggle_setup_notes.md` | Ghi chép đầy đủ torch==2.10.0+cu128, torchvision==0.25.0+cu128 từ log Kaggle |
| S1-03 | T1 | 6/6 thành viên clone repo về máy và kiểm tra môi trường cục bộ | Hạ tầng | Cả nhóm | S | Chưa làm | Chưa có bằng chứng, cần Leader (Nguyễn Đức) xác nhận | 6/6 người clone repo, chạy xong `00_setup_check` không lỗi |
| S1-04 | T1 | Gửi danh sách câu hỏi làm rõ đề tài cho giảng viên | Báo cáo | Nguyễn Đức (Leader) | S | Chưa làm | Chưa có bằng chứng, cần Leader (Nguyễn Đức) xác nhận | Câu hỏi cho giảng viên đã gửi bằng văn bản hoặc email |
| S1-05 | T2 | Xây dựng notebook `01_download_and_eda.ipynb` đọc dữ liệu từ Kaggle | Hạ tầng | Nguyễn Đức | M | Xong | PR #1 đã merge, `notebooks/01_download_and_eda.ipynb`, kernel `cxr-eda-manifest` | Notebook tự động tìm dataset, đọc dữ liệu, không có lỗi lập trình |
| S1-06 | T2 | Tạo file `manifest.csv`, đối chiếu số lượng ảnh và mask 4 lớp | Chống rò rỉ | Nguyễn Đức | M | Xong | PR #1 đã merge, `splits/manifest.csv`, `outputs/eda_manifest/manifest.csv` | Số ảnh mỗi lớp khớp chính xác số biết (21.165 ảnh), báo cáo mask khớp 100% |
| S1-07 | T2 | Thống kê độ sáng, lưới ảnh mẫu và phát hiện 54 hash trùng lặp | Chống rò rỉ | Nguyễn Đức | S | Xong | PR #1 đã merge, `results/eda/brightness_distribution.png`, `samples_grid.png` | Có danh sách nhóm ảnh trùng lặp, phân tích nghi vấn shortcut learning về độ sáng |

---

### Sprint 2 (Tuần 3 - 4): Khóa test, khung huấn luyện, baseline và ngưỡng chấp nhận
**Sprint Goal:** Hoàn thành lọc trùng và chia train/val/test 70/15/15, khóa nghiêm ngặt tập test; hoàn thiện khung `train.py` có checkpoint resume; huấn luyện thành công mô hình baseline và chốt ngưỡng chấp nhận.

| ID | Tuần | Công việc | Gắn với | Phụ trách | Size | Trạng thái | Bằng chứng | Tiêu chí nghiệm thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S2-01 | T3 | Lọc bỏ 54 ảnh trùng bằng imagehash trong `02_duplicates_and_split.ipynb` | Chống rò rỉ | Nguyễn Đức | M | Xong | PR #4 đã merge (commit `83531cc`), `notebooks/02_duplicates_and_split.ipynb`, kernel `cxr-duplicates-and-split`, `splits/README.md` | Lọc nhóm trùng pHash ngưỡng T=0 (178 nhóm, 401 ảnh), 0 cặp trùng khác nhãn, không rò rỉ nhóm giữa các split |
| S2-02 | T3 | Chia tập train/val/test theo tỉ lệ 70/15/15 và gắn tag `test-locked` | Chống rò rỉ | Nguyễn Đức | M | Xong | PR #4 đã merge, `splits/split_v1.csv`, `split_v1.sha256`, tag `test-locked` trỏ commit `e7c0993b`, `tests/test_split.py` pass | Tỉ lệ 70/15/15 chuẩn (độ lệch < 0.1%), khóa test set v1 bằng SHA256 và tag `test-locked` |
| S2-03 | T3 | Xây dựng DataLoader và Data Augmentation cơ bản trong `src/dataset.py` | Hạ tầng | Vũ Thương | M | Xong | PR #5 đã merge (commit `f5c688b`), `src/dataset.py`, `tests/test_resume.py` | Dataset đọc `split_v1.csv`, ảnh xám -> 3 kênh, chuẩn hóa ImageNet, augment chỉ cho train (không lật ảnh), chặn split test bằng `allow_test` |
| S2-04 | T3 | Xây dựng pipeline huấn luyện `src/train.py` có hỗ trợ resume | Hạ tầng | Minh Thuận | L | Xong | PR #5 đã merge, commit `f5c688b`, `src/train.py`, `src/metrics.py`, `src/models.py`, `tests/test_metrics.py`, `tests/test_resume.py` | Pipeline mixed precision AMP, lưu `last.pt` và `best.pt` (macro-F1), hỗ trợ resume tự động, tên run chuẩn `<rq>_<backbone>_<strategy>_<imb>_s<seed>` |
| S2-05 | T3 | Chạy smoke test trên `03_smoke_test_train.ipynb` | Hạ tầng | Minh Thuận | S | Xong | PR #5 đã merge, `notebooks/03_smoke_test_train.ipynb`, kernel `cxr-smoke-test-train` (GPU T4x2), `outputs/smoke_test/smoke_test_report.json` | 12/12 pytest pass, giả lập ngắt phiên và resume thành công epoch 1 -> 2 trên Kaggle GPU trong 49s |
| S2-06 | T4 | Huấn luyện mô hình cơ sở Baseline trên `04_baseline.ipynb` | Hạ tầng | Minh Thuận | L | Chưa làm | Chưa có nhánh/PR | Bảng baseline có macro-F1 và recall từng lớp trên tập validation |
| S2-07 | T4 | Đo đạc thời gian chạy thực tế mỗi run và ước tính tổng GPU-giờ | Hạ tầng | Minh Thuận | S | Chưa làm | Chưa có nhánh/PR | Có số liệu thời gian từng epoch và bảng ước tính tổng GPU-giờ cho các tuần sau |
| S2-08 | T4 | Xác lập ngưỡng hiệu năng tối thiểu chấp nhận được bằng văn bản | Báo cáo | Nguyễn Đức (Leader) | S | Chưa làm | Chưa có nhánh/PR | Ngưỡng chấp nhận viết bằng lời trong `results/`, gắn liền với kết quả baseline |

---

### Sprint 3 (Tuần 5 - 6): Hoàn tất RQ1 (So sánh backbone và chiến lược fine-tune)
**Sprint Goal:** Hoàn thành so sánh thực nghiệm giữa DenseNet121 và EfficientNet-B0 dưới 2 chiến lược (frozen vs fine-tune) trên 3 seed ngẫu nhiên; chọn ra 1 cấu hình tối ưu nhất đưa sang RQ2.

| ID | Tuần | Công việc | Gắn với | Phụ trách | Size | Trạng thái | Bằng chứng | Tiêu chí nghiệm thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S3-01 | T5 | Cài đặt các kiến trúc DenseNet121 và EfficientNet-B0 trong `src/models.py` | RQ1 | Thái Tú | M | Chưa làm | Chưa có nhánh/PR | Khởi tạo đúng kiến trúc, nạp đúng pretrained weights ImageNet |
| S3-02 | T5 | Thực hiện các run huấn luyện chiến lược frozen backbone | RQ1 | Thái Tú | L | Chưa làm | Chưa có nhánh/PR | Ít nhất 50% run RQ1 hoàn tất, mỗi run có đầy đủ config, log và file `best.pt` |
| S3-03 | T5 | Thực hiện các run huấn luyện chiến lược full fine-tuning | RQ1 | Thái Tú | L | Chưa làm | Chưa có nhánh/PR | Hoàn tất các run fine-tune trên cả 2 backbone với log và checkpoint |
| S3-04 | T6 | Chạy lặp lại thực nghiệm trên 3 seed ngẫu nhiên (s42, s43, s44) | RQ1 | Thái Tú | L | Chưa làm | Chưa có nhánh/PR | Đủ số liệu 3 seed cho từng cấu hình để tính toán thống kê |
| S3-05 | T6 | Tổng hợp bảng kết quả so sánh RQ1 trong `05_rq1_backbones.ipynb` | RQ1 | Thái Tú | M | Chưa làm | Chưa có nhánh/PR | Bảng RQ1 có trung bình cộng và độ lệch chuẩn qua 3 seed cho macro-F1, recall |
| S3-06 | T6 | Phân tích và chốt 1 cấu hình backbone tốt nhất trên validation cho RQ2 | RQ1 | Thái Tú | S | Chưa làm | Chưa có nhánh/PR | Có biên bản kết luận rõ ràng dựa trên validation metric để chuyển tiếp |

---

### Sprint 4 (Tuần 7 - 8): Hoàn tất RQ2, chốt cấu hình, Grad-CAM, phân tích lỗi, bộ ảnh che
**Sprint Goal:** Hoàn thành thử nghiệm các giải pháp xử lý mất cân bằng lớp (RQ2); đóng băng cấu hình tối ưu; cài đặt Grad-CAM; phân tích lỗi và tạo bộ ảnh che mặt nạ phổi.

| ID | Tuần | Công việc | Gắn với | Phụ trách | Size | Trạng thái | Bằng chứng | Tiêu chí nghiệm thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S4-01 | T7 | Cài đặt Weighted Cross-Entropy và Focal Loss trong `src/train.py` | RQ2 | Vũ Thương | M | Chưa làm | Chưa có nhánh/PR | Hàm mất mát tính đúng đạo hàm, hỗ trợ truyền trọng số lớp |
| S4-02 | T7 | Thử nghiệm WeightedRandomSampler và Data Augmentation bổ sung | RQ2 | Vũ Thương | M | Chưa làm | Chưa có nhánh/PR | Sampler cân bằng tỉ lệ lấy mẫu giữa lớp ít (Viral Pneumonia) và lớp nhiều (Normal) |
| S4-03 | T7 | Huấn luyện so sánh các chiến lược trên `06_rq2_imbalance.ipynb` | RQ2 | Vũ Thương | L | Chưa làm | Chưa có nhánh/PR | Bảng RQ2 ghi rõ recall và F1 riêng cho lớp Viral Pneumonia và các lớp khác, so với baseline |
| S4-04 | T8 | Chốt cấu hình mô hình tối ưu nhất và đóng băng tham số thực nghiệm | Hạ tầng | Cả nhóm | S | Chưa làm | Chưa có nhánh/PR | Cấu hình cuối cùng được ghi nhận văn bản và khóa chặt chẽ |
| S4-05 | T8 | Cài đặt module Grad-CAM trong `src/gradcam.py` và `07_gradcam_lung_attention.ipynb` | RQ3 | Lê Minh | L | Chưa làm | Chưa có nhánh/PR | Xuất được bản đồ nhiệt Grad-CAM phủ trên ảnh X-quang, đối chiếu trực quan với mask |
| S4-06 | T8 | Phân tích chi tiết các ca dự đoán sai trên `09_error_analysis.ipynb` | Báo cáo | Lê Minh | M | Chưa làm | Chưa có nhánh/PR | Lập danh sách các ca nhầm lẫn điển hình giữa COVID, Lung Opacity và Pneumonia |
| S4-07 | T8 | Tạo bộ ảnh che thử nghiệm (chỉ giữ phổi / che ngoài phổi) | RQ3 | Lê Minh | M | Chưa làm | Chưa có nhánh/PR | Bộ ảnh che được kiểm tra bằng mắt trên ít nhất 20 ảnh mỗi lớp không bị lệch mask |

---

### Sprint 5 (Tuần 9 - 10): RQ3 (Shortcut Learning), đánh giá test MỘT lần, suy luận
**Sprint Goal:** Đánh giá mô hình trên bộ ảnh che để đo lường độ lệ thuộc vào vùng ngoài phổi (RQ3); mở khóa tập test để đánh giá duy nhất một lần; hoàn thiện notebook suy luận độc lập.

| ID | Tuần | Công việc | Gắn với | Phụ trách | Size | Trạng thái | Bằng chứng | Tiêu chí nghiệm thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S5-01 | T9 | Đánh giá mô hình trên 3 tập (ảnh gốc, chỉ phổi, ngoài phổi) trong `08_rq3_masked_eval.ipynb` | RQ3 | Lê Minh | L | Chưa làm | Chưa có nhánh/PR | Bảng RQ3 trên tập validation thể hiện đầy đủ sự thay đổi độ chính xác trên 3 kiểu che |
| S5-02 | T9 | Tính toán chỉ số tập trung năng lượng Grad-CAM bên trong mask phổi | RQ3 | Lê Minh | M | Chưa làm | Chưa có nhánh/PR | Có tỉ lệ % năng lượng nằm trong phổi so với ngoài phổi |
| S5-03 | T9 | Soạn thảo kết luận nghiên cứu về nguy cơ shortcut learning | RQ3 | Lê Minh | M | Chưa làm | Chưa có nhánh/PR | Kết luận sơ bộ về mức độ shortcut learning dù kết quả có đẹp hay không |
| S5-04 | T10 | Mở khóa tập test và thực hiện đánh giá DUY NHẤT 1 LẦN trong `10_final_test_eval.ipynb` | Chống rò rỉ | Hải Lý | M | Chưa làm | Chưa có nhánh/PR | Kết quả test ghi đúng 1 lần duy nhất kèm mã hash file split để đảm bảo tính khách quan |
| S5-05 | T10 | Xuất ma trận nhầm lẫn (Confusion Matrix) và bảng chỉ số trên test | Báo cáo | Hải Lý | S | Chưa làm | Chưa có nhánh/PR | Bảng kết quả test đầy đủ accuracy, macro-F1 và recall từng lớp |
| S5-06 | T10 | Xây dựng notebook suy luận độc lập `11_inference_demo.ipynb` | Hạ tầng | Hải Lý | M | Chưa làm | Chưa có nhánh/PR | Notebook suy luận chạy lại được từ đầu trên một phiên Kaggle mới tinh |

---

### Sprint 6 (Tuần 11 - 12): Báo cáo, Demo, Bảo vệ và Hoàn tất
**Sprint Goal:** Hoàn thiện toàn diện báo cáo bài tập lớn, ứng dụng demo Gradio, slide thuyết trình; diễn tập bảo vệ và nộp sản phẩm đúng hạn.

| ID | Tuần | Công việc | Gắn với | Phụ trách | Size | Trạng thái | Bằng chứng | Tiêu chí nghiệm thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S6-01 | T11 | Soạn thảo báo cáo bài tập lớn trong thư mục `report/` | Báo cáo | Hải Lý | L | Chưa làm | Chưa có nhánh/PR | Báo cáo trình bày đầy đủ RQ1-3, giới hạn nghiên cứu và cảnh báo y khoa |
| S6-02 | T11 | Xây dựng ứng dụng demo Gradio tương tác trong `demo/` | Hạ tầng | Hải Lý | M | Chưa làm | Chưa có nhánh/PR | Một thành viên không phụ trách phần đó chạy lại được app và suy luận thành công |
| S6-03 | T11 | Hoàn thiện slide thuyết trình bảo vệ đề tài trong `slides/` | Báo cáo | Cả nhóm | M | Chưa làm | Chưa có nhánh/PR | Slide ngắn gọn, đầy đủ biểu đồ thực nghiệm và cấu trúc đề cương |
| S6-04 | T12 | Rà soát toàn bộ sản phẩm, code và định dạng theo yêu cầu giảng viên | Báo cáo | Cả nhóm | S | Chưa làm | Chưa có nhánh/PR | Đúng định dạng file, tiêu chuẩn kỹ thuật mà giảng viên yêu cầu |
| S6-05 | T12 | Tổ chức diễn tập thuyết trình và trả lời câu hỏi phản biện | Báo cáo | Cả nhóm | M | Chưa làm | Chưa có nhánh/PR | Diễn tập thuyết trình hoàn chỉnh ít nhất 1 lần trước buổi bảo vệ chính thức |
| S6-06 | T12 | Đóng gói sản phẩm cuối kỳ và nộp bài tập lớn | Báo cáo | Nguyễn Đức (Leader) | S | Chưa làm | Chưa có nhánh/PR | Nộp bài đúng hạn quy định, repo sạch sẽ và đồng bộ |

---

## Mục 4. Definition of Done chung

Một công việc chỉ được phép đánh dấu là **Xong** khi và chỉ khi thỏa mãn đầy đủ 6 điều kiện nghiêm ngặt sau đây:

1. **Pull Request được duyệt chéo:** Pull Request đã được ít nhất một thành viên trong cặp xem xét, kiểm tra và phê duyệt (Approve), sau đó được merge vào nhánh `main`.
2. **Notebook chạy lại được:** Tất cả notebook phải chạy lại thành công từ đầu đến cuối (`Run All`) trên môi trường sạch không phát sinh lỗi.
3. **Kết quả lưu đúng vị trí:** Bảng số liệu, log, checkpoint hoặc biểu đồ phải được lưu đúng thư mục quy định (`results/`, `splits/`, `report/`).
4. **Bảo mật và sạch repo:** Tuyệt đối không có dữ liệu ảnh thô, checkpoint trọng số lớn (`*.pt`, `*.pth`), token bí mật (`kaggle.json`, `.env`) bị commit vào Git.
5. **Đồng bộ tiến độ trên roadmap:** Dòng công việc tương ứng trong `docs/roadmap.md` đã được cập nhật trạng thái thành `Xong` kèm link Pull Request hoặc bằng chứng cụ thể.
6. **Tuân thủ khóa test:** Tuyệt đối không dùng tập test trong bất kỳ bước huấn luyện, chọn mô hình hay tinh chỉnh nào; tập test chỉ được mở ra đúng một lần tại Tuần 10.

---

## Mục 5. Vướng mắc và quyết định đang mở

Bảng tổng hợp các vấn đề cần giải quyết hoặc quyết định để tránh bị chặn tiến độ:

| Mục | Loại | Người quyết | Trạng thái | Ghi chú |
| :--- | :---: | :---: | :---: | :--- |
| Phương án tải trọng số ImageNet cho kernel huấn luyện | Quyết định | Leader (Nguyễn Đức) | Mở | Đề xuất (bật internet `enable_internet: true` cho kernel huấn luyện hoặc gắn Kaggle Dataset chứa weights), CHƯA CHỐT. Người quyết: Leader (Nguyễn Đức). Cần chốt trước khi chạy Baseline Tuần 4. |
| Phân công chủ sở hữu module `src/models.py` | Quyết định | Leader (Nguyễn Đức) | Đã giải quyết | Đã phân công Thái Tú (Hàng Thái Tú) làm chủ sở hữu `src/models.py`, kèm cặp bởi Vũ Thương (Nguyễn Vũ Thương) |
| Quyết định giữ `split_v1` hay tạo `split_v2` | Quyết định | Leader (Nguyễn Đức) | Mở | `split_v1` đã khóa với ngưỡng T=0 (178 nhóm, 401 ảnh). Đã thống kê 735 cặp gần trùng (Hamming 1-4) khác split (325 Train-Test, 335 Train-Val, 75 Val-Test; 229 khác nhãn, 506 cùng nhãn). Mở cho tới khi Leader (Nguyễn Đức) đánh giá có cần sửa ngưỡng hay không (735 cặp gần trùng là giới hạn đã biết). |
| Rubric chấm điểm chi tiết của giảng viên | Rủi ro | Giảng viên / Leader (Nguyễn Đức) | Đang chờ | Chưa có rubric chấm điểm chính thức; nhóm cần liên hệ hỏi giảng viên để bám sát trọng số điểm. |
| Hình thức sản phẩm nộp cuối kỳ | Quyết định | Giảng viên / Leader (Nguyễn Đức) | Đang chờ | Cần xác nhận sản phẩm nộp gồm những gì (mô hình fine-tune, notebook, báo cáo, có bắt buộc demo app Gradio hay không). |
| Thông tin nguồn gốc của bộ dữ liệu CXR (Shortcut Learning) | Rủi ro | Cả nhóm | Mở | Dataset tổng hợp từ nhiều nguồn, thiếu metadata bệnh nhân (`patient_id`) và thiết bị chụp; độ lệch độ sáng lớp COVID cao hơn rõ rệt; cần ghi rõ giới hạn này trong báo cáo và đánh giá tại RQ3. |

---

## Mục 6. Quy tắc khi trễ tiến độ

Trong quá trình thực hiện, nếu tiến độ thực tế bị trễ hơn 1 tuần so với kế hoạch Sprint, nhóm sẽ áp dụng quy tắc cắt giảm phạm vi công việc theo thứ tự ưu tiên sau đây:

1. **Cắt giảm 1:** Cắt bỏ phần RQ3-C (phần mở rộng: huấn luyện lại mô hình từ đầu trên tập ảnh chỉ chứa vùng phổi).
2. **Cắt giảm 2:** Cắt bỏ thử nghiệm Focal Loss trong RQ2 (chỉ giữ lại Weighted Cross-Entropy Loss).
3. **Cắt giảm 3:** Bớt đi một kiến trúc backbone trong RQ1 (chỉ tập trung vào DenseNet121 hoặc EfficientNet-B0).
4. **Cắt giảm 4:** Giảm số lượng seed ngẫu nhiên chạy lặp lại từ 3 seed xuống còn 2 seed để tiết kiệm thời gian tính toán.
5. **Cắt giảm 5:** Cắt bỏ phần ứng dụng demo giao diện (Gradio app), chỉ giữ lại notebook suy luận `11_inference_demo.ipynb`.

**Các phần tuyệt đối KHÔNG được phép cắt giảm:**
- Quy tắc khóa tập test và cách ly dữ liệu.
- Mô hình cơ sở Baseline và ngưỡng chấp nhận tối thiểu.
- Đánh giá Macro-F1 và Recall trên từng lớp bệnh riêng biệt.
- RQ3-A và RQ3-B (đánh giá trên ảnh che phổi và trực quan hóa Grad-CAM).
- Phần giới hạn nghiên cứu và cảnh báo y khoa trong báo cáo bài tập lớn.

---

## Mục 7. Sprint Review và Retrospective

Khung theo dõi đánh giá và rút kinh nghiệm cuối mỗi sprint (điền nội dung thực tế ở buổi họp cuối sprint, không tự ý bịa đặt):

### Sprint 1 (Tuần 1 - 2)
- **Đã làm được:** Chưa diễn ra (sẽ điền vào cuối Tuần 2)
- **Chưa xong và vì sao:** Chưa diễn ra
- **Đổi gì ở sprint sau:** Chưa diễn ra

### Sprint 2 (Tuần 3 - 4)
- **Đã làm được:** Hoàn thành chia split 70/15/15 chống rò rỉ pHash, khóa tập test (tag `test-locked`), xây dựng xong khung huấn luyện PyTorch AMP có resume, chạy smoke test thành công trên Kaggle GPU T4x2 đạt 12/12 pytest pass
- **Chưa xong và vì sao:** Các việc Tuần 4 (Baseline, đo giờ GPU, ngưỡng chấp nhận) chưa bắt đầu
- **Đổi gì ở sprint sau:** Chốt phương án trọng số ImageNet với Leader (Nguyễn Đức) để chạy Baseline

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
