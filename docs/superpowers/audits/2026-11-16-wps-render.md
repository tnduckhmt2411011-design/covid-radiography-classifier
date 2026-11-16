# Kiểm tra dựng trang `.docx` bằng WPS Office (16/11/2026)

- **Công cụ xuất PDF:** WPS Office Writer `12.1.0.29162` (COM `KWps.Application`), đọc PDF và dựng ảnh PNG 150 DPI bằng PyMuPDF (`fitz`).
- **Ghi chú tương thích:** Kết quả dưới đây phản ánh cách dàn trang của WPS Office; một số điểm co giãn bảng tự động (`autofit`) và cập nhật trường động có thể khác nhẹ khi mở bằng Microsoft Word (được đánh dấu **"chưa kết luận"** ở nơi phụ thuộc trình xem).

---

## Nền trước khi sửa (Task 1 — commit `b73205c`, 404.795 bytes)

- **Tệp PDF xuất thử:** 63 trang (`2.281.681` bytes), xuất thành công không lỗi hay hộp thoại.
- **Thông số vị trí trọng yếu:**
  - `P01` (Bìa chính, không số trang): **1 trang**.
  - `P02` (Bìa phụ, không số trang): **1 trang**.
  - `P03–P04` (`i–ii`): Lời cảm ơn (`P03`), Lời cam đoan (`P04`), mỗi mục 1 trang.
  - `P05` (`iii`): **TÓM TẮT** — nằm trọn **1 trang** (`P05`→`P05`).
  - `P06` (`iv`): **ABSTRACT** — nằm trọn **1 trang** (`P06`→`P06`).
  - `P07–P12` (`v–x`): Mục lục (`P07`), Danh mục ký hiệu (`P08–P10`), Danh mục bảng biểu (`P11`), Danh mục hình ảnh (`P12`).
  - `P13` (trang Ả Rập `1`): Chương 1 bắt đầu đúng quy chuẩn.
  - `P19` (tr. 7), `P31` (tr. 19), `P38` (tr. 26), `P44` (tr. 32): `Hình 2.1`, `3.1`, `4.1`, `5.1` căn giữa, sắc nét, chú thích nằm ngay dưới hình, không tràn lề.
  - `P21` (tr. 9): Công thức `(2.1)` dựng bằng phân số căn giữa, nhãn `(2.1)` sát lề phải.
  - `P34–P35` (tr. 22–23): Bảng ánh xạ kịch bản Chương 4 (sẽ chuyển thành danh sách ở Task 2) hiện bị tách giữa dòng 4 và dòng 5; Bảng 4.1 (`P35`) và Bảng 4.2 (`P35–P36`) vừa khổ ngang (`max_x ≤ 19,15 cm`), không bị cắt chữ.
  - `P48` (tr. 36): Bảng 6.1 nằm gọn trong 1 trang kèm chú thích và 2 đoạn thảo luận.
  - `P58–P63` (tr. 46–51): Phụ lục A (`P56–P58`), Phụ lục B (`P58–P61`), Phụ lục C (`P61–P63`).

### Phát hiện từ bản dựng nền

1. **[Lỗi builder — ngoài Tasks 2–5 -> Thêm Task W1] Chữ đầu trang bìa chính (`P01`) và bìa phụ (`P02`) đè lên họa tiết khung viền và bị lệch tâm 0,5 cm:**
   - Đo thực tế trên `report/figures/khung_trang_bia.png` (`2480 × 3508` px): đường khung trong cách mép giấy `1,94 cm`, nhưng chùm hoa góc trên/dưới vươn vào tới `x = 4,47 cm` ở dải `y = [2,0; 2,5] cm` và `x = 4,22 cm` ở `y = [3,0; 3,5] cm` (chỉ thoáng từ `y ≥ 3,5..4,0 cm` với `x ≥ 3,5 cm`).
   - Do Section 0 dùng lề trái `3,0 cm` / phải `2,0 cm` và đỉnh chữ bắt đầu ở `y = 1,94 cm` (`x = [3,12; 18,87] cm`), hai dòng đầu bìa chính (`TRƯỜNG ĐẠI HỌC...`, `KHOA...`) và bìa phụ (`BÁO CÁO...`, `PHÂN LOẠI...`) đè thẳng lên chùm hoa ở cả hai góc trên, đồng thời vùng căn giữa bị lệch `0,5 cm` sang phải so với khung đối xứng của tờ giấy A4.
2. **[Lỗi builder — ngoài Tasks 2–5 -> Thêm Task W2] Tiêu đề cột `Bảng B.2` đứng trơ ở đáy trang (`P59`, tr. 47):**
   - Trong `scripts/build_report_docx.py` (`_render_table`), `Caption Table` đã bật `keep_with_next = True` nên dính với hàng tiêu đề (`row 0`), nhưng các đoạn trong `row 0` chưa bật `keep_with_next = True`, khiến tiêu đề bảng `Module | Số phép kiểm thử` đứng một mình ở đáy trang `P59` còn dòng dữ liệu đầu tiên sang trang `P60`.
