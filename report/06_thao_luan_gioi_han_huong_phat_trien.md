# CHƯƠNG 6. THẢO LUẬN, GIỚI HẠN VÀ HƯỚNG PHÁT TRIỂN

## 6.1. Thảo luận kết quả đạt được

Cả ba câu hỏi nghiên cứu được trả lời trên cùng một tập 3.174 ảnh validation, giữ nguyên từ đầu đến cuối. Bảng 6.1 gom các kết quả chính để đối chiếu nhanh.

**Bảng 6.1: Tóm tắt macro-F1 của các cấu hình chính và khoảng tin cậy 95%**

| Hạng mục | Macro-F1 | 95% CI | Trình bày ở |
| :--- | ---: | :--- | :--- |
| RQ1: histogram 64 chiều, tham chiếu (Random Forest, TB 3 seed) | 0,7829 | [0,7643; 0,8002] | Bảng 3.1 |
| RQ1: nhóm ghép 152 chiều (Random Forest, TB 3 seed) | 0,8599 | [0,8452; 0,8732] | Bảng 3.1 |
| RQ2: Random Forest, mốc (TB 3 seed) | 0,8582 | [0,8432; 0,8716] | Bảng 3.3 |
| RQ2: SVM RBF, cấu hình được chọn | 0,9024 | [0,8909; 0,9129] | Bảng 3.3 |
| RQ3: ảnh gốc khi huấn luyện và đánh giá | 0,9024 | [0,8909; 0,9129] | Bảng 4.1 |
| RQ3: chỉ còn vùng phổi | 0,8490 | [0,8333; 0,8625] | Bảng 4.1 |
| RQ3: chỉ còn vùng ngoài mặt nạ phổi | 0,8921 | [0,8807; 0,9031] | Bảng 4.1 |
| Tập test độc lập (3.176 ảnh) | 0,8714 | [0,8579; 0,8840] | Bảng 5.1 |

*(Hàng RQ1 và RQ2 lấy trên 3.174 ảnh validation; hàng RQ3 cũng trên validation, một seed; hàng cuối là tập test. Random Forest ở RQ1 (500 cây, cố định) và ở RQ2 (300 cây theo kiểm định chéo) khác cấu hình (mục 3.3) nên chỉ số của bộ này giữa hai bảng không so trực tiếp được. Sáu bộ phân loại ở RQ2 và bốn nhóm đặc trưng ở RQ1 đều vượt hai mốc nền B0 = 0,1627 và A0 = 0,2397.)*

Nhóm ghép 152 chiều hơn histogram 0,0770 điểm macro-F1, khoảng tin cậy [+0,0611; +0,0925] không chứa 0, nên phép thay thế tham chiếu được chấp nhận theo quy tắc đã chốt. Nhóm ghép đã chứa histogram, nên chênh này gắn với việc bổ sung GLCM và LBP. Chi phí đi kèm là thời gian trích đặc trưng gấp 42,5 lần. Cả bốn nhóm đều vượt mốc A0, nên không nhóm nào chỉ đọc được độ sáng và định dạng tệp.

SVM kernel RBF đạt 0,9024, hơn mốc Random Forest 0,0442 với khoảng [+0,0320; +0,0580]. Gradient Boosting cũng hơn mốc 0,0286, nhưng giao thức chỉ so từng bộ với mốc nên đề tài không đưa ra kiểm định nào cho cặp SVM – Gradient Boosting.

Phép đo cho ra ba kết quả. Thứ nhất, chỉ còn vùng ngoài mặt nạ phổi vẫn đạt 0,8921; chênh so với ảnh gốc là 0,0103 với khoảng [−0,0017; +0,0220] chứa 0, nhưng cận trên vẫn vượt ngưỡng 0,005 nên cả hai phép kết luận "khác biệt" lẫn "tương đương" đều không vượt qua được. Thứ hai, mô hình chỉ nhìn vùng ngoài mặt nạ cao hơn mô hình chỉ nhìn vùng trong mặt nạ 0,0431 [+0,0281; +0,0582]. Thứ ba, phép tách theo nguồn: trong 2.237 ảnh cùng nguồn RSNA, lỗi cặp Normal – Lung_Opacity giữ nguyên ở mức gần bằng (10,86% lên 11,85%), và 197 ảnh Normal cùng nguồn Mooney không một ảnh bị đoán thành Viral Pneumonia ở cả ba kịch bản cùng chế độ. Vùng ngoài mặt nạ phổi vì thế mang thông tin liên quan đến lớp, không chỉ liên quan đến nguồn ảnh. Đặc điểm nào được dùng thì chương 4 không xác định được, và đề tài cũng không kết luận được đó có phải lối tắt theo nghĩa của Geirhos và cộng sự [4].

