# CHƯƠNG 2. DỮ LIỆU VÀ PHƯƠNG PHÁP NGHIÊN CỨU

## 2.1. Nguồn gốc bộ dữ liệu và độ tin cậy thông tin

Đề tài dùng bộ COVID-19 Radiography Database công bố trên Kaggle, tổng hợp trong hai bài báo của Chowdhury và cộng sự [1] và Rahman và cộng sự [2]. Bộ dữ liệu gồm 21.165 ảnh X-quang lồng ngực dạng PNG, kích thước 299 × 299 điểm ảnh, thuộc bốn lớp. Tổng số ảnh và số ảnh của từng lớp khớp với số liệu hai bài báo công bố; riêng phép cộng các nguồn thành phần của lớp COVID theo lời văn cho ra 3.615 ảnh, thấp hơn một ảnh so với con số công bố[^covid-src].

**Bảng 2.1: Thành phần bốn lớp theo nguồn gốc**

| Lớp | Số ảnh | Nguồn thành phần |
| :--- | ---: | :--- |
| COVID | 3.616 | Sáu kho công khai; lớn nhất là BIMCV-COVID19+ với 2.474 ảnh |
| Lung_Opacity | 6.012 | Toàn bộ từ cuộc thi RSNA Pneumonia Detection Challenge |
| Normal | 10.192 | 8.851 ảnh RSNA và 1.341 ảnh từ bộ `Chest X-Ray Images (Pneumonia)` |
| Viral Pneumonia | 1.345 | Toàn bộ từ bộ `Chest X-Ray Images (Pneumonia)` |

Lung_Opacity lấy trọn từ cuộc thi RSNA và Viral Pneumonia lấy trọn từ bộ `Chest X-Ray Images (Pneumonia)` của Paul Mooney[^mooney], còn Normal và COVID ghép từ nhiều nguồn (Bảng 2.1). Cặp cùng nguồn rõ nhất là 1.345 ảnh Viral Pneumonia và 1.341 ảnh Normal, cả hai đều từ bộ của Mooney; cặp này được dùng ở mục 2.2 để kiểm tra dấu hiệu RGB có theo nguồn ảnh hay không.

Nhãn bốn lớp được kế thừa trực tiếp từ các kho nguồn. Hai bài báo không mô tả bước tái thẩm định nhãn độc lập cho toàn bộ 21.165 ảnh, không cung cấp mã bệnh nhân, tuổi hay giới tính, và chỉ nêu thông tin thiết bị chụp cho một nguồn con của lớp COVID [2]. Mặt nạ phổi đi kèm 21.165 tệp, đều ở kích thước 256 × 256 nên không khớp với ảnh 299 × 299; các kịch bản che mặt nạ của RQ3 vì thế phải nội suy mask về kích thước ảnh trước khi trích đặc trưng.

Bộ dữ liệu được phát hành với nhãn giấy phép `copyright-authors` kèm dòng hướng dẫn dùng cho mục đích học thuật và phi thương mại.

## 2.2. Phân tích khám phá dữ liệu và nguy cơ học lối tắt từ độ sáng và metadata tệp

Với một bộ dữ liệu ghép từ nhiều nguồn, độ sáng là thuộc tính đầu tiên cần kiểm tra, vì một mô hình có thể nhận ra lớp nhờ nền ảnh sáng hay tối thay vì nhờ tổn thương phổi. Độ sáng được đo bằng trung bình mảng điểm ảnh của tệp gốc trên thang 0–255, tính một lần cho 21.165 ảnh và lưu trong `splits/manifest.csv`; mọi số dưới đây tính từ tệp đó. Bảng 2.2 tổng hợp theo lớp, Hình 2.1 vẽ phân bố đầy đủ.

**Bảng 2.2: Độ sáng trung bình theo lớp (thang 0–255)**

| Lớp | n | Trung bình ± SD | Trung vị | Khoảng tứ phân vị | Nhỏ nhất | AUC so với ba lớp còn lại |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| COVID | 3.616 | 139,5 ± 25,0 | 142,6 | 126,9–156,0 | 25,5 | 0,6585 |
| Lung_Opacity | 6.012 | 126,0 ± 23,6 | 120,8 | 110,6–142,1 | 32,2 | 0,4269 |
| Normal | 10.192 | 129,4 ± 22,4 | 125,5 | 113,5–143,6 | 26,4 | 0,4802 |
| Viral Pneumonia | 1.345 | 125,4 ± 19,0 | 126,9 | 113,5–137,8 | 64,8 | 0,4557 |

