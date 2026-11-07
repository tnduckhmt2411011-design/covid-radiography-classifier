# Báo cáo phân tích chi tiết các ca dự đoán sai trên tập Validation (S4-06)

Ngày ghi: 07/11/2026
Người thực hiện: Lê Minh (Cặp 3) — Kiểm duyệt: Nguyễn Minh Thuận & Trần Nguyễn Đức
Mô hình phân tích: `rq2_ghep_svm_s42` (`SVC(kernel='rbf', C=10.0, gamma='scale', class_weight='balanced')` + `StandardScaler` trên đặc trưng `ghep` 152 chiều, đã đóng băng tại `S4-04`).
Tập dữ liệu: `3.174` ảnh Validation của `splits/split_v1.csv` (`allow_test = False`).

## 1. Tổng quan phân bố lỗi
- **Tổng số ca dự đoán sai:** `349 / 3174` ảnh (`11.00%`; Accuracy = `89,00%`, Macro-F1 = `0,9024`).
- **Số ca khó đồng thuận (Consensus Hard Errors — cả 3 mô hình `svm`, `gb`, `rf` đều đoán sai):** `240 / 349` ca (`68.8%`). Điều này chứng tỏ hơn một nửa số ca sai không phải do hạn chế riêng của bộ phân loại SVM mà xuất phát từ sự chồng lấp đặc trưng mức xám/kết cấu hoặc nhiễu nhãn vùng biên giữa các lớp.
- **Phân tầng theo độ tự tin dự đoán (`proba_pred`):**
  - Sai tự tin cao (`p >= 0,80`): `138` ca (`39.5%`).
  - Sai mức trung bình (`0,55 <= p < 0,80`): `143` ca.
  - Sai vùng ranh giới (`p < 0,55`): `68` ca.

## 2. Phân rã 12 cặp nhầm lẫn ngoài đường chéo chính