Cấu hình đã chọn cho ra 0,8714 [0,8579; 0,8840] và accuracy 86,56% trên 3.176 ảnh test, thấp hơn validation 0,0310 (mục 5.2). F1 bốn lớp nằm trong khoảng 0,8152 đến 0,9214, và 71,19% lỗi dồn ở cặp Normal – Lung_Opacity; trên validation, cặp này chiếm 76,79% trong 349 lỗi (mục 3.4). Cả hai con số đều là phép đo trên từng tập; chương không nối chúng với nguyên nhân.

Pipeline suy luận xử lý được một ảnh trong khoảng 28–31 ms ngay sau khi máy nghỉ, và đạt trung vị đầu-cuối 131,8 ms khi chạy liên tiếp trong môi trường đã ghi (mục 5.5.4); cổng tương đương khớp nhãn 200/200 với kết quả của pipeline huấn luyện. Đây là minh hoạ phương pháp, chưa phải đánh giá một hệ thống triển khai.

Năm đóng góp đã nêu ở mục 1.4 đều có số liệu tương ứng trong báo cáo: phép chia tập đã kiểm soát ảnh trùng pHash trước khi chia 70/15/15 (mục 2.3 và 2.4); nhóm đặc trưng ghép vượt histogram 0,0770 điểm macro-F1 (mục 3.1); SVM kernel RBF đứng đầu trong sáu bộ phân loại với 0,9024 (mục 3.3); phép che mặt nạ đo được mức giữ hiệu năng khi chỉ còn vùng ngoài mặt nạ phổi (mục 4.1); ứng dụng Streamlit dùng lại đúng hàm trích đặc trưng đã đánh giá (mục 5.5). Hai câu hỏi đề tài không trả lời được: bản chất tín hiệu nằm ngoài vùng nhu mô phổi, và hiệu năng của mô hình trên ảnh của cơ sở khác.

## 6.2. Giới hạn nghiên cứu

Các giới hạn dưới đây đã được đăng ký trước khi chạy trong biên bản tiêu chí chấp nhận và trong biên bản của từng thực nghiệm. Phần liên quan đến dữ liệu đã trình bày ở mục 2.5; ở đây chỉ nhắc lại trong vai trò giới hạn của kết quả.