*(SD là độ lệch chuẩn mẫu; khoảng tứ phân vị là khoảng từ phân vị 25% đến phân vị 75%; AUC là xác suất một ảnh của lớp sáng hơn một ảnh ngẫu nhiên của ba lớp còn lại.)*

![Phân bố độ sáng trung bình của bốn lớp](../results/eda/brightness_distribution.png)

**Hình 2.1: Phân bố độ sáng trung bình của bốn lớp**

Bốn lớp đều có trung vị nằm trong dải 120,8–142,6, nhưng vị trí trong dải không đều. COVID sáng nhất với trung vị 142,6, cao hơn Lung_Opacity 21,8 đơn vị; ba lớp còn lại xếp sát nhau trong khoảng 120,8–126,9. Độ lệch chuẩn 19,0–25,0 và khoảng tứ phân vị rộng 24,3–31,5 đơn vị, tức biến thiên bên trong một lớp cùng cỡ với chênh lệch giữa hai trung vị xa nhất. Ba lớp có ảnh tối xuống dưới 33, riêng Viral Pneumonia không có ảnh nào dưới 64,8.

Ngoài trung vị, mỗi lớp được tính một giá trị AUC: xác suất một ảnh của lớp đó sáng hơn một ảnh lấy ngẫu nhiên từ ba lớp còn lại. COVID đạt 0,6585, nghĩa là trong hai ảnh chọn ngẫu nhiên, một của COVID và một của lớp khác, ảnh COVID sáng hơn với xác suất khoảng 66%. Ba lớp còn lại có AUC từ 0,4269 đến 0,4802. Giá trị dưới 0,5 chỉ cho biết lớp đó tối hơn phần còn lại, nên mức tách được đo bằng khoảng cách đến 0,5: COVID cách khoảng 0,16, Lung_Opacity 0,07, Viral Pneumonia 0,04 và Normal 0,02. Trên toàn bộ dữ liệu, 46,5% ảnh nằm trong khoảng tứ phân vị của Normal; nếu bốn phân bố trùng nhau thì tỉ lệ này là 50%, nên mức lệch tổng thể không lớn. Độ sáng tách COVID ở mức vừa, tách Lung_Opacity yếu, và gần như không tách Normal hay Viral Pneumonia. Vì vậy nó không đủ để giải thích lối tắt cho cả bốn lớp.

Một dấu vết khác nằm ở metadata của tệp. Có 140 trong 1.345 ảnh Viral Pneumonia (10,4%) lưu ở hệ màu RGB, ba lớp còn lại không có ảnh RGB nào. Toàn bộ 140 ảnh này có ba kênh bằng nhau (R = G = B), và pipeline ép mọi ảnh về ảnh xám 8-bit trước khi trích đặc trưng, nên giá trị điểm ảnh sau chuyển đổi trùng với ảnh xám; bản thân định dạng tệp không tạo ra khác biệt đặc trưng. Định dạng khác nhau cho thấy nhóm ảnh này nhiều khả năng không đi qua cùng một bước xuất tệp với phần còn lại của lớp. Dấu hiệu đó chỉ phủ 10,4% lớp Viral Pneumonia, phần còn lại không khác biệt ở các thuộc tính đã kiểm, nên nó không đủ để giải thích cả lớp.

Dấu RGB cũng không trùng với ranh giới nguồn. Cả 1.341 ảnh Normal lấy từ cùng bộ Kaggle với lớp Viral Pneumonia đều ở chế độ một kênh, nên dấu RGB gắn với riêng nhóm 140 ảnh này, không gắn với nguồn.

Mốc A0 ở mục 1.2 là phép thử trực tiếp cho hai kênh này. Random Forest chỉ dùng độ sáng trung bình và cờ is_rgb đạt macro-F1 0,2397 trên validation, cao hơn 0,1627 của mốc đoán toàn bộ Normal nhưng còn xa 0,8599 của nhóm đặc trưng ghép. Hai kênh này vì thế tự chúng không đủ để phân loại. Tuy vậy A0 chỉ dùng một con số độ sáng, trong khi histogram và các đặc trưng khác giữ nhiều thông tin cường độ hơn, nên A0 là cận dưới của mức lối tắt từ cường độ chứ chưa loại trừ được nó.

Những quan sát trên mới mô tả dữ liệu và một mốc tham chiếu đơn giản; chúng chưa cho biết mô hình dùng đặc trưng ảnh có dựa vào các dấu hiệu đó hay không. Việc đo nằm ở RQ3: che vùng phổi hoặc chỉ giữ vùng ngoài phổi rồi so macro-F1 với ảnh gốc. Chương 4 trình bày năm kịch bản của phép đo này.

