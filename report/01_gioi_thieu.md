# CHƯƠNG 1. GIỚI THIỆU VÀ TỔNG QUAN ĐỀ TÀI

## 1.1. Bối cảnh và lý do chọn đề tài

Ảnh X-quang lồng ngực (chest X-ray, CXR) là phương tiện chẩn đoán hình ảnh có sẵn ở hầu hết cơ sở y tế: thời gian chụp ngắn, chi phí thấp hơn nhiều so với cắt lớp vi tính. Khi dịch COVID-19 bùng phát, lượng bệnh nhân cần chụp và đọc phim tăng nhanh hơn năng lực của khoa chẩn đoán hình ảnh, nên bài toán phân loại ảnh X-quang tự động được nghiên cứu nhiều [1]. Tổn thương phổi do SARS-CoV-2 thường là các vùng mờ đục kính mờ và đông đặc, phân bố chủ yếu ở ngoại vi phổi. Những dấu hiệu này không đặc hiệu: viêm phổi do virus khác, viêm phổi không điển hình và cả vùng mờ phổi không do nhiễm trùng đều tạo ra hình ảnh tương tự [1], [2], khiến bài toán bốn lớp khó hơn bài toán hai lớp "COVID hay không COVID".

Bộ dữ liệu COVID-19 Radiography Database tập hợp 21.165 ảnh CXR thuộc bốn lớp: Normal 10.192 ảnh, Lung_Opacity 6.012 ảnh, COVID 3.616 ảnh và Viral Pneumonia 1.345 ảnh [1], [2]. Lớp lớn nhất nhiều gấp 7,6 lần lớp nhỏ nhất. Với phân bố lệch như vậy, một bộ phân loại luôn dự đoán Normal vẫn đạt accuracy xấp xỉ 48% nhưng chỉ đạt macro-F1 0,1627. Đề tài vì thế lấy macro-F1 làm thước đo chính và ghi mốc B0 = 0,1627 làm ngưỡng tầm thường mà mọi cấu hình phải vượt.

Nhãn lớp trong bộ dữ liệu không độc lập hoàn toàn với nguồn thu thập. Toàn bộ 1.345 ảnh Viral Pneumonia lấy từ một bộ dữ liệu Kaggle riêng của P. Mooney[^mooney]; 1.341 trong số 10.192 ảnh Normal cũng từ nguồn này, còn 18.479 ảnh do Chowdhury và cộng sự tập hợp [1], [2]. Nhiều khả năng các ảnh của Mooney là X-quang nhi khoa từ nghiên cứu của Kermany và cộng sự [3]. Nhãn Viral Pneumonia trùng với một nguồn duy nhất, nên mô hình có thể đạt điểm cao trên lớp này nhờ nhận ra khung viền, độ sáng nền, cách xử lý hậu kỳ hoặc kích thước ảnh đặc trưng của nguồn đó, trong khi không hề định vị tổn thương phổi. Geirhos và cộng sự gọi hiện tượng này là học lối tắt (shortcut learning) [4]. Zech và cộng sự ghi nhận mô hình phát hiện viêm phổi từ CXR giảm hiệu năng khi chuyển sang bệnh viện khác, kèm bằng chứng mô hình khai thác dấu hiệu đặc thù của cơ sở dữ liệu huấn luyện [5]. Bộ dữ liệu ghép từ nhiều nguồn nên nguy cơ trên là thực tế, và đề tài đo nó trực tiếp.

Đề tài dùng học máy cổ điển vì học phần quy định như vậy. Cách làm này cũng thuận cho việc đo đóng góp của từng nhóm đặc trưng: mỗi chiều đặc trưng ứng với một phép đo xác định trên ảnh nên so sánh thực nghiệm tách riêng được phần đóng góp của histogram, GLCM kết hợp LBP hay HOG. Toàn bộ pipeline trích đặc trưng thủ công rồi phân loại bằng scikit-learn [6] chạy trên CPU, không cần GPU, tái lập được từ một tệp cấu hình. Khi thay vùng ảnh đưa vào trích đặc trưng, mức thay đổi hiệu năng cho biết vai trò của vùng đó.

Đề tài đặt ba câu hỏi nối tiếp trên cùng một tập validation 3.174 ảnh: nhóm đặc trưng nào hiệu quả nhất, bộ phân loại nào phù hợp nhất với nhóm đặc trưng đó, và mô hình còn giữ được hiệu năng bao nhiêu khi vùng phổi bị che hoặc khi chỉ còn vùng ngoài phổi. Câu hỏi thứ ba dùng để kiểm tra nghi vấn lối tắt: nếu mô hình vẫn cho macro-F1 cao khi chỉ còn vùng ngoài phổi thì nhiều khả năng nó dựa vào tín hiệu không liên quan đến tổn thương; nếu macro-F1 giảm mạnh thì vùng phổi đóng góp phần lớn thông tin.

