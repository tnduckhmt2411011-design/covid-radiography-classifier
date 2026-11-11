# Cẩm nang Văn phong Khoa học Tiếng Việt và Quy chuẩn Tránh "AI Slop"

> **Tài liệu hướng dẫn kỹ thuật hành văn cho Báo cáo Bài tập lớn / Đồ án Tốt nghiệp**  
> **Cơ sở tham chiếu:**  
> * Phong cách ngôn ngữ khoa học tiếng Việt & Nghị định 30/2020/NĐ-CP của Chính phủ.  
> * Thông tư số 49/2026/TT-BGDĐT của Bộ Giáo dục & Đào tạo về ứng dụng công nghệ và liêm chính học thuật.  
> * Quyết định số 06/QĐ-NXB ĐHCT của Trường Đại học Cần Thơ về kiểm soát trùng lặp và liêm chính khoa học.  
> * Nghiên cứu quốc tế về "vết tích ngôn ngữ AI" (*Science Advances* 2025, Stanford / ICML 2024).  
> **Áp dụng trực tiếp:** Thư mục báo cáo `report/` (công việc **S6-01**) và rà soát định dạng (**S6-04**).

---

## Mục 1. Tính Cấp thiết và Bản chất của "AI Slop" trong Báo cáo Tiếng Việt

### 1.1. Khái niệm "AI Slop Tiếng Việt"
**AI Slop** (nội dung rác nhân tạo) trong văn bản tiếng Việt là hiện tượng văn bản được sinh ra bởi các mô hình ngôn ngữ lớn (ChatGPT, Gemini, Claude...) mang đặc trưng: **bề ngoài trôi chảy, bóng bẩy nhưng rỗng tuếch về thông tin, sáo rỗng về ngữ nghĩa, lạm dụng từ đao to búa lớn và thiếu vắng bằng chứng thực nghiệm cụ thể**.

Trong môi trường học thuật đại học Việt Nam, việc để văn bản báo cáo vướng phải "AI Slop" gây ra 3 tác hại nghiêm trọng:
1. **Mất độ tin cậy khoa học:** Hội đồng chấm điểm và giảng viên phản biện nhận diện ngay giọng điệu máy móc, dẫn đến nghi ngờ về tính xác thực của số liệu thực nghiệm.
2. **Vi phạm liêm chính học thuật:** Vi phạm Thông tư 49/2026/TT-BGDĐT và quy chế của Đại học Cần Thơ (QĐ 06/QĐ-NXB ĐHCT) nếu sử dụng văn bản AI tạo sẵn mà không có sự kiểm chứng và lao động trí tuệ của sinh viên.
3. **Phá vỡ tính chuẩn mực của Tiếng Việt khoa học:** Biến bài báo cáo kỹ thuật thành bài văn quảng cáo (marketing copy) hoặc văn dịch máy thô thiển.

---

## Mục 2. 5 "Bệnh Ngôn ngữ" Điển hình của AI Slop Tiếng Việt Cần Triệt tiêu

### Bệnh 1: Dịch thô các cụm từ sáo rỗng (Machine-Translation Clichés)
AI thường chuyển ngữ nguyên xi các thành ngữ/tính từ "thần chú" từ tiếng Anh sang tiếng Việt:
* ❌ *Tránh:* "bức tranh toàn cảnh đa sắc" (*rich tapestry*), "miền đất màu mỡ" (*rich realm*), "minh chứng hùng hồn/sống động" (*testament to*), "ngọn hải đăng soi sáng" (*beacon*), "lặn sâu vào tìm hiểu" (*delve into*), "bản giao hưởng công nghệ" (*symphony*).
* ✅ *Sửa lại:* Dùng từ ngữ kỹ thuật chính xác: **không gian bài toán, kết quả thực nghiệm chỉ ra, bằng chứng đo đạc cho thấy, phân tích cơ chế, khảo sát**.

