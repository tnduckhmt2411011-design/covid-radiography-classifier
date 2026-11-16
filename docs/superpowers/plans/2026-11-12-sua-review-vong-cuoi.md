# Kế hoạch thi công: Sửa review senior vòng cuối

REQUIRED SUB-SKILL: Dùng superpowers:executing-plans để thi công trực tiếp trong phiên này (implementer = chính tôi).

## Goal
Sửa toàn bộ điểm review senior vòng cuối (N1–N7, chênh số liệu, mục nhỏ) trên sáu chương, tài liệu tham khảo, ba phụ lục và tóm tắt của báo cáo tiếng Việt, trên nhánh riêng trong worktree, kèm hàng rào kiểm thử và một phép đo mới (bootstrap CI cho phép đo gần trùng), rồi mở PR để người dùng tự merge.

## Architecture
- Thay đổi văn bản nằm trong `report/` (7 tệp chương) cộng `report/README.md`.
- Hai nguồn sinh tự động: `scripts/report_appendix_b.py` (Phụ lục B) và `scripts/report_frontmatter.py` (mục lục); số bộ kiểm thử đồng bộ tay sau khi thêm hàng rào.
- Phép đo mới duy nhất: mở rộng `scripts/val_near_duplicate_subset.py` (khoảng tin cậy bootstrap cho hiệu 0,0051 + recall từng lớp), ghi kết quả vào `results/val_near_duplicate_subset/`.
- Hàng rào: +5 phép kiểm thử (4 ở `tests/test_report_consistency.py`, 1 ở `tests/test_val_near_duplicate_subset.py`); mở rộng hàng rào Bảng B.1 ở `tests/test_report_tables_match_sources.py`.

## Tech Stack
- Python 3.12 môi trường demo, chạy bằng đường dẫn tuyệt đối tới python của cây chính; pytest, pandas, numpy.
- Git: worktree riêng `C:\Users\LENOVO\AppData\Local\Temp\opencode\wt-review-cuoi`, nhánh `report/sua-review-vong-cuoi`, gốc `cec8a8a`.

## Spec
`docs/superpowers/specs/2026-11-12-sua-review-vong-cuoi-design.md` (commit `4dcd1fd`)

## Ràng buộc toàn cục
- Làm việc trong worktree; không đổi nhánh ở cây làm việc chính (đang ở nhánh slides của người dùng).
- Mọi số liệu mới phải do chạy script sinh ra rồi mới ghi vào báo cáo; không gõ số bằng tay.
- Không stage `results/report_rq*/bootstrap_config.json`; không sửa `demo/requirements.txt`; không đụng `slides/`.
- Người dùng tự merge PR: không chạy `gh pr merge`.
- Quy ước văn bản: dấu phẩy thập phân, chấm phân cách hàng nghìn, không dùng dấu gạch dài trong câu mới, không cụm AI slop, không nêu nguyên nhân cho chênh validation–test (quy tắc D4).
- PowerShell 5.1 lỗi encoding với tiếng Việt inline: ghi script phụ ra tệp UTF-8 rồi chạy; commit message qua `git commit -F <tệp>`; không dùng backtick trong lệnh shell.
- Python cho pytest/script: `D:\Use Antigravity\Medical Vision\.venv-demo\Scripts\python.exe`, luôn kèm `$env:PYTHONUTF8 = '1'`.

## Trọng tâm rà soát
1. **Số bộ kiểm thử lệch chỗ**: thêm 5 phép làm đổi 344/28/343 thành 349/28/348 ở ~10 vị trí; bỏ sót một chỗ là hỏng hàng rào số.
2. **Trích dẫn lệch số**: đổi `[7]`/`[8]` cũ của Chương 5 thành `[12]`/`[13]`; trích dẫn cũ tại vị trí cũ không được còn sót.
3. **Ký tự thừa trong văn bản mới**: dấu gạch dài, ngoặc kép lệch chuẩn, cụm AI slop lọt vào câu mới.
4. **Số đo mới không khớp nguồn**: khoảng tin cậy bootstrap trong Ch2/Ch6 phải trùng giá trị trong JSON do script sinh.
5. **Hàng rào mới yếu**: phép kiểm chỉ đúng trên nội dung hiện tại, không bắt được lỗi tương tự của vòng sau.

## Nhiệm vụ

### Nhiệm vụ 1: Phụ lục A (N3 + kernel v3 + HTTP 200 + D4)

