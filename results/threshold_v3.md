# Tiêu chí chấp nhận v3 [ĐỀ XUẤT, CHỜ NHÓM CHỐT]
Ngày soạn: 16/10/2026. Ngày chốt: [ĐIỀN NGÀY HỌP]

Thay cho results/threshold_v2.md. v1 và v2 giữ nguyên để lưu vết. Mọi nội dung Deep Learning trong v1/v2 (B2, B3, epoch, backbone, GPU, Grad-CAM) không còn hiệu lực theo quy định của giảng viên: chỉ dùng Machine Learning cổ điển và đặc trưng ảnh thủ công.

## 1. Đề tài và câu hỏi nghiên cứu
Đề tài: Phân loại 4 nhóm ảnh X-quang ngực (COVID-19, Lung Opacity, Normal, Viral Pneumonia) bằng học máy cổ điển với đặc trưng thủ công.
- RQ1: Nhóm đặc trưng nào (histogram độ xám; GLCM + LBP; HOG; hoặc ghép) cho macro-F1 validation cao nhất, với MỘT bộ phân loại cố định chọn trước khi chạy: Random Forest (RandomForestClassifier của scikit-learn), 500 cây, class_weight="balanced_subsample", seed 42/43/44, cấu hình cố định không tinh chỉnh.
- RQ2: Với nhóm đặc trưng tốt nhất của RQ1, bộ phân loại nào (Logistic Regression, k-NN, Decision Tree, Random Forest, SVM, Gradient Boosting) tốt nhất?
- RQ3: Che/cắt theo mask phổi có làm đổi macro-F1 không? (mask resize nearest về 299x299; kiểm tra kích thước mask thật trước khi dùng).

