# Tóm tắt tiếng Việt và Abstract

Hai mục này viết sau cùng, khi sáu chương và phụ lục đã đóng băng. Mọi con số trong hai phần
đều lấy từ bảng của các chương tương ứng (ghi ở Ghi chú kỹ thuật cuối tệp).

## 1. Tóm tắt tiếng Việt

Phân loại tự động ảnh X-quang lồng ngực (CXR) nổi lên khi COVID-19 bùng phát, nhưng mô hình có
thể dựa vào đặc điểm nguồn ảnh thay vì tổn thương phổi. Đề tài giải ba câu hỏi nối tiếp trên
21.165 ảnh CXR bốn lớp: nhóm đặc trưng thủ công nào hiệu quả nhất, bộ phân loại cổ điển nào
vượt trội, và mô hình phụ thuộc vùng trong hay vùng ngoài mặt nạ phổi. Thực nghiệm chỉ dùng học
máy cổ điển trên CPU, gom nhóm ảnh trùng bằng pHash trước khi chia 70/15/15 thành
14.815/3.174/3.176 ảnh, và tính khoảng tin cậy bằng bootstrap ghép cặp 2.000 lần.

RQ1: nhóm ghép 152 chiều (histogram 64, GLCM 60, LBP 28) đạt macro-F1 0,8599 ± 0,0030, vượt nhóm
histogram 64 chiều 0,0770 [+0,0611; +0,0925]. RQ2: trên nhóm ghép, SVM kernel RBF đạt 0,9024
[0,8909; 0,9129], cao nhất trong sáu bộ và vượt mốc Random Forest 0,0442. RQ3: trên năm kịch bản
che mặt nạ, chỉ còn vùng ngoài mặt nạ phổi, mô hình vẫn đạt 0,8921 [0,8807; 0,9031], còn chỉ vùng
phổi thì đạt 0,8490 [0,8333; 0,8625]; hiệu hai kịch bản là +0,0431 [+0,0281; +0,0582]. Vùng ngoài
mặt nạ còn phân biệt được hai lớp cùng nguồn RSNA (2.237 ảnh), và không ảnh Normal nguồn Mooney
nào (197 ảnh) bị đoán thành Viral Pneumonia. Vùng ngoài mặt nạ phổi vì vậy mang thông tin liên
quan đến lớp; đề tài không xác định được đặc điểm nào được dùng nên chưa kết luận được đây là học
lối tắt.

Mô hình được chọn đo một lần trên tập test: macro-F1 0,8714 [0,8579; 0,8840], accuracy 86,56%,
thấp hơn validation 0,0310; trong 427 ảnh sai, 304 lỗi (71,19%) thuộc cặp
Normal – Lung_Opacity. Hệ thống kèm 344 phép kiểm thử trong 28 module và ứng dụng demo kiểm tra
băm SHA-256 trước khi nạp mô hình, độ trễ đầu-cuối trung vị 131,8 ms. Đặc trưng thủ công nhờ đó
thay được mốc đã đăng ký, song việc mô hình dựa vào vùng ngoài mặt nạ phổi làm nó chưa thể dùng
như công cụ chẩn đoán ngoài bộ dữ liệu này.

## 2. Abstract

Automated classification of chest X-ray images (CXR) drew much research attention during the
COVID-19 pandemic, yet such models may rely on source-specific artefacts instead of lung
pathology. This study answers three linked questions on a dataset of 21,165 four-class
radiographs: which hand-crafted feature group works best, which classical classifier is strongest,
and whether the model depends on the lung-masked region or the region outside the mask. All
experiments use classical machine learning on CPU only, paired bootstrap with 2,000 resamples, and
pHash grouping before a 70/15/15 split (14,815/3,174/3,176 images).

RQ1: the 152-dimensional grouped features (64-bin histogram, 60 GLCM, 28 LBP) reach macro-F1
0.8599 ± 0.0030, exceeding the histogram group by 0.0770 [0.0611; 0.0925]. RQ2: among six
classifiers, an RBF-kernel SVM reaches 0.9024 [0.8909; 0.9129], the best result and 0.0442 above
the Random Forest reference. RQ3: under five masking scenarios, with only the region outside the
lung mask the model still reaches 0.8921 [0.8807; 0.9031] versus 0.8490 [0.8333; 0.8625] with the
lung region only; the difference is +0.0431 [0.0281; 0.0582]. The
outside-mask region also separates two classes sharing the same RSNA source (2,237 images), and
none of the 197 Mooney-source Normal images is predicted as Viral Pneumonia. The outside-mask
region therefore carries class-relevant information; since the used features cannot be identified,
the study does not conclude that this is shortcut learning.

The selected model was evaluated once on the held-out test set: macro-F1 0.8714 [0.8579; 0.8840],
accuracy 86.56%, 0.0310 below validation; 304 of 427 misclassified images (71.19%) belong to the
Normal – Lung_Opacity pair. The system ships 344 automated tests in 28 modules and a demo that
verifies SHA-256 before loading the model, with a median end-to-end latency of 131.8 ms.
Hand-crafted features thus replace the registered baseline, while reliance on the outside-mask
region keeps the model from being usable as a diagnostic tool for images from other institutions.

## Ghi chú kỹ thuật

- **Quy ước định dạng số:** phần tiếng Việt giữ nguyên quy ước của quyển (dấu phẩy thập phân,
  chấm phân cách hàng nghìn); phần tiếng Anh dùng dấu chấm thập phân theo thông lệ bài báo quốc
  tế. Giá trị không đổi, chỉ khác cách viết.
- **Nguồn từng nhóm số:** 21.165 ảnh, tỉ lệ 14.815/3.174/3.176 và các mốc B0 = 0,1627, A0 =
  0,2397 lấy ở Chương 1 (mục 1.1); macro-F1 0,8599 ± 0,0030 và hiệu +0,0770 [+0,0611; +0,0925]
  lấy ở Bảng 3.1 và Bảng 3.2 của Chương 3; 0,9024 [0,8909; 0,9129] và hiệu 0,0442 so với Random
  Forest lấy ở Bảng 3.3 và mục 3.4 của Chương 3; các kịch bản RQ3 (0,8921, 0,8490, +0,0431,
  2.237 ảnh RSNA, 197 ảnh Mooney) lấy ở Bảng 4.1 và Bảng 4.4 của Chương 4; 0,8714 [0,8579; 0,8840],
  accuracy 86,56%, −0,0310, 427 lỗi và 304 lỗi (71,19%) lấy ở mục 5.1–5.3 và Bảng 5.1 của Chương
  5; 344 phép kiểm thử trong 28 module lấy ở mục 5.4; độ trễ trung vị 131,8 ms lấy ở mục 6.2 của
  Chương 6 (ghi lại từ Bảng 5.5).
- Hai phần này không đưa thêm số liệu nào ngoài các bảng đã liệt kê; mọi câu mô tả kết quả đều
  tra được về Chương 3–6.
