# Thư mục Báo cáo Bài tập lớn (S6-01)

Thư mục này chứa báo cáo cuối kỳ của đề tài **Phân loại Ảnh X-quang Lồng ngực (COVID-19 Radiography Database)**. Tệp này là **đề cương và bản đồ nguồn số liệu**: mỗi mục của báo cáo phải trích từ đúng tệp ghi bên dưới.

Người soạn: Nguyễn Đức. Người duyệt: Hải Lý (theo [`docs/OWNERS.md`](../docs/OWNERS.md)).

---

## 1. Quy chuẩn trình bày bắt buộc

Chi tiết đầy đủ tại [`docs/report_standards.md`](../docs/report_standards.md) và [`docs/academic_writing_guide.md`](../docs/academic_writing_guide.md).

| Hạng mục | Quy định |
| :--- | :--- |
| Khổ giấy | A4 (210 × 297 mm), in một mặt, hướng đứng |
| Lề | Trên 2,0–2,5 cm; Dưới 2,0–2,5 cm; Trái 3,0–3,5 cm; Phải 2,0 cm |
| Phông chữ | Times New Roman, Unicode dựng sẵn |
| Cỡ chữ | Heading 1: 14–16 pt in hoa đậm; Heading 2: 13–14 pt đậm; Heading 3: 13 pt đậm nghiêng; thân bài 13 pt; bảng và chú thích 10–11 pt |
| Giãn dòng | 1,2–1,3 lines (khuyến nghị 1,3) |
| Đoạn | Before/After 3–6 pt, thụt đầu dòng 1,0–1,27 cm, canh đều hai bên |
| Đánh số trang | Phần mở đầu: La Mã thường (i, ii, iii); từ Chương 1: Ả Rập (1, 2, 3); bìa không đánh số |
| Trích dẫn | IEEE, số thứ tự trong ngoặc vuông `[1]`, xếp theo thứ tự xuất hiện |
| Giới hạn số trang | Không có giới hạn cứng. Quy chuẩn chỉ định dạng trang, không quy định độ dài |

Tên trường trên bìa: **TRƯỜNG ĐẠI HỌC KỸ THUẬT - CÔNG NGHỆ CẦN THƠ (CTUT)**, khoa Công nghệ Thông tin và Truyền thông (CICT). Giảng viên hướng dẫn: TS. Lê Anh Nhã Uyên. Danh sách sinh viên và MSSV lấy từ [`docs/OWNERS.md`](../docs/OWNERS.md) và bảng xác nhận của lớp.

---

## 2. Nguyên tắc bắt buộc khi viết

1. **Quy tắc D4, giữ nguyên văn:** *"Mọi lời giải thích về sự khác biệt giữa val và test đều là giả thuyết chưa kiểm chứng, không nêu nguyên nhân."*
   Nguồn: [`docs/report_standards.md`](../docs/report_standards.md) dòng 176, [`docs/academic_writing_guide.md`](../docs/academic_writing_guide.md) mục 3, [`results/final_test_protocol_record.md`](../results/final_test_protocol_record.md) quyết định D4. Không dùng chữ "nguyên nhân", "do đó", "vì vậy" khi nói về chênh lệch val–test.
2. **Số liệu test chỉ lấy từ tệp kết quả.** Không đọc, không mở, không trích dẫn bất kỳ ảnh nào của split `test`. Nguồn duy nhất: `results/final_test/*.json`.
3. **Mỗi con số phải truy về CSV/JSON gốc.** Không chép lại bảng từ tệp `.md` tóm tắt. Bảng RQ3 trong `results/rq3_shortcut_learning_conclusion.md` từng bị chép tay lệch 23 ô so với CSV; nay đã đồng bộ và có kiểm thử chặn tái phát.
4. **Chỉ học máy cổ điển.** Cổng H7 cấm `torch`, `torchvision`, `tensorflow`, `keras`, `timm` trong toàn bộ mã và notebook.
5. **Không trộn tập.** Validation có 3.174 ảnh, test có 3.176 ảnh. Số lỗi validation là 349; số lỗi test là 427. Hai bộ số này không thay thế nhau.
6. **RQ3 có 5 kịch bản, không phải 3.** Ba chế độ mask (`original`, `lung_only`, `outside_only`) tạo ra 5 kịch bản: `orig_to_orig`, `lung_to_lung`, `out_to_out`, `orig_to_out`, `orig_to_lung`.
7. **Văn phong:** theo [`docs/academic_writing_guide.md`](../docs/academic_writing_guide.md). Không dùng từ ngữ cường điệu, không mở bài rập khuôn, không danh từ hóa rườm rà, không nhồi liên từ nối.

