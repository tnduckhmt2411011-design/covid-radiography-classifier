# Quản lý Phân chia Dữ liệu (Dataset Splits) - COVID-19 Radiography

> **Phiên bản:** `v1.0` (Sprint 2 - Tuần 3)  
> **Người phụ trách (Code Owner):** Nguyễn Đức (Kèm cặp: Hải Lý)  
> **Quyết định phê duyệt:** Leader (Nguyễn Đức) (chốt ngưỡng $T=0$ tại Cổng A2)

---

## 1. Tổng quan & Tính toàn vẹn

Thư mục này chứa file phân chia dữ liệu chính thức [`split_v1.csv`](file:///d:/Use%20Antigravity/Medical%20Vision/splits/split_v1.csv) và mã băm xác thực [`split_v1.sha256`](file:///d:/Use%20Antigravity/Medical%20Vision/splits/split_v1.sha256) cho đồ án phân loại 4 nhóm ảnh X-quang ngực (COVID-19 Radiography Database).

- **Tổng số mẫu:** 21.165 ảnh (khớp 100% với `manifest.csv`).
- **Mã băm SHA256:**
  ```text
  f99e03d3d5cfc32f2bbc9befbdef45a07a256458a837a6d420a6658ed7583d98  split_v1.csv
  ```
- **Lệnh kiểm tra toàn vẹn:**
  ```powershell
  python -X utf8 tests/test_split.py
  ```

---

## 2. Quy tắc phân chia Train / Validation / Test

Dữ liệu được phân chia theo phương pháp **Stratified Group Splitting** (`StratifiedGroupKFold`, 20 folds, `random_state=42`) với tỷ lệ mục tiêu **70% Train / 15% Validation / 15% Test**:
- **Train (14 folds):** 14.815 ảnh (70,00%)
- **Validation (3 folds):** 3.174 ảnh (15,00%)
- **Test (3 folds):** 3.176 ảnh (15,01%)

### Bảng phân bố chi tiết 4 lớp theo từng tập

| Nhãn (Class) | Tổng số ảnh | Train (70%) | Validation (15%) | Test (15%) | Tỷ lệ Train / Val / Test |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **COVID** | 3.616 | 2.535 | 539 | 542 | 70,1% / 14,9% / 15,0% |
| **Lung_Opacity** | 6.012 | 4.204 | 902 | 906 | 69,9% / 15,0% / 15,0% |
| **Normal** | 10.192 | 7.134 | 1.529 | 1.529 | 70,0% / 15,0% / 15,0% |
| **Viral Pneumonia** | 1.345 | 942 | 204 | 199 | 70,0% / 15,1% / 14,9% |
| **TỔNG CỘNG** | **21.165** | **14.815** | **3.174** | **3.176** | **70,00% / 15,00% / 15,01%** |

*Ghi chú:* Độ lệch tỷ lệ giữa các tập ở mỗi lớp tối đa chỉ $\pm 0,1\%$, đảm bảo phân bố lớp đồng đều tuyệt đối trên mọi tập dữ liệu.

---

## 3. Cơ chế khử trùng lặp & Quyết định chọn ngưỡng (Cổng A2)

### Quy trình kỹ thuật
1. Tính mã băm tệp MD5 (`file_hash`) và perceptual hash 64-bit DCT (`pHash`) cho toàn bộ 21.165 ảnh.
2. Vector hóa chuỗi bit pHash thành mảng nhị phân $\{-1, 1\}$ và tính ma trận khoảng cách Hamming $D = (64 - u \cdot v) // 2$ thông qua nhân ma trận khối.
3. Gom cụm ảnh tương đồng bằng thuật toán Disjoint Set Union (Union-Find) thành các nhóm định danh `group_id`.
4. Ràng buộc: Toàn bộ ảnh trong cùng một `group_id` bắt buộc phải nằm trọn vẹn trong cùng 1 split duy nhất, triệt tiêu nguy cơ rò rỉ nhóm.

### Quyết định của Leader
Leader đã đánh giá kết quả thực nghiệm 3 ngưỡng ứng viên tại kernel `cxr-duplicates-and-split` và phê duyệt **Ngưỡng $T = 0$ (Exact pHash)**:
- **Số nhóm trùng lặp:** 178 nhóm (gồm 401 ảnh).
- **Số ảnh duy nhất (độc lập):** 20.764 ảnh.
- **Số nhóm lệch nhãn (cross-class duplicates):** 0 nhóm (100% các nhóm trùng $T=0$ đều thuần nhất về mặt bệnh học).

---

## 4. Phân tích rủi ro tồn dư (Residual Risk Analysis)

Theo chỉ đạo của Leader, nhóm kỹ thuật đã thực hiện quét toàn diện các cặp ảnh có khoảng cách Hamming nằm trong khoảng $1 \le D \le 4$ còn nằm ở hai split khác nhau nhằm đánh giá rủi ro rò rỉ tiềm ẩn.

### Thống kê số lượng
- **Tổng số cặp có $1 \le D \le 4$ trong toàn bộ dataset:** 1.570 cặp.
- **Số cặp nằm ở hai split khác nhau:** 735 cặp (chiếm 46,8% tổng số cặp tương đồng).
  - Phân bố theo khoảng cách Hamming:
    - $D = 1$: 0 cặp (không có bất kỳ cặp nào lệch 1 bit do tính đối xứng của DCT pHash).
    - $D = 2$: 70 cặp.
    - $D = 3$: 0 cặp.
    - $D = 4$: 665 cặp.
  - Phân bố theo cặp split:
    - Train $\leftrightarrow$ Test: 325 cặp.
    - Train $\leftrightarrow$ Val: 335 cặp.
    - Val $\leftrightarrow$ Test: 75 cặp.
  - Phân bố theo quan hệ nhãn:
    - **Lệch nhãn (Cross-Class):** 229 cặp (14 cặp $D=2$, 215 cặp $D=4$).
    - **Cùng nhãn (Same-Class):** 506 cặp (56 cặp $D=2$, 450 cặp $D=4$).

### 6 Cặp mẫu tiêu biểu kiểm tra thị giác
1. `COVID-1002.png` (Train) $\leftrightarrow$ `COVID-322.png` (Test) | $D = 4$ | *Cùng nhãn*
2. `COVID-1011.png` (Val) $\leftrightarrow$ `COVID-1150.png` (Train) | $D = 2$ | *Cùng nhãn*
3. `COVID-1016.png` (Train) $\leftrightarrow$ `COVID-2740.png` (Val) | $D = 4$ | *Cùng nhãn*
4. `COVID-1006.png` (Val) $\leftrightarrow$ `Normal-8045.png` (Train) | $D = 4$ | *Lệch nhãn*
5. `COVID-1048.png` (Val) $\leftrightarrow$ `Lung_Opacity-3279.png` (Test) | $D = 4$ | *Lệch nhãn*
6. `COVID-1086.png` (Train) $\leftrightarrow$ `Normal-5763.png` (Val) | $D = 4$ | *Lệch nhãn*

### Đánh giá mức độ rủi ro & Giới hạn khoa học
1. **Bản chất của độ tương đồng pHash $D \le 4$:**  
   Sự hiện diện của 229 cặp **lệch nhãn** (ví dụ COVID gộp với Normal hoặc Lung Opacity với khoảng cách Hamming = 4) chứng minh rằng ở mức $D \le 4$, độ tương đồng pHash phản ánh **hình thái giải phẫu đại thể chung của lồng ngực người trưởng thành** (khung sườn đối xứng, bóng tim, góc sườn hoành) chứ không phải do cùng một bệnh nhân chụp nhiều lần.
2. **Mức độ rủi ro tồn dư (Residual Risk Level): THẤP ĐẾN TRUNG BÌNH (Low-to-Medium).**  
   - Đối với 506 cặp cùng nhãn có $D \le 4$, kiểm tra hình ảnh cho thấy đây chủ yếu là các ca chụp có độ tương phản và góc chụp tiêu chuẩn tương tự nhau.
   - **Giới hạn khoa học thừa nhận:** Do bộ dữ liệu gốc `COVID-19 Radiography Database` không cung cấp metadata mã định danh bệnh nhân (`patient_id`), nguy cơ rò rỉ giữa các ảnh chụp lặp lại của cùng một bệnh nhân ở các thời điểm khác nhau không thể triệt tiêu 100%.
3. **Biện pháp giảm thiểu rủi ro trong quá trình huấn luyện:**
   - Sử dụng các kỹ thuật tăng cường dữ liệu thích hợp (xoay góc nhỏ $\pm 7^\circ$, co giãn nhẹ, điều chỉnh độ sáng/tương phản; **tuyệt đối không lật ngang** để bảo toàn vị trí tim bên trái).
   - Sử dụng Lung Mask để tập trung vào nhu mô phổi thực sự thay vì khung xương lồng ngực.
   - Dùng Grad-CAM ở Tuần 7 để giải thích vùng quan sát, đảm bảo mô hình không dựa vào viền xương lồng ngực hay ký tự đánh dấu phim.

---

## 5. Quy tắc khóa tập Test (Test Set Locking)

1. Tập dữ liệu `test` (3.176 ảnh, 15,01%) **đã được khóa cố định** cùng với mã SHA256.
2. **Nguyên tắc đạo đức nghiên cứu & chống rò rỉ dữ liệu:**
   - Trong suốt các Tuần 4 đến Tuần 9 (huấn luyện Baseline, tinh chỉnh mô hình RQ1, RQ2, tối ưu siêu tham số, phân tích lỗi), **TUYỆT ĐỐI KHÔNG ĐƯỢC PHÉP TRUY CẬP HOẶC ĐÁNH GIÁ TRÊN TẬP TEST**.
   - Mọi quyết định lựa chọn mô hình chỉ được dựa trên tập Validation.
   - Tập `test` chỉ được mở ra đánh giá **DUY NHẤT 1 LẦN** tại Tuần 10 (`10_final_test_eval.ipynb`) trên mô hình tốt nhất đã chốt.