1. **Ảnh gần trùng xuyên hai tập.** Toàn bộ dữ liệu còn 1.570 cặp có khoảng cách Hamming từ 2 đến 4, trong đó 735 cặp nằm ở hai tập khác nhau; 273 trong 3.174 ảnh validation (8,6%) và 243 trong 3.176 ảnh test (7,7%) có ít nhất một ảnh gần trùng ở tập khác. Bước chia theo nhóm pHash chỉ chặn được trùng tuyệt đối (Hamming 0), nên mô hình có thể đã gặp một bản gần giống lúc huấn luyện; macro-F1 vì thế có thể cao hơn mức thực trên ảnh chưa từng thấy. Phép đo bổ sung ở mục 2.5 cho thấy trên 273 ảnh có ảnh gần trùng mô hình đạt 0,9068, trên 2.901 ảnh còn lại đạt 0,9017, chênh 0,0051; khoảng tin cậy 95% của chênh này là [−0,0462; 0,0386] (bootstrap 2.000 lần lấy mẫu lại độc lập trong từng tập con, seed 42), chứa 0, nên đề tài không kết luận được mức ảnh hưởng, kể cả theo hướng "không ảnh hưởng". Hai tập con có cơ cấu lớp khác nhau và macro-F1 phụ thuộc cơ cấu lớp, nên phép so recall từng lớp ở ghi chú Chương 2 là phép so công bằng hơn.
2. **Không có mã bệnh nhân.** Bộ dữ liệu không cung cấp mã bệnh nhân, nên ảnh của cùng một người chụp ở các ngày khác nhau không gom được; báo cáo gốc cho bộ dữ liệu có khoảng 15.000 bệnh nhân [2], tức một người có thể có nhiều ảnh nằm rải giữa các tập.
3. **Nguồn và tuổi chưa xác minh.** Hai bài báo không mô tả bước tái thẩm định nhãn độc lập, không cung cấp tuổi hay giới tính; lớp Viral Pneumonia và 1.341 ảnh Normal lấy từ cùng một bộ của Mooney (số ảnh còn lại của lớp Normal, 8.851 ảnh, lấy từ RSNA), nên đóng góp của lứa tuổi cho kết quả RQ3 không tách được hoàn toàn. Đối chứng ở mục 4.1 cho thấy một phần đã tách được: 197 ảnh Normal cùng nguồn Mooney không có ảnh nào bị đoán thành Viral Pneumonia ở cả ba kịch bản cùng chế độ; nhãn tuổi vẫn thiếu nên kiểm trực tiếp chưa làm được.
4. **Chọn cấu hình trên validation.** Cùng tập validation dùng để chọn nhóm đặc trưng, chọn bộ phân loại và chọn kịch bản RQ3, nên các số trên validation có xu hướng cao hơn mức thực trên ảnh mới. Điểm trên tập test thấp hơn 0,0310; hai khoảng tin cậy 95% không chồng nhau (cận dưới bên validation, 0,8909, cao hơn cận trên bên test, 0,8840). Ước lượng thô từ độ rộng hai khoảng cho hiệu số bằng khoảng −3,6 lần sai số chuẩn của nó; đây là số mô tả, không phải kiểm định đã đăng ký. Đề tài không đo phần đóng góp của chọn lọc vào mức chênh này, nên không gán nguyên nhân cho nó. Số dùng để trích dẫn kết quả mô hình là con số trên tập test, 0,8714.
5. **Kích thước các nhóm đặc trưng lệch nhau nhiều.** 64, 88, 152 và 10.404 chiều; mỗi lần chia nút, Random Forest chỉ xét một phần nhỏ trong 10.404 chiều của HOG nên thứ hạng nhóm đặc trưng có thể bị lệch do kích thước. Phép so chính của RQ1 lại lấy nhóm có điểm cao nhất rồi mới so với histogram, nên chênh 0,0770 còn mang cả chọn lọc của bước chọn; tuy nhiên nhóm ghép cũng hơn nhóm đứng thứ hai (GLCM kết hợp LBP) tới 0,0443, nên phần lệch do bước chọn có lẽ nhỏ.
6. **Nhóm tham chiếu có thể bắt lối tắt độ sáng.** Histogram dựa trên phân bố cường độ, và đo AUC ở mục 2.2 cho thấy trung vị độ sáng phân biệt được một phần giữa các lớp; biên bản tiêu chí chấp nhận ghi rõ rủi ro này cho nhóm tham chiếu.
7. **Mặt nạ phổi do mạng tự sinh.** Các kịch bản RQ3 dùng mặt nạ kèm bộ dữ liệu, sinh bởi mạng Modified U-Net, không do bác sĩ vẽ, và 2.686 ảnh thuộc nguồn Mooney không có mô tả nguồn gốc mặt nạ (mục 4.1). "Ngoài mặt nạ phổi" vì thế chưa chắc đã là "ngoài phổi", và kết luận RQ3 chỉ giới hạn ở phép che.
8. **Các giả thuyết về vùng ngoài mặt nạ phổi còn mở.** Ba giả thuyết ở mục 4.3 (hình học lồng ngực trẻ nhỏ, ký hiệu thiết bị, dịch chuyển phân phối khi che) đều chưa được kiểm chứng; ba phép kiểm bổ sung có thể chạy trên dữ liệu và mặt nạ đã có (diện tích vùng phổi theo lớp, bộ phân loại chỉ dùng hình học mặt nạ, phân phối đặc trưng theo chế độ ảnh) chưa được thực hiện.
9. **Độ trễ đo ở máy cá nhân.** Số ở mục 5.5.4 ghi nhận trên một máy Windows với môi trường pin của ứng dụng, không phải trên máy chủ triển khai thật; chênh lệch phần cứng làm con số chỉ mang tính minh hoạ cho môi trường đã ghi.
10. **Lớp nhỏ làm rộng khoảng tin cậy theo lớp.** Lớp Viral Pneumonia có 203 ảnh validation và 200 ảnh test. Theo công thức xấp xỉ đã đăng ký, sai số chuẩn của recall là 0,007 cho toàn bộ tập (n = 3.174) nhưng 0,028 cho riêng lớp đó (n = 203); nếu đặt recall thật của lớp vào công thức (191/203 trên validation và 177/200 trên tập test), sai số lần lượt là 0,017 và 0,023, nên chỉ số của lớp nhỏ kém chắc hơn chỉ số toàn cục.
11. **Phạm vi ngoại suy.** Toàn bộ số liệu của đề tài thu được trên một bộ dữ liệu ghép nhiều nguồn; hiệu năng trên ảnh từ cơ sở y tế hoặc thiết bị khác chưa được kiểm, còn nghiên cứu [5] cho thấy hiệu năng có thể giảm khi chuyển sang cơ sở khác. Hạng mục này nằm ngoài biên bản đã đăng ký, được nêu thêm trong quá trình viết báo cáo.