Tham số trích đặc trưng (chốt trước khi chạy, không đổi sau khi xem kết quả): ảnh xám 8-bit 299x299, không resize, không cân bằng histogram. Histogram: 64 bin trên 0-255, chuẩn hoá tổng bằng 1 (64 chiều). GLCM: 32 mức (img // 8), khoảng cách [1, 3, 5], 4 góc (0, pi/4, pi/2, 3pi/4), symmetric=True, normed=True, 5 thuộc tính (contrast, dissimilarity, homogeneity, energy, correlation), 60 chiều; correlation NaN thì thay bằng 0 và ghi số ảnh bị thay vào log. LBP uniform: (P=8, R=1) 10 bin và (P=16, R=2) 18 bin, mỗi histogram chuẩn hoá tổng bằng 1 rồi nối lại (28 chiều). HOG: ô 16x16, khối 2x2, 9 hướng, L2-Hys (10.404 chiều). Ghép = cả bốn nhóm (10.556 chiều).

## 2. Ba loại tiêu chí
- Cổng hợp lệ: đạt/không đạt, áp dụng cho MỌI run.
- Quy tắc chọn cấu hình: chỉ quyết định cấu hình nào đi tiếp sang RQ tiếp theo; không dùng để loại kết quả khỏi báo cáo.
- Báo cáo bắt buộc: không có ngưỡng nhưng phải có trong báo cáo.

## 3. Mốc nền (validation, 3.174 ảnh)
B0 0,1627 (dự đoán toàn bộ là lớp Normal); A0 tốt nhất 0,2397 (Random Forest; phép thử lối tắt bằng metadata tệp, không dùng nội dung ảnh).

## 4. Cổng hợp lệ
- H1 Truy vết: mỗi run có `results/<run_id>/{config.yaml, metrics.json, log, preds_val.csv}`. preds_val.csv ghi id ảnh, nhãn thật, nhãn dự đoán, xác suất từng lớp (nếu bộ phân loại có). config ghi nhóm đặc trưng, tham số trích đặc trưng, bộ phân loại, siêu tham số, seed, commit.
- H2 Chỉ validation: allow_test=False; không dùng test cho bất kỳ quyết định nào.
- H3 So sánh công bằng: cùng cách đọc ảnh (xám, giữ 299x299, không resize), cùng thứ tự manifest, cùng seed 42/43/44 cho thành phần ngẫu nhiên. RQ1: bộ phân loại giữ cấu hình cố định, không tinh chỉnh siêu tham số, để chênh lệch đến từ đặc trưng. Từ RQ2: siêu tham số chọn bằng cross-validation trên train (StratifiedGroupKFold, chia nhóm theo cột group_id của splits/split_v1.csv, là nhóm pHash T=0, đã xác nhận có sẵn), cùng lưới tham số ghi trước cho mỗi bộ phân loại. Mô hình tất định chạy một lần và ghi rõ không có độ lệch chuẩn.
- H4 Vượt mốc tầm thường: macro-F1 > B0 và > A0 tốt nhất. Nếu đặc trưng ảnh không vượt A0, ghi rõ trong báo cáo vì đó là dấu hiệu bất thường.
- H5 Ngân sách: ghi thời gian trích đặc trưng và huấn luyện (giây CPU) từng run; chạy thử một run trước khi chạy cả lô.
- H6 Chống rò rỉ: mọi bước học từ dữ liệu (chuẩn hoá, PCA, chọn đặc trưng) chỉ fit trên train; không đọc test split; nhãn và mask không dùng làm đặc trưng đầu vào (RQ3 dùng mask để cắt vùng, ghi rõ).
- H7 Phạm vi: không import torch, torchvision, tensorflow, keras, timm ở mã đang theo dõi; kiểm tra bằng git grep.

## 5. Quy tắc chọn cấu hình đi tiếp
Cấu hình tham chiếu của RQ1 là histogram độ xám (A1). Nhóm đặc trưng khác chỉ thay tham chiếu khi chênh macro-F1 trung bình >= 0,005 VÀ khoảng tin cậy 95% (bootstrap ghép cặp theo ảnh, 2.000 lần, trên 3.174 ảnh validation) của hiệu số không chứa 0. Nếu không, giữ cấu hình rẻ hơn (rẻ = thời gian trích đặc trưng đo được, ghi trước khi xem macro-F1). RQ2 dùng cùng quy tắc, tham chiếu là bộ phân loại đã dùng ở RQ1. Mỗi RQ chỉ có MỘT phép so sánh chính, đóng băng và ghi vào biên bản trước khi xem kết quả. Ngưỡng 0,005 là quy ước của nhóm, không có căn cứ dữ liệu. Mọi cấu hình đều được báo cáo đầy đủ.

## 6. Báo cáo bắt buộc
- R1 macro-F1, recall/precision/F1 từng lớp, ma trận nhầm lẫn; trung bình ± độ lệch chuẩn mẫu (nếu có nhiều seed) kèm khoảng tin cậy bootstrap.
- R2 Ma trận con Normal - Lung Opacity.
- R3 Kiểm tra lối tắt: A0; A1; RQ3 (đặc trưng chỉ từ trong phổi so với chỉ từ ngoài phổi); permutation importance. Kênh màu: cả 140 ảnh RGB của Viral Pneumonia có R=G=B nên is_rgb chỉ là dấu hiệu định dạng file.
- R4 Sai số lấy mẫu (xấp xỉ): sai số chuẩn ≈ sqrt(p(1-p)/n) với n = 3.174 (toàn bộ) và n = 203 (Viral Pneumonia); tính lại theo p thực đo (ví dụ p = 0,8: khoảng 0,007 và 0,028).
- R5 Giới hạn: 735 cặp gần trùng khác split; cross-validation chia nhóm theo group_id chỉ chặn trùng pHash tuyệt đối (Hamming 0), không chặn gần trùng (Hamming 1-4) nằm trong train; không có mã bệnh nhân; nguồn và tuổi chưa xác minh; chỉ đánh giá trên validation (cũng dùng chọn mô hình nên số hơi lạc quan). Số chiều các nhóm đặc trưng lệch nhau rất lớn (64, 88, 10.404); trong nhóm ghép, HOG chiếm khoảng 98,6% số chiều nên kết quả ghép có thể gần với HOG đơn lẻ; histogram có thể bắt lối tắt độ sáng và độ tương phản của nguồn ảnh.
