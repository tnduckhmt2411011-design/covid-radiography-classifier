# Biên bản thứ hạng chi phí huấn luyện RQ2 (lô full)

Ngày ghi: 07/11/2026
Người ghi: Trần Nguyễn Đức

## 1. Nguồn số liệu
- Tệp `summary_full.json` của kernel `ductrannguyen/cxr-rq2-classifiers`, version 3, mode `full`.
- Commit mã: `1a0925dcbe5e7a847c65f9654574806122f75b3d` (merge PR #35 vào `main`).
- Nhóm đặc trưng cố định (đã chốt ở S3-06): `ghep` (152 chiều = 64 Histogram + 60 GLCM + 28 LBP).
- Dữ liệu: 17.989 ảnh (`14.815` train và `3.174` val) của `split_v1.csv` (SHA256 `f99e03d3d5cfc32f2bbc9befbdef45a07a256458a837a6d420a6658ed7583d98`). Tập test không được dùng (`allow_test = False`).
- Môi trường: Kaggle CPU, Python `3.13.15`, `scikit-learn 1.6.1`, `scikit-image 0.25.2`, `numpy 2.1.3`, `opencv-python-headless 4.14.0.94`.
- Thời gian trích đặc trưng `ghep` (dùng chung cho cả 6 bộ phân loại): `1.155,273` giây CPU (train) + `247,594` giây CPU (val) = `1.402,867` giây CPU (`0,077985` giây CPU/ảnh).
- Chi phí bộ phân loại = tổng giây CPU huấn luyện (`total_train_cpu_seconds` = giây CPU 5-fold `StratifiedGroupKFold` CV + tổng giây CPU fit trên toàn bộ tập `train` của các seed tương ứng).

## 2. Số đo chi phí huấn luyện và siêu tham số chọn qua 5-fold CV

| Hạng | Mã | Bộ phân loại | Tính chất | Số seed | Siêu tham số chọn qua 5-fold CV (`group_id`) | Giây CPU 5-fold CV | Giây CPU fit TB/seed | Tổng giây CPU huấn luyện |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **1** | `knn` | `KNeighborsClassifier` | Tất định | 1 (`s42`) | `n_neighbors=5, weights='distance'` | 18,467 | 0,039 | **18,506** |
| **2** | `dt` | `DecisionTreeClassifier` | Ngẫu nhiên | 3 (`s42, s43, s44`) | `max_depth=10, min_samples_leaf=1` | 189,601 | 4,254 | **202,362** |
| **3** | `lr` | `LogisticRegression` | Tất định | 1 (`s42`) | `C=10.0` | 86,869 | 185,638 | **272,507** |
| **4** | `svm` | `SVC` (RBF) | Tất định | 1 (`s42`) | `C=10.0, gamma='scale'` | 419,094 | 60,754 | **479,848** |
| **5** | `gb` | `GradientBoostingClassifier` | Ngẫu nhiên | 3 (`s42, s43, s44`) | `n_estimators=200, learning_rate=0.1, max_depth=5` | 1.765,091 | 132,789 | **2.163,459** |
| **6** | `rf` | `RandomForestClassifier` | Ngẫu nhiên | 3 (`s42, s43, s44`) | `n_estimators=300, max_depth=None` | 3.086,971 | 151,621 | **3.541,833** |

## 3. Thứ hạng chi phí chính thức (rẻ đến đắt)
1. `knn` (`18,506` giây CPU)
2. `dt` (`202,362` giây CPU)
3. `lr` (`272,507` giây CPU)
4. `svm` (`479,848` giây CPU)
5. `gb` (`2.163,459` giây CPU)
6. `rf` (`3.541,833` giây CPU)

## 4. Quy tắc áp dụng (theo mục 5 của `results/threshold_v3.md`)
- Cấu hình tham chiếu của RQ2 là bộ phân loại đã dùng ở RQ1: **Random Forest (`rf`)** trên nhóm đặc trưng `ghep`.
- Mỗi RQ chỉ có **MỘT phép so sánh chính**, đóng băng trước khi xem kết quả: bộ phân loại ứng viên (khác `rf`) có Macro-F1 trung bình trên tập `val` cao nhất so với tham chiếu `rf`.
- Bộ phân loại ứng viên chỉ thay thế tham chiếu `rf` khi chênh lệch Macro-F1 trung bình $\ge 0,005$ **VÀ** khoảng tin cậy 95% (bootstrap ghép cặp theo ảnh, `2.000` lần, `rng_seed=42`, trên `3.174` ảnh validation) của hiệu số không chứa `0`.
- Nếu ứng viên tốt nhất không vượt tham chiếu đủ ngưỡng $+0,005$ kèm CI 95% không chứa `0` (hoặc nếu cần phân xử khi tương đương hiệu năng trong phạm vi sai số), áp dụng quy tắc giữ cấu hình theo mục 5 của `results/threshold_v3.md`.

## 5. Xác nhận thời điểm ghi
Biên bản này được ghi và commit trước khi mở `metrics.json`, tệp `log` của từng run và nội dung `preds_val.csv` của lô `full` RQ2, và chưa tính bất kỳ điểm số nào từ lô `full` RQ2.
Xác nhận của người ghi: đã xác nhận
