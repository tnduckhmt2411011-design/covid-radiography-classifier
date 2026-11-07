# Biên bản thứ hạng chi phí trích đặc trưng RQ1 (lô full)

Ngày ghi: 07/11/2026
Người ghi: Trần Nguyễn Đức

## 1. Nguồn số liệu
- Tệp `summary_full.json` của kernel ductrannguyen/cxr-rq1-rf, version 5, mode full.
- Commit mã: 4c0b9cf2db903e76d08235fd83be653366c67ffe (merge PR #32 vào main).
- Dữ liệu: 17.989 ảnh (14.815 train và 3.174 val) của split_v1 (SHA256 f99e03d3d5cfc32f2bbc9befbdef45a07a256458a837a6d420a6658ed7583d98). Tập test không được dùng.
- Môi trường: Kaggle CPU, Python 3.13.15.
- Chi phí = giây CPU trích đặc trưng (time.process_time, Linux), cộng train và val, chia tổng số ảnh. Không tính thời gian đọc ảnh và huấn luyện.

## 2. Số đo

| Nhóm | Giây CPU train | Giây CPU val | Giây CPU mỗi ảnh |
|---|---|---|---|
| hist | 19,879 | 4,169 | 0,001337 |
| hog | 305,384 | 55,713 | 0,020073 |
| glcmlbp | 818,562 | 175,148 | 0,055240 |
| ghep | 841,487 | 179,804 | 0,056773 |

## 3. Thứ hạng chi phí chính thức (rẻ đến đắt)
1. hist
2. hog
3. glcmlbp
4. ghep

Ghi chú: hog đắt hơn hist 15,0 lần; glcmlbp đắt hơn hog 2,75 lần; ghep đắt hơn glcmlbp 1,028 lần (chênh 2,8%, hai nhóm gần như ngang chi phí). Thứ tự này trùng với lần chạy thử T0b (499 ảnh: 0,001419; 0,020370; 0,055102; 0,056672) và số đo HOG ở T1 (0,021705). Hai lần này chỉ để tham khảo, không phải số chính thức.

## 4. Quy tắc áp dụng (theo bản giao nhận)
- Tham chiếu của RQ1 là histogram. Chỉ thay khi chênh macro-F1 trung bình 3 seed không nhỏ hơn 0,005 VÀ CI 95% bootstrap ghép cặp (2.000 lần, cùng mẫu ảnh cho hai cấu hình, trung bình 3 seed) không chứa 0.
- Nếu không đạt ngưỡng thì giữ cấu hình rẻ hơn theo thứ hạng ở mục 3.
- Mỗi RQ chỉ có một phép so sánh chính, đóng băng trước khi xem kết quả, theo mục 5 của `results/threshold_v3.md`: "Phép so sánh chính của RQ1: nhóm đặc trưng (khác histogram) có macro-F1 trung bình cao nhất so với histogram."

## 5. Xác nhận thời điểm ghi
Biên bản này được ghi trước khi người ghi mở `metrics.json`, tệp `log` của từng run và `preds_val.csv` của lô full, và chưa tính bất kỳ điểm số nào từ lô full.
Xác nhận của người ghi: đã xác nhận