## 2.3. Gom nhóm ảnh trùng bằng pHash ngưỡng T = 0

Ảnh trùng rơi vào cả train và test sẽ thổi phồng điểm số, nên bước gom nhóm chạy trước phép chia. Mỗi ảnh được tính mã MD5 của tệp và pHash 64-bit DCT; khoảng cách Hamming giữa hai mã pHash được tính theo công thức:
$$D = \frac{64 - u \cdot v}{2} \qquad (2.1)$$

với $u$ và $v$ là hai vector bit đã đổi sang dạng $\{-1, 1\}$. Các ảnh có $D = 0$ được gom vào cùng một nhóm bằng thuật toán Union-Find, và định danh nhóm đó trở thành cột `group_id` trong `splits/split_v1.csv`.

Kết quả trên 21.165 ảnh: 20.942 nhóm, trong đó 178 nhóm chứa nhiều hơn một ảnh với tổng cộng 401 ảnh, số còn lại là 20.764 nhóm chỉ có một ảnh. Không có nhóm nào chứa ảnh của hai lớp khác nhau. Toàn bộ ảnh trong cùng một nhóm được gán về cùng một tập trước khi chia 70/15/15, nên ảnh trùng pHash không thể xuất hiện đồng thời ở hai tập.

Ở ngưỡng $T = 0$, 39 trong 178 nhóm có toàn bộ ảnh trùng cả mã MD5, tức trùng cả nội dung tệp; 139 nhóm còn lại trùng pHash nhưng khác MD5, nhiều khả năng là các bản khung hoặc bản nén khác nhau của cùng một ảnh. Hai trường hợp này đều là ảnh không độc lập, và cả hai đều được gom về cùng một tập.

Ngưỡng $T = 4$ và $T = 8$ cũng được thực nghiệm. Ở ngưỡng cao hơn, số ảnh nằm trong các nhóm lệch nhãn tăng từ 0 ở $T = 0$ lên 2.195 ảnh ở $T = 4$ (172 nhóm) và 14.758 ảnh ở $T = 8$ (107 nhóm). Số nhóm giảm trong khi số ảnh tăng, nhiều khả năng do các nhóm nhỏ bị nối thành nhóm rất lớn. Việc gom nhóm lệch nhãn sẽ trộn hai lớp vào cùng một nhóm và phá tính phân tầng của phép chia, nên ngưỡng $T = 0$ được chọn.

Đánh đổi của ngưỡng này: các cặp có khoảng cách Hamming lớn hơn 0 và không quá 4 không được gom nhóm, nên chúng có thể nằm ở hai tập khác nhau. Bộ dữ liệu không có mã bệnh nhân nên không có cách nào kiểm tra hai ảnh đó có phải cùng một người hay không; mức ảnh hưởng của hiện tượng này được phân tích ở mục 2.5.

## 2.4. Phân chia train/val/test 70/15/15 và cơ chế khóa tập test

Phép chia dùng StratifiedGroupKFold với 20 fold và `random_state = 42`, giữ nguyên `group_id` trong mỗi tập và phân tầng theo nhãn. 20 fold được chia thành 14 fold cho train (70%), 3 fold cho validation (15%) và 3 fold cho test (15%). Kết quả ghi trong `splits/split_v1.csv` và được tóm tắt ở Bảng 2.3.

**Bảng 2.3: Phân bố bốn lớp theo tập train, validation và test**

| Lớp | Tổng | Train | Val | Test |
| :--- | ---: | ---: | ---: | ---: |
| COVID | 3.616 | 2.536 | 537 | 543 |
| Lung_Opacity | 6.012 | 4.205 | 903 | 904 |
| Normal | 10.192 | 7.132 | 1.531 | 1.529 |
| Viral Pneumonia | 1.345 | 942 | 203 | 200 |
| **Tổng cộng** | **21.165** | **14.815** | **3.174** | **3.176** |

Tỷ lệ từng lớp trong validation và trong test đều lệch tối đa dưới 0,2 điểm phần trăm so với tỷ lệ của lớp đó trong toàn bộ dữ liệu: COVID chiếm 16,92% của validation và 17,10% của test, trong khi chiếm 17,09% của cả bộ. Tệp split được băm SHA-256 với giá trị `f99e03d3d5cfc32f2bbc9befbdef45a07a256458a837a6d420a6658ed7583d98`, và một bài kiểm thử tự động đối chiếu băm đó cùng số dòng từng tập, nên một thay đổi của tệp split sẽ làm bộ kiểm thử thất bại.

