# Kế hoạch thi công: Sửa các điểm review senior trên sáu chương

> **For agentic workers:** REQUIRED SUB-SKILL: Dùng superpowers:executing-plans (thi công trực tiếp trong phiên này). Các bước đánh dấu bằng checkbox (`- [ ]`) để theo dõi tiến độ.

**Goal:** Dọn các mâu thuẫn nội bộ và lỗi trình bày đã kiểm chứng trong review senior, chặn tái phát bằng ba phép kiểm thử hàng rào, giữ nguyên mọi số liệu truy được về nguồn.

**Architecture:** Sửa văn bản thuần trong 8 tệp báo cáo/tài liệu (nguyên văn cũ→mới đã chốt trong spec), thêm một tệp test hàng rào, rồi đồng bộ số bộ kiểm thử (344/28) và sinh lại nội dung do script sinh. Không đổi mã nguồn, không đổi môi trường chạy.

**Tech Stack:** pytest (hai môi trường `.venv` và `.venv-demo`), `scripts/report_appendix_b.py`, `scripts/report_frontmatter.py`, git, gh CLI.

**Spec:** `docs/superpowers/specs/2026-11-12-sua-review-senior-design.md` — mọi nguyên văn thay thế nằm ở mục 3 của spec, đánh số E1.1–E8.1. Kế hoạch này chỉ quyết định thứ tự, phép kiểm thử và lệnh xác minh.

## Global Constraints

- Số liệu mới chỉ từ nguồn trong kho, tính lại bằng script trước khi ghi (spec §2.1).
- Văn phong theo `docs/report_standards.md`: dấu phẩy thập phân, chấm phân cách hàng nghìn, không dấu gạch dài trong câu mới; Chương 1–4 chỉ số validation; không nêu nguyên nhân chênh validation–test.
- Không stage tệp không liên quan: `results/report_rq*/bootstrap_config.json` đang modified, để nguyên.
- Số bộ kiểm thử chỉ ghi sau khi đo bằng `pytest --collect-only -q` trên `.venv-demo`.
- PowerShell làm hỏng encoding khi viết script inline: ghi script ra tệp UTF-8 rồi chạy; commit message ghi qua tệp (`git commit -F <file>`).
- Người dùng tự merge PR: không chạy `gh pr merge`.

## Review Focus

1. **Số bộ kiểm thử lệch giữa các vị trí** (Chương 5, Phụ lục A.1, B.2, tóm tất, standards, README) — chặn bởi bước quét grep trong Task 8 và bộ `test_appendix_a1_test_count_matches_chapter5` đã có.
2. **Bảng B.2 sinh trên môi trường thiếu thư viện** cho số thấp hơn thực tế — chặn bằng bước chỉ chạy `report_appendix_b.py` trên `.venv-demo` (Task 8, bước 2).
3. **Bảng B.1 đếm tệp chưa `git add`** cho số cũ — chặn bằng bước `git add` ba tệp mới trước khi chạy script (Task 8, bước 1).
4. **Trích dẫn [7] lệch giữa Chương 5 và tệp 07** — chặn bằng bước so khớp nguyên văn trong Task 6.
5. **Sửa ghi chú làm mất nguồn số** (thay "dòng 187" bằng đoán mò) — chặn bằng mỏi neo đã xác minh trong spec §3 (E2.12, E2.14, E2.15, E3.2, E6.5).

---

### Task 1: Hàng rào kiểm thử (đỏ trước khi sửa)

**Files:**
- Create: `tests/test_report_consistency.py`
- Create: `docs/superpowers/tasks/2026-11-12-sua-review-senior.md` (nhật ký công việc, checklist theo spec)

**Interfaces:**
- Produces: ba tên phép kiểm thử mà Task 2–7 dùng làm tiêu chí pass: `test_rq3_decision_rule_lists_registered_comparisons`, `test_hamming_levels_are_even_levels_only`, `test_chapter1_has_no_internal_codes_or_overclaim`.