---

## 3. Cấu trúc báo cáo

Bố cục 6 chương theo [`docs/report_standards.md`](../docs/report_standards.md) mục 3.2. Tổng cộng **50 mục**: 9 mục đầu quyển, 37 tiểu mục trong 6 chương, 4 mục cuối quyển.

### Phần mở đầu (9 mục, đánh số La Mã)

| # | Mục | Nguồn |
| :-: | :--- | :--- |
| 1 | Trang bìa chính | [`00a_trang_bia_va_loi.md`](00a_trang_bia_va_loi.md) mục 1; khung viền `report/figures/khung_trang_bia.png` sinh bởi `scripts/make_cover_border.py`; thông tin bắt buộc theo `docs/report_standards.md` mục 3.1 |
| 2 | Trang bìa phụ | [`00a_trang_bia_va_loi.md`](00a_trang_bia_va_loi.md) mục 2 |
| 3 | Lời cảm ơn | [`00a_trang_bia_va_loi.md`](00a_trang_bia_va_loi.md) mục 3; viết mới |
| 4 | Lời cam đoan | [`00a_trang_bia_va_loi.md`](00a_trang_bia_va_loi.md) mục 4; viết mới, cam kết trung thực số liệu |
| 5 | Tóm tắt tiếng Việt và Abstract tiếng Anh | [`09_tom_tat_abstract.md`](09_tom_tat_abstract.md); mỗi bản không quá một trang: bối cảnh, phương pháp, kết quả test, kết luận; chỉ dùng số liệu đã có ở Chương 3–6 |
| 6 | Mục lục | [`00c_muc_luc_va_danh_muc.md`](00c_muc_luc_va_danh_muc.md) phần 1, sinh bởi `scripts/report_frontmatter.py` |
| 7 | Danh mục ký hiệu và chữ viết tắt | [`00b_danh_muc_ky_hieu.md`](00b_danh_muc_ky_hieu.md); chỉ ký hiệu đã xác minh xuất hiện trong sáu chương |
| 8 | Danh mục bảng biểu | [`00c_muc_luc_va_danh_muc.md`](00c_muc_luc_va_danh_muc.md) phần 2 (32 bảng), sinh bởi cùng script |
| 9 | Danh mục hình ảnh | [`00c_muc_luc_va_danh_muc.md`](00c_muc_luc_va_danh_muc.md) phần 3 (4 hình), sinh bởi cùng script |

### Chương 1. Giới thiệu và tổng quan đề tài (5 tiểu mục)

| # | Mục | Nguồn |
| :-: | :--- | :--- |
| 1.1 | Bối cảnh và lý do chọn đề tài | Nguồn ngoài: Chowdhury et al. (2020), Kermany et al. (2018). Số liệu dịch tễ phải có trích dẫn, không dùng số không nguồn |
| 1.2 | Mục tiêu và ba câu hỏi nghiên cứu RQ1–RQ3 | `results/threshold_v3.md` Mục 1 |
| 1.3 | Phạm vi nghiên cứu và ranh giới kỹ thuật (Cổng H7) | `results/threshold_v3.md` Mục 4 (H7); `tests/` kiểm tra cấm import học sâu |
| 1.4 | Đóng góp của đề tài | Tổng hợp từ Chương 3–5 |
| 1.5 | Cấu trúc báo cáo | Tệp này, mục 3 |

