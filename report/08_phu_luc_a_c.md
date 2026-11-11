# Phụ lục

Ba phụ lục này thuộc phần ghi chú kỹ thuật của quyển, nên đường dẫn tệp, tên lệnh và mã cấu hình được giữ nguyên. Mọi con số trong phụ lục lấy từ bản ghi trong kho (`results/`, `demo/README.md`) hoặc sinh bằng lệnh in kèm ở cuối mỗi phụ lục; phần bảng của Phụ lục B sinh bởi `scripts/report_appendix_b.py` để tránh chép tay.

## Phụ lục A. Cài đặt, tải mô hình và vận hành ứng dụng demo

### A.1. Môi trường và cài đặt

Ứng dụng demo (`demo/streamlit_app.py`) chạy trên Python 3.12 — cùng phiên bản mặc định của Streamlit Community Cloud và môi trường đã chạy toàn bộ kiểm thử của đề tài. Các bước:

```bash
python -m venv .venv-demo
.venv-demo\Scripts\activate        # Windows
pip install -r demo/requirements.txt
```

Toàn bộ 334 phép kiểm thử trong 26 module đã chạy đủ trên môi trường này (333 pass, 1 bỏ qua; mục 5.4 của Chương 5).

### A.2. Mô hình đóng băng và kiểm tra tính toàn vẹn

Artifact `cxr_inference_model_cache.joblib` (kernel v3) không nằm trong git; ứng dụng tải từ kho Hugging Face công khai `duc16/cxr-svm-demo`. Kho đã được kiểm tra tải ẩn danh: HTTP 200, đúng 7.842.399 byte và băm SHA-256 khớp giá trị công bố.

**Bảng A.2: Thông số mô hình đóng băng**

| Thành phần | Giá trị |
| :--- | :--- |
| Đặc trưng | 152 chiều: Histogram 64 + GLCM 60 + LBP 28 |
| Ảnh đầu vào | Xám, 299 × 299, ảnh gốc (không mask) |
| Bộ phân loại | `SVC(kernel="rbf", C=10.0, gamma="scale", class_weight="balanced", probability=True, random_state=42)` |
| Tiền xử lý | `StandardScaler` fit chỉ trên split `train` (14.815 ảnh) |
| Lớp dự đoán | COVID, Lung_Opacity, Normal, Viral Pneumonia |
| Kích thước tệp | 7.842.399 byte |
| SHA-256 | `3e14bd570c734d9d8f39a2d340b176a40a41c9559cc2da0ef67bbd8e15735058` |

Trước khi nạp, ứng dụng kiểm băm SHA-256 của tệp artifact, sau đó kiểm thêm băm của tệp split, phiên bản scikit-learn, số mẫu train, siêu tham số SVM và băm của mã trích đặc trưng. Trong đó khớp một điều kiện thì ứng dụng dừng và báo lỗi, không nạp mô hình.

### A.3. Biến môi trường

**Bảng A.1: Biến môi trường của ứng dụng demo**

| Biến | Bắt buộc | Ý nghĩa |
| :--- | :---: | :--- |
| `CXR_MODEL_PATH` | Không | Đường dẫn artifact cục bộ; nếu đặt thì bỏ qua tải mạng |
| `CXR_MODEL_REPO` | Không | Kho Hugging Face dạng `tai-khoan/ten-kho`; mặc định `duc16/cxr-svm-demo` |
| `CXR_MODEL_FILE` | Không | Tên tệp trong kho; mặc định `cxr_inference_model_cache.joblib` |
| `CXR_MODEL_REVISION` | Không | Nhánh/tag/commit của kho; mặc định nhánh mặc định |
| `CXR_MODEL_SHA256` | Không | Băm kỳ vọng; mặc định băm ở Bảng A.2 |
| `HF_TOKEN` | Không | Chỉ cần khi kho mô hình là private |

Với Streamlit Community Cloud, không bắt buộc khai báo secrets vì ứng dụng mặc định dùng kho công khai của dự án; secrets (`.streamlit/secrets.toml`, đã bị `.gitignore` chặn) chỉ cần khi trỏ sang kho khác.

### A.4. Vận hành và triển khai

Chạy cục bộ với artifact sẵn có (không cần mạng):

