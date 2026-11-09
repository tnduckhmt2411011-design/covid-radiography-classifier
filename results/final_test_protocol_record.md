# Biên bản Quy trình Đánh giá Tập Test Duy nhất (S5-04, S5-05)

- **Ngày ban hành:** 09/11/2026
- **Trạng thái:** ĐÃ ĐĂNG KÝ VÀ KHÓA QUY TRÌNH (TRƯỚC KHI MỞ KHÓA TẬP TEST)
- **Mã thực nghiệm:** S5-04 (Đánh giá tập test một lần), S5-05 (Báo cáo và ma trận nhầm lẫn)
- **Tài liệu căn cứ:** `results/threshold_v3.md` (H2, H6, R1–R5), `docs/roadmap.md`, `results/rq3_shortcut_learning_conclusion.md`
- **Mô hình đóng băng:** `orig_to_orig` = `StandardScaler` (chỉ fit trên train) + `SVC(kernel='rbf', C=10.0, gamma='scale', class_weight='balanced', probability=True, random_state=42)` trên 152 chiều đặc trưng ghép `ghep` (Histogram 64 + GLCM 60 + LBP 28), ảnh gốc 299×299 xám.

---

## 1. Quyết định Phương pháp (D1 – D4)

| Mã | Quyết định | Nội dung và Cơ sở |
| :-: | :--- | :--- |
| **D1** | **Mô hình test: Chỉ huấn luyện trên train** | Huấn luyện mô hình đóng băng duy nhất trên toàn bộ 14.815 ảnh của tập `train`. Cấu hình giữ nguyên tuyệt đối theo `results/rq3_ghep_svm_orig_to_orig_s42/config.yaml` (bao gồm `probability: true`). |
| **D2** | **Đánh giá đúng MỘT mô hình** | Chỉ đánh giá đúng 1 mô hình `orig_to_orig` trên 3.176 ảnh tập `test`. Tuyệt đối không đánh giá song song cấu hình `train+val`, không thử nghiệm mô hình che mask (`lung_to_lung` hay `out_to_out`) trên test. |
| **D3** | **Báo cáo toàn diện một lần** | Báo cáo test bao gồm: Macro-F1 điểm ước lượng kèm khoảng tin cậy 95% bootstrap 2.000 lần theo ảnh (`rng_seed=42`), Accuracy, Balanced Accuracy, Precision/Recall/F1 từng lớp, ma trận nhầm lẫn 4×4, ma trận con Normal–Lung_Opacity (R2), phân tích sai số lấy mẫu (R4), giới hạn mô hình (R5), và hiệu số học (Test − Val). |
| **D4** | **Báo cáo trung thực số đo — Không suy diễn nguyên nhân** | Báo cáo đúng số liệu đo được trên tập test. Bất kể Macro-F1 test cao hay thấp hơn val, không thay đổi mô hình, siêu tham số hay đặc trưng. Mọi lời giải thích về sự khác biệt giữa val và test (nếu có) **chỉ là giả thuyết chưa kiểm chứng**; báo cáo **không nêu nguyên nhân** (không suy diễn nguyên nhân). |

---

## 2. Hệ thống Sáu Cổng Bảo vệ (G1 – G6)

Pipeline đánh giá tập test bắt buộc phải vượt qua toàn bộ 6 cổng theo thứ tự tuần tự. Nếu bất kỳ cổng nào thất bại, quá trình dừng ngay lập tức và tập test **tuyệt đối không bị đọc**:

1. **G1 — Kiểm tra toàn vẹn phân chia (Split Integrity):**
   - SHA-256 của `splits/split_v1.csv` phải khớp tuyệt đối:
     `f99e03d3d5cfc32f2bbc9befbdef45a07a256458a837a6d420a6658ed7583d98`
   - Số dòng bắt buộc: `train: 14815`, `val: 3174`, `test: 3176`.
2. **G2 — Cấu hình đóng băng (Frozen Config Check):**
   - Đối chiếu tệp `reference/config.yaml` khớp tuyệt đối với tham số đóng băng: `features=ghep`, `classifier=SVC`, `probability=True`, `C=10.0`, `gamma=scale`, `class_weight=balanced`, `random_state=42`, `seed=42`, `scaler=StandardScaler`, `train_mask_mode=original`, `eval_mask_mode=original`, `evaluation.allow_test=false`.
3. **G3 — Chống chạy lần hai (Single-run Procedural Safeguard):**
   - Từ chối thực thi nếu tệp `UNLOCK_RECORD.json` đã tồn tại trong thư mục đầu ra `final_test/`.
   - *Lưu ý quan trọng:* Trên hạ tầng Kaggle, thư mục đầu ra `/kaggle/working` là tạm thời (ephemeral) và không được giữ lại giữa các lần chạy kernel. Do đó, G3 đóng vai trò chốt chặn theo quy trình cục bộ; chốt chặn thực sự trên Kaggle là **quy trình kiểm thủ công phiên bản kernel (Mục 4)**.
4. **G4 — Chuỗi xác nhận tường minh do người dùng gõ (Confirm String):**
   - Yêu cầu gói mã chứa tệp `CONFIRM_FINAL` mang nội dung chuỗi cố định do người dùng gõ.
   - **Mã băm SHA-256 đã đăng ký:**
     `9e935a10a3593fe72a6901ae2edbe232fc7a35f002af13bc9cb33cad02a689a2`
   - Bản rõ của chuỗi được người dùng nắm giữ và chỉ cung cấp qua tin nhắn chat khi đóng gói chạy final sau khi dry-run thành công; bản rõ KHÔNG lưu trong git.
