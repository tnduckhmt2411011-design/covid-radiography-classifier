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
| **Feature Extraction (B2)** | ResNet18 Head-only (3 seeds: 42, 43, 44) | **$0.8064 \pm 0.0059$** | $0.7946 \pm 0.0135$ | $0.8130 \pm 0.0030$ | Mốc cơ sở khi chỉ huấn luyện classifier head trên trọng số ImageNet đóng băng. |
| **Fine-tuning (B3)** | ResNet18 Full Fine-tune (3 seeds: 42, 43, 44) | **$0.9575 \pm 0.0016$** | $0.9519 \pm 0.0006$ | $0.9520 \pm 0.0027$ | Mốc cơ sở chính để so sánh cho toàn bộ các kiến trúc và kỹ thuật ở Sprint 3–5. |

---

## 2. Đề xuất Bộ Tiêu chí Chấp nhận (Acceptance Gates) cho Sprint 3–5

Nhằm đảm bảo quá trình cải tiến mô hình ở các tuần tiếp theo (xử lý mất cân bằng lớp, data augmentation nâng cao, thử nghiệm DenseNet-121, EfficientNet-B0) đạt hiệu quả thực chất, đề xuất áp dụng 4 cổng kiểm soát:

### Cổng 1: Vượt qua Ngưỡng Lối tắt Phi bệnh lý (Anti-Shortcut Gate)
* **Quy tắc:** Bất kỳ mô hình nào được xem xét **bắt buộc phải vượt xa mốc $0.2397$ (A0)** trên tập Validation.
* **Mục tiêu:** Chứng minh mạng nơ-ron học các tổn thương nhu mô phổi (đông đặc, kính mờ, thâm nhiễm) chứ không phải học viền đen, độ sáng nền hay metadata định dạng ảnh.

### Cổng 2: Điểm sàn Cải tiến so với Baseline B3 (Performance Gate)
* **Quy tắc:**
  * Mô hình cải tiến ở Sprint 3 và Sprint 4 phải đạt **Macro-F1 trung bình (3 seeds) $\ge 0.9575$** (ngang bằng hoặc cao hơn B3).
  * Một giải pháp kỹ thuật mới (ví dụ: Class Weights, Focal Loss, MixUp, hoặc kiến trúc mới) chỉ được xem là "có tiến bộ" nếu thỏa mãn:
    $$\overline{\text{Macro-F1}}_{\text{mới}} - \overline{\text{Macro-F1}}_{\text{B3}} \ge +0.0030 \quad \text{hoặc} \quad \text{Std}_{\text{mới}} < \text{Std}_{\text{B3}} \text{ (tính ổn định cao hơn)}$$
  * Nếu một kiến trúc phức tạp hơn (ví dụ DenseNet-121) có Macro-F1 $\le 0.9575$, giải pháp đó **bị từ chối đưa vào pipeline chính** để tránh lãng phí tài nguyên tính toán (nguyên tắc Occam's razor).

### Cổng 3: Bảo toàn Hiệu năng trên các Lớp Thiểu số (Per-Class Fairness Gate)
Do tình trạng mất cân bằng dữ liệu (`Normal` chiếm 48.1%, `Viral Pneumonia` chỉ chiếm 6.4%), mô hình không được đánh đổi hiệu năng lớp hiếm để lấy Accuracy tổng thể:
* **COVID-19 F1-score:** Không được thấp hơn **0.9750** (mốc B3 đạt $\sim 0.9835$).
* **Viral Pneumonia F1-score:** Không được thấp hơn **0.9600** (mốc B3 đạt $\sim 0.9648$).
* **Lung Opacity F1-score:** Phấn đấu cải thiện vượt mốc **0.9300** (lớp này hiện có F1 thấp nhất trong B3, đạt $\sim 0.9287$ do ranh giới mờ với Normal và COVID).

### Cổng 4: Ngân sách Tính toán & Thời gian Huấn luyện (Resource Gate)
* Thời gian huấn luyện cho 1 run (10 epochs) không được vượt quá **15 phút trên GPU T4** (tương đương $\le 0.25$ GPU-giờ).
* Tổng số run thử nghiệm trong mỗi Sprint không vượt quá **10 runs** (tiêu hao $\le 2.5$ giờ GPU/tuần trên hạn ngạch 30h).

---

## 3. Quy tắc Đạo đức Nghiên cứu & Giới hạn Cần lưu ý

1. **Tuyệt đối KHÔNG lấy con số từ 2 bài báo gốc làm chỉ tiêu đánh giá:**
   * Bài báo P1 (Chowdhury et al., IEEE Access 2020) và P2 (Rahman et al., CBM 2021) phân loại theo các bài toán khác (nhị phân 2 lớp, hoặc 3 lớp trên phiên bản dataset nhỏ chỉ ~1.200 đến ~3.600 ảnh).
   * Cả hai bài báo đều chia tập ngẫu nhiên theo ảnh mà không khử trùng lặp bệnh nhân, dẫn đến nguy cơ rò rỉ dữ liệu (data leakage) cao.
   * Dự án của nhóm phân loại **4 lớp** trên **21.165 ảnh** với split cố định đã lọc trùng lặp pHash $T=0$. Mọi so sánh trực tiếp với con số trong bài báo đều không hợp lệ về mặt khoa học.
2. **Nguyên tắc "Tập Test là Bất khả xâm phạm":**
   * Toàn bộ các cổng đánh giá ở trên chỉ được áp dụng trên tập **Validation**.
   * Nghiêm cấm mọi hành vi chạy thử trên tập Test để chọn checkpoint hay điều chỉnh siêu tham số.
   * Tập Test chỉ được đánh giá một lần duy nhất tại Tuần 10 sau khi Leader và Giảng viên nghiệm thu mô hình tối ưu cuối cùng.

---

## 4. Kế hoạch Họp Nhóm Thống nhất

* **Thời gian dự kiến:** Đầu Sprint 3 (trước khi triển khai công việc S3-01).
* **Nội dung thảo luận:**
  1. Thái Tú & Vũ Thương: Nhận xét về độ phân kỳ giữa B2 (Head-only 80.6%) và B3 (Fine-tuning 95.8%).
  2. Hải Lý: Đánh giá ma trận nhầm lẫn của B3 và xác nhận trọng số F1 lớp Lung Opacity.
  3. Minh Thuận: Đánh giá tính ổn định qua 3 seed (42, 43, 44) và cấu hình AMP.
  4. Nguyễn Đức (Leader): Biểu quyết chính thức chốt hoặc điều chỉnh các ngưỡng trong tài liệu này.