**Files:**
- Modify: `report/08_phu_luc_a_c.md`
- Test: `tests/test_report_consistency.py` (thêm phép 1 trong 4 phép mới)

**Interfaces:**
- Consumes: nội dung hiện có của Phụ lục A, `kaggle/inference_demo/kernel-metadata.json` (chứng cứ "kernel huấn luyện phiên bản 3").
- Produces: Phụ lục A đúng logic, bảng đánh số A.1 trước A.2; phép hàng rào `test_appendix_a_table_captions_in_order`.

**Steps:**
- [ ] Ghi phép kiểm mới vào `tests/test_report_consistency.py`: `test_appendix_a_table_captions_in_order` — yêu cầu chỉ số của dòng `**Bảng A.1: Thông số mô hình đóng băng**` nhỏ hơn chỉ số của `**Bảng A.2: Biến môi trường của ứng dụng demo**`; dòng `CXR_MODEL_SHA256` chứa "Bảng A.1"; chạy RED.
- [ ] Sửa `08` dòng 9: bỏ cụm "mặc định của Streamlit Community Cloud" (giữ "chạy trên Python 3.12, cùng phiên bản của môi trường đã chạy toàn bộ kiểm thử của đề tài").
- [ ] Sửa `08` dòng 21: tách câu artifact thành 3 câu: artifact không nằm trong git; artifact sinh ở bước S5-06 bởi kernel huấn luyện `ductrannguyen/cxr-inference-demo` phiên bản 3; kho được kiểm tra tải ẩn danh "tại thời điểm nộp".
- [ ] Sửa `08` dòng 35: đảo logic "khớp một điều kiện thì ứng dụng dừng" thành "một điều kiện không khớp thì ứng dụng dừng".
- [ ] Đổi tiêu đề `**Bảng A.2: Thông số mô hình đóng băng**` thành `**Bảng A.1: ...**` và `**Bảng A.1: Biến môi trường của ứng dụng demo**` thành `**Bảng A.2: ...**`; sửa nhắc lại "mặc định băm ở Bảng A.2" thành "Bảng A.1".
- [ ] Sửa `08` dòng 78 (A.6): bỏ "(quy ước D4)".
- [ ] Chạy phép kiểm mới: GREEN.

### Nhiệm vụ 2: .gitignore track 2 tệp JSON của outputs/split_check + dọn ghi chú Ch2

**Files:**
- Modify: `.gitignore`, `report/02_du_lieu_va_phuong_phap.md`
- Create (tracked): `outputs/split_check/duplicates_summary.json`, `outputs/split_check/cross_split_hamming_report.json`

**Interfaces:**
- Consumes: 2 tệp JSON đang có sẵn trên đĩa (đã bỏ qua bởi `outputs/`).
- Produces: 2 tệp được track làm nguồn cho ghi chú Chương 2; ghi chú Ch2 không còn tham chiếu "cell N".

**Steps:**
- [ ] Thêm vào `.gitignore` ngay sau dòng `outputs/`: `!outputs/split_check/`, rồi `outputs/split_check/*`, rồi `!outputs/split_check/duplicates_summary.json`, `!outputs/split_check/cross_split_hamming_report.json`.
- [ ] `git add` đúng 2 tệp JSON đó (không đụng tệp khác trong outputs).
- [ ] Trong `02`, dọn ghi chú kỹ thuật: bỏ tên "cell" (cell 5, cell 6, cell 3) ở các dòng 203, 204, 218, 221, 223, thay bằng tên notebook và phần (ví dụ "notebook 02, phần tạo split").
- [ ] `git ls-files outputs` cho đúng 2 tệp.

### Nhiệm vụ 3: Phụ lục B (dòng slides, hàng tổng) + mở rộng hàng rào B.1

**Files:**
- Modify: `report/08_phu_luc_a_c.md` (Bảng B.1), `scripts/report_appendix_b.py`, `tests/test_report_tables_match_sources.py`

**Interfaces:**
- Consumes: `git ls-files` trong worktree (số tệp thực tế sau Nhiệm vụ 2 và sau khi commit spec + kế hoạch).
- Produces: Bảng B.1 có hàng **Tổng cộng** khớp số tệp; mô tả `slides/` đúng thực tế; hàng rào B.1 kiểm cả hàng tổng lẫn tính đầy đủ.