```bash
set CXR_MODEL_PATH=outputs\k_v3_out\cxr_inference_model_cache.joblib
streamlit run demo/streamlit_app.py
```

Không đặt biến trên thì ứng dụng tải artifact từ kho công khai. Triển khai trên Streamlit Community Cloud: đẩy nhánh lên GitHub, mở pull request (chưa merge cũng được), đăng nhập `share.streamlit.io` bằng tài khoản GitHub có quyền với kho, chọn **Create app** với entrypoint `demo/streamlit_app.py`, chọn Python 3.12 rồi **Deploy**. Ứng dụng tự dùng `demo/requirements.txt` đặt cạnh entrypoint. Repo của đề tài ở chế độ private, nên tài khoản triển khai cần quyền admin với kho và cấp OAuth scope `repo`.

Cổng tương đương kiểm ứng dụng demo cho kết quả đúng như pipeline huấn luyện: chạy 200 ảnh validation (seed 42), đối chiếu nhãn với `results/rq3_ghep_svm_orig_to_orig_s42/preds_val.csv`, kỳ vọng `file_hash MD5 khớp: 200/200`, `NHÃN KHỚP: 200/200` và mã thoát 0. Cổng chỉ đọc split `val`, không đọc ảnh split `test`.

```bash
python demo/verify_model_equivalence.py --dataset-root D:\cxr_data\COVID-19_Radiography_Dataset
```

### A.5. Kiểm thử liên quan

Hai bộ test gắn với ứng dụng: `tests/test_model_artifact.py` (21 phép) kiểm tra nạp và kiểm băm artifact, từ chối tệp theo tên và định dạng; `tests/test_streamlit_app.py` (22 phép) kiểm tra tiền xử lý ảnh, cổng tên tệp, cảnh báo y khoa và việc không ghi ảnh tải lên xuống đĩa. Test dùng ảnh giả lập trong bộ nhớ, không đọc ảnh thật và không gọi mạng.

### A.6. Giới hạn và an toàn

- Ứng dụng là demo học thuật, không phải thiết bị y tế và chưa kiểm định lâm sàng; kết quả suy luận không được dùng cho quyết định y khoa.
- Chỉ tải ảnh X-quang đã ẩn danh; ảnh tải lên chỉ nằm trong bộ nhớ của phiên, không ghi xuống đĩa và không ghi vào nhật ký.
- Ảnh khác 299 × 299 được đổi cỡ kèm cảnh báo; mô hình chỉ được kiểm chứng trên ảnh 299 × 299 của bộ dữ liệu COVID-19 Radiography.
- Chênh lệch validation – test chỉ được nêu như quan sát, không nêu nguyên nhân (quy ước D4).

**Ghi chú nguồn Phụ lục A:** `demo/README.md` (toàn văn), `src/model_artifact.py`, `demo/streamlit_app.py`, `demo/verify_model_equivalence.py`, `demo/requirements.txt`.

---

## Phụ lục B. Cấu trúc kho mã nguồn và danh sách bài kiểm thử

### B.1. Cấu trúc kho

Số tệp dưới đây là số tệp được git theo dõi (`git ls-files`), đếm tại thời điểm nộp báo cáo; thư mục `results/` chứa tệp kết quả sinh trong quá trình chạy thực nghiệm nên chiếm phần lớn số lượng.

**Bảng B.1: Cấu trúc thư mục cấp một của kho**

