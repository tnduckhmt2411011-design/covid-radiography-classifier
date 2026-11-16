# Nhiệm vụ: nâng sàn cỡ chữ slide S6-03 lên 18 pt

Ngày: 12–13/11/2026 · Nhánh: `slides/s6-03-deck-bao-ve`

Căn cứ: 8 nguồn đã đọc bằng trình duyệt (PLOS CB, MIT CommKit, Penn State, Minnesota,
ODU, WUSTL, ĐH Văn Hiến, Bách khoa Hà Nội). Chữ trên slide trình chiếu trong phòng
nên ≥ 18–24 pt; ĐH Văn Hiến quy định tiêu đề 44 pt, nội dung 32 pt. Bộ slide đang
dùng sàn 14,25 pt kế thừa từ quy chuẩn văn bản .docx của báo cáo.

- [x] **1.** Đổi hằng cỡ chữ trong `slides/svgkit.py`: kicker 19→24 px, body 21→28,
      strong 22→28, small 19→24, line_h mặc định 26→30.
- [x] **2.** Thay mọi cỡ chữ ghi tay trong `slides_act1/2/3/backup.py` (19→24, 21→28,
      22→28, 20→24, 26→30), giữ nguyên chữ số lớn và chân trang.
- [x] **3.** Sửa `slides/audit.py`: sàn body 14 pt → 18 pt, chỉ miễn chân trang và số trang.
- [x] **4.** Dựng lại, sửa hết lỗi tràn khung do chữ to hơn (cả hai cổng phải đạt).
      Viết lại bố cục 16 trang: 1, 2, 3, 4, 5, 6, 8, 9, 16, 18, 20, 22, 24, 25, 26, 27
      và B1, B4, B5, B6. Sửa thêm ba lỗi chồng chữ trong thẻ do chữ to hơn: slide 9
      (thẻ giao thức đo), slide 20 (số lớn đè chú thích và CI đè cột thứ ba), slide 34
      (nhãn độ trễ đè lên giá trị).
- [x] **5.** Tăng cỡ chữ trong 8 biểu đồ (`slides/figures.py`): sinh PNG đúng kích thước
      ô ghép (1:1, không co), cỡ chữ tối thiểu 9,5 pt matplotlib ≥ 19,7 pt hiệu dụng;
      nới lề trái cho nhãn trục, rút gọn dòng chú thích cho vừa chiều rộng.
- [x] **6.** Xuất lại PPTX/PDF, vẽ lại 34 PNG, duyệt bằng mắt toàn bộ 34 trang.
- [x] **7.** Cập nhật `slides/README.md` (ghi rõ sàn 18 pt và căn cứ), commit.

## Ghi chú kỹ thuật cho lần sau

- Mô hình biên chữ dùng khi bố cục: đáy = baseline + 0,42·cỡ chữ + (số dòng − 1)·bề dòng;
  đỉnh = baseline − 0,88·cỡ chữ. Các khối cùng cột phải cách nhau theo công thức đó,
  không chỉ căn theo mắt.
- Chữ trong hình PNG ghép vào SVG theo đúng ô ghép: nếu tỷ lệ ô khác tỷ lệ ảnh,
  `preserveAspectRatio` co ảnh lại và cỡ chữ hiệu dụng tắt theo hệ số co. Phải giữ
  ô ghép đúng tỷ lệ ảnh (hoặc đo tỷ lệ ảnh rồi tự tính ô).
- Các cổng không phát hiện chữ đè lên chữ trong cùng một vùng: các lỗi kiểu này
  (slide 9, 20, 34) chỉ lộ ra khi duyệt PNG từng trang.

## Vòng rà soát từng điểm ảnh (13–14/11/2026)

Cùng nhánh, sau khi nâng sàn cỡ chữ; mục tiêu là soát từng trang ở mức điểm ảnh
chứ không chỉ dựa vào khung vùng.

- [x] **1.** Dựng lại 34 SVG, chạy lại `svg_quality_checker` (final,
  `--quick-generate --canonical-authoring`): 0 lỗi chặn, 0% lỗi.
- [x] **2.** Viết kiểm tra khe mực bằng PIL (`segoeui.ttf`/`seguibl.ttf`): hộp
  mực thật của từng dòng, cờ khe < 6 px giữa hai khối khác nhau và chữ cách mép
  thẻ < 3 px. Sửa hết: 0 lỗi.
- [x] **3.** Sửa bố cục theo kết quả đo: bề dòng tiêu đề 45→50 px; ngắt tiêu đề
  tường minh ở slide 3, 12, 21; slide 3 (thanh/số), 8 (ba mũi tên vector, ô
  trạm 1), 11 (nhãn trùng), 12 (chú thích CI), 13 (tiêu đề theo dữ liệu), 15
  (thứ tự số trước quy ước), 17 (dumbbell), 22 (nhãn trục ngắn), 23 (canh giữa
  ảnh chụp), 27 (`ngoài phổi − gốc`), cùng B1–B6.
- [x] **4.** Sửa hình: nền trắng, chừa 118 px đáy cho nhãn trục, dấu trừ
  Unicode, `fig_test_gap` thành forest plot, `fig_brightness` bỏ chú thích trong
  hình, `fig_rq3_scenarios` in B0/A0.
- [x] **5.** Kiểm thẻ (đáy ≤ 622 px, trong khung 82..1198 / 197..720): 0 lỗi;
  kiểm thanh: 0 lỗi; kiểm widow: còn 2 dòng đã chấp nhận (đường dẫn nguồn kết
  thúc bằng `/`; nhãn `GLCM +`/`LBP` ngắt ở toán tử).
- [x] **6.** Xuất lại PPTX/PDF/34 PNG, duyệt lại toàn bộ 34 trang; postflight
  `passed-with-warnings`, 45 cảnh báo không chặn.
- [x] **7.** Ghi lại phương pháp và danh sách sửa vào `slides/README.md`, cập nhật
  handoff, commit.

## Ghi chú kỹ thuật bổ sung

- PIL `getbbox` trả tọa độ tính từ đỉnh ascender: `ink = y + b/4 − ascent/4`;
  công thức cũ `− size` báo thiếu ~2 px và che mất va chạm.
- `data-pptx-bounds` hẹp hơn mực chữ Việt thật; chấp nhận vượt 1–3 px (cổng
  ppt-master cho phép 5%).
