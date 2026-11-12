# Mục 1–4: Trang bìa, lời cảm ơn và lời cam đoan

Bốn mục đầu của phần mở đầu quyển, đánh số La Mã (i–iv). Khi dựng bản Word, mỗi mục là một
trang riêng; bìa không đánh số trang, các trang còn lại đánh số i, ii, iii… theo
[`docs/report_standards.md`](../docs/report_standards.md) mục 2.4.

## 1. Trang bìa chính

**Bố cục.** Chèn khung viền [`report/figures/khung_trang_bia.png`](figures/khung_trang_bia.png)
(khung đôi + hoa văn bốn góc, sinh bởi `scripts/make_cover_border.py`) phủ toàn trang, xếp lớp
"Behind Text". Nội dung căn giữa theo thứ tự dưới đây; phông Times New Roman; cỡ chữ 13–14 pt
trừ phần tên đề tài 16 pt in đậm.

Khối 1 — thông tin trường (căn giữa, in đậm):

> **TRƯỜNG ĐẠI HỌC KỸ THUẬT – CÔNG NGHỆ CẦN THƠ (CTUT)**
> **KHOA CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG**

Khối 2 — logo chính thức của trường, cân giữa, chiều rộng khoảng 3,5 cm (tệp logo do sinh viên
chèn từ nguồn của trường; kho mã nguồn không lưu logo).

Khối 3 — đầu đề (căn giữa, in hoa đậm):

> **BÁO CÁO BÀI TẬP LỚN**
> **ĐỒ ÁN MÔN HỌC MÁY**

Khối 4 — đề tài:

> **ĐỀ TÀI:**
> **PHÂN LOẠI ẢNH X-QUANG LỒNG NGỰC BẰNG HỌC MÁY CỔ ĐIỂN VÀ ĐÁNH GIÁ NGUY CƠ SHORTCUT LEARNING TRÊN BỘ DỮ LIỆU COVID-19 RADIOGRAPHY**

Khối 5 — giảng viên hướng dẫn và sinh viên thực hiện (căn giữa):

> **GVHD: TS. Lê Anh Nhã Uyên**
>
> **SV Thực hiện:**
> Trần Nguyễn Đức (Nhóm trưởng) — KHMT2411011
> Lê Hải Lý — KHMT2411021
> Phạm Lê Minh — KHMT2411003
> Nguyễn Vũ Thương — KHMT2411022
> Nguyễn Trần Minh Thuận — KHMT2411014
> Hàng Thái Tú — KHMT2411046
>
> **LỚP: Khoa học máy tính 2024 — NHÓM: 10**

Khối 6 — địa danh và thời gian (căn giữa):

> **Cần Thơ – Tháng 11/2026**

Học kỳ và năm học ghi trong phần phụ bìa và ở trang bìa phụ: Học kỳ 1, năm học 2026–2027.

## 2. Trang bìa phụ

Trang đầu của phần mở đầu sau trang bìa chính; nội dung căn giữa, cùng khung viền với bìa chính:

> **BÁO CÁO BÀI TẬP LỚN – MÔN HỌC MÁY**
> **PHÂN LOẠI ẢNH X-QUANG LỒNG NGỰC BẰNG HỌC MÁY CỔ ĐIỂN VÀ ĐÁNH GIÁ NGUY CƠ SHORTCUT LEARNING TRÊN BỘ DỮ LIỆU COVID-19 RADIOGRAPHY**
>
> **Môn:** Học máy — Học kỳ 1, năm học 2026–2027
> **Lớp:** Khoa học máy tính 2024 — **Nhóm:** 10
> **GVHD:** TS. Lê Anh Nhã Uyên
>
> **SV Thực hiện:**
> Trần Nguyễn Đức (Nhóm trưởng) — KHMT2411011
> Lê Hải Lý — KHMT2411021
> Phạm Lê Minh — KHMT2411003
> Nguyễn Vũ Thương — KHMT2411022
> Nguyễn Trần Minh Thuận — KHMT2411014
> Hàng Thái Tú — KHMT2411046

## 3. Lời cảm ơn