**Steps:**
- [ ] Sửa `scripts/report_appendix_b.py`: thêm hàng `outputs/` (2 tệp, mô tả "Tệp kiểm tra trùng và gần trùng của notebook 02, được track làm nguồn cho ghi chú Chương 2") và hàng tổng cuối bảng; đổi chuỗi tổng ASCII "Tong cong" thành "Tổng cộng" (giữ dấu, khớp quy ước báo cáo).
- [ ] Chạy script trên .venv-demo trong worktree, lấy bảng B.1 mới dán vào `08`.
- [ ] Sửa dòng `slides/` trong B.1: mô tả thành "Chỗ để slide thuyết trình, mới có `.gitkeep` giữ chỗ".
- [ ] Mở rộng phép `test_appendix_b1_counts_match_git_ls_files`: kiểm hàng tổng bằng tổng các hàng và bằng số tệp `git ls-files`; kiểm mọi thư mục cấp một trong ls-files đều xuất hiện trong bảng.
- [ ] Chạy phép kiểm: GREEN. Commit cụm này.

### Nhiệm vụ 4: Phụ lục C (N1, N2, N7, chênh số liệu)

**Files:**
- Modify: `report/08_phu_luc_a_c.md` (C.1, C.2, C.3)
- Test: `tests/test_report_consistency.py` (phép thứ 2)

**Interfaces:**
- Consumes: `src/rq2_runner.py` (PARAM_GRIDS, CLASSIFIER_SPECS), `results/rq1_cost_rank_record.md`, `results/rq2_cost_rank_record.md`.
- Produces: C.1 đúng cơ chế trọng số + câu biên lưới; C.2 bỏ "cổng H3", đúng cấu hình rf; C.3 có câu môi trường hai lần đo.

**Steps:**
- [ ] Ghi phép kiểm `test_appendix_c1_class_weight_sentence`: `08` chứa "balanced_subsample" và "trọng số mẫu"; KHÔNG chứa "cân bằng bằng `weights='distance'`"; KHÔNG chứa "cổng H3". Chạy RED.
- [ ] Thay câu trọng số lớp ở C.1 bằng bản đúng (LR/DT/SVM dùng `class_weight='balanced'`; RF dùng `balanced_subsample`; GB dùng trọng số mẫu cân bằng truyền vào fit; knn không có cơ chế cân bằng lớp, `weights='distance'` là trọng số theo khoảng cách láng giềng).
- [ ] Thêm câu biên lưới sau đoạn C.1: "Năm trong sáu bộ phân loại có ít nhất một siêu tham số chọn nằm ở biên lưới: `lr` chọn `C=10,0` (lớn nhất trong lưới), `svm` chọn `C=10,0` (lớn nhất), `gb` chọn 200 cây và độ sâu 5 (đều lớn nhất), `dt` chọn độ sâu 10 (nhỏ nhất), `rf` chọn 300 cây (nhỏ nhất). Lưới vì vậy có thể chưa bao hết vùng tối ưu, thứ hạng giữa các bộ có thể thay đổi nếu mở rộng lưới; hệ quả với kết luận về bộ phân loại đứng đầu được ghi ở mục 6.2 của Chương 6."
- [ ] Thay câu mở C.2: bỏ "(cổng H3 của đề tài)", viết "Ba bộ tất định về nhãn dự đoán chạy mỗi bộ một lần nên không có độ lệch chuẩn."; sửa mô tả rf: "cấu hình chọn bằng kiểm định chéo (300 cây, độ sâu không giới hạn), khác cấu hình 500 cây cố định dùng ở RQ1".
- [ ] Thêm vào C.3 sau "...tức 0,077985 giây CPU một ảnh).": câu phân biệt hai lần đo (RQ2 kernel `cxr-rq2-classifiers` phiên bản 3 so với RQ1 kernel `cxr-rq1-rf` phiên bản 5; cùng môi trường Kaggle CPU nhưng khác phiên chạy nên không so trực tiếp).
- [ ] Chạy phép kiểm: GREEN.

### Nhiệm vụ 5: N6 đo bootstrap CI cho hiệu 0,0051 + recall từng lớp

**Files:**
- Modify: `scripts/val_near_duplicate_subset.py`, `tests/test_val_near_duplicate_subset.py`, `report/02_du_lieu_va_phuong_phap.md` (2.5), `report/06_thao_luan_gioi_han_huong_phat_trien.md` (giới hạn 1 + ghi chú)
- Create (tracked): `results/val_near_duplicate_subset/val_near_duplicate_subset.json` (ghi thêm khóa mới)