| Thư mục / tệp | Số tệp | Nội dung |
| :--- | ---: | :--- |
| `src/` | 15 | Mã nguồn: nạp dữ liệu, trích đặc trưng, bộ chạy RQ1–RQ3, metrics, bootstrap, suy luận, đo độ trễ, kiểm artifact |
| `notebooks/` | 9 | Notebook theo trình tự: kiểm môi trường, EDA, trùng lặp và chia tập, RQ1, RQ2, RQ3, phân tích lỗi, đánh giá test một lần, suy luận |
| `demo/` | 6 | Ứng dụng Streamlit, kiểm tra tải/kiểm băm artifact, cổng tương đương, yêu cầu thư viện |
| `tests/` | 26 | Bộ kiểm thử tự động pytest (danh sách ở Bảng B.2) |
| `scripts/` | 3 | Script sinh hình cho báo cáo và bảng Phụ lục B |
| `results/` | 186 | Tệp kết quả và biên bản của các bước S1–S6 |
| `kaggle/` | 23 | Mã và biên bản chạy thực nghiệm trên kernel Kaggle |
| `splits/` | 5 | Manifest, tệp phân chia và báo cáo kiểm tra sau chia |
| `docs/` | 7 | Quy chuẩn báo cáo, cẩm nang viết, phân công thành viên, kế hoạch, nguồn dữ liệu |
| `report/` | 13 | Sáu chương báo cáo, mục lục nguồn, tài liệu tham khảo, phụ lục, hình vẽ |
| `slides/` | 1 | Chỗ để slide thuyết trình (chưa có nội dung) |
| `configs/`, `.github/`, `.streamlit/` | 3 | Cấu hình cơ sở, mẫu pull request, cấu hình Streamlit |
| Tệp gốc (`README.md`, `requirements.txt`, `pytest.ini`, `.gitignore`, `.gitattributes`) | 5 | Điều khiển dự án và môi trường |

### B.2. Danh sách bài kiểm thử

Số phép kiểm thử của mỗi module đếm theo đầu ra `pytest --collect-only -q`, tức một test tham số hóa được đếm theo từng bộ tham số — cùng cách đo với số liệu ở mục 5.4 của Chương 5.

**Bảng B.2: 26 module kiểm thử và số phép kiểm thử (334 phép)**

| Module | Số phép kiểm thử |
| :--- | ---: |
| `test_bootstrap.py` | 13 |
| `test_dataset_grayscale.py` | 1 |
| `test_eda_brightness.py` | 11 |
| `test_error_analysis.py` | 2 |
| `test_features_hist_glcm_lbp.py` | 14 |
| `test_features_hog_ghep.py` | 14 |
| `test_final_test_report_and_notebook.py` | 6 |
| `test_final_test_runner.py` | 72 |
| `test_inference_demo.py` | 34 |
| `test_inference_demo_notebook.py` | 17 |
| `test_inference_latency.py` | 18 |
| `test_metrics.py` | 4 |
| `test_model_artifact.py` | 21 |
| `test_report_figures.py` | 5 |
| `test_report_figures_final_test.py` | 10 |
| `test_report_figures_rq3.py` | 6 |
| `test_report_tables_match_sources.py` | 4 |
| `test_rq1_report_and_selection.py` | 3 |
| `test_rq1_runner.py` | 17 |
| `test_rq2_report_and_selection.py` | 4 |
| `test_rq2_runner.py` | 10 |
| `test_rq3_report_and_selection.py` | 9 |
| `test_rq3_runner.py` | 7 |
| `test_source_labels.py` | 5 |
| `test_split.py` | 5 |
| `test_streamlit_app.py` | 22 |
| **Tổng cộng** | **334** |

Chạy đầy đủ trên môi trường pin của ứng dụng (`.venv-demo`, cùng `demo/requirements.txt`) cho 333 pass và 1 bỏ qua; phần bỏ qua là bộ kiểm thử notebook khi môi trường không có `nbformat`. Bảng này được sinh bằng:

```bash
python scripts/report_appendix_b.py
```

**Ghi chú nguồn Phụ lục B:** đầu ra `git ls-files` cho Bảng B.1; `scripts/report_appendix_b.py` (đọc trực tiếp đầu ra `pytest --collect-only -q`) cho Bảng B.2; số pass/skip ở mục 5.4 của Chương 5.

---

## Phụ lục C. Lưới siêu tham số và tham số chọn của sáu bộ phân loại

Sáu bộ phân loại của RQ2 chạy trên nhóm đặc trưng cố định `ghep` (152 chiều). Siêu tham số chọn bằng `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` trên tập `train` (14.815 ảnh), chia nhóm theo `group_id`. Ba bộ tất định (`lr`, `knn`, `svm`) chạy một lần ở seed 42; ba bộ ngẫu nhiên (`dt`, `rf`, `gb`) chạy ở ba seed 42, 43, 44. Các bộ nhạy cảm tỷ lệ (`lr`, `knn`, `svm`) dùng `StandardScaler` chỉ fit trên phần train của từng fold.

### C.1. Lưới siêu tham số

**Bảng C.1: Lưới siêu tham số của sáu bộ phân loại**