## 1.2. Mục tiêu và ba câu hỏi nghiên cứu

Mục tiêu của đề tài là xây dựng pipeline phân loại bốn lớp ảnh CXR chỉ bằng học máy cổ điển, đánh giá pipeline trên tập validation theo một giao thức cố định, rồi kiểm tra một lần trên tập test độc lập. Mục tiêu này được cụ thể hoá thành ba câu hỏi nghiên cứu (research question, viết tắt RQ).

Bốn nhóm đặc trưng thủ công gồm histogram độ xám 64 chiều, GLCM (Gray-Level Co-occurrence Matrix) kết hợp LBP (Local Binary Pattern) 88 chiều, HOG (Histogram of Oriented Gradients) 10.404 chiều và nhóm ghép 152 chiều. Sáu bộ phân loại ứng viên gồm Logistic Regression, k-NN, Decision Tree, Random Forest, SVM (Support Vector Machine) và Gradient Boosting.

**RQ1.** Nhóm đặc trưng nào trong bốn nhóm trên cho macro-F1 cao nhất trên tập validation khi dùng một bộ phân loại cố định chọn trước (Random Forest, 500 cây)?

**RQ2.** Với nhóm đặc trưng tốt nhất từ RQ1, bộ phân loại nào trong sáu ứng viên trên đạt macro-F1 cao nhất?

**RQ3.** Che hoặc cắt ảnh theo mặt nạ phổi có làm thay đổi macro-F1 không, và mức thay đổi đó cho biết gì về mức phụ thuộc của mô hình vào vùng ngoài phổi?

Ba câu hỏi dùng chung một giao thức đọc ảnh: ảnh xám 8-bit kích thước 299 × 299, không resize, không cân bằng histogram. Tham số trích đặc trưng và không gian siêu tham số được chốt trước khi chạy và không sửa sau khi xem điểm. Mọi thành phần ngẫu nhiên dùng seed 42, 43 và 44.

**Bảng 1.1: Ba câu hỏi nghiên cứu, thước đo và quy tắc ra quyết định**

| Câu hỏi | Biến độc lập | Thước đo | Quy tắc ra quyết định |
| --- | --- | --- | --- |
| RQ1 | Nhóm đặc trưng, 4 mức | Macro-F1 trung bình 3 seed trên 3.174 ảnh validation | Chọn nhóm cao nhất nếu chênh lệch so với nhóm histogram có khoảng tin cậy 95% không chứa 0 và vượt ngưỡng +0,005 |
| RQ2 | Bộ phân loại, 6 mức | Macro-F1 trên validation, Random Forest làm mốc tham chiếu | Chọn bộ cao nhất nếu khoảng tin cậy 95% của chênh lệch so với mốc không chứa 0 |
| RQ3 | Chế độ mặt nạ, 3 mức tạo 5 kịch bản | Macro-F1 trên validation, so sánh từng cặp kịch bản | Báo cáo toàn bộ 5 kịch bản, không loại kịch bản nào khỏi báo cáo |

Khoảng tin cậy trong Bảng 1.1 tính bằng bootstrap ghép cặp 2.000 lần trên cùng chỉ số ảnh, seed 42. Quy tắc này chỉ dùng để chọn cấu hình đi tiếp; các cấu hình còn lại vẫn được báo cáo đầy đủ. Mọi cấu hình phải vượt thêm mốc nền thứ hai là A0 = 0,2397, tức Random Forest chỉ dùng hai đại lượng đơn giản của tệp ảnh là độ sáng trung bình và định dạng màu, không dùng đặc trưng cấu trúc. Nếu đặc trưng ảnh không vượt được mô hình đó thì kết quả phải được nêu rõ trong báo cáo.

Random Forest ở RQ2 không dùng chung cấu hình với RQ1: siêu tham số được chọn bằng kiểm định chéo 5 fold trên lưới gồm 300 và 500 cây, mỗi giá trị kết hợp với độ sâu 20 hoặc không giới hạn, kết quả chọn 300 cây không giới hạn độ sâu. Vì vậy hai lần chạy cho 0,8599 và 0,8582, chênh nhau xấp xỉ 0,002.

## 1.3. Phạm vi nghiên cứu và ranh giới kỹ thuật