| Nhãn thực (`true_label`) | Nhãn dự đoán (`pred_label`) | Số ca (`count`) | % Tổng lỗi | % Lớp thực | Xác suất sai TB | Số ca `p >= 0,80` | Đồng thuận 3 mô hình | Các ca điển hình (`image_id`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `Normal` | `Lung_Opacity` | **144** | 41.26% | 9.41% | 0.6933 | 46 | 98 | `Normal-9540.png, Normal-4930.png, Normal-8652.png` |
| `Lung_Opacity` | `Normal` | **124** | 35.53% | 13.73% | 0.8127 | 71 | 101 | `Lung_Opacity-3644.png, Lung_Opacity-2478.png, Lung_Opacity-5495.png` |
| `Normal` | `COVID` | **18** | 5.16% | 1.18% | 0.5989 | 5 | 5 | `Normal-3652.png, Normal-7599.png, Normal-1709.png` |
| `Normal` | `Viral Pneumonia` | **16** | 4.58% | 1.05% | 0.5813 | 2 | 4 | `Normal-1387.png, Normal-1292.png, Normal-1154.png` |
| `COVID` | `Normal` | **13** | 3.72% | 2.42% | 0.7411 | 5 | 9 | `COVID-3419.png, COVID-32.png, COVID-3541.png` |
| `Lung_Opacity` | `COVID` | **12** | 3.44% | 1.33% | 0.6123 | 3 | 7 | `Lung_Opacity-3062.png, Lung_Opacity-5040.png, Lung_Opacity-195.png` |
| `COVID` | `Lung_Opacity` | **8** | 2.29% | 1.49% | 0.7346 | 3 | 6 | `COVID-1183.png, COVID-329.png, COVID-1084.png` |
| `Viral Pneumonia` | `Normal` | **7** | 2.01% | 3.45% | 0.7106 | 1 | 6 | `Viral Pneumonia-1072.png, Viral Pneumonia-699.png, Viral Pneumonia-138.png` |
| `Viral Pneumonia` | `COVID` | **4** | 1.15% | 1.97% | 0.7357 | 2 | 3 | `Viral Pneumonia-792.png, Viral Pneumonia-644.png, Viral Pneumonia-175.png` |
| `COVID` | `Viral Pneumonia` | **2** | 0.57% | 0.37% | 0.5719 | 0 | 0 | `COVID-1177.png, COVID-3579.png` |
| `Viral Pneumonia` | `Lung_Opacity` | **1** | 0.29% | 0.49% | 0.5127 | 0 | 1 | `Viral Pneumonia-622.png` |
| `Lung_Opacity` | `Viral Pneumonia` | **0** | 0.00% | 0.00% | 0.0000 | 0 | 0 | `None` |

## 3. Nguyên nhân gây nhầm lẫn theo từng cụm bệnh lý lâm sàng
1. **Cụm nhầm lẫn áp đảo `Normal <-> Lung_Opacity` (`268 / 349` ca = `76,79%` tổng số lỗi):**
   - Gồm `144` ca `Normal -> Lung_Opacity` và `124` ca `Lung_Opacity -> Normal` (khớp tuyệt đối với ma trận con R2).
   - **Nguyên nhân:** Cả hai nhóm này đều có nguồn gốc chủ yếu từ cuộc thi `RSNA Pneumonia Detection Challenge` (`6.012` ảnh `Lung_Opacity` và `8.851/10.192` ảnh `Normal`), dùng chung thiết bị chụp và tiền xử lý nên histogram độ xám toàn cục và kết cấu nền rất giống nhau. Các ca mờ phổi nhẹ hoặc khu trú chỉ làm thay đổi cục bộ một phần nhỏ diện tích phổi, bị trung bình hoá khi tính đặc trưng toàn ảnh `299x299`.
2. **Cụm nhầm lẫn `COVID <-> Lung_Opacity` (`20` ca: `12` `Lung_Opacity -> COVID` và `8` `COVID -> Lung_Opacity`):**
   - Các ca điển hình: `Lung_Opacity-3062.png`, `Lung_Opacity-5040.png`, `COVID-1183.png`, `COVID-329.png`.
   - **Nguyên nhân:** Tổn thương kính mờ (ground-glass opacity) lan tỏa của COVID-19 và mờ phổi không do COVID có cấu trúc mức xám và độ tương phản cục bộ (GLCM/LBP) chồng lấp; các ảnh `Lung_Opacity` có độ sáng trung bình cao dễ bị kéo về phía phân bố của `COVID`.
3. **Cụm nhầm lẫn `COVID <-> Normal` (`31` ca: `18` `Normal -> COVID` và `13` `COVID -> Normal`):**
   - Các ca điển hình: `Normal-3652.png`, `Normal-7599.png`, `COVID-3419.png`, `COVID-32.png`.
   - **Nguyên nhân:** Phù hợp với nhận xét của chính tác giả bài báo gốc P1 (Chowdhury et al., 2020): các ca COVID-19 giai đoạn sớm có rất ít dấu hiệu mờ trên X-quang, trong khi một số ảnh `Normal` có độ sáng cao hoặc viền chữ/khung chụp đặc trưng nguồn gây nhiễu đặc trưng toàn ảnh.
4. **Cụm nhầm lẫn liên quan `Viral Pneumonia` (`30` ca: `16` `Normal -> Viral Pneumonia`, `7` `Viral Pneumonia -> Normal`, `6` `COVID <-> Viral Pneumonia`, `1` `Viral Pneumonia -> Lung_Opacity`):**
   - Lớp `Viral Pneumonia` (`1.345` ảnh) và `1.341` ảnh `Normal` cùng xuất phát từ bộ Kaggle Nhi khoa (Kermany/Mooney), nên sự nhầm lẫn của `Viral Pneumonia` diễn ra chủ yếu với phần `Normal` cùng nguồn (`23/30` ca), trong khi hầu như tách biệt với `Lung_Opacity` của nguồn RSNA (chỉ `1` ca duy nhất `Viral Pneumonia-622.png` và `0` ca `Lung_Opacity -> Viral Pneumonia`). Đây là bằng chứng quan trọng gợi ý hiện tượng phụ thuộc nguồn dữ liệu (shortcut learning) sẽ được kiểm định trực tiếp bằng bộ ảnh che phổi ở **RQ3 (`S4-07`, `S5-01`, `S5-02`)**.
