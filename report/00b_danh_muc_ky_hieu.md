# Danh mục ký hiệu và chữ viết tắt

Chỉ những ký hiệu và chữ viết tắt thực sự xuất hiện trong báo cáo mới được liệt kê; cột thứ hai
ghi nghĩa, cột thứ ba ghi vị trí xuất hiện đầu tiên. Mã nội bộ của đề tài (các cổng kiểm soát
H1–H7, giới hạn R1–R5, quy tắc D1–D4, mã công việc S…) và mã lệnh viết trong dấu ngược đơn chỉ
xuất hiện trong ngoặc để tra cứu nên không nằm trong danh mục này; bảng đối chiếu của chúng nằm
trong phần ghi chú kỹ thuật của từng chương.

## 1. Chữ viết tắt

| Chữ viết tắt | Nghĩa | Xuất hiện đầu |
| :--- | :--- | :--- |
| AUC | Area Under the ROC Curve — diện tích dưới đường ROC; trong đề tài dùng để đo mức độ một lớp tách khỏi ba lớp còn lại theo độ sáng | Bảng 2.2 (mục 2.2) |
| BIMCV | Tên kho ảnh COVID-19+, một trong sáu kho thành phần của lớp COVID | Chú thích mục 2.1 |
| CI | Confidence interval — khoảng tin cậy 95%, tính bằng bootstrap ghép cặp 2.000 lần | Mục 3.1 |
| CPU / GPU | Bộ xử lý / bộ xử lý đồ họa; đề tài chỉ chạy trên CPU | Mục 1.3 |
| CXR | Chest X-ray — ảnh X-quang lồng ngực | Mục 1.1 |
| COVID | Lớp COVID-19 của bộ dữ liệu bốn lớp | Mục 1.1 |
| CV | Cross-validation — kiểm định chéo; đề tài dùng `StratifiedGroupKFold` 5-fold trên tập train | Mục 2.8 |
| DCT | Discrete Cosine Transform — biến đổi cosine rời rạc, bước trung gian khi tính pHash | Mục 2.3 |
| DT | Decision tree — cây quyết định, mã `dt` | Mục 2.8 |
| EDA | Exploratory data analysis — phân tích khám phá dữ liệu | Phụ lục B.1 (trong chương dùng cụm "phân tích khám phá") |
| GB | Gradient boosting — mã `gb` | Mục 2.8 |
| GLCM | Gray-level co-occurrence matrix — ma trận đồng hiện mức xám, nhóm đặc trưng kết cấu 60 chiều | Mục 2.6.2 |
| HOG | Histogram of oriented gradients — đặc trưng hướng biên dạng histogram | Mục 2.6.3 |
| HTTP | Giao thức truyền tải siêu văn bản; dùng trong phép kiểm tra tải ẩn danh artifact | Phụ lục A.2 |
| IEEE | Chuẩn trích dẫn tài liệu tham khảo của quyển báo cáo | Danh mục tài liệu tham khảo |
| JPG / PNG | Định dạng tệp ảnh nén; toàn bộ ảnh của bộ dữ liệu là PNG, giao diện nhận PNG và JPG | Mục 2.1; mục 5.5.2 |
| k-NN | k-nearest neighbours — mã `knn` | Mục 2.8 |
| LBP | Local binary pattern — mẫu nhị phân cục bộ | Mục 2.6.2 |
| LR | Logistic regression — hồi quy logistic, mã `lr` | Mục 2.8 |
| Macro-F1 | Trung bình cộng F1 của bốn lớp; thước đo chính để chọn mô hình | Mục 1.1 |
| MB | Megabyte — đơn vị giới hạn kích thước ảnh tải lên của ứng dụng | Mục 5.5.2 |
| MD5 | Một hàm băm; dùng ở cổng tương đương 200 ảnh của ứng dụng | Mục 5.5.1; Phụ lục A.4 |
| pHash | Perceptual hash — băm nhận thức 64 bit, dùng để gom ảnh gần trùng | Mục 2.3 |
| RBF | Radial basis function — hàm nhân toả của SVM | Mục 2.8 |
| RF | Random forest — rừng ngẫu nhiên, mã `rf`; đồng thời là cấu hình tham chiếu của RQ2 | Mục 2.8 |
| RSNA | Radiological Society of North America — cuộc thi là nguồn của lớp Lung_Opacity | Mục 2.1 |
| SD | Standard deviation — độ lệch chuẩn mẫu | Mục 2.2 |
| SHA-256 | Hàm băm SHA-256; dùng để kiểm tra artifact và tệp phân chia | Mục 2.4; mục 5.5.1 |
| SVM | Support vector machine — máy vectơ hỗ trợ, bộ phân loại được chọn | Mục 1.1 |
| SVC | Support vector classification — lớp `SVC` của scikit-learn | Mục 5.5.1 |
| StandardScaler | Lớp chuẩn hóa z-score của scikit-learn; chỉ fit trên tập train | Mục 2.7 |
| StratifiedGroupKFold | Bộ chia tầng theo nhóm cho kiểm định chéo 5-fold, nhóm theo `group_id` | Mục 2.8 |
| UTC | Giờ phối hợp quốc tế; mốc thời gian của lần mở khóa tập test | Mục 2.4 |

## 2. Ký hiệu toán học

| Ký hiệu | Nghĩa | Xuất hiện đầu |
| :--- | :--- | :--- |
| $n$ | Số ảnh của tập đang xét (3.174 ảnh validation, 3.176 ảnh test, 2.000 lần bootstrap) | Mục 2.9 |
| $D$ | Khoảng cách Hamming giữa hai pHash, tính theo công thức (2.1) | Mục 2.3 |
| $T$ | Ngưỡng gần trùng khi gom nhóm pHash; đề tài chốt $T = 0$ (trùng tuyệt đối) và có thử $T = 4$, $T = 8$ | Mục 2.3 |
| $u$, $v$ | Vec-tơ bit của hai pHash trong công thức tính $D$ | Mục 2.3 |
| $\pm$ (ký hiệu ±) | Khoảng một độ lệch chuẩn mẫu quanh giá trị trung bình; xuất hiện ở cột "Trung bình ± SD" và ở ghi chú mục 2.4 (lệch tối đa ± 0,1%) | Mục 2.2 |

## Ghi chú kỹ thuật

- Nguồn: đếm số lần xuất hiện trong thân bài sáu chương và phụ lục; chỉ ký hiệu đếm được từ một
  lần trở lên mới vào danh mục (chẳng hạn "EDA" chỉ xuất hiện ở Phụ lục B, trong chương dùng cụm
  "phân tích khám phá" nên ghi rõ trong bảng).
- Macro-F1 (thước đo chọn mô hình) phân biệt với F1 từng lớp: F1 theo lớp nằm ở Bảng 3.4, Bảng
  4.3 và Bảng 5.2, không dùng để chọn mô hình.
