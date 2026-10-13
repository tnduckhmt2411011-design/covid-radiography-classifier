# Tiêu chí chấp nhận v2 [ĐỀ XUẤT, CHỜ NHÓM CHỐT]

Thay cho results/threshold_v1.md (biên bản họp trước, giữ nguyên để lưu vết).

## 1. Ba loại tiêu chí
- Cổng hợp lệ: đạt/không đạt, áp dụng cho MỌI run.
- Quy tắc chọn cấu hình: chỉ để quyết định cấu hình nào đi tiếp sang RQ2; không dùng để loại kết quả khỏi báo cáo.
- Báo cáo bắt buộc: không có ngưỡng nhưng phải có trong báo cáo.

## 2. Mốc nền (validation, 3.174 ảnh; độ lệch chuẩn mẫu, 3 seed, 5 epoch)
B0 0,1627; A0 tốt nhất 0,2397; B2 0,8064 ± 0,0059; B3 0,9575 ± 0,0016.

## 3. Cổng hợp lệ
H1 Truy vết: mỗi run có results/<run_id>/{config.yaml, metrics.json, log.csv, preds_val.csv}. preds_val.csv ghi id ảnh, nhãn thật, nhãn dự đoán và xác suất từng lớp. config ghi seed, enum trọng số, siêu tham số, commit.
H2 Chỉ validation: allow_test=False; không dùng test cho bất kỳ quyết định nào.
H3 So sánh công bằng: cùng 5 epoch, seed 42/43/44, cách chọn checkpoint (macro-F1 validation tốt nhất), tiền xử lý, augmentation. Head-only được định nghĩa thống nhất cho mọi kiến trúc: backbone ở chế độ eval() khi huấn luyện (không cập nhật thống kê BatchNorm, không stochastic depth). B2 của Tuần 4 chưa theo định nghĩa này; nhóm quyết định chạy lại hay chỉ ghi chú.
H4 Vượt mốc tầm thường: macro-F1 > B0 và > A0 tốt nhất. Đây chỉ là kiểm tra hợp lý, không chứng minh mô hình học tổn thương.
H5 Ngân sách: ghi giây/epoch và GPU-giờ từng run; tổng theo kế hoạch không vượt quota còn lại. DenseNet121 và EfficientNet-B0 đo bằng một run thử trước khi duyệt cả lô.

## 4. Quy tắc chọn cấu hình đi tiếp (RQ1 sang RQ2)
Chọn cấu hình có macro-F1 trung bình cao nhất trên validation. Cấu hình mới chỉ thay ResNet18 full fine-tune (B3) khi chênh macro-F1 trung bình >= 0,005 VÀ khoảng tin cậy 95% (bootstrap ghép cặp trên 3.174 ảnh validation) của hiệu số không chứa 0. Nếu không, giữ cấu hình rẻ hơn. Mọi kiến trúc đều được báo cáo đầy đủ trong RQ1, kể cả khi không được chọn.

## 5. Báo cáo bắt buộc
R1 macro-F1, recall/precision/F1 từng lớp, ma trận nhầm lẫn; trung bình ± độ lệch chuẩn mẫu của 3 seed kèm khoảng tin cậy bootstrap.
R2 Ma trận con Normal - Lung Opacity.
R3 Kiểm tra lối tắt: A0, đề xuất thêm A1 (mô hình đơn giản trên histogram độ xám); RQ3 (Grad-CAM, ảnh che trong/ngoài phổi). Kênh màu: cả 140 ảnh RGB của lớp Viral Pneumonia có R=G=B nên is_rgb chỉ là dấu hiệu định dạng file, không phải tín hiệu màu đầu vào.
R4 Sai số lấy mẫu (xấp xỉ): validation 3.174 ảnh cho sai số chuẩn khoảng 0,004 với độ chính xác ~0,95; lớp Viral Pneumonia (203 ảnh) có sai số cỡ 0,015.
R5 Giới hạn: 735 cặp gần trùng, không có mã bệnh nhân, nguồn và tuổi chưa xác minh, chỉ đánh giá trên validation (cũng dùng để chọn checkpoint nên số hơi lạc quan).