12. **Siêu tham số chọn nằm ở biên lưới.** Năm trong sáu bộ phân loại có ít nhất một siêu tham số chọn ở biên lưới (`lr` và `svm` ở `C=10,0`; `gb` ở 200 cây và độ sâu 5; `dt` ở độ sâu 10; `rf` ở 300 cây). Lưới vì vậy có thể chưa bao hết vùng tối ưu, và thứ hạng giữa các bộ có thể thay đổi nếu mở rộng lưới. Hạng mục này suy ra từ Bảng C.1 và C.2 của Phụ lục C, không phải từ phép đo mới.

## 6.3. Cảnh báo y khoa và đạo đức nghiên cứu

**Cảnh báo y khoa.** Ứng dụng đặt cảnh báo ở đầu trang, cuối trang và thanh bên, với nguyên văn ghi ở mục 5.5.3. Kết quả suy luận của ứng dụng không được dùng để đưa ra quyết định điều trị hay bất kỳ quyết định y khoa nào. Các tài liệu ngoài được trích dẫn là hai bài báo về bộ dữ liệu [1, 2] và nghiên cứu về khả năng tổng quát hoá [5].

**Rủi ro khi triển khai.** Nghiên cứu [5] ghi nhận một mô hình CXR giảm hiệu năng rõ khi sang cơ sở y tế khác. Đề tài này có thêm một lý do để thận trọng, và lý do đó có cơ sở đo: mô hình đạt 0,8921 khi toàn bộ vùng trong mặt nạ phổi bị che đen (mục 4.1), và vùng ngoài mặt nạ phân biệt được cả hai lớp cùng nguồn ảnh. Một mô hình hoạt động được nhờ vùng ngoài mặt nạ phổi trên bộ ghép nhiều nguồn có thể bám vào những dấu vết không phải tổn thương, và những dấu vết đó khác nhau giữa các cơ sở. Điểm validation và test của đề tài vì thế không bảo đảm mô hình hoạt động tương tự ở nơi khác, và chưa có thực nghiệm nào trong đề tài đo phép đó.

**Vấn đề dữ liệu.** Bộ dữ liệu được phát hành với nhãn giấy phép `copyright-authors` kèm dòng hướng dẫn dùng cho mục đích học thuật và phi thương mại (ghi trong biên bản nguồn gốc bộ dữ liệu, mục 2.2), nên đề tài chỉ dùng trong phạm vi đó. Bộ dữ liệu không kèm mã bệnh nhân, tuổi hay giới tính (mục 2.1); repo không phát sinh thêm dữ liệu bệnh nhân nào; 3.176 ảnh của tập test chỉ được đọc đúng một lần trong lần chạy cuối và không được công bố dưới dạng ảnh. Ứng dụng chỉ xử lý ảnh trong bộ nhớ phiên, không ghi ảnh tải lên xuống đĩa, và yêu cầu người dùng chỉ tải ảnh đã ẩn danh.

## 6.4. Hướng phát triển