Tập test bị khóa trong suốt các giai đoạn chọn đặc trưng và chọn bộ phân loại. Mã nguồn mặc định từ chối đọc tập test, và mọi quyết định của RQ1 đến RQ3 chỉ dùng 3.174 ảnh validation. Tập test được mở đúng một lần vào lúc 07:43:34 UTC ngày 09/11/2026. Tệp `results/final_test/UNLOCK_RECORD.json` ghi lại lần mở khóa đó kèm commit, mã băm SHA-256 của tệp split, mã băm của chuỗi xác nhận do tác giả ký, và macro-F1 validation 0,9024 của mô hình dùng cho lần chạy đó, tức mốc được trình bày lại ở Chương 3.

Trước khi đánh giá trên tập test, pipeline phải vượt sáu bước kiểm soát:

1. Mã băm SHA-256 của tệp split phải khớp giá trị đã công bố.
2. Cấu hình mô hình phải trùng cấu hình đã đóng băng trước đó.
3. Không được phép chạy đánh giá trên tập test lần thứ hai.
4. Chuỗi xác nhận do tác giả ký phải khớp mã băm đã đăng ký.
5. Macro-F1 validation phải tái lập được trên cùng cấu hình.
6. Báo cáo phải công bố đầy đủ các chỉ số đã đăng ký trước.

Danh sách sáu bước ở dạng bảng nằm trong `results/final_test_protocol_record.md`.

## 2.5. Giới hạn còn lại của dữ liệu

Phép gom nhóm theo pHash chỉ gom được các ảnh trùng pHash. Toàn bộ dữ liệu còn 1.570 cặp có khoảng cách Hamming lớn hơn 0 và không quá 4, trong đó 735 cặp nằm ở hai tập khác nhau. Số liệu này được thống kê riêng sau khi phép chia đã chốt, nên nó không làm thay đổi `splits/split_v1.csv` mà chỉ mô tả phần rủi ro còn lại.

**Bảng 2.4: 735 cặp gần trùng nằm ở hai tập khác nhau**

| Cặp tập | Số cặp |
| :--- | ---: |
| Train – Validation | 335 |
| Train – Test | 325 |
| Validation – Test | 75 |
| **Tổng cộng** | **735** |

Về nhãn, 229 trong 735 cặp là lệch nhãn, tức 31,2%; 506 cặp còn lại cùng nhãn. Tất cả 735 cặp đều có khoảng cách chẵn: 665 cặp ở mức 4 và 70 cặp ở mức 2, không có cặp nào ở mức 1 hay 3. Nguyên nhân là mỗi mã pHash 64-bit sau khi ngưỡng theo trung vị chứa đúng 32 bit 1, nên hai mã có cùng số bit 1 thì khoảng cách Hamming luôn chẵn.
Số cặp chưa cho biết mức ảnh hưởng, vì một ảnh có thể nằm trong nhiều cặp. Đếm theo ảnh, 273 trong 3.174 ảnh validation (8,6%) và 243 trong 3.176 ảnh test (7,6%) có ít nhất một ảnh gần trùng ở tập khác. Với khoảng 8% ảnh đánh giá, mô hình có thể đã gặp một bản gần giống khi huấn luyện, nên macro-F1 có thể cao hơn mức thực của ảnh chưa từng thấy; đề tài chưa đo mức chênh này.

Trong 735 cặp, 229 cặp (31,2%) mang nhãn khác nhau. Hai ảnh gần giống về pHash mà khác nhãn có thể là nhiễu nhãn, hoặc là hai ảnh có hình thái lồng ngực tương tự nhưng thật sự khác nhau; kiểm tra cần xem ảnh gốc và nằm ngoài phạm vi đề tài. Kết quả này cùng chiều với mục 2.3, nơi ngưỡng T = 4 tạo ra 172 nhóm lệch nhãn.

Rủi ro cùng một bệnh nhân không xử lý được bằng kỹ thuật. Bộ dữ liệu không cung cấp mã bệnh nhân, nên không có cách nào gom ảnh của cùng một người chụp ở các ngày khác nhau, và bài báo nêu bộ dữ liệu có khoảng 15.000 bệnh nhân [2], tức mỗi bệnh nhân có thể có nhiều ảnh. Thông tin nhân khẩu học và thiết bị chụp cũng thiếu, trừ một nguồn con của lớp COVID. Các giới hạn này được xét lại ở Chương 6 khi đánh giá phạm vi áp dụng của mô hình.