**Interfaces:**
- Consumes: dự đoán có sẵn `results/rq2_ghep_svm_s42/preds_val.csv`, `splits/split_v1.csv`.
- Produces: JSON ghi thêm khóa `bootstrap_ci` (n=2000, seed 42, lo/hi, chứa 0 hay không) và recall từng lớp của hai tập con; văn bản 2.5 và giới hạn 1 có số đo mới.

**Steps:**
- [ ] Ghi phép kiểm `test_bootstrap_ci_reproducible` vào `tests/test_val_near_duplicate_subset.py`: đọc JSON, gọi hàm bootstrap từ script, khớp giá trị lo/hi làm tròn 4 chữ số. Chạy RED (khóa chưa có).
- [ ] Mở rộng `scripts/val_near_duplicate_subset.py`: hàm bootstrap lấy mẫu lại độc lập trong từng tập con (2000 lần, seed 42) cho hiệu macro-F1 (tập con trừ phần còn lại); ghi thêm khóa JSON (không đổi khóa cũ); in thêm recall từng lớp hai tập con vào md.
- [ ] Chạy script, đọc JSON lấy lo/hi và cờ chứa 0.
- [ ] Viết lại câu 2.5 và giới hạn 1 theo nhánh đúng: nếu khoảng tin cậy chứa 0 thì giữ kết luận "chưa kết luận được" kèm số; nếu không chứa 0 thì nêu hướng chênh. Cả hai chỗ đều ghi rõ: lớp Viral Pneumonia trong tập con chỉ có 4 ảnh nên khoảng tin cậy mang tính xấp xỉ, và phép so recall từng lớp công bằng hơn vì macro-F1 phụ thuộc cơ cấu lớp.
- [ ] Ghi chú 2.5 và ghi chú Ch6 bổ sung nguồn số (bootstrap 2000 lần, seed 42, trong cùng tệp JSON).
- [ ] Chạy phép kiểm: GREEN. Commit cụm này (JSON + md + script + test + 2 tệp chương).

### Nhiệm vụ 6: Ch6 thêm hạng mục 12 (biên lưới)

**Files:**
- Modify: `report/06_thao_luan_gioi_han_huong_phat_trien.md`

**Interfaces:**
- Consumes: câu biên lưới đã viết ở Phụ lục C (Nhiệm vụ 4).
- Produces: giới hạn 12 sau giới hạn 11.

**Steps:**
- [ ] Thêm hạng mục 12 sau dòng 48: "12. **Siêu tham số chọn nằm ở biên lưới.** Năm trong sáu bộ phân loại có ít nhất một siêu tham số chọn ở biên lưới (`lr` và `svm` ở `C=10,0`; `gb` ở 200 cây và độ sâu 5; `dt` ở độ sâu 10; `rf` ở 300 cây). Lưới vì vậy có thể chưa bao hết vùng tối ưu, và thứ hạng giữa các bộ có thể thay đổi nếu mở rộng lưới. Hạng mục này suy ra từ Bảng C.1 và C.2 của Phụ lục C, không phải từ phép đo mới."
- [ ] Ghi chú cuối chương: thêm "hạng 12 không thuộc biên bản đã đăng ký, suy ra từ Bảng C.1 và C.2 của Phụ lục C trong đợt rà cuối;".

### Nhiệm vụ 7: Ch5 sửa 3 ghi chú

**Files:**
- Modify: `report/05_ket_qa_test_va_trien_khai.md`

**Interfaces:**
- Consumes: `src/inference_demo.py` (đường dẫn `load_benchmark_metrics` thật).
- Produces: ghi chú 5.4, 5.5, 5.5.4 đúng thực tế.

**Steps:**
- [ ] Ghi chú 5.4: bỏ cụm ", chặn trường hợp chép lệch ô như từng xảy ra với bảng RQ3".
- [ ] Ghi chú 5.5: đổi đường dẫn `results/rq2_ghep_svm_orig_to_orig_s42/metrics.json` thành `results/rq3_ghep_svm_orig_to_orig_s42/metrics.json`, kèm "nếu không có thì dùng bản sao trong thư mục `reference/` của gói mã nguồn, cùng `results/final_test/metrics.json`".
- [ ] Ghi chú 5.5.4: đổi "khác đồng hồ và khác máy nên chỉ dùng làm mốc tham khảo." thành "đo ở phiên kernel khác nên chỉ dùng làm mốc tham khảo.".

### Nhiệm vụ 8: Trích dẫn [7]–[13] và viết lại tài liệu tham khảo

