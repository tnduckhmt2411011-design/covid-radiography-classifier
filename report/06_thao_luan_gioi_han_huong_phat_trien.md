# CHƯƠNG 6. THẢO LUẬN, GIỚI HẠN VÀ HƯỚNG PHÁT TRIỂN

## 6.1. Thảo luận kết quả đạt được

Ba câu hỏi nghiên cứu đã có câu trả lời bằng số đo, mỗi câu trên một tập ảnh giữ cố định. Bảng 6.1 gom các kết quả chính để đối chiếu nhanh.

**Bảng 6.1: Tóm tắt macro-F1 của các cấu hình chính và khoảng tin cậy 95%**

| Hạng mục | Macro-F1 | 95% CI | Trình bày ở |
| :--- | ---: | :--- | :--- |
| RQ1 — histogram 64 chiều, tham chiếu (Random Forest, TB 3 seed) | 0,7829 | [0,7643; 0,8002] | Bảng 3.1 |
| RQ1 — nhóm ghép 152 chiều (Random Forest, TB 3 seed) | 0,8599 | [0,8452; 0,8732] | Bảng 3.1 |
| RQ2 — Random Forest, mốc (TB 3 seed) | 0,8582 | [0,8432; 0,8716] | Bảng 3.3 |
| RQ2 — SVM RBF, cấu hình được chọn | 0,9024 | [0,8909; 0,9129] | Bảng 3.3 |
| RQ3 — ảnh gốc ở cả hai tập | 0,9024 | [0,8909; 0,9129] | Bảng 4.1 |
| RQ3 — chỉ còn vùng phổi | 0,8490 | [0,8333; 0,8625] | Bảng 4.1 |
| RQ3 — chỉ còn vùng ngoài phổi | 0,8921 | [0,8807; 0,9031] | Bảng 4.1 |
| Tập test độc lập (3.176 ảnh) | 0,8714 | [0,8579; 0,8840] | Bảng 5.1 |

*(Hàng RQ1 và RQ2 lấy trên 3.174 ảnh validation; hàng RQ3 cũng trên validation, một seed; hàng cuối là tập test. Random Forest của RQ1 và RQ2 khác cấu hình (mục 3.3) nên hai con số 0,7829 và 0,8582 không đặt thẳng cạnh nhau được. Sáu bộ phân loại ở RQ2 và bốn nhóm đặc trưng ở RQ1 đều vượt hai mốc nền B0 = 0,1627 và A0 = 0,2397.)*

**RQ1.** Nhóm ghép 152 chiều hơn histogram 0,0770 điểm macro-F1, khoảng tin cậy [+0,0611; +0,0925] không chứa 0, nên phép thay thế tham chiếu được chấp nhận theo quy tắc đã chốt. Nhóm ghép đã chứa histogram, nên chênh này gắn với việc bổ sung GLCM và LBP. Chi phí đi kèm là thời gian trích đặc trưng gấp 42,5 lần. Cả bốn nhóm đều vượt mốc A0, nên không nhóm nào chỉ đọc được độ sáng và định dạng tệp.

**RQ2.** SVM kernel RBF đạt 0,9024, hơn mốc Random Forest 0,0442 với khoảng [+0,0320; +0,0580]. Gradient Boosting cũng hơn mốc 0,0286, nhưng giao thức chỉ so từng bộ với mốc nên đề tài không đưa ra kiểm định nào cho cặp SVM – Gradient Boosting.

**RQ3.** Phép đo cho ba kết quả. Một, chỉ còn vùng ngoài mặt nạ phổi vẫn đạt 0,8921; chênh so với ảnh gốc là 0,0103 với khoảng [−0,0017; +0,0220] chứa 0, nhưng cận trên vẫn vượt ngưỡng 0,005 nên cả hai phép kết luận "khác biệt" lẫn "tương đương" đều không vượt qua được. Hai, mô hình chỉ nhìn vùng ngoài mặt nạ cao hơn mô hình chỉ nhìn vùng trong mặt nạ 0,0431 [+0,0281; +0,0582]. Ba, phép tách theo nguồn: trong 2.237 ảnh cùng nguồn RSNA, lỗi cặp Normal – Lung_Opacity giữ nguyên ở mức gần bằng (10,86% lên 11,85%), và 197 ảnh Normal cùng nguồn Mooney không một ảnh bị đoán thành Viral Pneumonia ở cả ba kịch bản cùng chế độ. Vùng ngoài mặt nạ phổi vì thế mang thông tin liên quan đến lớp, không chỉ liên quan đến nguồn ảnh. Đặc điểm nào được dùng thì chương 4 không xác định được, và đề tài cũng không kết luận được đó có phải lối tắt theo nghĩa của Geirhos và cộng sự [4].