### Chương 2. Dữ liệu và phương pháp nghiên cứu (12 tiểu mục)

| # | Mục | Nguồn |
| :-: | :--- | :--- |
| 2.1 | Nguồn gốc bộ dữ liệu và độ tin cậy thông tin | `docs/dataset_provenance.md`. Quy mô 21.165 ảnh: Normal 10.192, Lung_Opacity 6.012, COVID 3.616, Viral Pneumonia 1.345 (đếm từ `splits/split_v1.csv`) |
| 2.2 | Phân tích khám phá dữ liệu và nguy cơ học lối tắt từ độ sáng và metadata tệp | `src/eda_brightness.py` (chạy `python -m src.eda_brightness`) đọc `splits/manifest.csv`, ghi `results/eda/brightness_by_class.csv` (thống kê theo lớp + AUC) và `results/eda/brightness_channels.json` (tỉ lệ ảnh trong IQR của Normal, số ảnh theo hệ màu); hình `results/eda/brightness_distribution.png` từ `notebooks/01_download_and_eda.ipynb` cell 6. Kiểm thử: `tests/test_eda_brightness.py` |
| 2.3 | Gom nhóm ảnh trùng bằng pHash ngưỡng T = 0 | `notebooks/02_duplicates_and_split.ipynb`; 178 nhóm, 401 ảnh, 0 nhóm lệch nhãn (`docs/roadmap.md` dòng 93) |
| 2.4 | Phân chia train/val/test 70/15/15 và cơ chế khóa tập test (Cổng H2) | `splits/split_v1.csv` (14.815 / 3.174 / 3.176), SHA-256 `f99e03d3d5cfc32f2bbc9befbdef45a07a256458a837a6d420a6658ed7583d98`; `results/final_test/UNLOCK_RECORD.json`; `results/final_test_protocol_record.md` mục 2 (G1–G6) |
| 2.5 | Giới hạn tồn tại của dữ liệu | 735 cặp gần trùng Hamming 2–4 (325 Train–Test, 335 Train–Val, 75 Val–Test; 229 khác nhãn) tại `docs/roadmap.md` dòng 187; thiếu mã bệnh nhân và tuổi chưa xác minh tại `results/report_rq3/r5_gioi_han.md` và `results/threshold_v3.md` Mục 6 (R5). Phép đo macro-F1 trên 273 ảnh validation có ảnh gần trùng (0,9068 so với 0,9024 toàn tập) tại `results/val_near_duplicate_subset/`, sinh bởi `scripts/val_near_duplicate_subset.py` |
| 2.6.1 | Đặc trưng histogram cường độ sáng, 64 chiều | `src/features_hist_glcm_lbp.py` |
| 2.6.2 | Đặc trưng kết cấu GLCM 60 chiều và LBP 28 chiều | `src/features_hist_glcm_lbp.py`. GLCM: 5 thuộc tính × 3 khoảng cách × 4 góc = 60. LBP: R=1/P=8 (10 bin) + R=2/P=16 (18 bin) = 28 |
| 2.6.3 | Đặc trưng hướng biên HOG, 10.404 chiều | `src/features_hog_ghep.py` (`HOG_DIM = 10404`) || 2.6.4 | Nhóm đặc trưng ghép 152 chiều | `src/features_hog_ghep.py` (`N_FEATURES` = 152; `src/inference_demo.py`) |
| 2.7 | Chuẩn hóa dữ liệu, StandardScaler chỉ fit trên train (Cổng H6) | `src/rq2_runner.py` |
| 2.8 | Sáu thuật toán phân loại và không gian siêu tham số | `src/rq2_runner.py` (`CLASSIFIERS`); `results/rq2_classifier_selection_record.md` |
| 2.9 | Phương pháp đánh giá thống kê và bootstrap ghép cặp 2.000 lần | `src/bootstrap.py`; `results/report_rq1/bootstrap_config.json` |

