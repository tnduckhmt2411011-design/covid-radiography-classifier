# BẢN DỰ THẢO: TIÊU CHÍ CHẤP NHẬN MÔ HÌNH (THRESHOLD V1)

> **CẢNH BÁO QUAN TRỌNG: ĐỀ XUẤT, CHƯA CHỐT — CẦN HỌP NHÓM ĐỂ THỐNG NHẤT**  
> Tài liệu này là bản dự thảo kỹ thuật được lập dựa trên kết quả thực nghiệm Baseline Sprint 2 (Tuần 4) trên tập **Validation** (3.174 ảnh) thuộc [`splits/split_v1.csv`](../splits/split_v1.csv). Bản dự thảo này **chưa có hiệu lực ràng buộc chính thức** cho đến khi toàn thể 6 thành viên và Leader họp rà soát và thống nhất nghiệm thu.

---

## 1. Cơ sở Thực nghiệm từ Baseline Tuần 4

Toàn bộ các mô hình cơ sở đã được đo lường độc lập, khách quan và nghiêm ngặt trên tập Validation (khóa tập Test với `allow_test=False`):

| Cấp độ | Mô hình / Phương pháp | Macro-F1 | Balanced Acc | Accuracy | Vai trò kỹ thuật & Ý nghĩa |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Sàn tối thiểu (B0)** | Đa số (`Normal`) | **0.1627** | 0.2500 | 0.4824 | Điểm sàn lý thuyết của phân loại mù. Mọi mô hình có Macro-F1 $\le 0.1627$ bị coi là hỏng hoàn toàn. |
| **Ngưỡng lối tắt (A0)** | Logistic Regression (`brightness`, `is_rgb`) | **0.2132** | 0.2773 | 0.4899 | Đo lường mức độ khai thác đặc trưng phi bệnh lý (độ sáng trung bình và chế độ màu RGB). |
| **Ngưỡng lối tắt (A0)** | Random Forest (`brightness`, `is_rgb`) | **0.2397** | 0.2873 | 0.4956 | Ngưỡng cảnh báo học vẹt: 10.3% ảnh Viral Pneumonia có kênh RGB giúp bộ phân loại shortcut đạt Precision 100% trên lớp này. |
| **Feature Extraction (B2)** | ResNet18 Head-only (3 seeds: 42, 43, 44) | **$0.8064 \pm 0.0059$** | $0.7945 \pm 0.0135$ | $0.8131 \pm 0.0030$ | Mốc cơ sở khi chỉ huấn luyện classifier head trên trọng số ImageNet đóng băng. |
| **Fine-tuning (B3)** | ResNet18 Full Fine-tune (3 seeds: 42, 43, 44) | **$0.9575 \pm 0.0016$** | $0.9519 \pm 0.0006$ | $0.9520 \pm 0.0027$ | Mốc cơ sở chính để so sánh cho toàn bộ các kiến trúc và kỹ thuật ở Sprint 3–5. |

*(Ghi chú: Độ lệch chuẩn tính theo chuẩn mẫu số $ddof=1$ trên 3 seeds).*

---

## 2. Đề xuất Bộ Tiêu chí Chấp nhận (Acceptance Gates) cho Sprint 3–5 (ĐỀ XUẤT)

Nhằm đảm bảo quá trình cải tiến mô hình ở các tuần tiếp theo (xử lý mất cân bằng lớp, data augmentation nâng cao, thử nghiệm DenseNet-121, EfficientNet-B0) đạt hiệu quả thực chất, đề xuất áp dụng 4 cổng kiểm soát:

### Cổng 1: Vượt qua Ngưỡng Lối tắt Phi bệnh lý (Anti-Shortcut Gate)
* **Quy tắc:** Bất kỳ mô hình nào được xem xét **bắt buộc phải vượt xa mốc $0.2397$ (A0)** trên tập Validation.
* **Mục tiêu:** Đảm bảo mô hình đạt hiệu năng tối thiểu cao hơn đáng kể so với bộ phân loại chỉ dựa vào 2 đặc trưng phi bệnh lý đơn giản.