Các hướng dưới đây nằm trong phạm vi đã đăng ký của đề tài (mục 1.3): học máy cổ điển và đặc trưng thủ công. Mỗi hướng gắn với một giới hạn ở mục 6.2.

1. **Kiểm ba giả thuyết còn mở của RQ3** bằng chính dữ liệu và mặt nạ đã có: diện tích vùng phổi theo lớp, một bộ phân loại chỉ dùng đặc điểm hình học của mặt nạ (diện tích, hộp bao, trọng tâm), và phân phối đặc trưng theo từng chế độ ảnh. Ba phép này không cần ảnh mới và không đụng tập test; chỉ bộ phân loại hình học mặt nạ cần huấn luyện một mô hình nhỏ mới. Chúng chuyển phần diễn giải ở mục 4.3 thành số đo (giới hạn 8).
2. **Chia lại tập sau khi chặn gần trùng.** Chặn cả các cặp Hamming 2–4, chia lại tập, rồi huấn luyện và đánh giá lại cùng cấu hình trên tập mới; phép đo bổ sung đã chạy (macro-F1 trên 273 ảnh có ảnh gần trùng và 2.901 ảnh còn lại, mục 2.5) chỉ dùng dự đoán có sẵn nên chưa tách được ảnh hưởng của bản gần trùng lúc huấn luyện (giới hạn 1).
3. **Ghi nhận mã bệnh nhân và tuổi** nếu dùng lại bộ dữ liệu hoặc khi thu thập thêm, để kiểm trực tiếp giả thuyết nhi khoa ở lớp Viral Pneumonia và rủi ro cùng bệnh nhân (giới hạn 2 và 3).
4. **Đánh giá trên dữ liệu ngoài bộ Kaggle**, gồm ảnh từ cơ sở khác và thiết bị khác, theo đúng cách đánh giá của [5]. Đây mới là bằng chứng cho câu hỏi triển khai (giới hạn 11 và rủi ro ở mục 6.3).
5. **Chuẩn hóa đầu vào trước khi trích đặc trưng**: gỡ hoặc che ký hiệu in ngoài thành ngực và các dấu vết thiết bị, rồi đo lại hiệu năng. Phép này xem mô hình còn giữ được bao nhiêu khi bỏ đi đúng loại tín hiệu mà giả thuyết ở mục 4.3 đề cập (giới hạn 8).
6. **Đo độ trễ trên môi trường triển khai thật** hoặc trên Kaggle CPU với cùng kịch bản đã viết, để có mốc so với môi trường thực nghiệm RQ1 (giới hạn 9).

## 6.5. Kết luận

Đề tài xây dựng và đánh giá một pipeline học máy cổ điển cho bốn lớp ảnh X-quang lồng ngực. RQ1 trả lời: nhóm đặc trưng ghép 152 chiều (histogram 64, GLCM 60, LBP 28) vượt nhóm histogram 64 chiều 0,0770 điểm macro-F1 với khoảng tin cậy không chứa 0, và được chọn làm nhóm đặc trưng cho các câu hỏi sau. RQ2 trả lời: trong sáu bộ phân loại, SVM kernel RBF đạt 0,9024, cao nhất và vượt mốc Random Forest 0,0442. RQ3 trả lời được một phần. Khi che đen vùng trong mặt nạ phổi và chỉ giữ vùng ngoài, mô hình vẫn đạt 0,8921; khi chỉ giữ vùng trong mặt nạ, mô hình đạt 0,8490. Phép tách theo nguồn cho thấy vùng ngoài mặt nạ mang thông tin liên quan đến lớp chứ không chỉ liên quan đến nguồn ảnh. Đề tài không xác định được đặc điểm nào trong vùng đó được dùng, nên không kết luận được đó có phải lối tắt theo nghĩa của Geirhos và cộng sự [4].

Cấu hình đã chọn được đánh giá đúng một lần trên tập test chưa từng bị đọc: macro-F1 0,8714, khoảng tin cậy 95% [0,8579; 0,8840], accuracy 86,56%. Phép trừ với validation cho −0,0310; theo quy tắc đã đăng ký, đây là số đo và không kèm diễn giải nguyên nhân.