### Bệnh 2: Mô-típ mở đầu và kết luận rập khuôn (Formulaic Openings & Endings)
Đoạn văn nào cũng bắt đầu hoặc kết thúc bằng các công thức rập khuôn:
* ❌ *Tránh mở đầu:* *"Trong bối cảnh kỷ nguyên số/trí tuệ nhân tạo đang chuyển mình mạnh mẽ...", "Không thể phủ nhận rằng...", "Đóng vai trò như một nhân tố tối thượng..."*
* ❌ *Tránh kết luận:* *"Nhìn chung, điều này nhấn mạnh tầm quan trọng to lớn của...", "Qua đó mở ra một chân trời mới và đóng góp vào sự phát triển bền vững..."*
* ✅ *Sửa lại:* Đi thẳng vào bản chất kỹ thuật: *"Bộ dữ liệu COVID-19 Radiography Database chứa 21.165 ảnh phân bố trên 4 lớp..."*. Kết luận bằng số đo: *"Mô hình SVM đạt F1 = 0.8714 trên tập test, ghi nhận mức giảm 0.0310 so với validation"*.

### Bệnh 3: Bệnh "Danh từ hóa rườm rà" (Nominalization Overload)
Lỗi ghép chồng chéo các từ chỉ hành động thành danh từ chung chung, khiến câu văn nặng nề:
* ❌ *Tránh:* *"Chúng tôi tiến hành việc thực hiện quá trình triển khai việc trích xuất đặc trưng và đưa ra đánh giá..."* (17 từ)
* ✅ *Sửa lại:* *"Nhóm trích xuất 152 chiều đặc trưng và đánh giá bằng mô hình SVM..."* (12 từ, gọn gàng, trực diện).

### Bệnh 4: Nhồi nhét liên từ nối (Connector Stacking)
Đầu mỗi câu liên tiếp xuất hiện các liên từ cứng nhắc, tạo cảm giác máy móc:
* ❌ *Tránh:* *"Hơn thế nữa,... Thêm vào đó,... Mặt khác,... Tóm lại là,... Ngoài ra,... Do đó,..."*
* ✅ *Sửa lại:* Tạo mạch liên kết tự nhiên bằng logic ngữ nghĩa giữa các câu (liên kết ngầm), dùng cấu trúc đối chiếu trực tiếp: *"Ngược lại", "Cụ thể", "Đối chiếu với kết quả RQ1", "Về mặt định lượng"*.

### Bệnh 5: Cặp cấu trúc đối xứng "Bộ ba hoàn hảo" và Lời khen thổi phồng
AI luôn chia ý thành 3 vế cân xứng chằn chặn và dùng tính từ tâng bốc:
* ❌ *Tránh:* *"Phương pháp không chỉ tối ưu hóa thời gian, nâng cao độ chính xác, mà còn khẳng định sự vượt trội hoàn hảo không tì vết, mang tính bước ngoặt lịch sử."*
* ✅ *Sửa lại:* Đưa con số đo đạc cụ thể: *"Nhóm đặc trưng ghép (152 chiều) đạt Macro-F1 = 0,8599 trên Random Forest, cao hơn nhóm HOG (0,7625) và nhóm histogram (0,7829)."*

---

## Mục 3. Bảng Tra cứu Chuyển đổi: Từ vựng AI Slop $\rightarrow$ Tiếng Việt Học thuật

