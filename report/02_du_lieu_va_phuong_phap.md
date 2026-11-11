# CHƯƠNG 2. DỮ LIỆU VÀ PHƯƠNG PHÁP NGHIÊN CỨU

## 2.2. Phân tích khám phá dữ liệu và nguy cơ học lối tắt từ độ sáng và metadata tệp

Với một bộ dữ liệu ghép từ nhiều nguồn, độ sáng là thuộc tính đầu tiên cần kiểm tra, vì một mô hình có thể nhận ra lớp nhờ nền ảnh sáng hay tối thay vì nhờ tổn thương phổi. Độ sáng được đo bằng trung bình mảng điểm ảnh của tệp gốc trên thang 0–255, tính một lần cho 21.165 ảnh và lưu trong `splits/manifest.csv`; mọi số dưới đây tính từ tệp đó. Bảng 2.1 tổng hợp theo lớp, Hình 2.1 vẽ phân bố đầy đủ.

**Bảng 2.1: Độ sáng trung bình theo lớp (thang 0–255)**

| Lớp | n | Trung bình ± SD | Trung vị | Khoảng tứ phân vị | Nhỏ nhất | AUC so với ba lớp còn lại |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| COVID | 3.616 | 139,5 ± 25,0 | 142,6 | 126,9–156,0 | 25,5 | 0,6585 |
| Lung_Opacity | 6.012 | 126,0 ± 23,6 | 120,8 | 110,6–142,1 | 32,2 | 0,4269 |
| Normal | 10.192 | 129,4 ± 22,4 | 125,5 | 113,5–143,6 | 26,4 | 0,4802 |
| Viral Pneumonia | 1.345 | 125,4 ± 19,0 | 126,9 | 113,5–137,8 | 64,8 | 0,4557 |

**Hình 2.1: Phân bố độ sáng trung bình của bốn lớp**

![Phân bố độ sáng trung bình của bốn lớp](../results/eda/brightness_distribution.png)

Bốn lớp đều có trung vị nằm trong dải 120,8–142,6, nhưng vị trí trong dải không đều. COVID sáng nhất với trung vị 142,6, cao hơn Lung_Opacity 21,8 đơn vị; ba lớp còn lại xếp sát nhau trong khoảng 120,8–126,9. Độ lệch chuẩn 19,0–25,0 và khoảng tứ phân vị rộng 24,3–31,5 đơn vị, tức biến thiên bên trong một lớp cùng cỡ với chênh lệch giữa hai trung vị xa nhất. Đuôi thấp kéo dài xuống 25,5 ở COVID và 26,4 ở Normal, nghĩa là cả lớp có trung vị cao nhất lẫn lớp đông ảnh nhất đều chứa ảnh gần như đen.

Ngoài trung vị, mỗi lớp được tính một giá trị AUC: xác suất một ảnh của lớp đó sáng hơn một ảnh lấy ngẫu nhiên từ ba lớp còn lại. COVID đạt 0,6585, nghĩa là trong hai ảnh chọn ngẫu nhiên, một của COVID và một của lớp khác, ảnh COVID sáng hơn với xác suất khoảng 66%. Ba lớp còn lại có AUC từ 0,4269 đến 0,4802. Giá trị dưới 0,5 chỉ cho biết lớp đó tối hơn phần còn lại, nên mức tách được đo bằng khoảng cách đến 0,5: COVID cách khoảng 0,16, Lung_Opacity 0,07, Viral Pneumonia 0,04 và Normal 0,02. Độ sáng tách COVID ở mức vừa, tách Lung_Opacity yếu, và gần như không tách Normal hay Viral Pneumonia. Vì vậy nó không đủ để giải thích lối tắt cho cả bốn lớp. Trên toàn bộ dữ liệu, 46,5% ảnh nằm trong khoảng tứ phân vị của Normal; nếu bốn phân bố trùng nhau thì tỉ lệ này là 50%, nên mức lệch tổng thể không lớn.

Một dấu vết khác nằm ở metadata của tệp. 140 trong 1.345 ảnh Viral Pneumonia (10,4%) lưu ở hệ màu RGB, ba lớp còn lại không có ảnh RGB nào. Toàn bộ 140 ảnh này có ba kênh bằng nhau (R = G = B), và pipeline ép mọi ảnh về ảnh xám 8-bit trước khi trích đặc trưng, nên giá trị điểm ảnh sau chuyển đổi trùng với ảnh xám; bản thân định dạng tệp không tạo ra khác biệt đặc trưng. Định dạng khác nhau cho thấy nhóm ảnh này không đi qua cùng một bước xuất tệp với phần còn lại của lớp. Dấu hiệu đó chỉ phủ 10,4% lớp Viral Pneumonia, phần còn lại không có gì khác biệt ở metadata, nên nó không đủ để giải thích cả lớp.