3. **[Khác biệt trình xem — chưa kết luận] Trường động Mục lục / Danh mục (`P07`, `P11`, `P12`):**
   - Khi xuất PDF qua COM ở chế độ đọc (`ReadOnly=True`), WPS giữ nguyên chuỗi giữ chỗ `(Mở bằng Word, nhấn Ctrl+A rồi F9...)` do chưa kích hoạt cập nhật trường tự động; hành vi `Ctrl+A` → `F9` trong Word cần kiểm trực tiếp bằng Microsoft Word trước khi nộp.
4. **[Khác biệt trình xem — chưa kết luận] Ngắt dòng trong cột hẹp (`P35` Bảng 4.1, `P62` Bảng C.2):**
   - Cột `95% CI` của Bảng 4.1 và Bảng C.2 xuống dòng tại `[0,8909;` / `0,9129]` (không mất chữ); độ rộng cột thực tế do Word tính từ `table.autofit = True` có thể hơi khác WPS.

### Task bổ sung phát sinh từ kiểm tra WPS

- **Task W1 (sửa builder cho bìa — TDD trước Task 5 hoặc ghép cùng Task 5):** Căn vùng chữ trong `add_cover` vào lòng trắng đối xứng của khung viền bằng `left_indent = Cm(0.5)`, `right_indent = Cm(1.5)` (dải `x = [3,5; 17,5] cm` đối xứng giữa trang A4) và đẩy lề đỉnh khối đầu tiên thêm khoảng trống trên (`space_before` ở đoạn mở đầu của bìa chính và bìa phụ) để không đè hoa góc trên mà vẫn giữ mỗi bìa gọn 1 trang.
- **Task W2 (sửa builder cho tiêu đề bảng — TDD):** Trong `_render_table`, đặt `p.paragraph_format.keep_with_next = True` cho tất cả đoạn thuộc hàng tiêu đề (`row 0`) khi bảng có ít nhất 2 hàng để ngăn tiêu đề bảng đứng trơ ở cuối trang như `Bảng B.2` tại `P59`.

---

## Sau khi sửa (Task 6 — `report/dist/BaoCao_BTL_HocMay_Nhom10.docx`, `536.818` bytes)

- **Tệp PDF xuất lại qua WPS Office:** `63` trang (`2.409.084` bytes), xuất sạch không lỗi hay hộp thoại.
- **Đối chiếu từng hạng mục sau sửa:**
  - **Bìa chính (`P01`):** **1 trang** (`y = [4,27; 26,38] cm`, `x = [3,00; 18,02] cm`); logo CTUT (`slides/assets/logo_ctut.png`, rộng `3,0 cm`) hiển thị sắc nét ngay dưới tên khoa; chữ căn giữa cân đối trong khung viền, không còn điểm nào chạm họa tiết hoa góc trên/dưới.
  - **Bìa phụ (`P02`):** **1 trang** (`y = [4,19; 20,53] cm`, `x = [3,37; 17,63] cm`); nhờ dòng đệm cố định `line_spacing = 64 pt` đầu trang 2 (tránh bị Word/WPS bỏ `space_before` ngay sau `w:br`), toàn bộ tiêu đề bìa phụ nằm hoàn toàn trong lòng trắng khung viền.
  - **TÓM TẮT (`P05`, `iii`) và ABSTRACT (`P06`, `iv`):** mỗi bản nằm trọn **1 trang**.
  - **Công thức `(2.1)` (`P21`, tr. 9):** phân số hiển thị căn giữa kèm số `(2.1)` sát lề phải.
  - **Chương 4 (`P34–P35`, tr. 22–23):** bảng ánh xạ 5 kịch bản đã chuyển thành danh sách gạch đầu dòng gọn trên trang `P34`; Bảng 4.1 (`P35`) và Bảng 4.2 không bị cắt ngang (`max_x ≤ 19,00 cm`).
  - **Bảng 6.1 (`P48`, tr. 36) và Phụ lục (`P56–P63`, tr. 44–51):** mã và bảng `Bảng A.1` (kể cả chuỗi SHA-256 dài 64 ký tự) hiển thị bằng `Times New Roman`, vừa gọn một dòng trong cột `Giá trị`; **`Bảng B.2` (`P59`, tr. 47) đã giữ hàng tiêu đề đi cùng hai hàng dữ liệu đầu**, hết tình trạng tiêu đề đứng trơ ở đáy trang.
  - **Mục lục / Danh mục bảng / Danh mục hình (`P07`, `P11`, `P12`):** vẫn cần mở bằng Word (hoặc WPS Writer) và cập nhật trường (`Ctrl+A` → `F9`) để điền số trang thật; hành vi trường động này vẫn là **"chưa kết luận"** trên Microsoft Word cho tới khi bạn mở và nhấn `F9` trước lúc in.
  - **Độ xuống dòng cột hẹp (`Bảng 4.1`, `Bảng C.2`):** cột `95% CI` xuống 2 dòng tại dấu `;`, không mất chữ (`chưa kết luận` so với autofit trên Microsoft Word).