| Ngữ cảnh học thuật | Từ vựng AI Slop (CẤM DÙNG) | Diễn đạt Chuẩn mực Khoa học (NÊN DÙNG) |
| :--- | :--- | :--- |
| **Phân tích / Đánh giá** | Đi sâu tìm hiểu, lặn sâu vào bản chất, mổ xẻ tường tận, thấu suốt | Khảo sát, phân tích định lượng, đánh giá thực nghiệm, kiểm chứng giả thuyết |
| **Vai trò / Mức độ** | Vai trò tối thượng, ngọn hải đăng dẫn lối, chiếc chìa khóa vạn năng | Yếu tố chính, nhân tố ảnh hưởng trực tiếp, đóng vai trò chủ đạo |
| **Bối cảnh nghiên cứu** | Bức tranh đa sắc, miền đất mới, vũ trụ bao la, kỷ nguyên bùng nổ | Phạm vi đề tài, không gian bài toán, tập dữ liệu thực nghiệm |
| **Bằng chứng / Kết quả** | Minh chứng hùng hồn, minh chứng sống động, bản anh hùng ca | Bằng chứng thực nghiệm cho thấy, số liệu Bảng X phản ánh, kết quả đo đạc chỉ ra |
| **Độ chính xác** | Hoàn hảo không tì vết, chính xác tuyệt đối, cẩn trọng tột cùng | Độ tin cậy cao, kiểm soát sai số chặt chẽ, tuân thủ quy chuẩn đo lường |
| **Hiệu năng mô hình** | Hiệu năng thần kỳ, sức mạnh vượt bậc, bước ngoặt mang tính cách mạng | Hiệu năng cải thiện đáng kể ($\Delta \ge 0.005$), độ chính xác phân lớp vượt trội |
| **Tính liên kết** | Liền mạch như dòng chảy, nhịp nhàng như giao hưởng | Tương thích trực tiếp, pipeline khép kín, định dạng chuẩn hóa thống nhất |
| **Câu chuyển tiếp** | Hơn thế nữa, Thêm vào đó, Không thể không nhắc đến | Xét về phương diện..., Đối chiếu với..., Cụ thể..., Đáng chú ý là... |

---

## Mục 4. Kỹ thuật Viết Tiếng Việt Học thuật "Mượt mà và Đanh thép"

Để bài viết vừa đáp ứng tính hàn lâm vừa lôi cuốn, mượt mà người đọc, hãy áp dụng 3 kỹ thuật biên tập sau:

### 1. Kỹ thuật "Nhịp điệu câu biến thiên" (Sentence Burstiness)
Không viết toàn câu dài hoặc toàn câu ngắn. Hãy xen kẽ:
* **Câu ngắn (dưới 10 từ):** Dùng để khẳng định một sự thật khoa học không thể chối cãi.
* **Câu phức (15 – 25 từ):** Dùng để diễn giải logic, phân tích quan hệ nhân quả và điều kiện thực nghiệm.
* **Ví dụ mẫu:**
  > *"Tập test đã được khóa vĩnh viễn. Trong suốt quá trình thực nghiệm RQ1 và RQ2, nhóm chỉ sử dụng 5-fold cross-validation trên 14.815 ảnh train và đánh giá lựa chọn cấu hình trên 3.174 ảnh validation. Quy trình này bảo đảm tuyệt đối tính khách quan, triệt tiêu nguy cơ rò rỉ thông tin sang 3.176 ảnh của tập kiểm tra độc lập."*

### 2. Kỹ thuật "Dữ liệu làm chủ ngữ" (Evidence-Led Sentences)
Thay vì dùng đại từ nhân xưng hoặc câu bị động mông lung, hãy để **số liệu, bảng biểu và thuật toán** làm chủ ngữ:
* *Thay vì:* "Chúng tôi thấy rằng mô hình bị nhầm lẫn rất nhiều giữa hai lớp..."
* *Nên viết:* "Ma trận nhầm lẫn tại Hình 5.1 phản ánh 71.19% tổng số ca dự đoán sai trên tập test tập trung ở cặp `Normal` và `Lung_Opacity`."

### 3. Kỹ thuật Tuân thủ Quy tắc D4 (Khách quan tuyệt đối)
Khi giải thích sự khác biệt giữa các tập dữ liệu hoặc độ suy giảm hiệu năng:
* Tuyệt đối không võ đoán, không bao biện bằng các tính từ hoa mỹ.
* Giữ nguyên nguyên tắc cốt lõi: *"Mọi lời giải thích về sự khác biệt giữa val và test đều là giả thuyết chưa kiểm chứng, không nêu nguyên nhân."*

---

*Cẩm nang này là quy chuẩn bắt buộc áp dụng khi viết bài tập lớn S6-01 và rà soát định dạng S6-04 trong kho lưu trữ.*