- [ ] **Step 1: Tạo nhật ký công việc** tại `docs/superpowers/tasks/2026-11-12-sua-review-senior.md`: danh sách 9 task của kế hoạch dạng checkbox, ghi trạng thái "đang làm".

- [ ] **Step 2: Viết tệp test hàng rào** `tests/test_report_consistency.py`:

```python
"""Hang rao nhat quan noi bo giua cac chuong bao cao (sau dot ra review senior)."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "report"


def _body(name: str) -> str:
    """Than bai cua mot tep: bo phan tai lieu tham khao va ghi chu ky thuat."""
    text = (REPORT / name).read_text(encoding="utf-8")
    for marker in ("## Tài liệu tham khảo phát sinh trong chương", "## Ghi chú kỹ thuật"):
        if marker in text:
            text = text.split(marker)[0]
    return text


def _rows(name: str, caption_re: str) -> list[str]:
    body = _body(name)
    m = re.search(caption_re, body)
    assert m, caption_re
    rows = []
    for line in body[m.end():].splitlines():
        if line.startswith("|"):
            rows.append(line)
        elif rows:
            break
    return rows


def _cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def test_rq3_decision_rule_lists_registered_comparisons() -> None:
    """Dong RQ3 cua Bang 1.1 phai neu ca hai phep so da dang ky truoc."""
    rows = _rows("01_gioi_thieu.md", r"\*\*Bảng 1\.1:")
    rq3 = next(r for r in rows if _cells(r)[0] == "RQ3")
    rule = _cells(rq3)[-1]
    assert "chỉ phổi" in rule and "ngoài phổi" in rule, rule
    roles = " ".join(_cells(r)[-1] for r in _rows("04_hoc_loi_tat_rq3.md", r"\*\*Bảng 4\.2:"))
    assert "Phép so chính" in roles
    assert "Bắt buộc trình bày" in roles


def test_hamming_levels_are_even_levels_only() -> None:
    """Khoang cach Hamming chi o muc 2 va 4 o moi chuong neu so do."""
    for name in ("02_du_lieu_va_phuong_phap.md", "06_thao_luan_gioi_han_huong_phat_trien.md"):
        body = _body(name)
        assert "từ 1 đến 4" not in body, name
        assert ("từ 2 đến 4" in body) or ("mức 2 và 4" in body), name


def test_chapter1_has_no_internal_codes_or_overclaim() -> None:
    """Chuong 1 khong giu ma hieu noi bo va khong hua qua ve RQ3."""
    body = _body("01_gioi_thieu.md")
    for code in ("H2", "H6", "H7", "D4"):
        assert not re.search(rf"\b{code}\b", body), code
    for phrase in ("giải quyết RQ3", "đo nó trực tiếp", "hoặc cắt"):
        assert phrase not in body, phrase
```

- [ ] **Step 3: Chạy ba phép mới, xác minh ĐỎ trên cả hai môi trường**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_report_consistency.py -q`
Expected: 3 failed (chứng minh hàng rào bắt đúng các lệch hiện có).

Run: `.\.venv-demo\Scripts\python.exe -m pytest tests/test_report_consistency.py -q`
Expected: 3 failed.

- [ ] **Step 4: Cập nhật nhật ký** (Task 1 xong, đánh dấu Task 2 đang làm). Không commit ở task này.

### Task 2: Sửa Chương 1 (spec E1.1–E1.14)

**Files:**
- Modify: `report/01_gioi_thieu.md` (mục 1.1, 1.2, 1.4, 1.5, Bảng 1.1 dòng RQ3, Bảng 1.2, phần tài liệu phát sinh, ghi chú)

**Interfaces:**
- Consumes: nguyên văn cũ→mới ở spec §3.1.
- Produces: văn bản Chương 1 thỏa mãn `test_chapter1_has_no_internal_codes_or_overclaim` và `test_rq3_decision_rule_lists_registered_comparisons`.

- [ ] **Step 1: Áp dụng 14 thay đổi E1.1–E1.14** theo spec §3.1, dùng công cụ edit; với E1.7 và E1.12 chỉ thay ô quy tắc trong bảng, giữ nguyên các ô khác.
- [ ] **Step 2: Chạy hai hàng rào liên quan**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_report_consistency.py -q`
Expected: 2 passed, 1 failed (phép còn lại thuộc Chương 2, Task 3).

