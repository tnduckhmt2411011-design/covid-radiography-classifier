# Nhóm 2: Phần cuối quyển (12/11/2026)

Nhánh `report/phu-luc` (từ main sau khi merge PR #60 = 500aac5).

## Nội dung

1. `report/07_tai_lieu_tham_khao.md` — danh mục gộp `[1]`–`[8]`: sáu tài liệu từ Chương 1, hai tài liệu từ Chương 5; chép nguyên văn (đã bắt hai lỗi chép: "S. M. Zughaier" bị đảo thành "M. S.", "E. K. Oermann" bị rút thành "E."). Ghi chú kỹ thuật ghi quy tắc đánh số, thứ tự xuất hiện, lý do bỏ `van der Walt` (không còn trích dẫn trong 6 chương) và hai footnote không đánh số.
2. `report/08_phu_luc_a_c.md`:
   - **Phụ lục A** (môi trường Python 3.12, artifact 7.842.399 byte/SHA-256 `3e14bd…`, bảng biến môi trường, chạy cục bộ + Streamlit Cloud, cổng tương đương 200 ảnh val khớp 200/200, kiểm thử 21+22 phép, giới hạn an toàn).
   - **Phụ lục B** (B.1 cấu trúc kho đếm bằng `git ls-files`; B.2 danh sách 26 module kiểm thử, tổng 334 phép — sinh bởi `scripts/report_appendix_b.py`, đã sửa script đếm theo `pytest --collect-only` thay vì `def test_` để khớp số 334 của Chương 5).
   - **Phụ lục C** (C.1 lưới siêu tham số đọc từ `PARAM_GRIDS`; C.2 tham số chọn + Macro-F1/CI đối chiếu `results/rq2_classifier_selection_record.md`; C.3 thứ hạng chi phí đối chiếu `results/rq2_cost_rank_record.md`).
3. `report/README.md`: mục "Phần cuối (4 mục)" ghi rõ liên kết hai tệp mới và nguồn (thêm `src/rq2_runner.py` cho Phụ lục C); mục 5 trạng thái chuyển tài liệu tham khảo + Phụ lục A–C sang "đã viết", chỉ còn lại phần mở đầu quyển + MSSV.
4. `docs/report_standards.md` mục 3.3: "(275 tests passed)" → "334 phép kiểm thử trong 26 module (đếm tại thời điểm nộp)".

## Kiểm chứng

Script `C:\Users\LENOVO\AppData\Local\Temp\opencode\check_group2.py` (tra repo): đối chiếu nguyên văn 8 mục tài liệu tham khảo, mọi số Phụ lục A/B/C với `rq2_classifier_selection_record.md`, `rq2_cost_rank_record.md`, `git ls-files`, đầu ra `pytest --collect-only`, README và standards → TAT CA PASS.

## Lưu ý kế thừa

- Số bộ kiểm thử trong Phụ lục B (334/26) đã khớp Chương 5 sau PR #60; nếu thêm test mới, chạy lại `scripts/report_appendix_b.py` và cập nhật cả ba nơi (Chương 5, README, Phụ lục B).
