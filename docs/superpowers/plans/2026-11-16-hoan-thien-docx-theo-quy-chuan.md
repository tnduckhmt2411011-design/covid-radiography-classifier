# Hoàn thiện bản Word theo quy chuẩn CTUT — Kế hoạch triển khai

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (hoặc superpowers:subagent-driven-development). Mỗi bước dùng checkbox `- [ ]`.

**Goal:** Đóng 3 điểm lệch còn lại của `report/dist/BaoCao_BTL_HocMay_Nhom10.docx` so với `docs/report_standards.md`, nhúng logo thật vào bìa, và kiểm bố cục bằng WPS Office đã cài trên máy.

**Architecture:** Mọi thay đổi nằm ở `scripts/build_report_docx.py`, `scripts/audit_report.py`, hai tệp nguồn `report/*.md` và các bài kiểm thử đi kèm. Mỗi lỗi sửa theo TDD. Số phép kiểm thử đổi nên đồng bộ số liệu một lần ở Task 5. Task 1 và Task 6 là kiểm bằng mắt qua WPS, chạy trước và sau khi sửa.

**Tech Stack:** Python 3.12, `python-docx 1.2.0`, `markdown-it-py`, `pytest`, PyMuPDF (`fitz`, đã cài) để dựng PNG từ PDF, WPS Office 12.1 (COM `KWps.Application`, đã đăng ký trên máy).

**Spec:** `docs/report_standards.md` mục 2.2, 4.1, 4.2; `report/README.md`; ba điểm lệch tìm thấy khi kiểm lại ngày 16/11/2026: một bảng Chương 4 thiếu chú thích đánh số, phông Consolas cho mã, đường dẫn tệp trong chú thích `‡` của Chương 2.

## Global Constraints