Phạm vi dữ liệu gồm toàn bộ 21.165 ảnh của bộ COVID-19 Radiography Database, chia thành 14.815 ảnh train, 3.174 ảnh validation và 3.176 ảnh test theo tỉ lệ 70/15/15. Phép chia phân tầng theo nhãn và gom nhóm theo pHash, để ảnh trong cùng một nhóm trùng pHash không xuất hiện đồng thời ở hai tập. Tệp split được băm SHA-256 và giữ nguyên trong suốt quá trình thực nghiệm.

Đề tài không dùng học sâu (ràng buộc H7): một bài kiểm thử tự động quét mọi lệnh import trong `src/` và `notebooks/`, chặn `torch`, `torchvision`, `tensorflow`, `keras` và `timm`; vi phạm làm bộ kiểm thử thất bại. Ba ràng buộc còn lại liên quan đến cách đọc dữ liệu được tóm tắt trong Bảng 1.2.

**Bảng 1.2: Ràng buộc kỹ thuật và cơ chế kiểm soát**

| Ràng buộc | Cơ chế kiểm soát |
| --- | --- |
| Không đọc tập test cho bất kỳ quyết định nào trong RQ1–RQ3 (H2) | Mã nguồn mặc định từ chối đọc test; SHA-256 của tệp split; lần mở khóa duy nhất ghi kèm commit và thời điểm |
| Mọi bước học từ dữ liệu chỉ fit trên train (H6) | `StandardScaler` nằm trong pipeline, fit trên 14.815 ảnh train |
| Ảnh xám 8-bit 299 × 299, không resize, không cân bằng histogram | Chốt trong văn bản tiêu chí chấp nhận trước khi chạy |

Nằm ngoài phạm vi của đề tài: chẩn đoán lâm sàng, phân đoạn tổn thương, so sánh với học sâu, tinh chỉnh siêu tham số cho RQ1 và mọi phân tích theo thông tin bệnh nhân. Bộ dữ liệu không cung cấp mã bệnh nhân, tuổi hay tiền sử, nên các kết luận về mặt y khoa chỉ dừng ở mức phân loại hình ảnh.

## 1.4. Đóng góp của đề tài

1. **Phép chia tập có kiểm soát ảnh trùng pHash.** Bước gom nhóm ở ngưỡng T = 0 xác định 178 nhóm gồm 401 ảnh trùng pHash, và toàn bộ ảnh trong một nhóm được gán về cùng một tập trước khi chia 70/15/15.
2. **So sánh bốn nhóm đặc trưng thủ công (RQ1).** Trên 3.174 ảnh validation, nhóm ghép 152 chiều đạt macro-F1 0,8599, cao hơn GLCM kết hợp LBP 0,8156, histogram 0,7829 và HOG 0,7625.

3. **So sánh sáu bộ phân loại (RQ2).** SVM với kernel RBF (radial basis function) đạt macro-F1 0,9024, cao hơn mốc tham chiếu Random Forest 0,8582. Phần kiểm định và khoảng tin cậy để ở Chương 3.

4. **Đo mức phụ thuộc vào vùng ngoài phổi (RQ3).** Năm kịch bản che mặt nạ phổi kết hợp permutation importance trên 10 khối đặc trưng định lượng phần đóng góp của vùng phổi so với phần còn lại của ảnh. Chương 4 trình bày số đo; mọi diễn giải về chênh lệch đều ghi là giả thuyết chưa kiểm chứng (Quy tắc D4).

5. **Ứng dụng minh hoạ.** Ứng dụng Streamlit nhận một ảnh CXR, trả về xác suất bốn lớp và dùng lại đúng hàm trích đặc trưng đã đánh giá.

## 1.5. Cấu trúc báo cáo

Báo cáo gồm sáu chương. Chương 2 trình bày nguồn gốc bộ dữ liệu, quy trình kiểm soát rò rỉ thông tin và phương pháp: bốn nhóm đặc trưng thủ công, bước chuẩn hóa, sáu bộ phân loại và giao thức đánh giá thống kê. Chương 3 trình bày kết quả RQ1 và RQ2 trên 3.174 ảnh validation. Chương 4 giải quyết RQ3 bằng năm kịch bản che mặt nạ phổi.

Chương 5 công bố kết quả trên 3.176 ảnh test, phân tích ma trận nhầm lẫn và mô tả ứng dụng triển khai. Chương 6 thảo luận kết quả, nêu giới hạn của nghiên cứu, cảnh báo về phạm vi sử dụng và đề xuất hướng phát triển. Ba phụ lục gồm hướng dẫn vận hành ứng dụng, cấu trúc kho mã nguồn kèm danh sách bài kiểm thử, và bảng siêu tham số của các lần chạy thực nghiệm.