### Chương 3. Kết quả RQ1 và RQ2 trên tập validation (4 tiểu mục)

| # | Mục | Nguồn |
| :-: | :--- | :--- |
| 3.1 | RQ1: so sánh bốn nhóm đặc trưng trên Random Forest | `results/report_rq1/r1_summary.csv` (macro-F1 TB ± SD 3 seed và 95% CI: ghep 0,8599 ± 0,0030; glcmlbp 0,8156 ± 0,0023; hist 0,7829 ± 0,0013; hog 0,7625 ± 0,0038), `r1_per_seed.csv` (điểm từng seed), `results/rq1_cost_rank_record.md` (giây CPU mỗi ảnh). Bảng 3.1 trong báo cáo lấy từ `r1_summary.csv`; cột recall lớp Viral Pneumonia lấy từ cùng tệp |
| 3.2 | Kiểm định thống kê và quyết định chọn nhóm ghép cho RQ2 | `results/report_rq1/r1_bootstrap_vs_reference.csv`: ghep − hist = +0,0770, CI [+0,0611; +0,0925], không chứa 0; glcmlbp − hist = +0,0328, CI [+0,0131; +0,0513]; hog − hist = −0,0203, CI [−0,0419; +0,0014], chứa 0. Ngưỡng chấp nhận +0,005 ghi ở Bảng 1.1 của Chương 1 (`results/threshold_v3.md`). Quyết định chọn `ghep` sang RQ2 ở `results/rq1_feature_selection_record.md` mục 4 |
| 3.3 | RQ2: so sánh sáu bộ phân loại trên nhóm ghép | `results/report_rq2/r1_summary.csv` (svm 0,9024; gb 0,8868 ± 0,0030; rf 0,8582 ± 0,0033; lr 0,8370; knn 0,8242; dt 0,7271 ± 0,0017), `results/report_rq2/r1_bootstrap_vs_reference.csv` (năm phép so với mốc `rf`: svm +0,0442, CI [+0,0320; +0,0580]; bốn phép còn lại âm và CI không chứa 0), `results/report_rq2/bootstrap_config.json` (n = 3.174, 2.000 lần, seed 42). Cấu hình SVM đã chọn ở `results/rq2_ghep_svm_s42/metrics.json` |
| 3.4 | Đánh giá SVM RBF trên validation | `results/rq2_ghep_svm_s42/metrics.json` (accuracy 89,00%, balanced accuracy 0,9078, macro-F1 0,9024, chỉ số từng lớp, ma trận nhầm lẫn 4×4), `results/rq2_ghep_svm_s42/preds_val.csv` (nhãn thực, nhãn dự đoán và bốn cột xác suất từng ảnh), `results/eda/normal_source_labels.csv` (10.192 ảnh lớp Normal tách theo nguồn RSNA / Mooney, sinh bằng `python -m src.source_labels`), `results/error_analysis/error_analysis_summary.md` (349 lỗi; 240 lỗi đồng thuận; 138 lỗi có `proba_pred` từ 0,80). Hình 3.1 sinh bằng `python -m scripts.report_figures`, ghi ra `report/figures/03_ma_tran_nham_lon_svm_val.png`; kiểm thử `tests/test_report_figures.py` và `tests/test_source_labels.py`. Không dùng `results/final_test/confusion_matrix_test.png` vì thuộc Chương 5 |

### Chương 4. Mức phụ thuộc vào vùng ngoài mặt nạ phổi (RQ3) (3 tiểu mục)