### Cổng 2: Điểm sàn Cải tiến so với Baseline B3 (Performance Gate)
* **Quy tắc:**
  * Mô hình cải tiến ở Sprint 3 và Sprint 4 phải đạt **Macro-F1 trung bình (3 seeds) $\ge 0.9575$** (ngang bằng hoặc cao hơn B3).
  * Một giải pháp kỹ thuật mới (ví dụ: Class Weights, Focal Loss, MixUp, hoặc kiến trúc mới) chỉ được xem là "có tiến bộ" nếu thỏa mãn:
    $$\overline{\text{Macro-F1}}_{\text{mới}} - \overline{\text{Macro-F1}}_{\text{B3}} \ge +0.0030$$
  * Nếu một kiến trúc phức tạp hơn (ví dụ DenseNet-121) có Macro-F1 $\le 0.9575$, giải pháp đó **bị từ chối đưa vào pipeline chính** để tránh lãng phí tài nguyên tính toán (nguyên tắc Occam's razor).

### Cổng 3: Bảo toàn Hiệu năng theo Lớp (Per-Class Performance Retention Gate)
Do tình trạng phân bố dữ liệu (`Normal` chiếm 48.1%, `Viral Pneumonia` chỉ chiếm 6.4%), mô hình không được đánh đổi hiệu năng lớp hiếm để lấy Accuracy tổng thể:
* **COVID-19 F1-score:** Không được thấp hơn **0.9750** (mốc B3 đạt $\sim 0.9835$).
* **Viral Pneumonia F1-score:** Không được thấp hơn **0.9600** (mốc B3 đạt $\sim 0.9648$).
* **Lung Opacity F1-score:** Phấn đấu cải thiện vượt mốc **0.9300** (lớp này hiện có F1 thấp nhất trong B3, đạt $\sim 0.9287$ do ranh giới mờ với Normal và COVID).

### Cổng 4: Ngân sách Tính toán & Thời gian Huấn luyện (Resource Gate - ĐỀ XUẤT)
* **Cơ sở đo đạc thực tế:** Dữ liệu trích xuất từ 6 tệp `train_history.json` của kernel `cxr-baseline` (GPU Tesla T4x2) cho thấy thời gian trung bình thực tế của 30 epochs là **$117.7\text{ giây/epoch}$** (trong đó B3 trung bình $116.8\text{ s/epoch}$, B2 trung bình $118.6\text{ s/epoch}$). Một run 10 epochs ResNet18 thực tế mất khoảng $10 \times 117.7\text{s} \approx 19.6\text{ phút}$.
* **Đề xuất công thức ngưỡng cho 1 run (ResNet18):**
  $$T_{\text{run}} \le N_{\text{epochs}} \times 125\text{s} + 120\text{s}_{\text{overhead}} \quad (\text{khoảng } \le 22 - 25\text{ phút cho 10 epochs})$$
* **Bảng ước tính tổng GPU-giờ cho các kịch bản thực nghiệm Sprint 3–5 [ƯỚC TÍNH]:**
  - **Kịch bản 1 (24 runs $\times$ 10 epochs = 240 epochs):** $\approx \mathbf{7.85\text{ GPU-giờ}}$
  - **Kịch bản 2 (30 runs $\times$ 12 epochs = 360 epochs):** $\approx \mathbf{11.77\text{ GPU-giờ}}$
  - **Kịch bản 3 (30 runs $\times$ 15 epochs = 450 epochs):** $\approx \mathbf{14.71\text{ GPU-giờ}}$  
  *(Lưu ý: Đây là ước tính cho backbone ResNet18; DenseNet121 và EfficientNet-B0 ở Sprint 3 chưa đo, có thể mất nhiều thời gian hơn do độ sâu kiến trúc lớn hơn).*
* **Hạn mức Sprint:** Tổng số run thử nghiệm trong mỗi Sprint không vượt quá **10–12 runs** (tiêu hao $\le 4.0\text{ giờ GPU/tuần}$ trên hạn ngạch 30h của Kaggle).

---

## 3. Quy tắc Đạo đức Nghiên cứu & Giới hạn Cần lưu ý

1. **Tuyệt đối KHÔNG lấy con số từ 2 bài báo gốc làm chỉ tiêu đánh giá:**
   * **Bài 1:** Chowdhury et al. (Preprint arXiv:2003.13145v3 / công bố chính thức IEEE Access 2020) nghiên cứu trên phiên bản dữ liệu sơ khai gồm **3.487 ảnh** (423 COVID-19, 1.485 Viral Pneumonia, 1.579 Normal).
   * **Bài 2:** Rahman et al. (Preprint arXiv:2012.02238v1 / công bố chính thức Computers in Biology and Medicine 2021) nghiên cứu trên phiên bản dữ liệu 3 lớp gồm **18.479 ảnh** (3.616 COVID-19 + 8.851 Normal + 6.012 Lung Opacity; lưu ý số lượng Normal là 8.851, khác với 10.192 của phiên bản 4 lớp hiện tại).
   * Cả hai bài báo đều chia tập ngẫu nhiên theo ảnh mà không khử trùng lặp bệnh nhân, dẫn đến nguy cơ rò rỉ dữ liệu (data leakage) cao.
   * Dự án của nhóm phân loại **4 lớp** trên **21.165 ảnh** với split cố định đã lọc trùng lặp pHash $T=0$. Mọi so sánh trực tiếp với con số trong bài báo đều không hợp lệ về mặt khoa học.
2. **Nguyên tắc "Tập Test là Bất khả xâm phạm":**
   * Toàn bộ các cổng đánh giá ở trên chỉ được áp dụng trên tập **Validation**.
   * Nghiêm cấm mọi hành vi chạy thử trên tập Test để chọn checkpoint hay điều chỉnh siêu tham số.
   * Tập Test chỉ được đánh giá một lần duy nhất tại Tuần 10 sau khi Leader và Giảng viên nghiệm thu mô hình tối ưu cuối cùng.

---

## 4. Lưu ý Phương pháp luận cho Cuộc họp Nhóm (ĐỀ XUẤT, chưa phải quyết định)

1. **Ý nghĩa của việc vượt A0:** A0 chỉ gồm 2 đặc trưng thô (`mean_brightness` và `is_rgb`), do đó việc mô hình học sâu vượt qua A0 chỉ chứng minh mô hình không dừng lại ở hai lối tắt đơn giản này; điều này **chưa chứng minh mô hình đã học được tổn thương bệnh học thực sự**. Bằng chứng khoa học về việc chống học vẹt/lối tắt phải đến từ phân tích vùng chú ý và bộ ảnh che phổi ở RQ3 (Sprint 5).
2. **Nguyên tắc so sánh công bằng:** Để kết luận một giải pháp mới có tốt hơn baseline hay không, các thử nghiệm so sánh bắt buộc phải giữ nguyên số epoch, cùng tập 3 hạt giống (seeds 42, 43, 44) và cùng tiêu chí lưu checkpoint (`best.pt` theo validation Macro-F1). Quy tắc đánh giá bỏ vế *"hoặc độ lệch chuẩn nhỏ hơn"* vì cỡ mẫu 3 seeds ($N=3$) không đủ độ tin cậy thống kê để so sánh phương sai.
3. **Báo cáo đầy đủ ở RQ1:** Trong nghiên cứu khoa học, nhóm cần báo cáo đầy đủ kết quả của tất cả các kiến trúc được thử nghiệm (DenseNet121, EfficientNet-B0, ResNet18). Các cổng chất lượng chỉ đóng vai trò bộ lọc để chọn ra 1 cấu hình tối ưu nhất bước tiếp vào RQ2, tuyệt đối không dùng để loại bỏ hoặc che giấu số liệu kém khỏi báo cáo.
4. **Xây dựng ngưỡng từng lớp theo dung sai thống kê:** Ngưỡng chấp nhận cho từng lớp nên lấy từ giá trị F1 trung bình của B3 trừ đi một khoảng dung sai theo độ lệch chuẩn thực tế ($F1_i \ge \overline{F1}_{B3, i} - k \cdot \sigma_i$) thay vì ấn định con số tuyệt đối cứng nhắc. Nhóm cần theo dõi sát ma trận con giữa `Normal` và `Lung Opacity` (cặp nhãn có ranh giới lâm sàng mờ nhạt nhất). Lưu ý dùng thuật ngữ chính xác là "bảo toàn hiệu năng theo lớp", tránh gọi nhầm là "fairness" (thuật ngữ mang hàm nghĩa công bằng xã hội/nhân khẩu học trong AI).
5. **Độ lệch lạc quan trên tập Validation:** Do tập Validation được dùng đồng thời để chọn checkpoint tốt nhất và làm căn cứ so sánh, các chỉ số đo được có thể hơi lạc quan (optimistic bias). Mọi kết luận cuối cùng về khả năng tổng quát hóa của đồ án phải dựa trên tập Test độc lập ở Tuần 10.

---

## 5. Kế hoạch Họp Nhóm Thống nhất

* **Thời gian dự kiến:** Đầu Sprint 3 (trước khi triển khai công việc S3-01).
* **Nội dung thảo luận & Phân công phát biểu:**
  1. Thái Tú & Vũ Thương: Nhận xét về độ phân kỳ giữa B2 (Head-only 80.6%) và B3 (Fine-tuning 95.8%).
  2. Hải Lý: Đánh giá ma trận nhầm lẫn của B3 và xác nhận trọng số F1 lớp Lung Opacity.
  3. Minh Thuận: Đánh giá tính ổn định qua 3 seed (42, 43, 44) và cấu hình AMP.
  4. Lê Minh: [chờ leader phân công].
  5. Nguyễn Đức (Leader): Chủ trì biểu quyết chính thức chốt hoặc điều chỉnh các ngưỡng trong tài liệu này.