**Tập test.** Cấu hình đã chọn cho ra 0,8714 [0,8579; 0,8840] và accuracy 86,56% trên 3.176 ảnh test, thấp hơn validation 0,0310 (mục 5.2). F1 bốn lớp nằm trong khoảng 0,8152 đến 0,9214, và 71,19% lỗi dồn ở cặp Normal – Lung_Opacity; trên validation, cặp này chiếm 76,79% trong 349 lỗi (mục 3.4). Cả hai con số đều là phép đo trên từng tập; theo quy tắc D4, chương không nối chúng với nguyên nhân.

**Ứng dụng.** Pipeline suy luận chạy được trên một ảnh với trung vị 131,8 ms ở môi trường đã ghi (mục 5.5.4), và cổng tương đương khớp nhãn 200/200 với kết quả của pipeline huấn luyện. Đây là minh hoạ phương pháp chứ chưa phải đánh giá một hệ thống triển khai.

Nhìn lại toàn đề tài, năm điều đạt được: một pipeline học máy cổ điển truy vết được từng bước; một lần công bố số liệu test duy nhất kèm khoảng tin cậy; phép đo mức phụ thuộc vào vùng ngoài phổi trên năm kịch bản; một bộ kiểm thử chặn vi phạm quy trình; và một ứng dụng minh hoạ dùng lại đúng hàm đã đánh giá. Điều đề tài không trả lời được là bản chất tín hiệu nằm ngoài vùng phổi, và khả năng hoạt động của mô hình trên dữ liệu của cơ sở khác.

## 6.2. Giới hạn nghiên cứu

Các giới hạn dưới đây đã được đăng ký trước khi chạy trong biên bản tiêu chí chấp nhận (mục Báo cáo bắt buộc, R1–R5) và trong biên bản của từng thực nghiệm. Phần liên quan đến dữ liệu đã trình bày ở mục 2.5; ở đây chỉ nhắc lại trong vai trò giới hạn của kết quả.