Hai ranh giới cần nhắc lại khi dùng kết quả này. Thứ nhất, toàn bộ số liệu thu được trên một bộ dữ liệu ghép nhiều nguồn; nghiên cứu [5] cho thấy hiệu năng của mô hình CXR có thể giảm khi sang cơ sở khác, và đề tài chưa đo phép đó. Thứ hai, kết quả RQ3 cho thấy mô hình dựa được vào vùng ngoài mặt nạ phổi. Riêng về phạm vi sử dụng, mô hình là minh hoạ phương pháp chứ chưa phải một công cụ chẩn đoán, vì chưa được kiểm định lâm sàng. Mã nguồn, bản ghi kết quả và bộ kiểm thử đi kèm báo cáo để mọi phép đo ở trên kiểm lại được.

---

## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)

- **Bảng 6.1:** các giá trị đọc từ `results/report_rq1/r1_summary.csv` (dòng `hist` và `ghep`), `results/report_rq2/r1_summary.csv` (dòng `rf` và `svm`), `results/report_rq3/r1_summary.csv` (dòng `orig_to_orig`, `lung_to_lung`, `out_to_out`) và `results/final_test/final_test_report.json`. Các ô trùng khớp với Bảng 3.1, 3.3, 4.1 và 5.1 của các chương trước; cột "Trình bày ở" trỏ đến bảng tương ứng. Chênh RQ1 0,0770 đọc từ `results/report_rq1/r1_bootstrap_vs_reference.csv`; chênh RQ2 0,0442 và chênh Gradient Boosting 0,0286 đọc từ `results/report_rq2/r1_bootstrap_vs_reference.csv`; chênh RQ3 0,0103, 0,0431 đọc từ `results/report_rq3/r3_shortcut_bootstrap.csv`. Tỷ lệ 42,5 lần giữa chi phí trích đặc trưng tính từ hai giá trị chưa làm tròn trong `results/rq1_cost_rank_record.md`.
- **Mục 6.2:** các hạng mục từ `results/threshold_v3.md` mục 6 (R5): hạng 1, 2, 3, 5, 6 và hạng 10 (R4, sai số 0,007 và 0,028 tại p = 0,8; recall thật của lớp nhỏ tính từ `results/report_rq3/r1_confusion_matrices.json` và `results/final_test/confusion_matrix.json`); hạng 11 không thuộc biên bản đã đăng ký, nguồn là nghiên cứu [5] và mục 6.5 của chương; hạng 12 không thuộc biên bản đã đăng ký, suy ra từ Bảng C.1 và C.2 của Phụ lục C trong đợt rà cuối; số 735 cặp, 273/243 ảnh và phân bố theo khoảng cách Hamming ở mục 2.5 của Chương 2; khoảng tin cậy của hiệu số 0,0051 tính bằng bootstrap 2.000 lần lấy mẫu lại độc lập trong từng tập con (seed 42), sinh bởi `scripts/val_near_duplicate_subset.py` và ghi trong `results/val_near_duplicate_subset/val_near_duplicate_subset.json`; phép tách nguồn ở Bảng 4.4; mặt nạ ở bullet "Mặt nạ phổi" của Ghi chú kỹ thuật Chương 4 (mục 3.2 của `docs/dataset_provenance.md`); độ trễ ở mục 5.5.4 và hai bản ghi trong `results/demo_latency_*`.
- **Mục 6.3:** trích dẫn cánh báo đọc từ `demo/streamlit_app.py` dòng 60–64; điều khoản giấy phép (`copyright-authors`, "Academic/Non-Commercial Use") ở `docs/dataset_provenance.md` mục 2.2; cách xử lý ảnh tải lên ở `demo/README.md` mục "Giới hạn và an toàn"; trích dẫn [5] đã có số thứ tự từ Chương 1.
- **Mục 6.4:** các hướng 1, 3, 5 xuất phát từ các phép kiểm bổ sung đã ghi trong kế hoạch rà soát Chương 4 (diện tích vùng phổi theo lớp, hình học mặt nạ, phân phối đặc trưng theo chế độ); hướng 2 từ giới hạn Hamming 2–4 trong R5; hướng 4 từ [5]; hướng 6 từ giới hạn môi trường đo ở mục 5.5.4. Đề tài chưa có số liệu cho bất kỳ hướng nào, nên mục này không đưa ra ước lượng kết quả.