| # | Mục | Nguồn |
| :-: | :--- | :--- |
| 4.1 | Năm kịch bản che mặt nạ phổi | `results/report_rq3/r1_summary.csv` (macro-F1, CI, chỉ số từng lớp), `results/report_rq3/r4_sampling_error.csv` (accuracy, sai số chuẩn), `results/report_rq3/r3_shortcut_bootstrap.csv` (năm phép so ghép cặp) và `results/report_rq3/r1_bootstrap_vs_reference.csv` (bốn phép so với mốc `orig_to_orig`), `results/report_rq3/r2_normal_lung_opacity.csv` (cặp nhầm Normal–Lung_Opacity), `results/rq3_comparison_protocol_record.md` (thiết kế kịch bản, quy tắc đóng băng), `results/rq3_shortcut_learning_conclusion.md` mục 1.1 và 2. Mốc nền: `results/b0_majority/metrics.json`, `results/a0_shortcut/metrics.json`, `results/report_rq1/r1_summary.csv`. Hình 4.1 sinh bằng `python -m scripts.report_figures_rq3`, ghi ra `report/figures/04_macro_f1_kich_ban_rq3.png`; kiểm thử `tests/test_report_figures_rq3.py` |
| 4.2 | Tầm quan trọng đặc trưng theo 10 khối (permutation importance) | `results/rq3_permutation_importance.csv`. Ba khối tổng hợp: hist 64, GLCM 60, LBP 28; 5 tiểu khối GLCM 12 chiều; 2 tiểu khối LBP |
| 4.3 | Các giả thuyết chưa kiểm chứng về vùng ngoài mặt nạ phổi | `results/rq3_shortcut_learning_conclusion.md` mục 3.2. Mọi diễn giải phải gắn nhãn giả thuyết |

### Chương 5. Kết quả kiểm tra độc lập và triển khai (8 tiểu mục)

| # | Mục | Nguồn |
| :-: | :--- | :--- |
| 5.1 | Kết quả trên tập test độc lập, mở khóa một lần | `results/final_test/final_test_report.json`, `results/final_test/metrics.json`, `results/final_test/UNLOCK_RECORD.json`. Macro-F1 0,8714, CI [0,8579, 0,8840], Accuracy 86,56% |
| 5.2 | Chênh lệch validation và test | `results/final_test/final_test_report.json` (`test_minus_val` = −0,0310). Không nêu nguyên nhân; cách tính hiệu và ô Bảng 5.3 ghi trong Ghi chú kỹ thuật của chương |
| 5.3 | Phân tích lỗi sai và cặp nhầm lẫn Normal – Lung_Opacity | Ma trận nhầm lẫn trong `results/final_test/metrics.json`: 427 lỗi, trong đó 304 lỗi thuộc cặp Normal ↔ Lung_Opacity (71,19%). Hình 5.1 sinh bằng `python -m scripts.report_figures_final_test`, kiểm thử `tests/test_report_figures_final_test.py` |
| 5.4 | Tính độc lập và khả năng tái lập của thực nghiệm | `notebooks/10_final_test_eval.ipynb`; `results/final_test_protocol_record.md` (D1–D4, G1–G6); `results/final_test/UNLOCK_RECORD.json`. Bộ kiểm thử: 341 phép kiểm thử trong 27 module (đếm tại thời điểm nộp; số liệu chạy xem Ghi chú kỹ thuật của chương) |
| 5.5.1 | Pipeline suy luận từ ảnh xám 299×299 đến xác suất dự đoán | `src/inference_demo.py` (`N_FEATURES`, `IMAGE_SIZE`, các hàm `load_image_grayscale_299`, `extract_152_features`, `fit_or_load_model`, `predict_image`); `src/model_artifact.py` (kho `duc16/cxr-svm-demo`, SHA-256 `3e14bd570c734d9d8f39a2d340b176a40a41c9559cc2da0ef67bbd8e15735058`, 7.842.399 bytes) |
| 5.5.2 | Giao diện Streamlit và các thành phần tương tác | `demo/streamlit_app.py`; `demo/README.md` |
| 5.5.3 | Cảnh báo y khoa tích hợp trong ứng dụng | `demo/streamlit_app.py` dòng 61–63; `demo/README.md` mục giới hạn và an toàn |
| 5.5.4 | Độ trễ suy luận thực tế | `results/demo_latency_interactive/latency.json` (20 ảnh val đầu tiên ngay sau khi máy nghỉ, seed 42, một lượt) và `results/demo_latency_sustained/latency.json` (200 ảnh val, seed 42, 3 lượt; Bảng 5.5 thống kê trên trung vị ba lượt của mỗi ảnh, tức 200 giá trị), sinh bằng `python -m src.inference_latency`; kiểm thử `tests/test_inference_latency.py` |