1. **Ảnh gần trùng xuyên hai tập.** Toàn bộ dữ liệu còn 1.570 cặp có khoảng cách Hamming từ 2 đến 4, trong đó 735 cặp nằm ở hai tập khác nhau; 273 trong 3.174 ảnh validation (8,6%) và 243 trong 3.176 ảnh test (7,7%) có ít nhất một ảnh gần trùng ở tập khác. Kiểm định chéo chỉ chặn được trùng pHash tuyệt đối (Hamming 0), nên mô hình có thể đã gặp một bản gần giống lúc huấn luyện; macro-F1 vì thế có thể cao hơn mức thực trên ảnh chưa từng thấy. Đề tài chưa đo mức chênh này.
2. **Không có mã bệnh nhân.** Bộ dữ liệu không cung cấp mã bệnh nhân, nên ảnh của cùng một người chụp ở các ngày khác nhau không gom được; rủi ro cùng bệnh nhân nằm ở cả hai phía của ranh giới train–validation.
3. **Nguồn và tuổi chưa xác minh.** Hai bài báo không mô tả bước tái thẩm định nhãn độc lập, không cung cấp tuổi hay giới tính; lớp Viral Pneumonia và phần lớn lớp Normal lấy từ cùng một bộ của Mooney nên không tách được đóng góp của lứa tuổi cho kết quả RQ3.
4. **Chọn cấu hình trên validation.** Cùng tập validation dùng để chọn nhóm đặc trưng, chọn bộ phân loại và chọn kịch bản RQ3, nên các số trên validation mang tính chọn lọc. Phép đo trên tập test cho giá trị thấp hơn validation 0,0310; theo quy tắc D4, chương không nối phép đo này với nguyên nhân chọn lọc đó.
5. **Kích thước các nhóm đặc trưng lệch nhau nhiều.** 64, 88, 152 và 10.404 chiều; mỗi lần chia nút, Random Forest chỉ xét một phần nhỏ trong 10.404 chiều của HOG nên thứ hạng nhóm đặc trưng có thể bị lệch do kích thước. Phép so chính của RQ1 lại lấy nhóm khác histogram có điểm cao nhất rồi mới so với histogram, nên chênh 0,0770 còn mang cả chọn lọc của bước chọn.
6. **Nhóm tham chiếu có thể bắt lối tắt độ sáng.** Histogram dựa trên phân bố cường độ, và đo AUC ở mục 2.2 cho thấy trung vị độ sáng phân biệt được một phần giữa các lớp; R5 ghi rõ rủi ro này cho nhóm tham chiếu.
7. **Mặt nạ phổi do mạng tự sinh.** Các kịch bản RQ3 dùng mặt nạ kèm bộ dữ liệu, sinh bởi mạng Modified U-Net chứ không phải bác sĩ vẽ, và 2.686 ảnh thuộc nguồn Mooney không có mô tả nguồn gốc mặt nạ (mục 4.1). "Ngoài mặt nạ phổi" vì thế chưa chắc đã là "ngoài phổi", và kết luận RQ3 chỉ giới hạn ở phép che.
8. **Các giả thuyết về vùng ngoài phổi còn mở.** Ba giả thuyết ở mục 4.3 (hình học lồng ngực trẻ nhỏ, ký hiệu thiết bị, dịch chuyển phân phối khi che) đều chưa được kiểm chứng; ba phép kiểm bổ sung có thể chạy trên dữ liệu và mặt nạ đã có (diện tích vùng phổi theo lớp, bộ phân loại chỉ dùng hình học mặt nạ, phân phối đặc trưng theo chế độ ảnh) chưa được thực hiện.
9. **Độ trễ đo ở máy cá nhân.** Số ở mục 5.5.4 ghi nhận trên một máy Windows với môi trường pin của ứng dụng, không phải trên máy chủ triển khai thật; chênh lệch phần cứng làm con số chỉ mang tính minh hoạ cho môi trường đã ghi.
10. **Lớp nhỏ làm rộng khoảng tin cậy theo lớp.** Lớp Viral Pneumonia có 203 ảnh validation và 200 ảnh test. Sai số lấy mẫu xấp xỉ theo R4 với p = 0,8 là 0,007 cho toàn bộ tập (n = 3.174) nhưng 0,028 cho riêng lớp đó (n = 203), nên chỉ số của lớp nhỏ kém chắc hơn chỉ số toàn cục.

## 6.3. Cảnh báo y khoa và đạo đức nghiên cứu

**Cảnh báo y khoa.** Ứng dụng đặt cảnh báo ở đầu trang, cuối trang và thanh bên: *"KHÔNG DÙNG ĐỂ CHẨN ĐOÁN. Đây là demo học thuật của mô hình học máy truyền thống, không phải thiết bị y tế và chưa được kiểm định lâm sàng."* Kết quả suy luận của ứng dụng không được dùng để đưa ra quyết định điều trị hay bất kỳ quyết định y khoa nào. Báo cáo không quy khuyến cáo nào của tổ chức y tế cho kết luận này; các tài liệu ngoài được trích dẫn là hai bài báo về bộ dữ liệu [1, 2] và nghiên cứu về khả năng tổng quát hoá [5].

**Rủi ro khi triển khai.** Nghiên cứu [5] ghi nhận một mô hình CXR giảm hiệu năng rõ khi sang cơ sở y tế khác. Đề tài này có thêm một lý do để thận trọng, và lý do đó là số đo chứ không phải suy đoán: mô hình đạt 0,8921 khi toàn bộ vùng trong mặt nạ phổi bị che đen (mục 4.1), và vùng ngoài mặt nạ phân biệt được cả hai lớp cùng nguồn ảnh. Một mô hình hoạt động được nhờ vùng ngoài phổi trên bộ ghép nhiều nguồn có thể bám vào những dấu vết không phải tổn thương, và những dấu vết đó khác nhau giữa các cơ sở. Điểm validation và test của đề tài vì thế không bảo đảm mô hình hoạt động tương tự ở nơi khác, và chưa có thực nghiệm nào trong đề tài đo phép đó.