Mốc A0 ở mục 1.2 là phép thử trực tiếp cho hai kênh này. Random Forest chỉ dùng độ sáng và cờ is_rgb đạt macro-F1 0,2397 trên validation, cao hơn 0,1627 của mốc đoán toàn bộ Normal nhưng còn xa 0,8599 của nhóm đặc trưng ghép. Độ sáng và định dạng tệp vì thế là mối nghi có thật, đồng thời là kênh yếu: mô hình dùng đặc trưng ảnh vượt hai kênh này rất xa, và phần đóng góp thật của vùng ngoài phổi vẫn phải đo riêng.

Những quan sát trên mới mô tả dữ liệu và một mốc tham chiếu rẻ tiền; chúng chưa cho biết mô hình dùng đặc trưng ảnh có dựa vào các dấu hiệu đó hay không. Việc đo nằm ở RQ3: che vùng phổi hoặc chỉ giữ vùng ngoài phổi rồi so macro-F1 với ảnh gốc. Chương 4 trình bày năm kịch bản của phép đo này.

---

## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)

- **Chương này chưa đủ mục.** Hiện mới có 2.2; các mục 2.1 và 2.3–2.9 theo đề cương trong [`report/README.md`](README.md) sẽ viết tiếp. Số bảng và số hình đánh theo chương nên 2.2 bắt đầu từ Bảng 2.1, Hình 2.1.
- **Tiêu đề mục đã đổi** thành "từ độ sáng và metadata tệp" vì phát hiện về định dạng RGB không nằm trong khái niệm cường độ sáng. Dòng 2.2 trong `report/README.md` đã sửa theo; nếu đổi lại thì phải sửa cả hai chỗ.
- **Nguồn số liệu:** số trong Bảng 2.1 và các số dẫn xuất (AUC, khoảng cách đến 0,5, 46,5%, 140 ảnh RGB) sinh bằng `python -m src.eda_brightness` từ `splits/manifest.csv`, ghi ra `results/eda/brightness_by_class.csv` và `results/eda/brightness_channels.json`. Kiểm thử `tests/test_eda_brightness.py` đối chiếu CSV với manifest. Bảng trong văn bản lấy từ `format_markdown_table` của script rồi dán sang, nên nếu sửa tay một ô thì phải đối chiếu lại CSV; test không bắt được lỗi gõ lại.
- **Định nghĩa độ sáng:** trung bình mảng điểm ảnh của tệp gốc, thang 0–255, do `notebooks/01_download_and_eda.ipynb` cell 3 tính. Manifest ghi cả 21.165 ảnh đều 299 × 299, nên khác biệt độ sáng không đến từ kích thước ảnh.
- **Làm tròn:** độ sáng ghi một chữ số thập phân, AUC ghi bốn. Trung vị và tứ phân vị của COVID rơi đúng mốc ,xx5 (142,595 và 126,885), làm tròn hai chữ số sẽ phụ thuộc quy ước nên bảng cố ý dừng ở một chữ số. Số gốc sáu chữ số nằm trong CSV. Khoảng cách đến 0,5 ghi hai chữ số vì 0,6585 − 0,5 = 0,1585 cũng rơi đúng mốc ,xx5: nếu ghi ba chữ số thì người đọc trừ từ AUC đã làm tròn sẽ không biết là 0,158 hay 0,159. Cột `auc_distance_to_half` trong CSV giữ giá trị chưa làm tròn.
- **AUC:** tính bằng hạng trung bình (Mann–Whitney U) nên xử lý được giá trị đồng hạng. Không dùng p-value vì với n = 21.165, Kruskal–Wallis hầu như luôn bác bỏ giả thuyết không và không cho biết mức tách lớp.
- **Mốc A0:** macro-F1 0,2397 lấy từ `results/a0_shortcut/metrics.json` (khoá `random_forest`); hai đặc trưng `brightness` và `is_rgb` theo `kaggle/baseline/04_baseline.ipynb` cell 3; B0 = 0,1627 theo `results/threshold_v3.md` mục 3; 0,8599 là macro-F1 của nhóm ghép ở RQ1 (`results/report_rq1/r1_summary.csv`).
- **Ảnh RGB:** ghi chú "140 ảnh RGB có R = G = B" đã có trong `results/threshold_v3.md` mục 3; `src/dataset.py` ép `img.convert("L")` trước khi trích đặc trưng.
- **Hình:** `results/eda/brightness_distribution.png` do notebook cell 6 sinh, chưa vẽ lại. Khi chuyển sang Word, chèn ảnh và đặt chú thích Hình 2.1 bên dưới, cỡ 10–11 pt.
- **Chưa đưa vào chương:** không có số liệu tập test; RQ1–RQ3 để Chương 3–4.