- Nhánh làm việc: `check_and_convert_reports` (đang mở PR #71). Commit mới sẽ tự đẩy vào PR đó khi `git push`.
- Quy chuẩn 2.2: "Phông chữ (Font): **Times New Roman** (đồng nhất trên toàn bộ bài báo cáo, bao gồm cả nội dung, bảng biểu và phụ lục)".
- Quy chuẩn 4.1: "Vị trí tiêu đề: Đặt ở **phía trên** bảng"; đánh số `Bảng X.Y`.
- Quy chuẩn 4.2: "Không ghi đường dẫn tệp trong thân bài"; đường dẫn chỉ ở ghi chú kỹ thuật.
- Số cố định phải giữ nguyên: 21.165 ảnh; 14.815 / 3.174 / 3.176; macro-F1 test 0,8714; 32 bảng có số; 4 hình; 37 tiểu mục; `[1]`–`[13]`.
- Chạy test `.docx` bằng Python hệ thống (có `python-docx`); chạy toàn bộ kho bằng `D:\Use Antigravity\Medical Vision\.venv-demo\Scripts\python.exe -m pytest -q`; sau đó luôn `git checkout -- results/report_rq1/bootstrap_config.json results/report_rq2/bootstrap_config.json results/report_rq3/bootstrap_config.json`.
- Không đưa số kiểm thử vào báo cáo trước khi đo: lấy từ đầu ra của `scripts/report_appendix_b.py` chạy ở Task 5 Step 5, sau khi mọi test mới đã có.

## Quyết định cần bạn xác nhận (mặc định đã chọn sẵn)

| # | Quyết định | Mặc định kế hoạch | Cái giá |
|---|---|---|---|
| D1 | Bảng ánh xạ 5 kịch bản ở Chương 4 | Đổi thành danh sách gạch đầu dòng, giữ nguyên thông tin | Không phải đánh số lại Bảng 4.1–4.5 và mọi chỗ dẫn chiếu; còn 34 bảng trong `.docx` thay vì 35 |
| D2 | Phông chữ mã (`StandardScaler`, lệnh ở Phụ lục A) | Đổi sang Times New Roman toàn bộ | Mã khó phân biệt hơn với chữ thường; đổi lại một hằng số nếu hội đồng chấp nhận Consolas |
| D3 | Logo bìa | Nhúng `slides/assets/logo_ctut.png` (1200 × 1200, RGBA; dấu tròn ghi "Trường Đại học Kỹ thuật – Công nghệ Cần Thơ", chưa xác minh là bản chính thức) ở bìa chính, rộng 3,0 cm; nếu tệp thiếu thì giữ dòng đỏ `[Chèn logo CTUT]` | Builder phụ thuộc thư mục `slides/`; nếu logo không phải bản chính thức thì thay tệp |

## Review Focus

1. Logo làm bìa chính tràn sang trang thứ hai. Mong đợi: bìa chính một trang, bìa phụ một trang. Kiểm ở Task 1 và Task 6 (không thể kiểm bằng `python-docx`).
2. Chuyển bảng thành danh sách làm mất một cột thông tin. Mong đợi: cả 5 tên kịch bản, vai trò và mã trong kho đều còn trong văn bản. Test ở Task 2.
3. Chú thích khác cũng chứa đường dẫn. Mong đợi: kiểm toán bắt mọi định nghĩa `[^khóa]:`, không riêng `[^covid-src]`. Test ở Task 3.
4. Tệp logo vắng (ví dụ chạy trong `tmp_path`). Mong đợi: vẫn dựng được tệp Word, có dòng giữ chỗ. Test ở Task 5.
5. Đếm lệch số kiểm thử và số tệp sau khi thêm test và tệp kế hoạch. Mong đợi: `test_report_tables_match_sources.py` xanh. Kiểm ở Task 6.

---

### Task 1: Kiểm bố cục nền bằng WPS (trước khi sửa)

**Files:**
- Create: `docs/superpowers/audits/2026-11-16-wps-render.md`
- Scratch (không commit): `C:\Users\LENOVO\.gemini\antigravity\brain\2100be04-1ec5-45ae-9373-7571bc1c8f21\scratch\wps_export.py`

**Interfaces:**
- Produces: `wps_export.py <docx> <pdf>`, trả mã thoát 0 khi PDF được ghi; dùng lại ở Task 6.

- [ ] **Step 1: Viết `wps_export.py`**: dùng `win32com`/PowerShell `New-Object -ComObject KWps.Application`, mở tệp chỉ đọc, không hiện cửa sổ, xuất PDF (`ExportAsFixedFormat`), rồi `Quit()` chỉ phiên do chính script mở. Giới hạn 120 giây.
- [ ] **Step 2: Chạy** trên `report/dist/BaoCao_BTL_HocMay_Nhom10.docx`. Kết quả mong đợi: PDF được ghi. Nếu COM lỗi, treo hoặc hiện hộp thoại: dừng, ghi lý do, nhờ bạn mở tệp bằng WPS thủ công theo danh sách ở Step 4.
- [ ] **Step 3: Đọc PDF bằng PyMuPDF**: tổng số trang; trang bắt đầu và kết thúc của "TÓM TẮT" và "ABSTRACT" (mỗi phần phải nằm trọn một trang); số trang của hai trang bìa (mỗi bìa một trang); dựng PNG cho bìa chính, trang có công thức (2.1), trang có Bảng 4.1 và Bảng 6.1, một trang Phụ lục C.
- [ ] **Step 4: Ghi** vào `2026-11-16-wps-render.md` từng phát hiện kèm trang. Phát hiện do builder gây ra mà ngoài 4 task dưới thì thêm task mới vào tệp này; phát hiện chỉ do WPS khác Word thì ghi "chưa kết luận" (bố cục Word có thể khác).
- [ ] **Step 5: Commit**: `git add docs/superpowers/audits/2026-11-16-wps-render.md && git commit -m "docs: wps render baseline for report docx"`

### Task 2: Bảng ánh xạ kịch bản Chương 4 thành danh sách (D1)

**Files:**
- Modify: `report/04_hoc_loi_tat_rq3.md` (khối bảng ngay sau câu "Để gọn, từ đây ba kịch bản…")
- Modify: `docs/superpowers/audits/2026-11-16-audit-report.md` (dòng F08 và dòng "35 bảng")
- Test: `tests/test_build_report_docx.py`

**Interfaces:**
- Produces: `test_body_tables_have_caption_above(tmp_path)`.

- [ ] **Step 1: Viết test thất bại** `test_body_tables_have_caption_above`: dựng `.docx`, mọi `w:tbl` sau đoạn Heading 1 "CHƯƠNG 1." phải có ngay phía trước một đoạn kiểu `Caption Table`; hai bảng ký hiệu ở phần mở đầu được miễn. Thêm trong cùng test: văn bản Chương 4 chứa đủ năm cụm `Ảnh gốc cả hai tập`, `Chỉ phổi cả hai tập`, `Chỉ ngoài phổi cả hai tập`, `Gốc học, phổi đánh giá`, `Gốc học, ngoài phổi đánh giá` và đủ năm mã `orig_to_orig`, `lung_to_lung`, `out_to_out`, `orig_to_lung`, `orig_to_out`.
- [ ] **Step 2: Chạy** `python -m pytest tests/test_build_report_docx.py::test_body_tables_have_caption_above -v`. Mong đợi FAIL ở Chương 4.
- [ ] **Step 3: Sửa `04`**: thay bảng 5 hàng bằng 5 gạch đầu dòng, mỗi dòng gồm tên kịch bản, ảnh train, ảnh validation, vai trò và mã trong ngoặc. Tìm mọi chỗ nhắc "bảng tên kịch bản" trong `04` và `report/README.md` rồi sửa cho khớp.
- [ ] **Step 4: Chạy** test ở Step 2 và `python -m scripts.audit_report`. Mong đợi PASS và `total=0`. Sửa F08 trong audit thành "đã chuyển thành danh sách", bảng trong `.docx` còn 34.
- [ ] **Step 5: Commit**: `git add tests/test_build_report_docx.py report/04_hoc_loi_tat_rq3.md docs/superpowers/audits/2026-11-16-audit-report.md && git commit -m "report: replace unnumbered scenario table in chapter 4 with a list"`

### Task 3: Bỏ đường dẫn khỏi chú thích `‡` và mở rộng kiểm toán

**Files:**
- Modify: `report/02_du_lieu_va_phuong_phap.md` (định nghĩa `[^covid-src]:`)
- Modify: `scripts/audit_report.py`
- Test: `tests/test_audit_report.py`, `tests/test_build_report_docx.py`

**Interfaces:**
- Produces: `check_footnote_paths(report_dir: Path | None = None) -> list[Finding]` trong `scripts/audit_report.py`, gọi từ `run_all_checks`; `Finding("minor", file, line, "footnote-path", ...)`.

- [ ] **Step 1: Viết hai test thất bại.** `test_check_footnote_paths_flags_path` (`tests/test_audit_report.py`): thư mục tạm có một `.md` chứa `[^a]: xem docs/x.md` thì kết quả có đúng một `Finding` loại `footnote-path`; không có đường dẫn thì danh sách rỗng. Trong `test_no_technical_notes_and_no_paths` (`tests/test_build_report_docx.py`) thêm `assert "docs/" not in body_txt`.
- [ ] **Step 2: Chạy** hai test. Mong đợi FAIL (hàm chưa có; Chương 2 còn `docs/dataset_provenance.md`).
- [ ] **Step 3: Cài `check_footnote_paths`** dùng lại `path_re` của `check_h7_and_paths`; quét mọi dòng `[^khóa]:` của các tệp chương, không bỏ qua phần ghi chú kỹ thuật.
- [ ] **Step 4: Sửa `[^covid-src]`** trong `02`: bỏ câu "Chi tiết ở `docs/dataset_provenance.md` mục 2.1 và 2.3." (đường dẫn này đã nằm ở mục "Nguồn mục 2.1" của ghi chú kỹ thuật). Chạy lại hai test và `python -m scripts.audit_report`. Mong đợi PASS, `total=0`.
- [ ] **Step 5: Commit**: `git add scripts/audit_report.py tests/test_audit_report.py tests/test_build_report_docx.py report/02_du_lieu_va_phuong_phap.md && git commit -m "report: drop file path from covid-src footnote and audit footnote paths"`

### Task 4: Times New Roman cho cả mã (D2)

**Files:**
- Modify: `scripts/build_report_docx.py` (hằng `CODE_FONT` dòng 25; cỡ chữ mã trong dòng ở dòng 461; mã khối ở dòng 679)
- Test: `tests/test_build_report_docx.py` (`test_no_raw_markdown_leaks` dòng 213, `test_fonts_all_times_new_roman` dòng 364, test mới)

**Interfaces:**
- Produces: `test_no_monospace_font_anywhere(tmp_path)`.

- [ ] **Step 1: Viết test thất bại** `test_no_monospace_font_anywhere`: dựng `.docx`, duyệt mọi `w:rFonts` trong thân, bảng, header và footer; tập tên phông có tên rõ ràng (không tính phông toán Cambria Math trong `m:r`) phải bằng `{"Times New Roman"}`. Sửa `test_fonts_all_times_new_roman` còn chấp nhận duy nhất `Times New Roman`; sửa `test_no_raw_markdown_leaks` để đoạn mã `StandardScaler` dùng `Times New Roman` thay cho `Consolas 11 pt`.
- [ ] **Step 2: Chạy** ba test. Mong đợi FAIL (hiện còn 26 đoạn Consolas ở thân Chương 1–6, 78 ở phần cuối, 124 trong bảng).
- [ ] **Step 3: Đặt `CODE_FONT = FONT_NAME`.** Mã trong dòng dùng cỡ thân; mã khối (Phụ lục A) dùng 10,5 pt, thụt trái 0,5 cm, không thụt đầu dòng. Giữ nguyên mọi chỗ khác.
- [ ] **Step 4: Chạy** toàn bộ `python -m pytest tests/test_build_report_docx.py -v`. Mong đợi PASS toàn bộ.
- [ ] **Step 5: Commit**: `git add scripts/build_report_docx.py tests/test_build_report_docx.py && git commit -m "feat: render code in Times New Roman per report standard"`

### Task 5: Nhúng logo CTUT vào bìa chính (D3), đồng bộ số liệu, dựng lại tệp

**Files:**
- Modify: `scripts/build_report_docx.py` (`add_cover` dòng 1025; `build_docx` dòng 1101–1133)
- Modify: `report/README.md` (bước 1 của danh sách kiểm Word, mục 5), `docs/superpowers/audits/2026-11-16-audit-report.md` (mục "Kiểm tra độc lập `.docx`")
- Test: `tests/test_build_report_docx.py`
- Sync số kiểm thử (6 chỗ cũ): `report/05_ket_qua_test_va_trien_khai.md`, `report/08_phu_luc_a_c.md`, `report/09_tom_tat_abstract.md`, `docs/report_standards.md`, `report/README.md`, `report/00c_muc_luc_va_danh_muc.md` (sinh lại) và `test_numbers_survive_conversion`

**Interfaces:**
- Consumes: `add_cover(doc, md, border_png, subtitle)` hiện có.
- Produces: `add_cover(doc: Document, md: str, border_png: Path, subtitle: bool = False, logo_png: Path | None = None) -> None`. Có `logo_png` tồn tại thì chèn ảnh rộng `Cm(3.0)` căn giữa thay cho dòng giữ chỗ; không có thì giữ dòng đỏ `[Chèn logo CTUT]`. `build_docx` truyền `logo_png = report_dir.resolve().parent / "slides" / "assets" / "logo_ctut.png"` cho bìa chính.

- [ ] **Step 1: Viết hai test thất bại.** `test_cover_embeds_logo_when_available`: gọi `add_cover(..., logo_png=Path("slides/assets/logo_ctut.png"))` thì có đúng một ảnh inline, rộng 3,0 cm (dung sai 0,05 cm) và văn bản không chứa `[Chèn logo CTUT]`. `test_cover_placeholder_when_logo_missing`: `logo_png` trỏ tệp không tồn tại thì còn dòng giữ chỗ. Test `test_cover_content` hiện có (không truyền `logo_png`) vẫn phải qua.
- [ ] **Step 2: Chạy** hai test. Mong đợi FAIL (`add_cover` chưa nhận `logo_png`).
- [ ] **Step 3: Cài** theo chữ ký trên.
- [ ] **Step 4: Chạy** `python -m pytest tests/test_build_report_docx.py tests/test_audit_report.py -v`. Mong đợi PASS.
- [ ] **Step 5: Đo lại số liệu**: `& "D:\Use Antigravity\Medical Vision\.venv-demo\Scripts\python.exe" scripts/report_appendix_b.py`. Cập nhật 6 chỗ đồng bộ, Bảng B.1 (tệp kế hoạch và tệp WPS làm `docs/` và tổng tăng) và `test_numbers_survive_conversion` theo đúng số in ra; không dùng số ước lượng. Sinh lại `00c`: `python -m scripts.report_frontmatter`. README: bỏ bước "thay `[Chèn logo CTUT]`", thay bằng "logo lấy từ `slides/assets/logo_ctut.png`; thay tệp nếu cần bản khác".
- [ ] **Step 6: Dựng lại** `python -m scripts.build_report_docx --out report/dist/BaoCao_BTL_HocMay_Nhom10.docx` rồi `python -m scripts.audit_report`. Mong đợi `total=0`.
- [ ] **Step 7: Commit**: `git add scripts/build_report_docx.py tests/test_build_report_docx.py report docs && git commit -m "feat: embed CTUT logo on cover and sync test counts"`

### Task 6: Kiểm toàn bộ và kiểm bố cục sau sửa bằng WPS

**Files:**
- Modify: `docs/superpowers/audits/2026-11-16-wps-render.md` (thêm mục "Sau khi sửa")

- [ ] **Step 1: Chạy toàn bộ.** `python -m pytest tests/test_build_report_docx.py tests/test_audit_report.py -v` (Python hệ thống), rồi `.venv-demo` `pytest -q`; sau đó `git checkout -- results/report_rq1/bootstrap_config.json results/report_rq2/bootstrap_config.json results/report_rq3/bootstrap_config.json`. Mong đợi 0 lỗi; số skipped giải thích được (thiếu `python-docx` trong `.venv-demo`, thiếu `nbformat`, thiếu tệp `.joblib` cục bộ).
- [ ] **Step 2: Lặp lại Task 1 Step 2–3** trên tệp mới. Mong đợi: bìa chính một trang kèm logo, bìa phụ một trang, "TÓM TẮT" và "ABSTRACT" mỗi phần trọn một trang, công thức (2.1) nằm giữa dòng và số `(2.1)` sát lề phải, các bảng 6–8 cột không bị cắt. Chỗ nào lệch thì ghi trang và nguyên nhân; chỗ do WPS khác Word ghi "chưa kết luận".
- [ ] **Step 3: Cập nhật mục "Sau khi sửa"** trong `2026-11-16-wps-render.md`, commit: `git add docs/superpowers/audits/2026-11-16-wps-render.md && git commit -m "docs: wps render check after fixes"`.
- [ ] **Step 4: Đẩy** `git push` (cập nhật PR #71) khi bạn đồng ý; báo kết quả từng bước bằng đầu ra thật.

---

## Self-review

- **Phủ spec:** 3 điểm lệch (bảng chưa có chú thích → Task 2; Consolas → Task 4; đường dẫn trong chú thích → Task 3), logo (Task 5), WPS (Task 1 và 6). Hai việc ngoài phạm vi: Turnitin và kiểm trong Microsoft Word, cả hai vẫn do bạn làm.
- **Nhất quán chữ ký:** `add_cover(..., logo_png)` chỉ do Task 5 định nghĩa và chỉ `build_docx` gọi; `check_footnote_paths` chỉ do Task 3 định nghĩa.
- **Rủi ro còn lại:** COM của WPS chưa thử trên máy; nếu thất bại, Task 1 và 6 chuyển thành checklist thủ công. WPS không thay Word cho bước kiểm cuối nếu trường dùng Word.