**Files:**
- Modify: `report/01_gioi_thieu.md`, `report/02_du_lieu_va_phuong_phap.md`, `report/05_ket_qa_test_va_trien_khai.md`, `report/07_tai_lieu_tham_khao.md`, `report/README.md`
- Test: `tests/test_report_consistency.py` (phép thứ 3)

**Interfaces:**
- Consumes: danh sách 8 tài liệu hiện có; các điểm nhắc phương pháp ở 1.2, 1.3, 2.7, 5.5.1, 5.5.2.
- Produces: danh mục 13 tài liệu đánh số theo thứ tự xuất hiện; phép hàng rào `test_reference_list_contiguous_and_matches_ch5`.

**Steps:**
- [ ] Ghi phép kiểm: `07` có các mục `[1]` đến `[13]` liên tục; hai mục cuối khớp nguyên văn danh mục cuối Chương 5. Chạy RED.
- [ ] `01` mục 1.2: thêm `[7]` sau tên đầy đủ GLCM, `[8]` sau LBP, `[9]` sau HOG; mục 1.3: thêm `[10]` sau "bootstrap ghép cặp".
- [ ] `01` ghi chú cuối chương: đổi câu đánh số thành "tài liệu xuất hiện sau Chương 1 đánh số tiếp nối (mục 1.2 và 1.3 của chương này, mục 2.7 của Chương 2, mục 5.5.1 và 5.5.2 của Chương 5)."; thêm `[7]`–`[10]` vào danh mục cuối chương.
- [ ] `02` mục 2.7: thêm `[11]` sau "nội suy Platt"; thêm mục "Tài liệu tham khảo phát sinh trong chương" chứa `[11]` trước phần ghi chú.
- [ ] `05` thân bài và danh mục cuối chương: đổi `[7]` thành `[12]` (artifact), `[8]` thành `[13]` (Streamlit).
- [ ] Viết lại `07`: câu mở đầu đếm đúng 13 mục theo chương phát sinh; bullet nguồn thành ba danh mục (Ch1 `[1]`–`[10]`, Ch2 `[11]`, Ch5 `[12]`, `[13]`); bullet thứ tự liệt kê vị trí từng số; thêm bullet pHash (không có bài gốc duy nhất, tính bằng `imagehash`, không vào danh mục); thêm 5 mục mới `[7]`–`[11]` và 2 mục đổi số `[12]`, `[13]` theo chuẩn IEEE đã chốt trong spec.
- [ ] `README`: đổi hai chỗ `[1]`–`[8]` thành `[1]`–`[13]`; mô tả cách gộp danh mục thành "Chương 1 (`[1]`–`[10]`), Chương 2 (`[11]`) và Chương 5 (`[12]`, `[13]`)".
- [ ] Chạy phép kiểm: GREEN. Grep không còn `[7]`/`[8]` ở vị trí cũ.

### Nhiệm vụ 9: Tóm tắt (N4, N5, độ trễ, "trả lời")

**Files:**
- Modify: `report/09_tom_tat_abstract.md`
- Test: `tests/test_report_consistency.py` (phép thứ 4)

**Interfaces:**
- Consumes: Bảng 4.1 (`report/04_ket_qua_thuc_nghiem.md`) cho hai số 0,0723 và 0,2084.
- Produces: tóm tắt hai ngôn ngữ đầy đủ 5 kịch bản RQ3; phép hàng rào `test_abstract_mentions_inference_masking`.

**Steps:**
- [ ] Ghi phép kiểm: `09` chứa "0,0723" và "0,2084"; Bảng 4.1 chứa hai số đó ở đúng hàng. Chạy RED.
- [ ] Sửa dòng 9: "giải ba câu hỏi" thành "trả lời ba câu hỏi".
- [ ] RQ3 tiếng Việt: thêm mệnh đề "Che vùng ảnh chỉ ở lúc đánh giá thì macro-F1 giảm còn 0,0723 nếu chỉ còn vùng phổi và 0,2084 nếu chỉ còn vùng ngoài mặt nạ."; tiếng Anh thêm câu tương ứng (0.0723 lung-only, 0.2084 outside-mask-only).
- [ ] Câu cuối tiếng Việt: thay bằng "Nhóm đặc trưng thủ công thay được nhóm histogram làm mốc tham chiếu ở RQ1, song mô hình chưa kiểm định lâm sàng và chưa kiểm trên ảnh của cơ sở khác nên chưa thể dùng như công cụ chẩn đoán."; tiếng Anh thay tương ứng.
- [ ] Độ trễ: tiếng Việt thêm "khi chạy liên tiếp" sau 131,8 ms; tiếng Anh thêm "in sustained mode"; ghi chú cuối tệp đổi nguồn trích dẫn thành mục 5.5.4 và Bảng 5.5 của Chương 5.
- [ ] Ghi chú cuối tệp: thêm hai số 0,0723 và 0,2084 vào ngoặc nguồn Bảng 4.1.
- [ ] Đếm từ hai bản; siết câu chữ nếu cần để bù mệnh đề thêm vào, rủi ro vẫn ghi rõ; kiểm không quá một trang.