**Vấn đề dữ liệu.** Bộ dữ liệu được phát hành với nhãn giấy phép `copyright-authors` kèm dòng hướng dẫn dùng cho mục đích học thuật và phi thương mại (ghi trong biên bản nguồn gốc bộ dữ liệu, mục 2.2), nên đề tài chỉ dùng trong phạm vi đó. Bộ dữ liệu không kèm mã bệnh nhân, tuổi hay giới tính (mục 2.1); repo không phát sinh thêm dữ liệu bệnh nhân nào; 3.176 ảnh của tập test chỉ được đọc đúng một lần trong lần chạy cuối và không được công bố dưới dạng ảnh. Ứng dụng chỉ xử lý ảnh trong bộ nhớ phiên, không ghi ảnh tải lên xuống đĩa, và yêu cầu người dùng chỉ tải ảnh đã ẩn danh.

## 6.4. Hướng phát triển

Các hướng dưới đây nằm trong phạm vi đã đăng ký của đề tài (mục 1.3): học máy cổ điển và đặc trưng thủ công. Mỗi hướng gắn với một giới hạn ở mục 6.2.

1. **Kiểm ba giả thuyết còn mở của RQ3** bằng chính dữ liệu và mặt nạ đã có: diện tích vùng phổi theo lớp, một bộ phân loại chỉ dùng đặc điểm hình học của mặt nạ (diện tích, hộp bao, trọng tâm), và phân phối đặc trưng theo từng chế độ ảnh. Cả ba đều không cần huấn luyện lại, và chuyển phần diễn giải ở mục 4.3 thành số đo (giới hạn 8).
2. **Chặn gần trùng rồi đánh giá lại.** Chia lại tập sau khi chặn cả các cặp Hamming 1–4, huấn luyện và đánh giá cùng cấu hình, để đo mức chênh với 0,8714 hiện tại (giới hạn 1).
3. **Ghi nhận mã bệnh nhân và tuổi** nếu dùng lại bộ dữ liệu hoặc khi thu thập thêm, để kiểm trực tiếp giả thuyết nhi khoa ở lớp Viral Pneumonia và rủi ro cùng bệnh nhân (giới hạn 2 và 3).
4. **Đánh giá trên dữ liệu ngoài bộ Kaggle** — ảnh từ cơ sở khác, thiết bị khác, theo đúng cách đánh giá của [5]. Đây mới là bằng chứng cho câu hỏi triển khai (giới hạn 4 và rủi ro ở mục 6.3).
5. **Chuẩn hóa đầu vào trước khi trích đặc trưng**: gỡ hoặc che ký hiệu in ngoài thành ngực và các dấu vết thiết bị, rồi đo lại hiệu năng. Phép này xem mô hình còn giữ được bao nhiêu khi bỏ đi đúng loại tín hiệu mà giả thuyết ở mục 4.3 đề cập (giới hạn 6 và 8).
6. **Đo độ trễ trên môi trường triển khai thật** hoặc trên Kaggle CPU với cùng kịch bản đã viết, để có mốc so với môi trường thực nghiệm RQ1 (giới hạn 9).

## 6.5. Kết luận

Đề tài xây dựng và đánh giá một pipeline học máy cổ điển cho bốn lớp ảnh X-quang lồng ngực. RQ1 trả lời: nhóm đặc trưng ghép 152 chiều (histogram 64, GLCM 60, LBP 28) vượt nhóm histogram 64 chiều 0,0770 điểm macro-F1 với khoảng tin cậy không chứa 0, và được chọn làm nhóm đặc trưng cho các câu hỏi sau. RQ2 trả lời: trong sáu bộ phân loại, SVM kernel RBF đạt 0,9024, cao nhất và vượt mốc Random Forest 0,0442. RQ3 trả lời một nửa: che vùng ngoài mặt nạ phổi không làm mô hình mất khả năng phân loại (0,8921), và phép tách theo nguồn cho thấy vùng này mang thông tin liên quan đến lớp; đặc điểm nào được dùng thì không xác định được, nên đề tài cũng không kết luận được đó có phải lối tắt theo nghĩa của Geirhos và cộng sự [4].

