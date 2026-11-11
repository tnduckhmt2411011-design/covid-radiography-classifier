# CHƯƠNG 2. DỮ LIỆU VÀ PHƯƠNG PHÁP NGHIÊN CỨU

## 2.2. Phân tích khám phá dữ liệu và nguy cơ học lối tắt do chênh lệch cường độ sáng

Với một bộ dữ liệu ghép từ nhiều nguồn, độ sáng là thuộc tính đầu tiên cần kiểm tra, vì một mô hình có thể nhận ra lớp nhờ nền ảnh sáng hay tối thay vì nhờ tổn thương phổi. Với 21.165 ảnh của bộ dữ liệu, độ sáng được đo bằng trung bình mảng điểm ảnh của tệp gốc trên thang 0–255, tính một lần và lưu trong `splits/manifest.csv`; mọi số dưới đây tính từ tệp đó. Bảng 2.1 tổng hợp theo lớp, Hình 2.1 vẽ phân bố đầy đủ.

**Bảng 2.1: Độ sáng trung bình theo lớp (thang 0–255)**

| Lớp | n | Trung bình ± SD | Trung vị | Khoảng tứ phân vị | AUC so với ba lớp còn lại |
| :--- | ---: | ---: | ---: | ---: | ---: |
| COVID | 3.616 | 139,5 ± 25,0 | 142,6 | 126,9–156,0 | 0,6585 |
| Lung_Opacity | 6.012 | 126,0 ± 23,6 | 120,8 | 110,6–142,1 | 0,4269 |
| Normal | 10.192 | 129,4 ± 22,4 | 125,5 | 113,5–143,6 | 0,4802 |
| Viral Pneumonia | 1.345 | 125,4 ± 19,0 | 126,9 | 113,5–137,8 | 0,4557 |

**Hình 2.1: Phân bố độ sáng trung bình của bốn lớp**

![Phân bố độ sáng trung bình của bốn lớp](../results/eda/brightness_distribution.png)

Bốn lớp đều có trung vị nằm trong dải 120,8–142,6, nhưng vị trí trong dải không đều. COVID là lớp sáng nhất, trung vị 142,6, cao hơn Lung_Opacity 21,8 đơn vị; ba lớp còn lại xếp sát nhau trong khoảng 120,8–126,9. Độ lệch chuẩn 19,0–25,0 và khoảng tứ phân vị rộng 24,3–31,5 đơn vị, tức biến thiên trong một lớp cùng cỡ với chênh lệch giữa hai trung vị xa nhất. Đuôi thấp kéo dài xuống 25,5 ở COVID và 26,4 ở Normal, tức vẫn có ảnh gần như đen trong hai lớp sáng nhất. Phân bố vì thế không đồng nhất, nhưng chưa đủ để kết luận lớp nào nhận ra được chỉ từ độ sáng.

Để đo mức tách lớp thay vì chỉ nhìn trung vị, mỗi lớp được tính một giá trị AUC: xác suất một ảnh của lớp đó sáng hơn một ảnh lấy ngẫu nhiên từ ba lớp còn lại. COVID đạt 0,6585, nghĩa là trong hai ảnh chọn ngẫu nhiên, một của COVID và một của lớp khác, ảnh COVID sáng hơn với xác suất khoảng 66%. Ba lớp còn lại nằm trong khoảng 0,4269–0,4802, sát mức 0,5 của một phép đo không phân biệt được gì. Giá trị dưới 0,5 không phải "kém hơn ngẫu nhiên": 0,4269 chỉ cho biết Lung_Opacity tối hơn phần còn lại. Một phép đo thứ hai củng cố nhận định này: 46,5% toàn bộ ảnh nằm trong khoảng tứ phân vị của Normal, gần mức 50% sẽ có nếu bốn phân bố giống hệt nhau. Độ sáng tách được COVID ở mức vừa và gần như không tách được ba lớp kia, nên nó không đủ để giải thích lối tắt cho cả bốn lớp.

Một dấu vết rõ hơn nằm ở metadata của tệp. 140 trong 1.345 ảnh Viral Pneumonia (10,4%) lưu ở hệ màu RGB, ba lớp còn lại không có ảnh RGB nào. Toàn bộ 140 ảnh này có ba kênh bằng nhau (R = G = B), và pipeline ép mọi ảnh về ảnh xám 8-bit trước khi trích đặc trưng, nên giá trị điểm ảnh sau chuyển đổi không khác gì ảnh xám. Bản thân định dạng tệp không tạo ra khác biệt đặc trưng. Nó là dấu hiệu cho thấy nhóm ảnh này không đi qua cùng một bước xuất tệp với phần còn lại của lớp. Lớp Viral Pneumonia lại đến trọn vẹn từ một nguồn duy nhất, nên khả năng mô hình bám vào đặc điểm của nguồn đó là có cơ sở; Chương 1 đã xếp lớp này vào diện nghi vấn lối tắt vì lý do tương tự.

Ba quan sát trên mới mô tả dữ liệu, chưa đo được mô hình có dùng những dấu hiệu đó hay không. Việc đo nằm ở RQ3: che vùng phổi hoặc chỉ giữ vùng ngoài phổi rồi so macro-F1 với ảnh gốc. Chương 4 trình bày năm kịch bản của phép đo này.

---

## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)

- **Chương này chưa đủ mục.** Hiện mới có 2.2; các mục 2.1 và 2.3–2.9 theo đề cương trong [`report/README.md`](README.md) sẽ viết tiếp. Số bảng và số hình đánh theo chương nên 2.2 bắt đầu từ Bảng 2.1, Hình 2.1.
- **Nguồn số liệu:** toàn bộ số trong Bảng 2.1 và ba số dẫn xuất (AUC, 46,5%, 140 ảnh RGB) sinh bằng `python -m src.eda_brightness` từ `splits/manifest.csv`, ghi ra `results/eda/brightness_by_class.csv` và `results/eda/brightness_channels.json`. Kiểm thử `tests/test_eda_brightness.py` đối chiếu lại CSV với manifest nên bảng trong báo cáo không thể lệch nguồn mà không làm test thất bại.
- **Định nghĩa độ sáng:** trung bình mảng điểm ảnh của tệp gốc, thang 0–255, do `notebooks/01_download_and_eda.ipynb` cell 3 tính. Manifest ghi cả 21.165 ảnh đều 299 × 299, nên khác biệt độ sáng không đến từ kích thước ảnh.
- **Làm tròn:** độ sáng ghi một chữ số thập phân, AUC ghi bốn. Hai giá trị trung vị và tứ phân vị rơi đúng mốc ,xx5 (142,595 và 126,885), làm tròn hai chữ số sẽ phụ thuộc quy ước nên bảng cố ý dừng ở một chữ số. Số gốc sáu chữ số nằm trong CSV.
- **AUC:** tính bằng hạng trung bình (Mann–Whitney U) nên xử lý được giá trị đồng hạng. Không dùng p-value vì với n = 21.165, Kruskal–Wallis luôn bác bỏ giả thuyết không và không cho biết mức tách lớp.
- **Ảnh RGB:** ghi chú "140 ảnh RGB có R = G = B" đã có trong `results/threshold_v3.md` mục 3; `src/dataset.py` ép `img.convert("L")` trước khi trích đặc trưng.
- **Hình:** `results/eda/brightness_distribution.png` do notebook cell 6 sinh, chưa vẽ lại. Khi chuyển sang Word, chèn ảnh và đặt chú thích Hình 2.1 bên dưới, cỡ 10–11 pt.
- **Chưa đưa vào chương:** không có số liệu tập test; RQ1–RQ3 để Chương 3–4.