### Chương 6. Thảo luận, giới hạn và hướng phát triển (5 tiểu mục)

| # | Mục | Nguồn |
| :-: | :--- | :--- |
| 6.1 | Thảo luận kết quả đạt được | Tổng hợp từ `results/report_rq1/r1_summary.csv`, `results/report_rq2/r1_summary.csv`, `results/report_rq3/r1_summary.csv`, `results/final_test/final_test_report.json` |
| 6.2 | Giới hạn nghiên cứu | `results/report_rq3/r5_gioi_han.md`; `results/threshold_v3.md` Mục 6 (R5). Gồm 11 hạng mục (xem chương 6): 735 cặp gần trùng mà bước chia nhóm pHash không chặn (chỉ chặn trùng tuyệt đối; phép đo trên 273 ảnh validation có ảnh gần trùng cho 0,9068 so với 0,9024 toàn tập, xem `results/val_near_duplicate_subset/`), thiếu mã bệnh nhân, nguồn và tuổi chưa xác minh, đánh giá trên validation nên số có xu hướng cao hơn, phạm vi ngoại suy |
| 6.3 | Cảnh báo y khoa và đạo đức nghiên cứu | `demo/streamlit_app.py` dòng 61–63. Không quy cho WHO/ACR hay bất kỳ khuyến cáo nào không có trong repo |
| 6.4 | Hướng phát triển | Viết mới, dựa trên giới hạn ở 6.2 |
| 6.5 | Kết luận | Viết mới, không thêm số liệu mới |

### Phần cuối (4 mục)

| # | Mục | Nguồn |
| :-: | :--- | :--- |
| 1 | Tài liệu tham khảo (IEEE `[1]`–`[8]`) | [`07_tai_lieu_tham_khao.md`](07_tai_lieu_tham_khao.md); gộp từ danh mục cuối Chương 1 (`[1]`–`[6]`) và Chương 5 (`[7]`, `[8]`) |
| 2 | Phụ lục A: cài đặt, tải mô hình từ Hugging Face và vận hành demo | [`08_phu_luc_a_c.md`](08_phu_luc_a_c.md) mục A; `demo/README.md`; `src/model_artifact.py` |
| 3 | Phụ lục B: cấu trúc kho mã nguồn và danh sách bài kiểm thử | [`08_phu_luc_a_c.md`](08_phu_luc_a_c.md) mục B; `tests/`; 341 phép kiểm thử trong 27 module (đếm tại thời điểm nộp), sinh bởi `scripts/report_appendix_b.py` |
| 4 | Phụ lục C: lưới siêu tham số và tham số chọn của sáu bộ phân loại | [`08_phu_luc_a_c.md`](08_phu_luc_a_c.md) mục C; `src/rq2_runner.py` (`PARAM_GRIDS`); `results/rq2_classifier_selection_record.md`; `results/rq2_cost_rank_record.md` |

---

## 4. Quy ước trích số liệu

