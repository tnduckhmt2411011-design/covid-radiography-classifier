# Kế hoạch: Rà soát báo cáo và dựng bản Word hoàn chỉnh

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (khuyến nghị, vì người dùng sẽ đổi model rồi chạy trong một phiên) hoặc superpowers:subagent-driven-development. Mỗi bước dùng checkbox `- [ ]`.

**Goal:** Rà soát văn phong, logic, số liệu, định dạng của toàn bộ tệp trong `report/`; nếu sạch thì chuyển sang `.docx` và ghép thành một quyển báo cáo duy nhất đúng quy chuẩn CTUT.

**Architecture:** Hai giai đoạn có cổng chặn. Giai đoạn A chỉ đọc và đối chiếu (script + review từng chương) rồi ghi một báo cáo phát hiện. Giai đoạn B chỉ chạy khi cổng A đạt: một script Python (`scripts/build_report_docx.py`) đọc các tệp `.md` theo thứ tự quyển và dựng `.docx` bằng `python-docx`, có kiểm thử cấu trúc.

**Tech Stack:** Python 3.12, `python-docx 1.2.0`, `markdown-it-py 4.2.0` (đã cài), `pytest`. Không có pandoc, Word hay LibreOffice trên máy (đã kiểm tra).

**Spec:** `docs/report_standards.md` (định dạng, cấu trúc 50 mục, cổng H2/H7, quy tắc D4), `docs/academic_writing_guide.md` (văn phong), `report/README.md` (bản đồ nguồn số liệu, thứ tự mục).

## Global Constraints