- [ ] **Step 3: Rà tay bằng grep** — không còn "(H2)", "(H6)", "(ràng buộc H7)", "(Quy tắc D4)" trong `report/01_gioi_thieu.md`; có "[7]" ở phần tài liệu phát sinh.
- [ ] **Step 4: Commit** (kèm tệp test đỏ của Task 1 và nhật ký):

```bash
git add tests/test_report_consistency.py docs/superpowers/tasks/2026-11-12-sua-review-senior.md report/01_gioi_thieu.md
git commit -F <file thong diep>
```

Thông điệp: "report: fix chapter 1 overclaim, seed/numbering and internal codes (senior review)".

### Task 3: Sửa Chương 2 (spec E2.1–E2.16)

**Files:**
- Modify: `report/02_du_lieu_va_phuong_phap.md` (mục 2.3, 2.4, 2.5, 2.6.1, 2.6.4, 2.7, 2.9, ghi chú)

- [ ] **Step 1: Áp dụng 16 thay đổi E2.1–E2.16** theo spec §3.2. Với E2.3–E2.5 chỉ thay nội dung ba bước trong danh sách sáu bước, giữ nguyên đầu đề và câu kết.
- [ ] **Step 2: Chạy cả ba hàng rào**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_report_consistency.py -q`
Expected: 3 passed.

- [ ] **Step 3: Rà tay bằng grep** — không còn "tác giả ký", "từ 1 đến 4", "dòng 187", "dòng 2.2", "cell 4–5", "bản trước ghi 7,6%" trong tệp.
- [ ] **Step 4: Commit** — thông điệp: "report: align chapter 2 gates, Hamming levels and notes (senior review)".

### Task 4: Sửa Chương 3 (spec E3.1–E3.3)

**Files:**
- Modify: `report/03_ket_qua_rq1_rq2.md` (mục 3.4, hai bullet ghi chú)

- [ ] **Step 1: Áp dụng E3.1–E3.3** theo spec §3.3.
- [ ] **Step 2: Rà tay bằng grep** — không còn "dòng 433", "Bản trước ghi", "khó tách nhất".
- [ ] **Step 3: Commit** — thông điệp: "report: clean chapter 3 clinical claim and notes (senior review)".

### Task 5: Sửa Chương 4, gồm số liệu mới tính từ CSV (spec E4.1–E4.6)

**Files:**
- Modify: `report/04_hoc_loi_tat_rq3.md` (mục 4.1, 4.3, Bảng 4.4, ghi chú)

- [ ] **Step 1: Tính lại bốn số nhóm Mooney từ nguồn, ghi kết quả ra màn hình trước khi sửa**

Ghi script tạm UTF-8 rồi chạy (mã hóa 0=COVID, 1=Lung_Opacity, 2=Normal, 3=Viral Pneumonia): ghép `results/rq3_ghep_svm_{orig_to_orig,lung_to_lung,out_to_out}_s42/preds_val.csv` với `results/eda/normal_source_labels.csv`; đếm (a) ảnh Viral Pneumonia bị đoán thành Normal của mỗi kịch bản, (b) ảnh Normal nguồn Mooney bị đoán thành Viral Pneumonia.
Expected: (a) = 7, 5, 6; (b) = 0, 0, 0; tỷ lệ (a)+(b) chia 400 = 1,75%, 1,25%, 1,50%.

- [ ] **Step 2: Áp dụng E4.1–E4.6** theo spec §3.4: thêm ô vào ba hàng Bảng 4.4, bổ sung cột đầu bảng, hai câu thân bài, hai câu ghi chú. Chú thích bảng giữ nguyên.
- [ ] **Step 3: Rà tay bằng grep** — Bảng 4.4 có đúng 4 cột ở mỗi hàng; ghi chú có câu giải thích cột mới; có câu chú thích trùng hợp LBP.
- [ ] **Step 4: Commit** — thông điệp: "report: add Mooney-400 rates and LBP rounding note to chapter 4 (senior review)".

### Task 6: Sửa Chương 5, tệp tài liệu tham khảo và roadmap (spec E5.1–E5.7, E7.1, E8.1)

**Files:**
- Modify: `report/05_ket_qua_test_va_trien_khai.md` (mục 5.4, 5.5.1, 5.5.4, khối tài liệu, ghi chú)
- Modify: `report/07_tai_lieu_tham_khao.md` (mục [7])
- Modify: `docs/roadmap.md` (một dòng trong bảng quyết định)

- [ ] **Step 1: Áp dụng E5.1–E5.7** theo spec §3.5. E5.1/E5.2 giữ nguyên số 341→344 chưa đổi ở bước này; số sẽ đổi đồng loạt ở Task 8 (ghi chú trong nhật ký).
- [ ] **Step 2: Áp dụng E7.1**: thay mục [7] trong `report/07_tai_lieu_tham_khao.md` bằng nguyên văn E5.6.
- [ ] **Step 3: Áp dụng E8.1** trong `docs/roadmap.md`.
- [ ] **Step 4: So khớp trích dẫn** — dòng [7] trong hai tệp giống nhau từng ký tự (so bằng lệnh so sánh hai dòng trích xuất từ grep).
- [ ] **Step 5: Rà tay bằng grep** — không còn "của mỗi lượt", "Hugging Face Hub documentation", dấu gạch dài trong câu 5.5.4 và ghi chú; có cụm "chống nhầm lẫn chứ không chống cố ý".
- [ ] **Step 6: Commit** — thông điệp: "report: fix chapter 5 latency/notebook wording and cite artifact repo (senior review)".

### Task 7: Sửa Chương 6 (spec E6.1–E6.5)

**Files:**
- Modify: `report/06_thao_luan_gioi_han_huong_phat_trien.md` (mục 6.1, 6.2, 6.4, 6.5, ghi chú)

- [ ] **Step 1: Áp dụng E6.1–E6.5** theo spec §3.6.
- [ ] **Step 2: Rà tay bằng grep** — không còn "định lượng được mức phụ thuộc", "có lẻ nhỏ", "trên chính tập validation hiện có"; dấu gạch dài trong ghi chú đã bỏ.
- [ ] **Step 3: Chạy lại ba hàng rào** trên cả hai môi trường: 3 passed.
- [ ] **Step 4: Commit** — thông điệp: "report: fix chapter 6 typo, direction 2 and conclusion split (senior review)".

### Task 8: Đồng bộ số 344/28, sinh lại Phụ lục B và mục lục

**Files:**
- Modify: `report/08_phu_luc_a_c.md`, `report/09_tom_tat_abstract.md`, `docs/report_standards.md`, `report/README.md`, `scripts/report_appendix_b.py`, `report/00c_muc_luc_va_danh_muc.md` (sinh lại), `docs/superpowers/specs/2026-11-12-sua-review-senior-design.md` (add vào git)

- [ ] **Step 1: `git add` toàn bộ tệp mới** (test, nhật ký, spec) để `git ls-files` đã thấy chúng trước khi sinh Bảng B.1.

- [ ] **Step 2: Sinh lại Phụ lục B trên môi trường đủ thư viện**

Run: `.\.venv-demo\Scripts\python.exe scripts\report_appendix_b.py` → dán Bảng B.1 và Bảng B.2 vào `report/08_phu_luc_a_c.md` thay hai bảng cũ.
Expected: B.2 có 28 dòng module (trong đó `test_report_consistency.py` | 3), tổng 344; B.1 ghi `docs/` = 13.

- [ ] **Step 3: Sửa câu Phụ lục A.1** thành: "Toàn bộ 344 phép kiểm thử trong 28 module đã chạy được trên môi trường này (343 pass, 1 bỏ qua; mục 5.4 của Chương 5)."

- [ ] **Step 4: Sửa docstring `scripts/report_appendix_b.py`**: thay câu ghi "334 phép kiểm thử trong 26 module" bằng câu đọc số tại thời điểm chạy.

- [ ] **Step 5: Đồng bộ số ở năm tệp còn lại**: `report/05_ket_qua_test_va_trien_khai.md` (bullet ghi chú kỹ thuật mục 5.4: 341→344, 27→28 module, 340→343 pass), `report/09_tom_tat_abstract.md` (ba chỗ: bản tiếng Việt, bản English, dòng ghi nguồn), `docs/report_standards.md` mục 3.3, `report/README.md` (mọi chỗ ghi 341/27/340 pass — tìm bằng grep). Con số: 344 phép trong 28 module, 343 pass và 1 bỏ qua. Thân bài Chương 5 đã ghi 344/28 từ Task 6, chỉ bỏ sót ghi chú.

- [ ] **Step 6: Sinh lại mục lục**

Run: `.\.venv\Scripts\python.exe scripts\report_frontmatter.py`
Expected: in ra "32 bang, 4 hinh"; `git diff report/00c_muc_luc_va_danh_muc.md` không thay đổi.

- [ ] **Step 7: Quét số cũ**

Run: grep "334\|337\|341\|340 pass\|27 module" trong `report\` và `docs\` (trừ `docs/superpowers/` là nhật ký lịch sử).
Expected: không còn kết quả ngoài nhật ký lịch sử.

- [ ] **Step 8: Chạy toàn bộ kiểm thử**

Run: `.\.venv-demo\Scripts\python.exe -m pytest -q`
Expected: 343 passed, 1 skipped.

Run: `.\.venv-demo\Scripts\python.exe -m pytest --collect-only -q`
Expected: "344 tests collected".

- [ ] **Step 9: Commit** — thông điệp: "report: sync test counts to 344/28 and regenerate appendix B".

### Task 9: Xác minh cuối, mở PR (không merge)

**Files:**
- Modify: `docs/superpowers/tasks/2026-11-12-sua-review-senior.md` (chốt trạng thái)

- [ ] **Step 1: Viết và chạy bộ đối chiếu tổng hợp** (script tạm ngoài kho) kiểm các điều kiện trong spec §6.2, tối thiểu: không còn "từ 1 đến 4"/"tác giả ký"/mã nội bộ ở Ch1; Bảng 1.1 dòng RQ3 đủ hai phép so; mục 5.5.4 ghi "lượt đầu"; cổng tên tệp; dòng [7] giống nhau hai tệp; Bảng 4.4 có cột Mooney với ba ô; không còn dấu gạch dài ở 5.5.4 và ghi chú Ch6; 344/28 nhất quán sáu vị trí; ba hàng rào pass trên cả hai môi trường.
Expected: TẤT CẢ PASS.

- [ ] **Step 2: Kiểm tra idempotent của hai script sinh**: chạy lại `scripts/report_appendix_b.py` (trên `.venv-demo`) và `scripts/report_frontmatter.py`, `git diff` đối với hai tệp trong `report/` không đổi.

- [ ] **Step 3: Kiểm tra cây làm việc**: `git status --short` không có `results/report_rq*/bootstrap_config.json` trong danh sách staged; nhánh `report/sua-review-senior` tạo từ `main`.

- [ ] **Step 4: Đẩy nhánh và mở PR**

```bash
git push -u origin report/sua-review-senior
gh pr create --base main --head report/sua-review-senior --title "report: resolve senior review cross-chapter inconsistencies" --body-file <file>
```

Thân PR ghi: các điểm đã sửa (N1–N10, N13, 15 điểm nhỏ, 6 lỗi ghi chú), ba hàng rào mới, số liệu mới tính từ CSV, số kiểm thử đồng bộ, và ghi rõ "không đổi môi trường, không đổi `requirements.txt`". **Không chạy `gh pr merge`** — người dùng tự merge.

- [ ] **Step 5: Chốt nhật ký công việc**: đánh dấu toàn bộ task hoàn thành, ghi kết quả xác minh (số pass, số collect) vào `docs/superpowers/tasks/2026-11-12-sua-review-senior.md` và commit nốt.