| Muốn trích | Lấy từ |
| :--- | :--- |
| Macro-F1, CI, precision/recall/F1 từng lớp của RQ1 | `results/report_rq1/r1_summary.csv` |
| Kết quả kiểm định RQ1 | `results/report_rq1/r1_bootstrap_vs_reference.csv` |
| Thời gian trích đặc trưng mỗi ảnh | `results/rq1_cost_rank_record.md` |
| Macro-F1, CI, recall từng lớp của RQ2 | `results/report_rq2/r1_summary.csv` |
| Kết quả kiểm định RQ2 | `results/report_rq2/r1_bootstrap_vs_reference.csv` |
| Siêu tham số đã chọn của 6 bộ phân loại | `results/rq2_classifier_selection_record.md` |
| Macro-F1, CI, recall của 5 kịch bản RQ3 | `results/report_rq3/r1_summary.csv` |
| Accuracy của 5 kịch bản RQ3 | `results/report_rq3/r4_sampling_error.csv` |
| So sánh cặp giữa các kịch bản RQ3 | `results/report_rq3/r3_shortcut_bootstrap.csv` |
| Ma trận nhầm lẫn RQ3 | `results/report_rq3/r1_confusion_matrices.json` |
| Permutation importance 10 khối | `results/rq3_permutation_importance.csv` |
| Toàn bộ số liệu test | `results/final_test/final_test_report.json` và `results/final_test/metrics.json` |
| Mốc thời gian và commit mở khóa test | `results/final_test/UNLOCK_RECORD.json` |

Không dùng: `results/rq3_shortcut_learning_conclusion.md` như nguồn số liệu gốc (chỉ dùng cho diễn giải), các tệp trong `results/rq2_ghep_*/` và `results/rq3_ghep_svm_*/` như nguồn chính (chỉ dùng khi cần kiểm tra chéo), bất kỳ ảnh nào của split `test`.

---

## 5. Trạng thái hiện tại

- Đủ 6 chương đã merge vào `main`: Chương 1 tại [`01_gioi_thieu.md`](01_gioi_thieu.md), Chương 2 tại [`02_du_lieu_va_phuong_phap.md`](02_du_lieu_va_phuong_phap.md), Chương 3 tại [`03_ket_qua_rq1_rq2.md`](03_ket_qua_rq1_rq2.md), Chương 4 tại [`04_hoc_loi_tat_rq3.md`](04_hoc_loi_tat_rq3.md), Chương 5 tại [`05_ket_qua_test_va_trien_khai.md`](05_ket_qua_test_va_trien_khai.md), Chương 6 tại [`06_thao_luan_gioi_han_huong_phat_trien.md`](06_thao_luan_gioi_han_huong_phat_trien.md).
- Chương 2 đủ 12 tiểu mục; Chương 3 đủ 4 tiểu mục; Chương 4 đủ 3 tiểu mục; Chương 5 đủ 8 tiểu mục kèm Hình 5.1; Chương 6 đủ 5 tiểu mục kèm Bảng 6.1.
- Hai đợt rà soát đã xong và đã sửa: rà số liệu toàn bộ 6 chương (PR #59) và rà theo review senior của Chương 5–6 (PR #58, #59). Số liệu kiểm thử trong Chương 5 đo lại: 341 phép kiểm thử trong 27 module, 340 pass và 1 bỏ qua.
- Còn thiếu: tóm tắt tiếng Việt và Abstract (viết sau cùng, khi mọi chương và phụ lục đóng băng); MSSV đã có đủ và đã ghi trên bìa. Chương 3 chưa đưa vào: thời gian huấn luyện của từng bộ phân loại, chỉ số theo từng seed riêng lẻ, phân tích lỗi theo mức độ tin cậy chi tiết hơn.
- Mở đầu quyển đã viết: [`00a_trang_bia_va_loi.md`](00a_trang_bia_va_loi.md) (bìa chính, bìa phụ, lời cảm ơn, lời cam đoan), [`00b_danh_muc_ky_hieu.md`](00b_danh_muc_ky_hieu.md), [`00c_muc_luc_va_danh_muc.md`](00c_muc_luc_va_danh_muc.md) (mục lục, 32 bảng, 4 hình — sinh bởi `scripts/report_frontmatter.py`). Phần cuối quyển đã viết: tài liệu tham khảo gộp `[1]`–`[8]` tại [`07_tai_lieu_tham_khao.md`](07_tai_lieu_tham_khao.md) và Phụ lục A–C tại [`08_phu_luc_a_c.md`](08_phu_luc_a_c.md).
- Khung viền bìa: `report/figures/khung_trang_bia.png` (A4, 300 DPI) sinh bởi `python scripts/make_cover_border.py`.
