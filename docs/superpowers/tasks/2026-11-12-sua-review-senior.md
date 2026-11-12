# Nhật ký công việc: sửa các điểm review senior (12/11/2026)

Kế hoạch: `docs/superpowers/plans/2026-11-12-sua-review-senior.md`
Spec: `docs/superpowers/specs/2026-11-12-sua-review-senior-design.md`
Nhánh: `report/sua-review-senior` (tạo từ `main` `3be1e1f`). Người dùng tự merge PR.

## Trạng thái

- [x] Task 1: Hàng rào kiểm thử (đỏ trước khi sửa) — `tests/test_report_consistency.py`, 3 phép, RED đã xem trên cả hai môi trường.
- [x] Task 2: Sửa Chương 1 (E1.1–E1.14) — `443cc02`
- [x] Task 3: Sửa Chương 2 (E2.1–E2.16) — `f732dc5`, hàng rào chuyển xanh.
- [x] Task 4: Sửa Chương 3 (E3.1–E3.3) — `10980d6`
- [x] Task 5: Sửa Chương 4 (E4.1–E4.6) — `f72e9f3`; số Mooney tính lại từ CSV khớp (7/5/6 và 0/0/0).
- [x] Task 6: Sửa Chương 5 + tệp 07 + roadmap — `f2447d6`
- [x] Task 7: Sửa Chương 6 (E6.1–E6.5) — `3071973`
- [x] Task 8: Đồng bộ 344/28, sinh lại Phụ lục B và mục lục — `6987eda`
- [x] Task 9: Xác minh cuối, mở PR (không merge)

## Kết quả xác minh

- Đối chiếu tổng hợp từng điểm senior: TẤT CẢ PASS (49 tiêu chí).
- `pytest -q` trên tập 28 module đã track (`.venv-demo`): 343 passed, 1 skipped; collect: 344.
- Hai script sinh idempotent (mục lục không đổi khi chạy lại).
- Không stage `results/report_rq*/bootstrap_config.json`.

## Quyết định đáng ghi (rulings)

1. **Số bộ kiểm thử đếm theo nội dung đã track:** tệp `tests/test_slides_data.py` (untracked, thuộc luồng `slides/` chưa track) làm `pytest` thu thập 352 thay vì 344. Spec và báo cáo phản ánh kho mã nguồn, nên `scripts/report_appendix_b.py` và hai hàng rào (B.2, A↔Ch5) chuyển sang đọc `git ls-files tests/test_*.py`. Không đụng tệp của người dùng. Hệ quả nếu chọn sai: báo cáo ghi số chỉ đúng trên máy có rác trong cây làm việc.
2. **Dòng "Tổng cộng" của Bảng B.2 giữ tiếng Việt** ("Tổng cộng", không phải "Tong cong" từ đầu ra ASCII) vì hàng rào B.2 nhận diện hàng tổng bằng chuỗi có dấu.
3. **Đồng bộ số 344/28 của Chương 5 làm ở Task 6** thay vì Task 8 để không sửa một câu hai lần.