- Nguồn sự thật của số liệu là CSV/JSON trong `results/`, không phải tệp `.md` tóm tắt. Không mở ảnh nào của split `test`.
- Số liệu cố định phải khớp ở mọi chương: 21.165 ảnh; train/val/test = 14.815 / 3.174 / 3.176; 349 lỗi val, 427 lỗi test; macro-F1 test 0,8714, CI [0,8579; 0,8840]; accuracy test 86,56%; chênh −0,0310; 304/427 = 71,19%; 735 cặp gần trùng (CI hiệu tập con gần trùng [−0,0462; 0,0386]); 351 phép kiểm thử / 28 module (350 pass, 1 skip); RQ3 có 5 kịch bản (gồm 0,0723 và 0,2084); 12 giới hạn ở Chương 6.
- Quy tắc D4 nguyên văn: *"Mọi lời giải thích về sự khác biệt giữa val và test đều là giả thuyết chưa kiểm chứng, không nêu nguyên nhân."* Không dùng "nguyên nhân", "do đó", "vì vậy" cho chênh lệch val–test.
- Chỉ học máy cổ điển (H7): báo cáo không nhắc `torch`, `tensorflow`, `keras`, `timm` ngoài chỗ nêu rõ là bị cấm.
- Trang: A4 đứng, một mặt; lề trên/dưới 2,0–2,5 cm, trái 3,0–3,5 cm, phải 2,0 cm. Times New Roman; thân 13 pt; H1 14–16 pt in hoa đậm; H2 13–14 pt đậm; H3 13 pt đậm nghiêng; bảng và chú thích 10–11 pt. Giãn dòng 1,3; before/after 3–6 pt; thụt đầu dòng 1,0–1,27 cm; canh đều.
- Đánh số trang: bìa chính và bìa phụ không đánh số; từ Lời cảm ơn đến Danh mục hình dùng i, ii, iii; từ Chương 1 đến hết Phụ lục dùng 1, 2, 3 (bắt đầu lại từ 1).
- Tiêu đề bảng ở trên (`Bảng X.Y`), tiêu đề hình ở dưới (`Hình X.Y`), in đậm. Bảng kiểu Booktabs, không kẻ dọc, hàng tiêu đề tô xám 10–15%.
- Trích dẫn IEEE `[n]` theo thứ tự xuất hiện lần đầu; hiện có `[1]`–`[13]`.
- Không ghi đường dẫn tệp trong thân bài (chỉ trong "Ghi chú kỹ thuật"); mã nội bộ (D1–D4, G1–G6, H2, R1–R5, PR #) chỉ đặt trong ngoặc.

## Review Focus

Các tình huống spec ngầm đòi hỏi mà không task nào kiểm bằng test sẵn:

1. Thứ tự mục đầu quyển đang mâu thuẫn: `report_standards.md` mục 3.1 và `README.md` để Mục lục (6) trước Danh mục ký hiệu (7), còn `00c_muc_luc_va_danh_muc.md` đánh số vi = ký hiệu, vii = mục lục. Docx phải theo đúng một thứ tự.
2. Mục lục và hai danh mục trong `00c` để trống số trang; máy không có Word nên không tính được số trang thật. Docx phải dùng trường (field) để Word tự cập nhật, và phải nhắc người dùng cập nhật.
3. Các đoạn "Ghi chú kỹ thuật (không thuộc nội dung báo cáo)" và đoạn hướng dẫn dựng bản Word ở đầu `00a`, `00c` không được lọt vào quyển.
4. Ký hiệu toán trong dòng (`$u$`, `$D = 0$`, `$\pm$`) và công thức (2.1) phải hiển thị đúng, không còn dấu `$`.
5. Hình trong `report/figures/` phải vừa lề (chiều rộng ≤ 15,5 cm với lề trái 3,0 cm, phải 2,0 cm).

---

## Quyết định cần người dùng xác nhận trước khi chạy (đã đặt mặc định)

| # | Quyết định | Mặc định của kế hoạch | Lý do |
| :-: | :--- | :--- | :--- |
| Q1 | Công cụ chuyển đổi | Script `python-docx` tự viết, không cài thêm | Cần kiểm soát đánh số trang hai kiểu, khung viền bìa, trường mục lục. Pandoc không làm được các việc này nếu không hậu xử lý bằng `python-docx`, và máy chưa có pandoc |
| Q2 | Nếu rà soát ra lỗi | Tự sửa lỗi cơ học có nguồn rõ (số lệch CSV, bảng hỏng, chữ cấm); lỗi cần quyết định của tác giả thì dừng và báo cáo | Yêu cầu gốc là "nếu không có vấn đề thì convert"; không tự ý đổi lập luận |
| Q3 | "Ghi chú kỹ thuật" | Loại khỏi bản Word | Chính tệp ghi là "không thuộc nội dung báo cáo" |
| Q4 | Kiểm tra hiển thị | Người dùng mở bằng Word, bấm *Update field* (F9) và xem bằng mắt | Máy không có Word/LibreOffice. Có thể cài LibreOffice bằng `winget` nếu người dùng đồng ý, để xuất PDF kiểm tra |
| Q5 | Vị trí đầu ra | `report/dist/BaoCao_BTL_HocMay_Nhom10.docx`, thêm `report/dist/` vào `.gitignore` | Sản phẩm sinh ra, không commit |

---

## File Structure

| Tệp | Trách nhiệm |
| :--- | :--- |
| `docs/superpowers/audits/2026-11-16-audit-report.md` (tạo) | Bảng phát hiện hợp nhất: mức độ, vị trí, vấn đề, bằng chứng, cách sửa, trạng thái |
| `scripts/audit_report.py` (tạo) | Kiểm tra tự động: số liệu chéo chương, từ cấm, tham chiếu bảng/hình, trích dẫn, đếm mục |
| `tests/test_audit_report.py` (tạo) | Kiểm thử cho các hàm của `audit_report.py` bằng đoạn văn mẫu |
| `scripts/build_report_docx.py` (tạo) | Đọc `.md`, dựng `.docx` |
| `tests/test_build_report_docx.py` (tạo) | Mở lại `.docx` sinh ra và khẳng định cấu trúc, định dạng |
| `report/*.md` (sửa nếu A phát hiện lỗi) | Chỉ sửa theo bảng phát hiện đã duyệt |
| `.gitignore` (sửa) | Thêm `report/dist/` |

Nhánh làm việc: giữ nguyên worktree `check_and_convert_reports`.

---

# Giai đoạn A: Rà soát (chỉ đọc, trừ khi sửa lỗi ở A4)

### Task A1: Kiểm tra tự động bằng script

**Files:**
- Create: `scripts/audit_report.py`, `tests/test_audit_report.py`

**Interfaces:**
- Produces: `load_chapters() -> dict[str, str]` (tên tệp → nội dung UTF-8, đã bỏ mục "Ghi chú kỹ thuật"); `check_banned_phrases(text: str) -> list[Finding]`; `check_fixed_numbers(chapters: dict[str, str]) -> list[Finding]`; `check_captions_and_refs(chapters) -> list[Finding]`; `check_citations(chapters, refs_text) -> list[Finding]`; `check_section_counts(chapters) -> list[Finding]`; `Finding = NamedTuple(severity, file, line, rule, excerpt)`.

- [ ] **Step 1: Viết test lỗi trước** cho từng hàm, dùng đoạn văn mẫu nhỏ. Ví dụ: `check_banned_phrases("Chênh lệch này do đó phát sinh vì nguyên nhân X")` trả về ít nhất 1 Finding mức `critical` (quy tắc D4); `check_fixed_numbers` bắt `3.714` thay vì `3.174`.
- [ ] **Step 2: Chạy** `pytest tests/test_audit_report.py -v`. Mong đợi: FAIL (hàm chưa có).
- [ ] **Step 3: Cài đặt** các hàm trong `scripts/audit_report.py`. Quy tắc cần mã hóa:
  - Từ cấm D4: "nguyên nhân", "do đó", "vì vậy" trong cửa sổ 200 ký tự quanh "val" và "test".
  - Từ sáo rỗng lấy từ bảng mục 3 của `docs/academic_writing_guide.md` (ví dụ "đi sâu tìm hiểu", "minh chứng hùng hồn", "bức tranh toàn cảnh", "hoàn hảo không tì vết", "tuyệt đối", "bước ngoặt"), kèm đếm liên từ nối đầu câu ("Hơn nữa", "Thêm vào đó", "Ngoài ra", "Do đó") và báo khi ≥ 3 câu liên tiếp.
  - Số cố định ở mục Global Constraints: với mỗi số, báo các biến thể sai (đổi chữ số, dùng dấu chấm thập phân kiểu `0.8714`, thiếu dấu tách nghìn).
  - Nhất quán dấu thập phân: chỉ dùng dấu phẩy ở thân bài (`0,8714`); báo `71.19%` kiểu dấu chấm.
  - Bảng/hình: mọi `**Bảng X.Y:` / `**Hình X.Y:` đánh số liên tục trong từng chương, có đúng 32 bảng và 4 hình toàn quyển, và mỗi cái được nhắc trong văn bản ít nhất một lần.
  - Trích dẫn: các `[n]` xuất hiện lần đầu theo thứ tự tăng dần, mọi `[n]` có trong `07_tai_lieu_tham_khao.md` (`[1]`–`[13]`), không có mục tham khảo nào không được dùng.
  - Đếm mục: 37 tiểu mục đúng như `report_standards.md` mục 3.2; chương 2 có 12, chương 3 có 4, chương 4 có 3, chương 5 có 8, chương 6 có 5.
  - Cổng H7 và H2: không có `torch|tensorflow|keras|timm` ngoài câu mô tả cổng; chương 1–4 không chứa số `3.176` hay `427` hay `0,8714` (số test chỉ từ chương 5).
  - Đường dẫn tệp (`results/`, `src/`, `.py`, `.csv`, `.json`) xuất hiện ngoài mục "Ghi chú kỹ thuật" → mức `minor`.
- [ ] **Step 4: Chạy lại test.** Mong đợi: PASS.
- [ ] **Step 5: Chạy toàn bộ trên báo cáo thật:** `python -m scripts.audit_report > docs/superpowers/audits/_auto_findings.txt`. Ghi nhận kết quả (chưa sửa gì).
- [ ] **Step 6: Commit**
  ```bash
  git add scripts/audit_report.py tests/test_audit_report.py
  git commit -m "test: add automated report audit checks"
  ```

### Task A2: Chạy bộ kiểm thử sẵn có làm đường cơ sở

**Files:** không sửa.

- [ ] **Step 1:** `pytest -q tests/test_report_tables_match_sources.py tests/test_report_figures.py tests/test_report_figures_rq3.py tests/test_report_figures_final_test.py tests/test_val_near_duplicate_subset.py tests/test_report_consistency.py` — Mong đợi: tất cả pass.
- [ ] **Step 2:** `pytest -q` toàn bộ trên `.venv-demo`. Mong đợi: 350 passed, 1 skipped (khớp Chương 5: 351 phép / 28 module). Nếu khác, ghi vào bảng phát hiện mức `major`.
- [ ] **Step 3:** `python -m scripts.report_frontmatter` và `python -m scripts.report_appendix_b`, rồi `git diff --stat report/`. Mong đợi: không có thay đổi (mục lục đang đồng bộ; Phụ lục B in ra stdout khớp bảng trong `08`). Nếu có diff, ghi lại và hoàn nguyên bằng `git checkout -- report/` trước khi rà tiếp.

### Task A3: Rà soát thủ công từng chương (đọc cả văn bản và nguồn)

Các lát cắt độc lập, chỉ đọc, có thể giao song song cho subagent `research` (mỗi lát một subagent); mỗi lát trả về bảng phát hiện theo mẫu dưới. Nếu chạy tuần tự trong một phiên thì làm lần lượt từng lát.

**Mẫu phát hiện:** `| ID | Mức (critical/major/minor) | Tệp:dòng | Loại (số liệu/logic/văn phong/định dạng) | Vấn đề | Bằng chứng (đường dẫn nguồn + giá trị) | Đề xuất sửa |`

Mức độ: *critical* = số sai, vi phạm D4/H2/H7, mâu thuẫn giữa chương; *major* = lập luận không đủ chứng cứ, thiếu dẫn chiếu, mâu thuẫn quy chuẩn; *minor* = văn phong, chính tả, định dạng.

Các lát:

- [ ] **A3.1 Đầu quyển:** `00a`, `00b`, `00c`, `09_tom_tat_abstract.md`. Kiểm: tên, MSSV khớp `docs/OWNERS.md`; dòng bìa theo `report_standards.md` mục 3.1 (tên trường, tên đề tài viết hoa, "Cần Thơ – Tháng 11/2026"); lời cam đoan trung thực; mỗi bản tóm tắt không quá một trang (đếm số từ, ước lượng ≤ 350 từ); mọi số trong tóm tắt và Abstract khớp Chương 3–6 (dùng đúng dấu phẩy/dấu chấm theo ngôn ngữ); bản Abstract tiếng Anh dùng số kiểu Anh và nhất quán với bản Việt; mọi ký hiệu trong `00b` có xuất hiện trong chương và ngược lại; **thứ tự mục đầu quyển (Review Focus #1)**.
- [ ] **A3.2 Chương 1** (`01_gioi_thieu.md`): số liệu dịch tễ có trích dẫn; RQ1–RQ3 khớp `results/threshold_v3.md` Mục 1; ngưỡng +0,005 khớp Bảng 1.1; phần cấu trúc báo cáo khớp bố cục thật; không dùng số test.
- [ ] **A3.3 Chương 2** (`02_du_lieu_va_phuong_phap.md`): đối chiếu từng con số với nguồn: 21.165 và phân bố 4 lớp theo `splits/split_v1.csv`; 178 nhóm/401 ảnh; 735 cặp (325/335/75), 229 khác nhãn; 273 ảnh và 0,9068 so với 0,9024, CI [−0,0462; 0,0386] theo `results/val_near_duplicate_subset/`; chiều đặc trưng 64+60+28=152 và HOG 10.404; công thức (2.1) đúng toán (D = (64 − u·v)/2); SHA-256 của split khớp README; logic từ EDA đến lựa chọn pHash T = 0.
- [ ] **A3.4 Chương 3** (`03_ket_qua_rq1_rq2.md`): đối chiếu 6 bảng với `results/report_rq1/*.csv` và `results/report_rq2/*.csv` (macro-F1, SD, CI, hiệu bootstrap); ghi nhận hiệu CI chứa 0 thì không được viết là "cao hơn có ý nghĩa"; ma trận nhầm lẫn 4×4 cộng đúng 3.174 và 349 lỗi; Hình 3.1 đúng tệp.
- [ ] **A3.5 Chương 4** (`04_hoc_loi_tat_rq3.md`): 5 kịch bản (không phải 3); bảng khớp `results/report_rq3/*.csv`; diễn giải ở 4.3 đều gắn nhãn *giả thuyết*; permutation importance cộng đúng 10 khối; không quy kết nhân quả.
- [ ] **A3.6 Chương 5** (`05_ket_qua_test_va_trien_khai.md`): số test chỉ từ `results/final_test/*.json` (0,8714; CI; 86,56%; −0,0310; 427 lỗi, 304 cặp Normal–Lung_Opacity = 71,19%); **D4**: tìm mọi câu giải thích chênh val–test; số liệu độ trễ khớp `results/demo_latency_*/latency.json`; SHA-256 và dung lượng mô hình (7.842.399 bytes); 351/28 và 350 pass/1 skip; Hình 5.1 khớp `results/final_test/confusion_matrix_test.png`.
- [ ] **A3.7 Chương 6 và cuối quyển** (`06`, `07`, `08`): 12 giới hạn đủ và khớp `results/report_rq3/r5_gioi_han.md` + biên lưới Phụ lục C; kết luận 6.5 không thêm số mới; cảnh báo y khoa không quy cho WHO/ACR; tài liệu tham khảo định dạng IEEE đầy đủ (`[1]`–`[13]`) và khớp trích dẫn trong thân bài; Phụ lục C khớp `PARAM_GRIDS` trong `src/rq2_runner.py`.
- [ ] **A3.8 Văn phong toàn quyển** (một lượt đọc xuyên suốt sau khi A3.1–A3.7 xong): theo `docs/academic_writing_guide.md`: mở bài rập khuôn, cụm dịch máy, bộ ba đối xứng, tính từ khen ngợi, nhịp câu đơn điệu, thuật ngữ không nhất quán giữa các chương (ví dụ "nhóm ghép" / "nhóm đặc trưng ghép", "validation" / "tập kiểm định"), từ viết tắt dùng trước khi định nghĩa.
- [ ] **A3.9 Ba chỗ nghi ngờ đã thấy khi lập kế hoạch**, cần xác nhận hoặc bác bỏ trong bảng phát hiện:
  1. `report/README.md` dòng 81: hai hàng bảng dính nhau (`... (\`HOG_DIM = 10404\`) || 2.6.4 ...`), thiếu xuống dòng.
  2. `report/README.md` mục 5 "Trạng thái hiện tại" còn ghi "Còn thiếu: tóm tắt tiếng Việt và Abstract" trong khi `09_tom_tat_abstract.md` đã có.
  3. `docs/report_standards.md` mục 3.3 mô tả Phụ lục C là "kết quả đo đạc các run thực nghiệm", còn README và `08_phu_luc_a_c.md` mô tả là lưới siêu tham số và tham số chọn.

### Task A4: Hợp nhất, phân loại và cổng quyết định

**Files:**
- Create: `docs/superpowers/audits/2026-11-16-audit-report.md`
- Modify: `report/*.md` (chỉ các lỗi đã duyệt)

- [ ] **Step 1:** Gộp kết quả A1–A3 vào một bảng duy nhất, khử trùng, sắp theo mức độ. Ghi rõ dòng đầu: số critical / major / minor.
- [ ] **Step 2: Cổng.**
  - Không có critical hoặc major: ghi "Cổng A: ĐẠT", sang giai đoạn B.
  - Có lỗi: theo Q2, sửa các lỗi cơ học có nguồn rõ trong `report/*.md`. Với mỗi lỗi: sửa, chạy lại `python -m scripts.audit_report` và `pytest -q tests/test_report_tables_match_sources.py`, ghi trạng thái "đã sửa" kèm commit. Lỗi cần quyết định của tác giả: để trạng thái "chờ tác giả", **dừng ở đây**, báo người dùng, không sang giai đoạn B.
  - Nếu sửa số liệu Chương 5 hoặc số phép kiểm thử, đồng bộ cả bảy vị trí liệt kê trong `docs/superpowers/tasks/2026-11-12-do-gioi-han-1.md` (Chương 5 thân + ghi chú, Phụ lục B, Tóm tắt, Abstract, `report_standards.md` mục 3.3, README).
- [ ] **Step 3:** Chạy lại `python -m scripts.report_frontmatter` nếu thêm hoặc bớt bảng, hình, tiểu mục; kiểm tra `git diff --stat report/00c_muc_luc_va_danh_muc.md`.
- [ ] **Step 4: Commit**
  ```bash
  git add docs/superpowers/audits report
  git commit -m "report: audit findings and fixes before docx build"
  ```

---

# Giai đoạn B: Dựng `.docx` (chỉ sau khi Cổng A đạt)

Thứ tự quyển (theo `report_standards.md` mục 3.1, vì README cũng ghi thế; nếu A3.1 xác định `00c` mới là đúng thì sửa `00c` và README trước khi dựng):

1. Bìa chính (từ `00a` mục 1), 2. Bìa phụ (`00a` mục 2), 3. Lời cảm ơn, 4. Lời cam đoan (`00a` mục 3–4), 5. Tóm tắt và Abstract (`09`), 6. Mục lục (trường TOC), 7. Danh mục ký hiệu (`00b`), 8. Danh mục bảng (trường), 9. Danh mục hình (trường), Chương 1–6 (`01`–`06`), Tài liệu tham khảo (`07`), Phụ lục A–C (`08`).

### Task B1: Khung tài liệu, kiểu chữ và mục (heading)

**Files:**
- Create: `scripts/build_report_docx.py`, `tests/test_build_report_docx.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `build_docx(report_dir: Path, out_path: Path) -> Path`; `strip_technical_notes(md: str) -> str` (bỏ từ dòng `## Ghi chú kỹ thuật` đến hết tệp); `new_document() -> docx.Document` (A4, lề trái 3,0 / phải 2,0 / trên 2,0 / dưới 2,0 cm, Normal = Times New Roman 13 pt, giãn 1,3, canh đều, thụt 1,0 cm, before/after 4 pt).

- [ ] **Step 1: Viết test lỗi:** `test_page_setup_a4_margins` (rộng 21,0 cm, cao 29,7 cm, lề đúng); `test_normal_style_font` (Times New Roman, 13 pt, `line_spacing == 1.3`, `alignment == JUSTIFY`); `test_heading_styles` (Heading 1 in hoa, đậm, 15 pt; Heading 2 đậm 13,5 pt; Heading 3 đậm nghiêng 13 pt; cả ba có `rFonts` ascii/hAnsi/eastAsia = Times New Roman); `test_strip_technical_notes`.
- [ ] **Step 2: Chạy** `pytest tests/test_build_report_docx.py -v`; mong đợi FAIL.
- [ ] **Step 3: Cài đặt** `new_document`, `strip_technical_notes` và đặt phông cho cả `eastAsia` (tránh Word thay phông tiếng Việt). Thêm `report/dist/` vào `.gitignore`.
- [ ] **Step 4: Chạy test;** mong đợi PASS.
- [ ] **Step 5: Commit** `feat: docx builder skeleton with page setup and styles`.

### Task B2: Chuyển đổi Markdown sang phần tử Word

**Files:** Modify: `scripts/build_report_docx.py`, `tests/test_build_report_docx.py`

**Interfaces:**
- Consumes: `new_document()`.
- Produces: `render_markdown(doc, md: str, base_dir: Path) -> None` hỗ trợ: tiêu đề `#`/`##`/`###`; đoạn văn; in đậm, in nghiêng, mã nội dòng (Consolas 11 pt); danh sách `-` và `1.`; trích dẫn `>`; bảng pipe; ảnh `![alt](path)`; toán trong dòng `$..$`; công thức khối `$$..$$`; liên kết (giữ chữ, bỏ URL trừ mục tài liệu tham khảo).

- [ ] **Step 1: Viết test lỗi** (mỗi test một khối nhỏ):
  - `test_table_booktabs`: bảng 3×3 có viền trên và dưới đậm, một đường mảnh dưới hàng tiêu đề, không có viền dọc; hàng tiêu đề tô xám `D9D9D9`, cỡ chữ 10,5 pt; cột số căn phải.
  - `test_caption_placement`: dòng `**Bảng 3.1: ...**` đứng ngay trước bảng, in đậm, style `Caption Table`; dòng `**Hình 3.1: ...**` đứng ngay sau ảnh, căn giữa, style `Caption Figure`.
  - `test_image_fits_margins`: ảnh `khung_trang_bia.png` loại trừ; mọi ảnh khác rộng ≤ 15,5 cm, căn giữa.
  - `test_inline_math`: `"$u$ và $D = 0$"` không còn ký tự `$`; `u` in nghiêng; `$\pm$` thành `±`; `$\{-1, 1\}$` thành `{−1, 1}`.
  - `test_display_equation`: `$$D = \frac{64 - u \cdot v}{2} \qquad (2.1)$$` tạo một đoạn có phần tử `m:oMathPara` và số `(2.1)` căn sát lề phải bằng tab.
  - `test_no_raw_markdown_leaks`: sau khi dựng toàn quyển, không đoạn nào chứa `**`, `` ` ``, `](`, `$$`, `\frac`.
- [ ] **Step 2: Chạy;** mong đợi FAIL.
- [ ] **Step 3: Cài đặt** bằng `markdown-it-py` (bật `table`), duyệt token, tạo phần tử `python-docx`. Công thức (2.1) dựng trực tiếp thành OMML (chỉ có một công thức khối duy nhất nên viết hàm riêng `omml_fraction(num, den)` là đủ, không cần bộ dịch LaTeX tổng quát). Với toán trong dòng chỉ có tập ký hiệu nhỏ ở `00b` và chương 2, dùng bảng ánh xạ thay thế.
- [ ] **Step 4: Chạy test;** mong đợi PASS.
- [ ] **Step 5: Commit** `feat: docx markdown renderer for tables, figures, equations`.

### Task B3: Bìa, phần đầu quyển và ngắt mục (section)

**Files:** Modify: `scripts/build_report_docx.py`, `tests/test_build_report_docx.py`

**Interfaces:**
- Consumes: `render_markdown`.
- Produces: `add_cover(doc, md: str, border_png: Path, subtitle: bool) -> None`; `add_section_break(doc, page_format: Literal["none","lowerRoman","decimal"], restart_at: int | None) -> None`; `add_toc_field(doc, instruction: str) -> None`.

- [ ] **Step 1: Viết test lỗi:**
  - `test_cover_has_no_page_number`: section đầu tiên (bìa chính + bìa phụ) có footer rỗng.
  - `test_front_matter_roman_numbering`: section thứ hai có `w:pgNumType w:fmt="lowerRoman" w:start="1"`, footer có trường `PAGE`, canh giữa.
  - `test_body_arabic_restart`: section thứ ba bắt đầu tại Chương 1 với `w:fmt="decimal" w:start="1"`.
  - `test_each_chapter_starts_new_page`: mỗi Heading 1 có `page_break_before` hoặc đứng sau ngắt trang.
  - `test_toc_fields_present`: tài liệu có đúng một trường `TOC \o "1-3" \h \z \u` và hai trường danh mục bảng/hình (`TOC \h \z \t "Caption Table,1"` và `... "Caption Figure,1"`), cùng `w:updateFields` trong `settings.xml`.
  - `test_cover_content`: bìa chứa "TRƯỜNG ĐẠI HỌC KỸ THUẬT", "TS. Lê Anh Nhã Uyên", đủ 6 MSSV (`KHMT2411011`, `…021`, `…003`, `…022`, `…014`, `…046`), "Cần Thơ – Tháng 11/2026"; khung viền `khung_trang_bia.png` xếp lớp "Behind Text".
- [ ] **Step 2: Chạy;** mong đợi FAIL.
- [ ] **Step 3: Cài đặt.** Bìa lấy các khối trích dẫn (`>`) trong `00a` mục 1 và 2; bỏ các đoạn mô tả bố cục ("Bố cục.", "Khối 1 — …"), vì đó là hướng dẫn dựng, không phải nội dung. Logo trường: kho mã không có logo, nên chèn một đoạn giữ chỗ có chữ `[Chèn logo CTUT]` cỡ 11 pt màu đỏ và liệt kê trong báo cáo cuối kỳ cho người dùng thay bằng logo thật. Bỏ nội dung `00c` (mục lục tĩnh) và thay bằng trường Word.
- [ ] **Step 4: Chạy test;** mong đợi PASS.
- [ ] **Step 5: Commit** `feat: docx cover, sections, roman/arabic page numbering, TOC fields`.

### Task B4: Ghép toàn quyển và kiểm tra tổng

**Files:** Modify: `scripts/build_report_docx.py`, `tests/test_build_report_docx.py`

- [ ] **Step 1: Viết test lỗi** chạy trên báo cáo thật (đánh dấu `@pytest.mark.slow` nếu cần):
  - `test_full_build_order`: danh sách Heading 1 theo đúng thứ tự: 6 chương `CHƯƠNG 1.` … `CHƯƠNG 6.`, sau đó `TÀI LIỆU THAM KHẢO`, `PHỤ LỤC`.
  - `test_counts`: đủ 32 đoạn caption bảng và 4 caption hình; 13 mục `[n]` trong tài liệu tham khảo (`[1]`–`[13]`).
  - `test_no_technical_notes_and_no_paths`: không có chuỗi `Ghi chú kỹ thuật`, `results/`, `src/` trong thân Chương 1–6 (đường dẫn trong Phụ lục A–C được phép, vì phụ lục là hướng dẫn vận hành).
  - `test_fonts_all_times_new_roman`: duyệt mọi run, không run nào có phông khác (trừ mã nội dòng Consolas và đoạn giữ chỗ logo).
  - `test_numbers_survive_conversion`: các số cố định ở Global Constraints đều xuất hiện trong văn bản `.docx` đúng dạng (`3.174`, `0,8714`, `71,19%`, `351`).
- [ ] **Step 2: Chạy;** mong đợi FAIL (hoặc lộ lỗi dựng).
- [ ] **Step 3: Cài đặt** `build_docx` ghép các tệp theo thứ tự trên và chèn ngắt mục; thêm lệnh `python -m scripts.build_report_docx --out report/dist/BaoCao_BTL_HocMay_Nhom10.docx`.
- [ ] **Step 4:** Chạy `python -m scripts.build_report_docx --out report/dist/BaoCao_BTL_HocMay_Nhom10.docx` rồi `pytest tests/test_build_report_docx.py -v`. Mong đợi: tệp được tạo (> 200 KB do có ảnh) và test PASS.
- [ ] **Step 5: Kiểm tra độc lập, không dùng chính script dựng:** dùng `python-docx` mở lại tệp, in số đoạn, số bảng, số ảnh, số section; so với số liệu đếm từ `report/*.md` (số bảng pipe trừ các bảng của README, số `![`). Ghi kết quả vào cuối `docs/superpowers/audits/2026-11-16-audit-report.md`.
- [ ] **Step 6: Commit** `feat: build merged report docx`.

### Task B5: Bàn giao

- [ ] **Step 1:** Chạy `pytest -q` toàn bộ để chắc không làm hỏng kiểm thử cũ (mong đợi bộ test đầy đủ khớp số liệu đã đồng bộ ở Chương 5 và Phụ lục B).
- [ ] **Step 2:** Cập nhật `report/README.md` mục 5 "Trạng thái hiện tại": thêm dòng nêu cách dựng bản Word (`python -m scripts.build_report_docx`) và sửa mục "Còn thiếu" nếu A3.9 xác nhận đã lỗi thời. Khi thêm hai tệp test mới (`test_audit_report.py`, `test_build_report_docx.py`), đồng bộ số phép kiểm thử và Bảng B.1/B.2 ở tất cả vị trí liên quan (`05`, `08`, `09`, `docs/report_standards.md`, `report/README.md`, `00c`) trước khi dựng `.docx` cuối cùng để `test_report_tables_match_sources.py` và `test_report_consistency.py` đều xanh.
- [ ] **Step 3:** Báo cáo cho người dùng: đường dẫn `.docx`, bảng phát hiện A, danh sách việc người dùng phải làm thủ công: (a) thay giữ chỗ logo CTUT; (b) mở bằng Word, nhấn Ctrl+A rồi F9 để cập nhật mục lục và hai danh mục; (c) xem lại bằng mắt các trang có bảng rộng (Bảng 3.5, bảng ma trận nhầm lẫn, Phụ lục C) và ngắt trang xấu; (d) chạy kiểm tra trùng lặp (Turnitin hoặc phần mềm nội bộ) theo `report_standards.md` mục 5.2.
- [ ] **Step 4: Commit** `docs: record docx build procedure in report README`.

---

## Self-Review

1. **Spec coverage:** văn phong (A1 từ cấm + A3.8), logic (A3.2–A3.7), số liệu (A1 số cố định, A3.3–A3.6 đối chiếu nguồn), định dạng (B1–B3), thứ tự 50 mục (A1 đếm mục, phần "Thứ tự quyển"), đánh số trang (B3), trích dẫn IEEE (A1, A3.7), H2/H7/D4 (A1, A3.6), ghép thành một tệp (B4). Không còn yêu cầu nào thiếu task.
2. **Step scan:** các bước kiểm thử nêu tên test và giá trị cụ thể; cài đặt chỉ nêu chữ ký và ràng buộc.
3. **Type consistency:** `Finding`, `load_chapters`, `new_document`, `render_markdown`, `add_cover`, `add_section_break`, `add_toc_field`, `build_docx` dùng cùng tên ở mọi task.
4. **Review Focus:** mỗi mục có task sở hữu: #1 A3.1 và phần thứ tự quyển; #2 B3 `test_toc_fields_present` và B5 Step 3(b); #3 B1 `test_strip_technical_notes`, B3 Step 3, B4 `test_no_technical_notes_and_no_paths`; #4 B2 `test_inline_math`, `test_display_equation`, `test_no_raw_markdown_leaks`; #5 B2 `test_image_fits_margins`.
5. **Proportion:** kế hoạch dài hơn nhờ phần rà soát, nhưng không chứa thân hàm.

## Rủi ro đã biết

- Không có Word hay LibreOffice nên không xuất PDF để nhìn trang; nội dung trang thực tế chỉ xác nhận được khi người dùng mở bằng Word (Q4).
- Thêm tệp test mới đổi số 341/27 đang được khóa bằng `tests/test_report_tables_match_sources.py` và các tệp báo cáo; B5 Step 2 xử lý.
- Logo CTUT không có trong kho; bìa dùng giữ chỗ.
