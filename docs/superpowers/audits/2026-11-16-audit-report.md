# Báo cáo rà soát toàn bộ hồ sơ báo cáo (Giai đoạn A)

- **Ngày rà soát:** 16/11/2026
- **Nền tảng kiểm tra:** nhánh `report/sua-review-vong-cuoi` (`11d7bf6`, sau PR #68) trên worktree `check_and_convert_reports`.
- **Tổng hợp phát hiện trước sửa:** **0 critical / 4 major / 6 minor** (đã rà lại sau khi sửa: **0 critical / 0 major / 0 minor mở**).
- **Trạng thái cổng:** **Cổng A: ĐẠT** (toàn bộ phát hiện đều là lỗi cơ học có nguồn rõ từ CSV/JSON/spec, đã sửa và kiểm tra lại; không có vấn đề cần quyết định lại lập luận từ tác giả).

## Bảng phát hiện hợp nhất (A1–A3)

| ID | Mức | Tệp:dòng | Loại | Vấn đề | Bằng chứng (nguồn + giá trị) | Cách sửa & trạng thái |
| :-: | :---: | :--- | :--- | :--- | :--- | :--- |
| F01 | Major | `report/05_ket_qua_test_va_trien_khai.md:18,126` | Số liệu | Viết tỷ lệ ảnh đoán sai trên test là `13,45%` (`86,56% + 13,45% = 100,01%`) | `427 / 3.176 = 0,1344458...` → `13,44%` (`results/final_test/final_test_report.json`, `metrics.json`: accuracy `86,56%`) | Đã sửa thành `13,44%` ở cả dòng 18 và dòng 126 |
| F02 | Major | `report/08_phu_luc_a_c.md:39,164,181,196` | Định dạng | Bảng A.2, Bảng C.1, Bảng C.2, Bảng C.3 chưa được dẫn chiếu trực tiếp trong văn bản của phụ lục | `docs/report_standards.md` mục 4.1 yêu cầu mọi bảng biểu phải được dẫn chiếu trong văn bản (`audit_report.py`) | Đã bổ sung câu dẫn chiếu trực tiếp cho cả 4 bảng tại A.3, C.1, C.2, C.3 |
| F03 | Major | `report/00c_muc_luc_va_danh_muc.md:13-21`, `scripts/report_frontmatter.py:17-27`, `report/00a_trang_bia_va_loi.md:3-4,54` | Quy chuẩn | Thứ tự Mục lục / Danh mục ký hiệu bị đảo ngược so với quy chuẩn (`vi. Danh mục ký hiệu` trước `vii. Mục lục`); hai trang bìa bị đánh số La Mã `i–ii` | `docs/report_standards.md` mục 2.4 (hai trang bìa không đánh số trang), mục 3.1 và `report/README.md` mục 3 (`#6 Mục lục`, `#7 Danh mục ký hiệu`) | Đã sửa `FRONT` trong `scripts/report_frontmatter.py`, chỉnh `00a` và sinh lại `00c` |
| F04 | Major | `report/00b_danh_muc_ky_hieu.md:11-45` | Quy chuẩn | Thiếu `RGB`, `RQ`; sai thứ tự chữ cái (`CXR` trước `COVID`, `SVM` trước `SVC`); `CV`, `DT`, `GB`, `LR`, `RF` ghi xuất hiện ở Mục 2.8 nhưng thân bài không viết tắt; `IEEE` xuất hiện từ Chương 1 | Kiểm tra toàn văn `01`–`08`: `CV`/`dt`/`gb`/`lr`/`rf` chỉ xuất hiện ở Phụ lục C; `RGB` ở 2.1/2.2; `RQ` ở 1.2; `IEEE` ở Chương 1 | Đã sắp lại thứ tự A–Z, bổ sung `RGB`/`RQ`, sửa vị trí xuất hiện đầu cho chuẩn thực tế |
| F05 | Minor | `report/00c_muc_luc_va_danh_muc.md:3`, `scripts/report_frontmatter.py:71` | Chính tả | Gõ nhầm `"Tệp này gộm ba mục"` | `scripts/report_frontmatter.py:71` | Đã sửa thành `"gồm"` và sinh lại `00c` |
| F06 | Minor | `report/06_thao_luan_gioi_han_huong_phat_trien.md:84` | Chính tả | Gõ nhầm `"cánh báo"` trong Ghi chú kỹ thuật | `demo/streamlit_app.py` / ngữ cảnh cảnh báo y khoa | Đã sửa thành `"cảnh báo"` |
| F07 | Minor | `report/01_gioi_thieu.md:78`, `report/07_tai_lieu_tham_khao.md:3,38` | Trích dẫn | Ghi `[10]` xuất hiện ở mục `1.3`, nhưng thực tế `[10]` nằm ở dòng 37 thuộc mục `1.2` (mục `1.3` bắt đầu ở dòng 41) | `report/01_gioi_thieu.md:37,41` | Đã chỉnh mô tả vị trí `[10]` về mục `1.2` ở `01` và `07` |
| F08 | Minor | `report/04_hoc_loi_tat_rq3.md:13-19` | Định dạng | Bảng ánh xạ tên 5 kịch bản đặt trước Bảng 4.1 không đánh số `Bảng X.Y` | `docs/report_standards.md` mục 4.1; giữ đúng 32 bảng đánh số khóa bởi `tests/test_report_tables_match_sources.py:209` | Đã chuyển thành danh sách gạch đầu dòng (16/11/2026) |
| F09 | Minor | `report/README.md:81,165`, `docs/report_standards.md:142` | Tài liệu phụ trợ | (1) Dòng 81 dính hai hàng `2.6.3` và `2.6.4` (`\|\|`); (2) mục 5 còn ghi thiếu tóm tắt dù `09` đã có; (3) `report_standards.md` mô tả Phụ lục C lệch tên thực tế | `report/README.md`, `report/09_tom_tat_abstract.md`, `report/08_phu_luc_a_c.md` | Đã tách dòng 81, cập nhật mục 5 README và đồng bộ mô tả Phụ lục C ở `report_standards.md` |
| F10 | Minor | `report/01_gioi_thieu.md`, `02`, `06`, `08_phu_luc_a_c.md:181` | Văn phong / chi tiết | Lẫn `tỉ lệ` (2 chỗ) với `tỷ lệ` (13 chỗ), thanh điệu cũ `hoá`/`hoạ` (6 chỗ) với `hóa`/`họa` (32 chỗ); mục `C.1` mới nêu 1 tham số biên của `dt` | Kiểm tra tần suất trên `01`–`06` và `PARAM_GRIDS` trong `src/rq2_runner.py` (`dt` có cả `max_depth=10` và `min_samples_leaf=1` ở biên dưới) | Đã thống nhất `tỷ lệ`, `hóa`/`họa` và bổ sung `min_samples_leaf=1` tại `08:181` |

## Xác minh văn phong, logic, số liệu và cổng kiểm soát (toàn quyển)

- **Văn phong (`docs/academic_writing_guide.md`):** không phát hiện AI slop, không nhồi nhét liên từ nối, câu ngắn–dài đan xen tự nhiên, số liệu làm chủ ngữ. Hai bản tóm tắt trong `09_tom_tat_abstract.md` dài 393 từ (tiếng Việt) và 337 từ (tiếng Anh), mỗi bản vừa một trang A4.
- **Quy tắc D4 & cổng H2/H7:** 0 vi phạm D4 (không nêu nguyên nhân chênh lệch val–test); 0 rò rỉ số liệu đánh giá tập test sang Chương 1–4; 0 vi phạm H7.
- **Đối chiếu nguồn gốc (`results/`, `splits/`, `src/`):**
  - Toàn bộ số liệu Chương 2 khớp `splits/split_v1.csv` (21.165 ảnh; 14.815/3.174/3.176; SHA-256 `f99e03d3...`), `results/eda/brightness_by_class.csv`, `brightness_channels.json`, `outputs/split_check/*.json`, `results/val_near_duplicate_subset/val_near_duplicate_subset.json` và công thức (2.1).
  - Toàn bộ 6 bảng Chương 3 khớp `results/report_rq1/*.csv`, `results/report_rq2/*.csv`, `results/rq2_ghep_svm_s42/metrics.json` và `results/error_analysis/error_analysis_summary.md` (349 lỗi val).
  - Toàn bộ 5 kịch bản, 5 bảng và 10 khối hoán vị Chương 4 khớp `results/report_rq3/*.csv`, `r1_confusion_matrices.json`, `preds_val.csv`, `results/rq3_permutation_importance.csv`; các diễn giải mục 4.3 đều gắn nhãn giả thuyết.
  - Toàn bộ 5 bảng Chương 5 (trừ `13,45%` đã sửa thành `13,44%`) và mục độ trễ 5.5.4 khớp `results/final_test/*.json`, `UNLOCK_RECORD.json`, `results/demo_latency_sustained/latency.json`, `results/demo_latency_interactive/latency.json` và `per_image.csv`.
  - Chương 6 đủ 12 giới hạn, không thêm số mới ở Kết luận 6.5, cảnh báo y khoa khớp `demo/streamlit_app.py`.
  - Tài liệu tham khảo `[1]`–`[13]` xuất hiện đúng thứ tự tăng dần; Phụ lục A–C khớp `src/rq2_runner.py`, `src/model_artifact.py`, `results/rq2_cost_rank_record.md`.
- **Kiểm tra lại sau khi sửa:** `python -m scripts.audit_report` trả về `critical=0, major=0, minor=0`; `test_report_consistency.py`, `test_val_near_duplicate_subset.py`, `test_audit_report.py` (21 passed) và các phép đối chiếu bảng–nguồn + mục lục của `test_report_tables_match_sources.py` (5 passed) đều xanh. Ghi chú: ba phép đếm tệp/module trong `test_report_tables_match_sources.py` (`B.1`, `B.2`, `A.1`) sẽ được đồng bộ ở Giai đoạn B sau khi thêm xong `scripts/build_report_docx.py` và `tests/test_build_report_docx.py`.

## Kiểm tra độc lập tệp `.docx` sau khi dựng (Giai đoạn B)

Kiểm tra trực tiếp bằng `python-docx` (độc lập với `scripts/build_report_docx.py`) đối chiếu với số đếm từ `report/*.md` (trừ `README.md`, `00c` và phần `Ghi chú kỹ thuật`):

- **Tệp đầu ra:** `report/dist/BaoCao_BTL_HocMay_Nhom10.docx` (`537.174` bytes).
- **Số đoạn (`paragraphs`):** `400` đoạn (sau khi chuyển `2 × 6` dòng `SV Thực hiện:` ở bìa chính và bìa phụ vào 2 bảng không viền).
- **Số bảng (`tables`):** `36` bảng trong `.docx` = `34` bảng pipe trong các tệp `.md` (`32` bảng có chú thích `Bảng X.Y`, `2` bảng ký hiệu trong `00b`) + `2` bảng không viền `6 hàng × 2 cột` cho danh sách `SV Thực hiện:` ở hai trang bìa.
- **Số hình (`inline_shapes`):** `5` hình trong `.docx` — gồm `4` hình nội dung (`Hình 2.1`, `3.1`, `4.1`, `5.1`) và `1` logo CTUT trên bìa chính (`slides/assets/logo_ctut.png`, rộng `3,0 cm`), kèm `1` ảnh khung viền trang bìa `wp:anchor` đặt lớp *Behind Text* trong header section 0.
- **Số section (`sections`):** `3` section — section 0 (bìa chính & bìa phụ): không đánh số; section 1 (mở đầu quyển): `lowerRoman`, `start="1"`; section 2 (Chương 1–6, Tài liệu tham khảo, Phụ lục): `decimal`, `start="1"`.