---

## Tài liệu tham khảo phát sinh trong chương

Các mục dưới đây đánh số theo thứ tự xuất hiện trong Chương 1 và giữ nguyên số khi ghép vào danh mục tài liệu tham khảo cuối quyển; tài liệu của các chương sau đánh tiếp từ [7].

[1] M. E. H. Chowdhury, T. Rahman, A. Khandakar, R. Mazhar, M. A. Kadir, Z. B. Mahbub, K. R. Islam, M. S. Khan, A. Iqbal, N. Al-Emadi, M. B. I. Reaz, and M. T. Islam, "Can AI help in screening viral and COVID-19 pneumonia?," *IEEE Access*, vol. 8, pp. 132665–132676, 2020, doi: 10.1109/ACCESS.2020.3010287.

[2] T. Rahman, A. Khandakar, Y. Qiblawey, A. Tahir, S. Kiranyaz, S. B. A. Kashem, M. T. Islam, S. Al Maadeed, S. M. Zughaier, M. S. Khan, and M. E. H. Chowdhury, "Exploring the effect of image enhancement techniques on COVID-19 detection using chest X-ray images," *Computers in Biology and Medicine*, vol. 132, p. 104319, 2021, doi: 10.1016/j.compbiomed.2021.104319.

[3] D. S. Kermany, M. Goldbaum, W. Cai, et al., "Identifying medical diagnoses and treatable diseases by image-based deep learning," *Cell*, vol. 172, no. 5, pp. 1122–1131.e9, 2018.

[4] R. Geirhos, J.-H. Jacobsen, C. Michaelis, R. Zemel, W. Brendel, M. Bethge, and F. A. Wichmann, "Shortcut learning in deep neural networks," *Nature Machine Intelligence*, vol. 2, no. 11, pp. 665–673, 2020, doi: 10.1038/s42256-020-00257-z.

[5] J. R. Zech, M. A. Badgeley, M. Liu, A. B. Costa, J. J. Titano, and E. K. Oermann, "Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study," *PLOS Medicine*, vol. 15, no. 11, e1002683, 2018, doi: 10.1371/journal.pmed.1002683.

[6] F. Pedregosa, G. Varoquaux, A. Gramfort, et al., "Scikit-learn: Machine learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.

---

## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)

- **Chuyển sang Word:** Heading 1 = 14–16 pt Times New Roman, in hoa, in đậm; Heading 2 = 13–14 pt in đậm; thân bài 13 pt, canh đều hai bên, thụt đầu dòng 1,0–1,27 cm, giãn dòng 1,3.
- **Bảng:** tiêu đề đặt phía trên, cỡ 10–11 pt, in đậm; bảng theo kiểu Booktabs, không kẻ đường dọc.
- **Mã hiệu:** H2, H6, H7 và Quy tắc D4 chỉ dùng trong ngoặc để tra cứu chéo với `results/threshold_v3.md`; nội dung đã diễn giải bằng lời trong chương. `UNLOCK_RECORD.json` là biên bản ghi lần mở khóa tập test duy nhất, có commit và thời điểm.
- **Trích dẫn:** số thứ tự [1]–[6] theo thứ tự xuất hiện. Nếu chèn thêm tài liệu vào chương này, phải đánh lại toàn bộ số về sau.
- **Chú thích chân trang:** `[^mooney]` là nguồn của bộ dữ liệu Kaggle, không tính vào danh mục [1]–[6] nên không làm lệch số thứ tự; khi chuyển sang Word thì chèn thành footnote tại chỗ.
- **Nguồn số liệu:** 21.165 ảnh và phân bố bốn lớp đếm từ `splits/split_v1.csv`; B0, A0 từ `results/threshold_v3.md` mục 3; macro-F1 của RQ1 và RQ2 từ `results/report_rq1/r1_summary.csv` và `results/report_rq2/r1_summary.csv`; khoảng tin cậy từ `results/report_rq1/r1_bootstrap_vs_reference.csv` và `results/report_rq2/r1_bootstrap_vs_reference.csv`; SHA-256 tệp split từ `splits/`; 178 nhóm và 401 ảnh từ `docs/roadmap.md`.
- **Chưa đưa vào chương:** số liệu tập test, để dành cho Chương 5.

[^mooney]: P. Mooney, "Chest X-Ray Images (Pneumonia)," Kaggle, 2018, https://www.kaggle.com/paultimothymooney/chest-xray-pneumonia.