Chúng em xin gửi lời cảm ơn đến TS. Lê Anh Nhã Uyên, giảng viên hướng dẫn môn Học máy, đã góp ý
về phạm vi đề tài, yêu cầu đóng băng siêu tham số trước khi chạy và cách viết báo cáo kèm bằng
chứng; các ý kiến đó chi phối toàn bộ cách tổ chức thực nghiệm của nhóm, từ bước phân chia dữ
liệu đến lần đo duy nhất trên tập test. Chúng em cảm ơn Khoa Công nghệ Thông tin và Truyền thông
đã tạo điều kiện về thời gian và cơ sở học tập trong suốt học kỳ.

Đề tài dựa trên bộ dữ liệu COVID-19 Radiography Database do Chowdhury và cộng sự cùng Rahman và
cộng sự tập hợp và công bố công khai cho mục đích học thuật; phần lớp Normal và Viral Pneumonia
có nguồn từ bộ Kaggle của Paul Mooney. Các công cụ dùng trong đề tài là thư viện nguồn mở của
cộng đồng, chủ yếu là scikit-learn, cùng tài liệu về scikit-learn, Streamlit và Hugging Face Hub
đã nêu trong danh mục tài liệu tham khảo. Cuối cùng, chúng em cảm ơn sáu thành viên trong nhóm
đã phân công rõ nhiệm vụ và duyệt chéo lẫn nhau trong suốt quá trình thực hiện.

## 4. Lời cam đoan

Chúng em — sáu thành viên của Nhóm 10, lớp Khoa học máy tính 2024 — cam đoan về báo cáo này
như sau:

1. Toàn bộ số liệu trong báo cáo được trích từ tệp kết quả và biên bản trong kho mã nguồn của
   đề tài; mỗi bảng đều ghi rõ tệp nguồn trong phần ghi chú kỹ thuật của chương tương ứng.
2. Các trích dẫn tài liệu được ghi đúng nguồn; chưa có công trình nào bị nêu sai hoặc mô tả
   vượt quá nội dung của nó.
3. Báo cáo không sao chép từ công trình của người khác; các đoạn mô tả kết quả do nhóm tự viết
   trên số liệu tự chạy.
4. Số liệu trên tập test chỉ được tính một lần, trong lần mở khóa duy nhất đã ghi trong bản ghi
   mở khóa của đề tài; các quyết định chọn mô hình chỉ dùng tập validation.
5. Mọi phân tích mang tính suy diễn đều được ghi nhãn là giả thuyết chưa kiểm chứng; chênh lệch
   giữa kết quả validation và test được nêu như quan sát, không nêu nguyên nhân.
6. Ứng dụng kèm theo là sản phẩm học thuật, không phải thiết bị y tế và không được dùng để
   chẩn đoán hay đưa ra quyết định điều trị.

Bản Word khi nộp sẽ có chữ ký của từng thành viên tại mục này; bản trong kho để chỗ ký.

## Ghi chú kỹ thuật

- Nguồn tên và MSSV: thông tin do nhóm trưởng cung cấp (khớp [`docs/OWNERS.md`](../docs/OWNERS.md));
  vai trò "Nhóm trưởng" lấy từ cột trách nhiệm của TV1 trong tệp đó.
- Thông tin bắt buộc trên bìa theo [`docs/report_standards.md`](../docs/report_standards.md) mục
  3.1: tên trường, khoa, đầu đề, đề tài, giảng viên hướng dẫn, danh sách sinh viên kèm MSSV, lớp,
  nhóm, địa danh và thời gian. Logo trường không nằm trong kho nên bước dựng Word chèn từ nguồn
  chính thức của trường.
- Khung viền: [`report/figures/khung_trang_bia.png`](figures/khung_trang_bia.png), khổ A4
  (2.480 × 3.508 px, 300 DPI), sinh bởi `python scripts/make_cover_border.py`.
- Lời cảm ơn và lời cam đoan viết mới cho quyển này; các cam kết ở mục 4 là diễn giải lại quy
  trình đã ghi trong biên bản của đề tài (phân chia tập, mở khóa một lần, quy tắc D4), không bổ
  sung thông tin mới.