5. **G5 — Tái lập Macro-F1 tập Validation (Val Reproduction):**
   - Huấn luyện mô hình trên tập train và suy luận trên tập val.
   - Macro-F1 val tái lập phải khớp với mốc tham chiếu `0.9024` trong dung sai $|Δ| \le 0.002$ (tức thuộc đoạn $[0.9004, 0.9044]$). Nếu lệch quá ngưỡng, dừng ngay trước khi mở khóa test.
6. **G6 — Ghi vết mở khóa (Unlock Record):**
   - Ghi tệp `final_test/UNLOCK_RECORD.json` (chứa thời điểm UTC, commit hash, SHA256 split, Macro-F1 val tái lập, SHA256 chuỗi xác nhận) và thực hiện `flush + os.fsync` **trước khi nạp ảnh test đầu tiên**.
   - **Dùng đúng mô hình đã fit ở G5:** Dự đoán trên test bằng chính các đối tượng `StandardScaler` và `SVC` đã fit ở G5; tuyệt đối không fit lại mô hình.

---

## 3. Quy tắc Xử lý Sự cố Hạ tầng (Infrastructure Failure Rules)

Nhằm bảo vệ tính nghiêm ngặt khoa học, mọi sự cố kỹ thuật xảy ra trong quá trình chạy kernel final được điều chỉnh bởi các quy định sau:

### 3.1. Định nghĩa Sự cố Hạ tầng
Sự cố hạ tầng là tình huống kernel Kaggle `ductrannguyen/cxr-final-test` bị hủy hoặc dừng đột ngột ngoài ý muốn do:
- Hết bộ nhớ (Out-Of-Memory - OOM).
- Quá thời gian chạy tối đa của Kaggle (Kernel Timeout > 9 giờ).
- Đứt kết nối môi trường máy ảo Kaggle hoặc lỗi phần cứng máy chủ.
- Lỗi I/O đọc dữ liệu ảnh từ dataset nguồn.

### 3.2. Điều kiện được coi là "Chưa Tiêu thụ Tập Test" (Chưa Dùng Test)
Lần chạy gặp sự cố được coi là **chưa dùng test** và cho phép xem xét chạy lại KHI VÀ CHỈ KHI thỏa mãn ĐỒNG THỜI 3 điều kiện sau:
1. Thư mục đầu ra `final_test/` **KHÔNG** chứa tệp `final_test_report.json` và **KHÔNG** chứa `metrics.json`.
2. Tệp dự đoán chi tiết `preds_test.csv` (nếu có dở dang) có số dòng **nhỏ hơn strictly 3.176 dòng** (chưa dự đoán hết toàn bộ tập test).
3. **Không có bất kỳ số liệu tổng hợp nào** về hiệu năng test (Macro-F1, Accuracy) bị hiển thị trên màn hình console log của Kaggle hoặc ghi ra tệp log.

### 3.3. Thẩm quyền Quyết định Xóa Record và Cấp phép Chạy lại
- **CHỈ NGƯỜI DÙNG (Human Partner) MỚI CÓ THẨM QUYỀN DUY NHẤT** quyết định bằng văn bản (qua tin nhắn chat) về việc:
  - Công nhận sự cố thuộc diện hạ tầng.
  - Cho phép hủy bỏ kết quả dở dang và xóa bản ghi để cấp phép chạy lại.
- **Tác tử AI (Assistant/Agent) TUYỆT ĐỐI KHÔNG ĐƯỢC PHÉP**:
  - Tự ý quyết định xóa `UNLOCK_RECORD.json`.
  - Tự ý trigger lại kernel hoặc chạy lại pipeline final khi chưa có lệnh bằng văn bản từ người dùng.
- Mọi sự cố phải được ghi chép đầy đủ vào Bảng Nhật ký Sự cố (Mục 5).

---

## 4. Quy trình Kiểm toán Phiên bản Thủ công (Manual Version Audit)

Vì Kaggle không lưu giữ `/kaggle/working` giữa các phiên bản kernel, quy trình kiểm soát phiên bản thủ công sau đây là bắt buộc:

1. **Trước khi chạy:**
   - Người dùng và tác tử kiểm tra danh sách kernel trên Kaggle: kernel `ductrannguyen/cxr-final-test` phải ở trạng thái chưa từng chạy hoặc chưa tồn tại version nào.
2. **Khi khởi chạy:**
   - Đẩy mã nguồn và tạo kernel: kernel `ductrannguyen/cxr-final-test` có **đúng 1 version duy nhất (Version 1)**.
3. **Sau khi chạy xong:**
   - Kiểm tra trạng thái kernel: kernel `ductrannguyen/cxr-final-test` vẫn phải giữ **đúng 1 version duy nhất (Version 1)**.
   - Bằng chứng kiểm toán phiên bản (ảnh chụp màn hình hoặc kết quả API Kaggle) được lưu trữ và đính kèm vào báo cáo PR B.
   - Tuyệt đối không bấm nút "Quick Save", không "Run All", không push đè phiên bản mới lên kernel này.

---

## 5. Bảng Nhật ký Sự cố (Incident Log Table)

| Thời điểm (UTC) | Commit SHA | Mô tả sự cố | Trạng thái tập test | Quyết định của người dùng | Chữ ký xác nhận |
| :---: | :---: | :--- | :---: | :---: | :---: |
| *(Chưa ghi nhận sự cố)* | - | Không có sự cố nào xảy ra. Pipeline sẵn sàng cho PR A. | Chưa mở | - | - |