Cấu hình đã chọn được đánh giá đúng một lần trên tập test chưa từng bị đọc: macro-F1 0,8714, khoảng tin cậy 95% [0,8579; 0,8840], accuracy 86,56%. Phép trừ với validation cho −0,0310; theo quy tắc D4, đây là số đo và không kèm diễn giải nguyên nhân.

Hai ranh giới cần nhắc lại khi dùng kết quả này. Thứ nhất, toàn bộ số liệu thu được trên một bộ dữ liệu ghép nhiều nguồn; nghiên cứu [5] cho thấy hiệu năng của mô hình CXR có thể giảm khi sang cơ sở khác, và đề tài chưa đo phép đó. Thứ hai, kết quả RQ3 cho thấy mô hình dựa được vào vùng ngoài phổi, nên mô hình là minh hoạ phương pháp chứ không phải công cụ chẩn đoán. Mã nguồn, bản ghi kết quả và bộ kiểm thử đi kèm báo cáo để mọi phép đo ở trên kiểm lại được.

---

## Ghi chú kỹ thuật (không thuộc nội dung báo cáo)

- **Bảng 6.1:** các giá trị đọc từ `results/report_rq1/r1_summary.csv` (dòng `hist` và `ghep`), `results/report_rq2/r1_summary.csv` (dòng `rf` và `svm`), `results/report_rq3/r1_summary.csv` (dòng `orig_to_orig`, `lung_to_lung`, `out_to_out`) và `results/final_test/final_test_report.json`. Các ô trùng khớp với Bảng 3.1, 3.3, 4.1 và 5.1 của các chương trước; cột "Trình bày ở" trỏ đến bảng tương ứng. Chênh RQ1 0,0770 đọc từ `results/report_rq1/r1_bootstrap_vs_reference.csv`; chênh RQ2 0,0442 và chênh Gradient Boosting 0,0286 đọc từ `results/report_rq2/r1_bootstrap_vs_reference.csv`; chênh RQ3 0,0103, 0,0431 đọc từ `results/report_rq3/r3_shortcut_bootstrap.csv`. Tỷ lệ 42,5 lần giữa chi phí trích đặc trưng tính từ hai giá trị chưa làm tròn trong `results/rq1_cost_rank_record.md`.
- **Mục 6.2:** các hạng mục từ `results/threshold_v3.md` mục 6 (R5) — hạng 1, 2, 3, 5, 6 và hạng 10 (R4, sai số 0,007 và 0,028 tại p = 0,8); số 735 cặp, 273/243 ảnh và phân bố theo khoảng cách Hamming ở mục 2.5 của Chương 2; phép tách nguồn ở Bảng 4.4; mặt nạ ở bullet "Mặt nạ phổi" của Ghi chú kỹ thuật Chương 4 (mục 3.2 của `docs/dataset_provenance.md`); độ trễ ở mục 5.5.4 và hai bản ghi trong `results/demo_latency_*`.
- **Mục 6.3:** trích dẫn cánh báo đọc từ `demo/streamlit_app.py` dòng 60–64; điều khoản giấy phép (`copyright-authors`, "Academic/Non-Commercial Use") ở `docs/dataset_provenance.md` mục 2.2; cách xử lý ảnh tải lên ở `demo/README.md` mục "Giới hạn và an toàn"; trích dẫn [5] đã có số thứ tự từ Chương 1.
- **Mục 6.4:** các hướng 1, 3, 5 xuất phát từ các phép kiểm bổ sung đã ghi trong kế hoạch rà soát Chương 4 (diện tích vùng phổi theo lớp, hình học mặt nạ, phân phối đặc trưng theo chế độ); hướng 2 từ giới hạn Hamming 1–4 trong R5; hướng 4 từ [5]; hướng 6 từ giới hạn môi trường đo ở mục 5.5.4. Đề tài chưa có số liệu cho bất kỳ hướng nào, nên mục này không đưa ra ước lượng kết quả.
