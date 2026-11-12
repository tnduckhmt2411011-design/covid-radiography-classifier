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