## 2.6. Trích xuất đặc trưng thủ công trên ảnh xám 299 × 299

Bốn nhóm đặc trưng đều tính trên ảnh xám 8-bit 299 × 299 sau khi pipeline đã ép toàn bộ ảnh về một kênh; không resize, không cân bằng histogram. Thứ tự và số chiều của bốn nhóm được tóm tắt ở Bảng 2.5.

**Bảng 2.5: Bốn nhóm đặc trưng và số chiều**

| Nhóm | Nội dung | Số chiều |
| :--- | :--- | ---: |
| Histogram | Phân bố mức xám | 64 |
| GLCM và LBP | Kết cấu và mẫu nhị phân cục bộ | 88 |
| HOG | Hướng biên | 10.404 |
| Ghép | Histogram + GLCM + LBP | 152 |

### 2.6.1. Đặc trưng histogram cường độ sáng, 64 chiều

Ảnh được chia thành 64 bin trên khoảng mức xám từ 0 đến 255, mỗi bin rộng 4 mức xám. Mỗi bin chia cho tổng số điểm ảnh, nên tổng vector bằng 1. Nhóm này chỉ mô tả ảnh có sáng hay tối và độ tương phản phân bố thế nào, không mang thông tin vị trí. Ở RQ1, histogram 64 chiều đạt macro-F1 0,7829, trong khi mốc A0 chỉ dùng độ sáng trung bình đạt 0,2397. Nghĩa là phân bố cường độ toàn ảnh, dù không có thông tin vị trí, đã đủ để phân loại khá tốt; liệu thông tin đó đến từ vùng phổi hay từ đặc điểm nguồn ảnh là điều RQ3 phải đo.

### 2.6.2. Đặc trưng kết cấu GLCM 60 chiều và LBP 28 chiều

GLCM (Gray-Level Co-occurrence Matrix) đo mối quan hệ giữa các cặp điểm ảnh. Mức xám được giảm từ 256 xuống 32 mức (mỗi mức gộp 8 giá trị gốc) để ma trận không quá thưa. Ma trận được tính ở ba khoảng cách 1, 3 và 5 điểm ảnh, theo bốn hướng 0°, 45°, 90° và 135°. Mỗi hướng và khoảng cách cho năm thuộc tính: contrast, dissimilarity, homogeneity, energy và correlation. Năm thuộc tính nhân ba khoảng cách nhân bốn hướng cho ra 60 chiều.

Riêng thuộc tính correlation phụ thuộc vào độ lệch chuẩn của phân bố biên; khi ảnh chỉ chứa một mức xám sau bước giảm về 32 mức, hệ số tương quan không xác định theo định nghĩa. Các giá trị không xác định được thay bằng 0 và số lượng được đếm.

LBP (Local Binary Pattern) ghi nhận mẫu cục bộ quanh mỗi điểm ảnh. Đề tài dùng hai bộ tham số: 8 điểm lân cận bán kính 1 và 16 điểm lân cận bán kính 2, đều ở dạng uniform. Histogram của hai bộ cho 10 bin và 18 bin, chia cho tổng số điểm ảnh rồi nối lại thành vector 28 chiều.

### 2.6.3. Đặc trưng hướng biên HOG, 10.404 chiều