| Bộ phân loại | Lưới siêu tham số (số lượng cụm) |
| :--- | :--- |
| `lr` | `C` ∈ {0,01; 0,1; 1,0; 10,0} (4) |
| `knn` | `n_neighbors` ∈ {3; 5; 11} × `weights` ∈ {uniform; distance} (6) |
| `dt` | `max_depth` ∈ {10; 20; None} × `min_samples_leaf` ∈ {1; 5} (6) |
| `rf` | `n_estimators` ∈ {300; 500} × `max_depth` ∈ {20; None} (4) |
| `svm` | `C` ∈ {1,0; 10,0} × `gamma` ∈ {scale; auto} (4) |
| `gb` | `n_estimators` ∈ {100; 200} × `learning_rate` = 0,1 × `max_depth` ∈ {3; 5} (4) |

Trọng số lớp (`class_weight='balanced'`) là thành phần cố định của bộ phân loại, không nằm trong lưới; `knn` không hỗ trợ trọng số lớp nên dùng cân bằng bằng `weights='distance'`. Lưới trên đọc trực tiếp từ `PARAM_GRIDS` trong `src/rq2_runner.py`.

### C.2. Tham số chọn và kết quả trên tập validation

**Bảng C.2: Siêu tham số chọn qua 5-fold CV và Macro-F1 validation của sáu bộ phân loại**

| Hạng F1 | Mã | Siêu tham số chọn | Số seed | Macro-F1 (TB ± SD) | 95% CI bootstrap |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | `svm` | `C=10.0, gamma='scale'` | 1 | 0,9024 | [0,8909; 0,9129] |
| 2 | `gb` | `n_estimators=200, learning_rate=0.1, max_depth=5` | 3 | 0,8868 ± 0,0030 | [0,8749; 0,8976] |
| 3 | `rf` | `n_estimators=300, max_depth=None` | 3 | 0,8582 ± 0,0033 | [0,8432; 0,8716] |
| 4 | `lr` | `C=10.0` | 1 | 0,8370 | [0,8221; 0,8505] |
| 5 | `knn` | `n_neighbors=5, weights='distance'` | 1 | 0,8242 | [0,8075; 0,8397] |
| 6 | `dt` | `max_depth=10, min_samples_leaf=1` | 3 | 0,7271 ± 0,0017 | [0,7090; 0,7449] |

Ba bộ tất định không có độ lệch chuẩn (cổng H3 của đề tài). Bộ phân loại tham chiếu của RQ2 là `rf` (cấu hình dùng ở RQ1); ứng viên `svm` vượt tham chiếu 0,0442 điểm macro-F1 với khoảng tin cậy 95% của hiệu số `[+0,031983; +0,058032]` không chứa 0.

### C.3. Thứ hạng chi phí huấn luyện

**Bảng C.3: Chi phí huấn luyện của sáu bộ phân loại (giây CPU)**

| Hạng chi phí | Mã | Giây CPU 5-fold CV | Fit trung bình mỗi seed | Tổng giây CPU |
| :---: | :--- | ---: | ---: | ---: |
| 1 | `knn` | 18,467 | 0,039 | 18,506 |
| 2 | `dt` | 189,601 | 4,254 | 202,362 |
| 3 | `lr` | 86,869 | 185,638 | 272,507 |
| 4 | `svm` | 419,094 | 60,754 | 479,848 |
| 5 | `gb` | 1.765,091 | 132,789 | 2.163,459 |
| 6 | `rf` | 3.086,971 | 151,621 | 3.541,833 |

Chi phí của một bộ phân loại là tổng giây CPU huấn luyện (5-fold CV cộng fit trên toàn bộ tập train của các seed tương ứng), không gồm trích đặc trưng: bước trích nhóm `ghep` dùng chung cho cả sáu bộ tốn 1.402,867 giây CPU (1.155,273 giây cho train và 247,594 giây cho validation, tức 0,077985 giây CPU một ảnh). Biên bản thứ hạng chi phí được ghi và commit trước khi mở điểm số của lô chạy.

**Ghi chú nguồn Phụ lục C:** `src/rq2_runner.py` (`PARAM_GRIDS`, `CLASSIFIERS`), `results/rq2_classifier_selection_record.md`, `results/rq2_cost_rank_record.md`, `results/summary_rq2_full.json`.