### Nhiệm vụ 10: Ghi nhật ký, sinh lại Phụ lục B và mục lục, đồng bộ số

**Files:**
- Create: `docs/superpowers/tasks/2026-11-12-sua-review-vong-cuoi.md`
- Modify: `report/08_phu_luc_a_c.md` (B.1, B.2), `report/05_ket_qa_test_va_trien_khai.md`, `report/09_tom_tat_abstract.md`, `docs/report_standards.md`, `report/README.md`

**Interfaces:**
- Consumes: `scripts/report_appendix_b.py`, `scripts/report_frontmatter.py` chạy trên .venv-demo trong worktree.
- Produces: số đồng bộ 349 phép / 28 module / 348 pass + 1 bỏ qua ở mọi vị trí; mục lục khớp tiêu đề mới.

**Steps:**
- [ ] Ghi tệp nhật ký nhiệm vụ (trạng thái, quyết định, số đo mới) vào `docs/superpowers/tasks/`.
- [ ] Chạy `scripts/report_appendix_b.py`, dán B.1 và B.2 mới vào `08`; kiểm B.2: `test_val_near_duplicate_subset.py` 4 phép, `test_report_consistency.py` 7 phép, tổng 349.
- [ ] Đồng bộ số 349/28/348 tại: thân Ch5 + ghi chú 5.4, câu A.1 + ghi chú B.2, ba chỗ trong `09`, `docs/report_standards.md` mục 3.3, hai dòng trong `README`.
- [ ] Chạy `scripts/report_frontmatter.py` sinh lại mục lục (tiêu đề Bảng A.1/A.2 đã đổi, B.2 thành "(349 phép)").
- [ ] Chạy toàn bộ pytest trên các module được track: kỳ vọng 349 phép, 348 pass, 1 skip.

### Nhiệm vụ 11: Xác minh cuối + PR

**Files:**
- Modify: nhật ký nhiệm vụ (cập nhật kết quả)
- Create: tệp thân bài PR (tạm, ngoài repo hoặc trong temp)

**Interfaces:**
- Consumes: mọi thay đổi của các nhiệm vụ trước.
- Produces: nhánh đã đẩy, PR mở, người dùng tự merge.

**Steps:**
- [ ] Chạy script đối chiếu từng điểm review (viết tệp UTF-8 riêng): N1 đến N7, chênh số liệu, từng mục nhỏ; in PASS/FAIL.
- [ ] Grep quét sạch: `[7]`/`[8]` cũ, "cổng H3" trong `08`, "341/340/27 module", dấu gạch dài trong câu mới, "cell" trong ghi chú Ch2.
- [ ] Kiểm idempotent: chạy lại hai script sinh, `git diff` phải sạch.
- [ ] Kiểm staged: không có `bootstrap_config.json`, không có tệp slides, không có `demo/requirements.txt`.
- [ ] Cập nhật nhật ký nhiệm vụ với kết quả xác minh; commit nốt.
- [ ] Đẩy nhánh, mở PR bằng `gh pr create` với thân bài từ tệp; KHÔNG merge.

## Tự rà
- Đủ 11 nhiệm vụ, thứ tự khớp mục 4 của spec (Phụ lục A, B, C, N6, Ch6, Ch5, trích dẫn, tóm tắt, hàng rào rải vào từng nhiệm vụ, sinh lại, xác minh).
- Mỗi nhiệm vụ ghi rõ tệp, giao diện vào/ra, bước kiểm tra được–không được.
- Số kiểm thử mới (349/28/348) được tính trong Nhiệm vụ 10 và đối chiếu trong Nhiệm vụ 11.
- Rủi ro đã liệt kê ở "Trọng tâm rà soát" đều có bước chặn tương ứng.