HOG (Histogram of Oriented Gradients) tính gradient tại mỗi điểm ảnh rồi thống kê hướng gradient trên từng ô. Đề tài dùng ô 16 × 16 điểm ảnh, mỗi khối 2 × 2 ô, bình thường hóa theo chuẩn L2-Hys và 9 bin hướng cho mỗi ô. Với ảnh 299 × 299, 18 ô đầy đủ mỗi chiều chiếm 288 điểm ảnh, còn 11 điểm ảnh ở mép không nằm trong ô nào; số khối được tính là ((299 // 16) − 1)² = 289, mỗi khối cho 4 × 9 = 36 giá trị, tức 289 × 36 = 10.404 chiều.

### 2.6.4. Nhóm đặc trưng ghép 152 chiều

Nhóm ghép lấy histogram 64 chiều, GLCM 60 chiều và LBP 28 chiều rồi nối thẳng lại, cho 152 chiều. Nhóm này không gồm HOG, nên kích thước của nó bằng khoảng 1/68 nhóm HOG: 152 chiều so với 10.404 chiều. Hệ quả của chênh lệch số chiều đối với kết quả được xét ở Chương 3.

---

## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)

- **Chương này chưa đủ mục.** Hiện đã có 2.1–2.6.4; các mục 2.7–2.9 theo đề cương trong [`report/README.md`](README.md) sẽ viết tiếp. Số bảng, số hình và số công thức đánh theo thứ tự xuất hiện trong chương, không theo số mục: Bảng 2.1–2.3 (2.1, 2.2, 2.4), Bảng 2.4 (2.5), Bảng 2.5 (2.6), Hình 2.1 (2.2), công thức (2.1) (2.3).
- **Tiêu đề mục 2.2 đã đổi** thành "từ độ sáng và metadata tệp" vì phát hiện về định dạng RGB không nằm trong khái niệm cường độ sáng. Tiêu đề cũng được đổi ở `docs/report_standards.md` mục 3.2 và `report/README.md` dòng 2.2, cả ba chỗ giờ khớp nhau. Tiêu đề mục 2.3 đổi từ "Lọc trùng lặp" thành "Gom nhóm ảnh trùng" vì bước này không loại bỏ ảnh nào.
- **Nguồn số liệu:** số trong Bảng 2.1 và các số dẫn xuất (AUC, khoảng cách đến 0,5, 46,5%, 140 ảnh RGB) sinh bằng `python -m src.eda_brightness` từ `splits/manifest.csv`, ghi ra `results/eda/brightness_by_class.csv` và `results/eda/brightness_channels.json`. Kiểm thử `tests/test_eda_brightness.py` đối chiếu CSV với manifest. Bảng trong văn bản lấy từ `format_markdown_table` của script rồi dán sang, nên nếu sửa tay một ô thì phải đối chiếu lại CSV; test không bắt được lỗi gõ lại.
- **Nguồn mục 2.1:** `docs/dataset_provenance.md` mục 2.1 (thành phần bốn lớp, số lượng từng nguồn), mục 2.2 (giấy phép, tệp `.metadata.xlsx`), mục 3.2 (kích thước ảnh 299 × 299, mask 256 × 256, `mask_match_size = False`) và mục 3.1 (nhãn kế thừa, thiếu `patient_id`, tuổi, thiết bị). Số đếm 21.165 / 10.192 / 6.012 / 3.616 / 1.345 đối chiếu lại bằng pandas trên `splits/split_v1.csv`. Chênh lệch 3.615 so với 3.616 của lớp COVID ghi ở `docs/dataset_provenance.md` mục 2.3 hàng 1.
- **Chú thích chân trang:** `[^covid-src]` giữ chi tiết sáu kho và chênh lệch 3.615 so với 3.616 của lớp COVID ngoài thân bài. `[^mooney]` là nguồn của bộ dữ liệu Kaggle, được gọi ở mục 2.1 và dùng lại từ Chương 1. Cả hai không tính vào danh mục [1]–[6] nên không làm lệch số thứ tự.
- **Tên tệp trong thân bài:** mỗi mục giữ một đường dẫn để chỉ nguồn số (`splits/manifest.csv` ở 2.2, `splits/split_v1.csv` ở 2.4, `results/final_test/UNLOCK_RECORD.json` và `results/final_test_protocol_record.md` ở 2.4). Các chi tiết kỹ thuật như `mask_match_size`, `group_id`, `allow_test`, `format_markdown_table` và tên bài kiểm thử đã rút khỏi thân bài, chuyển sang ghi chú này và Phụ lục B (cấu trúc kho mã nguồn).
- **Nguồn mục 2.3:** `splits/README.md` mục 3 (phương pháp MD5 + pHash + Union-Find, 178 nhóm, 401 ảnh, 0 nhóm lệch nhãn ở $T = 0$) và `notebooks/02_duplicates_and_split.ipynb` cell 4–5. Số 172 nhóm lệch nhãn ở $T = 4$ và 107 nhóm ở $T = 8$ lấy từ `outputs/split_check/duplicates_summary.json`, tệp do notebook cell 5 sinh. Số nhóm trùng cả MD5 (39 trên 178) và số nhóm chỉ trùng pHash (139) tính trực tiếp bằng pandas trên cột `file_hash` của `splits/split_v1.csv`. Lưu ý cách đọc số: `splits/README.md` ghi "20.764 ảnh duy nhất", nhưng đếm trên `splits/split_v1.csv` cho thấy 20.764 là số *nhóm chỉ có một ảnh*, còn tổng số nhóm là 20.942 (178 + 20.764); `duplicates_summary.json` cũng ghi `num_unique_images = 20764`. Báo cáo ghi theo cách thứ hai để không hiểu nhầm.
- **Nguồn mục 2.4:** `splits/README.md` mục 2 (bảng phân bố theo lớp, lệch tối đa $\pm 0,1\%$) và mục 5 (khóa tập test, một lần mở duy nhất); chia 14/3/3 fold từ `notebooks/02_duplicates_and_split.ipynb` cell 6; SHA-256 từ `splits/split_v1.sha256`; lần mở khóa và macro-F1 0,9024 từ `results/final_test/UNLOCK_RECORD.json`; sáu bước kiểm soát G1–G6 từ `results/final_test_protocol_record.md` mục 2. Không đưa bất kỳ số liệu nào của tập test vào chương này.
- **Cách tính 16,92%:** 537 ảnh COVID trong validation chia cho 3.174 ảnh validation. Tỷ lệ cùng lớp trên toàn bộ dữ liệu là 3.616/21.165 = 17,09%. `splits/README.md` ghi độ lệch $\pm 0,1\%$, nhưng đó là độ lệch giữa tỷ lệ *ảnh của một lớp rơi vào một tập* với 70/15/15; báo cáo dùng cách thứ nhất và nói rõ cách tính trong câu.
- **Nguồn mục 2.5:** `docs/roadmap.md` dòng 187 (735 cặp: 325 Train–Test, 335 Train–Val, 75 Val–Test; 229 lệch nhãn, 506 cùng nhãn) và `results/report_rq3/r5_gioi_han.md` (thiếu mã bệnh nhân, nguồn và tuổi chưa xác minh). Phân bố theo khoảng cách Hamming (665 cặp ở $D = 4$, 70 cặp ở $D = 2$) và phân bố theo quan hệ nhãn (215 + 14 = 229 lệch nhãn) lấy từ `outputs/split_check/cross_split_hamming_report.json`. Mức "khoảng 15.000 bệnh nhân" lấy từ [2] theo `docs/dataset_provenance.md` mục 2.4 hàng H4.
- **Số ảnh bị ảnh hưởng (273 ảnh validation, 243 ảnh test) tính lại từ đầu** bằng cách nhân ma trận khối trên cột `phash` của `splits/split_v1.csv`: với mỗi vector bit $u$, $v \in \{0, 1\}^{64}$ cùng trọng số 32, khoảng cách Hamming là $D = 64 - 2(u \cdot v)$. Kết quả tính lại khớp đúng 735 cặp, 229 cặp lệch nhãn và phân bố 325/335/75 với báo cáo gốc, nên hai số ảnh này được coi là kiểm chứng. Tệp JSON chỉ lưu sáu cặp mẫu nên không tra được số ảnh trực tiếp từ đó.
- **Tính chẵn của khoảng cách Hamming:** đếm số bit 1 của 3.000 mã đầu tiên trong `splits/split_v1.csv`, cả 3.000 đều có đúng 32 bit 1. Hai vector cùng trọng số 32 bit thì $D = 64 - 2(u \cdot v)$ luôn chẵn, nên mức 1 và 3 không thể xuất hiện.
- **Correlation:** thử trực tiếp trên scikit-image 0.25.2: ảnh hằng (một mức xám) cho correlation = 1,0, không phải giá trị không xác định; 300 ảnh ngẫu nhiên 64 × 64 không cho giá trị không xác định nào. Báo cáo vì thế chỉ ghi quy ước xử lý (thay bằng 0 và đếm), còn hành vi của thư viện để ở ghi chú này. Mã nguồn vẫn giữ bước xử lý (`src/features_hist_glcm_lbp.py`), và bài kiểm thử `tests/test_features_hist_glcm_lbp.py` dòng 148 cho phép cả hai kết quả 0 hoặc 12.
- **Mức ảnh hưởng so với RQ3:** `results/report_rq3/r2_normal_lung_opacity.csv` cho thấy Chương 4 phân tích cặp nhầm Normal ↔ Lung_Opacity, không có kịch bản so Normal với Viral Pneumonia. Câu ở mục 2.1 vì thế không hứa Chương 4 làm phép đối chiếu cùng nguồn, mà gắn vào mục 2.2, nơi cặp cùng nguồn (1.345 Viral Pneumonia và 1.341 Normal) thực sự được dùng để kiểm tra dấu hiệu RGB.
- **Nguồn mục 2.6:** `src/features_hist_glcm_lbp.py` (histogram 64 bin khoảng (0, 256), mỗi bin 4 mức xám, chuẩn hóa tổng bằng 1; GLCM giảm về 32 mức bằng `img // 8`, ba khoảng cách, bốn hướng, năm thuộc tính, `symmetric=True`, `normed=True`; LBP hai bộ (8, 1) và (16, 2), `method="uniform"`, 10 bin và 18 bin) và `src/features_hog_ghep.py` (HOG 9 bin hướng, ô 16 × 16, khối 2 × 2, `block_norm="L2-Hys"`, công thức `((h//16)-1)*((w//16)-1)*2*2*9`; `GLCMLBP_DIM = 88`, `GHEP_DIM = 152`).
- **Kiểm chứng công thức HOG:** tính tay cho ảnh 299 × 299: $299 // 16 = 18$, trừ 1 được 17 ô mỗi chiều, tức $17 \times 17 = 289$ khối; mỗi khối $2 \times 2 \times 9 = 36$ giá trị; $289 \times 36 = 10.404$. Số khối 289 khớp với `HOG_DIM` trong `src/features_hog_ghep.py`.
- **Chữ viết tắt:** pHash (perceptual hash, băm tri giác), MD5, DCT (discrete cosine transform, biến đổi cosine rời rạc), SD (độ lệch chuẩn mẫu), AUC, PNG, RF/GB/LR/k-NN/DT sẽ được giải thích ở lần xuất hiện đầu trong các mục còn lại, khớp danh mục ký hiệu ở phần mở đầu.
- **Định nghĩa độ sáng:** trung bình mảng điểm ảnh của tệp gốc, thang 0–255, do `notebooks/01_download_and_eda.ipynb` cell 3 tính. Manifest ghi cả 21.165 ảnh đều 299 × 299, nên khác biệt độ sáng không đến từ kích thước ảnh.
- **Làm tròn:** độ sáng một chữ số thập phân, AUC bốn chữ số, số gốc sáu chữ số nằm trong CSV; một số giá trị rơi đúng mốc ,xx5 (trung vị 142,595, q1 126,885, 0,6585 − 0,5 = 0,1585) nên bảng dừng ở đó thay vì làm tròn thêm.
- **AUC:** tính bằng hạng trung bình (Mann–Whitney U) nên xử lý được giá trị đồng hạng. Không dùng p-value vì với n = 21.165, Kruskal–Wallis hầu như luôn bác bỏ giả thuyết không và không cho biết mức tách lớp.
- **Mốc A0:** macro-F1 0,2397 lấy từ `results/a0_shortcut/metrics.json` (khoá `random_forest`); hai đặc trưng `brightness` và `is_rgb` theo `kaggle/baseline/04_baseline.ipynb` cell 3; B0 = 0,1627 theo `results/threshold_v3.md` mục 3; 0,8599 là macro-F1 của nhóm ghép ở RQ1 (`results/report_rq1/r1_summary.csv`). Mô tả của A0 trong mục 1.2 đã đổi thành "hai đại lượng đơn giản của tệp ảnh" cho khớp với định nghĩa độ sáng ở trên.
- **Ảnh RGB:** ghi chú "140 ảnh RGB có R = G = B" đã có trong `results/threshold_v3.md` mục 3; `src/dataset.py` ép `img.convert("L")` trước khi trích đặc trưng. Xác nhận của "cùng nguồn" cho 1.341 ảnh Normal và 1.345 ảnh Viral Pneumonia lấy từ `docs/dataset_provenance.md` mục 2.1; hệ màu từng ảnh đọc trực tiếp từ `splits/manifest.csv`.
- **Hình:** `results/eda/brightness_distribution.png` do notebook cell 6 sinh, chưa vẽ lại. Khi chuyển sang Word, chèn ảnh và đặt chú thích Hình 2.1 bên dưới, cỡ 10–11 pt.
- **Chưa đưa vào chương:** không có số liệu tập test; RQ1–RQ3 để Chương 3–4.

[^covid-src]: Lớp COVID-19 được ghép từ sáu kho theo đường dẫn trong tệp `COVID.metadata.xlsx`: BIMCV-COVID19+ (2.474 ảnh), COVID-CXNet (400), Eurorad (258), kho `ieee8023` (182), SIRM (119) và kho ảnh của một trường y tại Đức (183). Bài báo [2] gộp sáu kho thành bốn nguồn: 2.473 + 183 + 559 + 400 = 3.615, thiếu một ảnh so với số công bố 3.616. Bài báo ghi BIMCV là 2.473 trong khi tệp metadata đếm được 2.474, đồng thời gộp Eurorad, ieee8023 cùng SIRM thành cụm 559 ảnh (258 + 182 + 119). Chi tiết ở `docs/dataset_provenance.md` mục 2.1 và 2.3.
