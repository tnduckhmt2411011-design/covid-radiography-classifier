# Nhóm 4: Tóm tắt tiếng Việt và Abstract (12/11/2026)

Nhánh `report/tom-tat` từ main `102b29c` (sau khi PR #61, #62 merge). Đây là nhóm cuối của kế hoạch 4 nhóm.

## Nội dung

- `report/09_tom_tat_abstract.md` (mới): tóm tắt tiếng Việt và Abstract tiếng Anh, mỗi bản không quá một trang theo `docs/report_standards.md` mục 3.1 (bối cảnh, phương pháp, kết quả test, kết luận).
  - Tóm tắt tiếng Việt ~340 từ; Abstract ~350 từ. Không đưa số liệu nào ngoài bảng đã có ở Chương 3–6; Ghi chú kỹ thuật liệt kê nguồn từng nhóm số (Bảng 3.1/3.2/3.3, 4.1/4.4, 5.1, mục 5.4, mục 6.2).
  - Quy ước định dạng số: bản tiếng Việt giữ dấu phẩy thập phân; bản tiếng Anh dùng dấu chấm thập phân theo thông lệ quốc tế — ghi rõ trong Ghi chú kỹ thuật.
  - Giữ nguyên quy tắc D4: chênh val–test nêu như số đo, không nêu nguyên nhân; kết luận RQ3 là "chưa xác định được đặc điểm" chứ không khẳng định học lối tắt.
- `report/README.md`: mục "Phần mở đầu" hàng 5 ghi liên kết tệp và yêu cầu một trang; đây là mục cuối cùng trong danh sách còn thiếu → quyển đã đủ 50 mục.
- `docs/superpowers/tasks/2026-11-12-nhom4-tom-tat-abstract.md` (tệp này).

## Kiểm chứng

Script `C:\Users\LENOVO\AppData\Local\Temp\opencode\check_group4.py`: 56 mục PASS — gồm (1) mỗi con số trong hai phần phải xuất hiện trong chương nguồn tương ứng; (2) quét toàn bộ chuỗi số trong hai phần, không còn số nào không truy về được; (3) độ dài mỗi bản ≤ một trang (VI 340, EN ~350 từ theo ngưỡng tự đặt); (4) không có cụm AI-slop theo `docs/academic_writing_guide.md`; (5) đủ bốn thành phần bắt buộc của tóm tắt.

## Ghi chú quản trị

Ruleset "Protect main branch" (id 24117045) đã được đổi theo yêu cầu: chỉ còn hai quy tắc `deletion` và `non_fast_forward`, bỏ quy tắc `pull_request` (yêu cầu 1 approving review). Các PR sau này merge không cần duyệt. Muốn bật lại: Settings → Rules → Rulesets → "Protect main branch" → thêm rule "Require pull request before merging" (có thể đặt số phê duyệt tối thiểu).
