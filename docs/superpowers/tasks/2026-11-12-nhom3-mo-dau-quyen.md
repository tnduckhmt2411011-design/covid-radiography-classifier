# Nhóm 3: Phần mở đầu quyển (12/11/2026)

Nhánh `report/mo-dau-quyen` (tạo từ `report/phu-luc`, tức đã chứa nội dung nhóm 2 — tài liệu tham khảo + Phụ lục A–C của PR #61).

## Nội dung

- `report/00a_trang_bia_va_loi.md` (mới): bìa chính theo chuẩn `docs/report_standards.md` mục 3.1 (CTUT, Khoa CNTT&TT, GVHD TS. Lê Anh Nhã Uyên, đề tài đúng nguyên văn, 6 sinh viên kèm MSSV, LỚP: Khoa học máy tính 2024 — NHÓM: 10, Cần Thơ – Tháng 11/2026); bìa phụ; lời cảm ơn; lời cam đoan (6 điểm, gắn với quy trình đã ghi trong biên bản, không bổ sung thông tin mới).
- `report/00b_danh_muc_ky_hieu.md` (mới): 33 chữ viết tắt + 6 ký hiệu toán học, mỗi dòng đếm thực tế trong thân bài sáu chương và phụ lục. Bẫy đã bắt khi tự kiểm: ký hiệu $\Delta$ tôi định ghi là "hiệu số điểm" nhưng không xuất hiện ở bất kỳ chương nào → đã bỏ; $T$ ghi đúng bối cảnh "T = 0 chốt, T = 4/T = 8 có thử".
- `report/00c_muc_luc_va_danh_muc.md` (mới, sinh tự động): mục lục 9 mục đầu quyển + 37 tiểu mục 6 chương + phần cuối; danh mục 32 bảng; 4 hình (kèm tệp nguồn; Hình 2.1 nằm ở `results/eda/`).
- `scripts/make_cover_border.py` (mới): sinh khung viền A4 2.480 × 3.508 px 300 DPI bằng PIL (khung đôi + hoa văn bốn góc), ra `report/figures/khung_trang_bia.png`. Viết bằng script thay vì sinh bằng image model (image model lỗi hết credit; script cho kết quả lặp lại được).
- `scripts/report_frontmatter.py` (mới): sinh mục lục và hai danh mục từ chính sáu chương + phụ lục; bảng sắp theo số, bỏ hạng mục "Ghi chú kỹ thuật"; chạy lại (idempotent) khi chương thêm mục/bảng.
- `report/README.md`: mục "Phần mở đầu (9 mục)" ghi rõ tệp nào cho từng mục; sửa hàng 3.4 bỏ "và ma trận nhầm lẫn" (khớp tên thật của chương); mục 5 cập nhật trạng thái (đã viết mở đầu trừ tóm tất, MSSV đã đủ).
- `docs/superpowers/tasks/2026-11-12-nhom3-mo-dau-quyen.md` (tệp này).

## Kiểm chứng

Script `C:\Users\LENOVO\AppData\Local\Temp\opencode\check_group3.py`: 25 mục PASS — gồm nguyên văn đề tài/GVHD khớp standards, 6 cặp tên–MSSV khớp ảnh người dùng cung cấp và `docs/OWNERS.md`, ký hiệu chỉ ghi cái có thật, TOC idempotent, 32 bảng/4 hình, khung 2.480 × 3.508 px 300 DPI.
