# Spec: Sửa các điểm review senior vòng cuối (rá vòng cuối Chương 1–6, tài liệu tham khảo, phụ lục, tóm tắt)

Ngày: 2026-11-12
Nhánh: `report/sua-review-vong-cuoi` (tạo từ `origin/main` = `cec8a8a`, PR #68 đã merge)
Worktree thi công: `C:\Users\LENOVO\AppData\Local\Temp\opencode\wt-review-cuoi` (cây làm việc chính đang ở nhánh `slides/s6-03-deck-bao-ve` của người dùng, không được đụng).

## 1. Bối cảnh và phạm vi

Sau khi PR #68 merge, senior rà vòng cuối toàn bộ sáu chương, tài liệu tham khảo, ba phụ lục và tóm tắt/Abstract. Đa số điểm đã sửa đúng ở lượt trước. Phần còn lại gồm ba lỗi sự thật trong phụ lục (N1, N2, N3), hai điểm ở tóm tắt/Abstract (N4, N5), hai phép đo/giới hạn nên thêm (N6, N7), một chỗ lệch số giữa các chương (thời gian trích đặc trưng), và một loạt mục nhỏ.

Quy ước ràng buộc: `docs/report_standards.md` (IEEE, chú thích bảng, mỗi bản tóm tắt không quá một trang), `docs/academic_writing_guide.md` (dấu phẩy thập phân, chấm phân cách hàng nghìn, không dấu gạch dài trong câu mới, không slop), Quy tắc D4 (không nêu nguyên nhân cho chênh validation–test), mọi số liệu truy về bản ghi trong kho.

Phạm vi KHÔNG gồm: nhánh `slides/` của người dùng, `demo/requirements.txt`, `results/report_rq*/bootstrap_config.json` (rác sửa dở trong cây chính, không stage).

## 2. Các thay đổi

### 2.1 N1 — Phụ lục C.1, câu trọng số lớp (lỗi sự thật)

Câu hiện tại (08_phu_luc_a_c.md, C.1): "Trọng số lớp (`class_weight='balanced'`) là thành phần cố định của bộ phân loại, không nằm trong lưới; `knn` không hỗ trợ trọng số lớp nên dùng cân bằng bằng `weights='distance'`."

Ba lỗi: (a) `weights='distance'` là trọng số theo khoảng cách láng giềng, không cân bằng lớp; (b) Random Forest dùng `balanced_subsample`, Gradient Boosting dùng `sample_weight`, không phải `class_weight`; (c) chỉ Logistic Regression, Decision Tree và SVM dùng `balanced`.

Bằng chứng: `src/rq2_runner.py` `CLASSIFIER_SPECS` (lr/dt/svm: `balanced`; rf: `balanced_subsample`; gb: `sample_weight`; knn: `none`), `tests/test_rq2_runner.py` dòng 180–186, `notebooks/06_rq2_classifiers.ipynb` dòng 85, Bảng 2.6 và thân bài mục 2.8 của Chương 2 (dòng 167–175, 179) đã viết đúng.

Thay bằng câu mô tả đúng như Bảng 2.6: trọng số lớp là thành phần cố định không nằm trong lưới; Logistic Regression, Decision Tree và SVM dùng cân bằng lớp; Random Forest dùng cân bằng theo mẫu con (`balanced_subsample`); Gradient Boosting nhận trọng số mẫu cân bằng truyền vào bước fit; k-NN không có cách cân bằng lớp (trọng số `distance` trong lưới của `knn` là trọng số theo khoảng cách tới láng giềng). Giữ nguyên câu "Lưới trên đọc trực tiếp từ `PARAM_GRIDS` trong `src/rq2_runner.py`".

### 2.2 N2 — Phụ lục C.2, bộ tham chiếu `rf` và mã nội bộ (lỗi sự thật)

- "Bộ phân loại tham chiếu của RQ2 là `rf` (cấu hình dùng ở RQ1)" → "Bộ phân loại tham chiếu của RQ2 là `rf`, với cấu hình chọn bằng kiểm định chéo (300 cây, độ sâu không giới hạn), khác cấu hình 500 cây cố định dùng ở RQ1."
  Bằng chứng: Ch2 dòng 181 ("RQ1 dùng một cấu hình cố định chốt trước, gồm 500 cây... Ở RQ2, số cây là siêu tham số"), Ch3 dòng 61.
- "Ba bộ tất định không có độ lệch chuẩn (cổng H3 của đề tài)" → "Ba bộ tất định về nhãn dự đoán chạy mỗi bộ một lần nên không có độ lệch chuẩn." (bỏ mã nội bộ H3; dùng cách nói của Ch2 dòng 159).

### 2.3 N3 — Phụ lục A: logic cổng, đánh số bảng, phiên bản Python (lỗi sự thật)

- A.2: "Trong đó khớp một điều kiện thì ứng dụng dừng và báo lỗi, không nạp mô hình." → "Trong đó một điều kiện không khớp thì ứng dụng dừng và báo lỗi, không nạp mô hình."
  Bằng chứng: `src/model_artifact.py` ném `ModelArtifactError` khi không khớp (dòng 62, 72, 81, 118–119, 142–163).
- Đánh số lại bảng: bảng ở mục A.2 (Thông số mô hình đóng băng) đổi thành **Bảng A.1**; bảng ở mục A.3 (Biến môi trường) đổi thành **Bảng A.2**. Sửa tham chiếu chéo trong hàng `CXR_MODEL_SHA256`: "mặc định băm ở Bảng A.2" → "mặc định băm ở Bảng A.1". Sinh lại mục lục (`scripts/report_frontmatter.py`).
- A.1: bỏ "— cùng phiên bản mặc định của Streamlit Community Cloud"; giữ "môi trường đã chạy toàn bộ kiểm thử của đề tài" (mâu với A.4 "chọn Python 3.12").

### 2.4 N7 — Lưới chọn tham số ở biên (giới hạn mới)

Bằng chứng (`PARAM_GRIDS` + Bảng C.2): `lr` chọn C=10,0 (lớn nhất); `svm` chọn C=10,0 (lớn nhất); `gb` chọn 200 cây và độ sâu 5 (đều lớn nhất); `dt` chọn độ sâu 10 (nhỏ nhất); `rf` chọn 300 cây (nhỏ nhất trong {300; 500}). Năm trong sáu bộ có ít nhất một siêu tham số nằm ở biên lưới; chỉ `knn` chọn ở trong lưới. (Senior đếm bốn bộ; thực tế còn `rf` — spec giữ con số đúng năm và liệt kê đủ.)

- Phụ lục C.1, sau bảng lưới, thêm một câu: năm trong sáu bộ có ít nhất một siêu tham số chọn ở biên lưới (liệt kê), nên lưới có thể chưa bao hết vùng tối ưu và thứ hạng giữa các bộ có thể thay đổi nếu mở rộng lưới; hệ quả cho kết luận "SVM tốt nhất" được ghi ở giới hạn 12 của Chương 6.
- Chương 6 (mục 6.2), thêm hạng mục **12. Siêu tham số chọn ở biên lưới.** với nội dung như trên, ghi rõ nguồn là Bảng C.1 và C.2 của Phụ lục C.
- Ghi chú kỹ thuật mục 6.2: thêm một câu ghi rõ hạng 12 không thuộc biên bản R5 đã đăng ký, suy ra từ Bảng C.1/C.2 trong lượt rà cuối.

### 2.5 Chênh số trích đặc trưng giữa Chương 3 và Phụ lục C.3

Hai số đo cùng đại lượng (giây CPU trích nhóm `ghep` cho 17.989 ảnh) nhưng khác lần chạy: 0,056773 (`results/rq1_cost_rank_record.md`, kernel `cxr-rq1-rf` phiên bản 5) và 0,077985 (`results/rq2_cost_rank_record.md`, kernel `cxr-rq2-classifiers` phiên bản 3); cả hai đều trên Kaggle CPU.

- Phụ lục C.3, sau câu tính 0,077985, thêm: "Con số này đo ở lần chạy RQ2 (kernel `cxr-rq2-classifiers` phiên bản 3); con số 0,056773 ở Chương 3 đo ở lần chạy RQ1 (kernel `cxr-rq1-rf` phiên bản 5). Cùng môi trường Kaggle CPU nhưng khác phiên chạy nên hai số không so trực tiếp được."
- Ghi chú Chương 5 mục 5.5.4: "khác đồng hồ và khác máy nên chỉ dùng làm mốc tham khảo" → "đo ở phiên kernel khác nên chỉ dùng làm mốc tham khảo".

### 2.6 N6 — Khoảng tin cậy cho hiệu số 0,0051 (phép đo mới)

Mở rộng `scripts/val_near_duplicate_subset.py` (chỉ thêm, không đổi khóa JSON cũ):

- Bootstrap 2.000 lần, seed 42: mỗi lần lấy mẫu lại **độc lập trong từng tập con** (273 ảnh và 2.901 ảnh), tính macro-F1 từng tập con rồi lấy hiệu; khoảng tin cậy 95% lấy phân vị 2,5% và 97,5%. Ghi thêm khóa `bootstrap` vào JSON/MD với: `resamples: 2000`, `seed: 42`, `ci95_diff: [lo, hi]`, `contains_zero: bool`.
- Ghi thêm cơ cấu lớp và recall từng lớp của cả hai tập con (khóa `complement_per_class`, `recall_subset`, `recall_complement`) để so sánh công bằng hơn (macro-F1 phụ thuộc cơ cấu lớp).
- Ghi rõ trong kết quả và trong báo cáo: lớp Viral Pneumonia chỉ có 4 ảnh trong tập con 273, nên CI của hiệu số mang tính xấp xỉ.

Cập nhật văn bản theo kết quả đo (hai nhánh xử lý nếu CI chứa 0 hoặc không):

- Ch2 mục 2.5 (dòng 101): thay "đề tài không có khoảng tin cậy cho hiệu số 0,0051 giữa hai tập con, nên chưa kết luận được..." bằng câu ghi hiệu số cùng CI đo được và kết luận tương ứng; thêm câu cảnh báo cơ cấu lớp hai tập con (Normal 164/273, Viral Pneumonia 4/273) nên so per-class recall.
- Ch6 giới hạn 1 (dòng 38): cập nhật tương tự.
- Ghi chú Ch2 mục 2.5 và ghi chú Ch6 mục 6.2: bổ sung thông tin bootstrap (2.000 lần, seed 42, CI, tính chất xấp xỉ).
- `tests/test_val_near_duplicate_subset.py`: thêm một phép kiểm CI tái lập được (đọc khóa mới, kiểm 2000/seed và `ci95_diff` suy ra lại từ JSON hoặc kiểm tính tái lập của phân vị).

### 2.7 N4, N5 và các mục nhỏ của tóm tắt/Abstract (`report/09_tom_tat_abstract.md`)

- N4 (cả hai ngôn ngữ): thay câu cuối đoạn 2. Tiếng Việt: *"Nhóm đặc trưng thủ công thay được nhóm histogram làm mốc tham chiếu ở RQ1, song mô hình chưa kiểm định lâm sàng và chưa kiểm trên ảnh của cơ sở khác nên chưa thể dùng như công cụ chẩn đoán."* Tiếng Anh: *"Hand-crafted features replace the histogram reference group in RQ1, while the model has not been clinically validated nor tested on images from other institutions, so it cannot yet serve as a diagnostic tool."* (Bỏ "nhờ đó thay được mốc đã đăng ký" mơ hồ; tách lý do "chưa dùng được" khỏi kết quả RQ3 như sửa ở 6.5.)
- N5: sau câu hiệu hai kịch bản, thêm mệnh đề: *"che vùng ảnh chỉ ở lúc đánh giá khiến macro-F1 giảm còn 0,0723 (chỉ còn vùng phổi) và 0,2084 (chỉ còn vùng ngoài mặt nạ)."* (Bản Anh tương ứng.) Số liệu từ Bảng 4.1 (Ch4 dòng 28–29).
- "Đề tài giải ba câu hỏi" → "Đề tài trả lời ba câu hỏi".
- "độ trễ đầu-cuối trung vị 131,8 ms" → "độ trễ đầu-cuối trung vị 131,8 ms khi chạy liên tiếp"; bản Anh: "with a median end-to-end latency of 131.8 ms in sustained mode".
- Ghi chú nguồn: "độ trễ trung vị 131,8 ms lấy ở mục 6.2 của Chương 6 (ghi lại từ Bảng 5.5)" → "lấy ở mục 5.5.4 và Bảng 5.5 của Chương 5"; bổ sung 0,0723 và 0,2084 vào danh sách số từ Bảng 4.1.
- Siết chặt câu chữ cho bù mệnh đề mới, mục tiêu mỗi bản không quá một trang (theo `docs/report_standards.md` mục 5); bỏ lặp ở câu "không xác định được đặc điểm nào".

### 2.8 Trích dẫn phương pháp (mục nhỏ của senior)

Thêm 5 trích dẫn, đánh số theo thứ tự xuất hiện (kiểm tra toàn bộ vị trí trích dẫn trước khi ghi):

- Ch1 mục 1.2 (dòng 19, chỗ định nghĩa): `[7]` Haralick (GLCM), `[8]` Ojala (LBP), `[9]` Dalal-Triggs (HOG).
- Ch1 mục 1.3 (dòng 37): `[10]` Efron (bootstrap).
- Ch2 mục 2.7 (dòng 159): `[11]` Platt (nội suy Platt).
- Ch5 mục 5.5.1/5.5.2: `[7]`→`[12]` (artifact), `[8]`→`[13]` (Streamlit).
- pHash: ghi chú trong 07 là kỹ thuật chuẩn, đề tài tính bằng thư viện mã nguồn mở `imagehash`, không có một bài báo gốc duy nhất nên không đưa vào danh mục.

Sửa kèm: note cuối Ch1 (dòng 78: "tài liệu của các chương sau đánh tiếp từ [7]" → đánh số tiếp nối, danh mục gộp giữ nguyên số), `report/README.md` dòng 130 và 165 (`[1]`–`[13]`, gộp từ Ch1 `[1]`–`[10]`, Ch2 `[11]`, Ch5 `[12]`, `[13]`), `report/07_tai_lieu_tham_khao.md` (câu mở đầu: mười tài liệu đầu ở Ch1, một ở Ch2, hai ở Ch5; sửa phạm vi chú thích chân trang `[^mooney]` xuất hiện ở Chương 1 và Chương 2; cập nhật bullet "Thứ tự xuất hiện"; thêm câu pHash). `[6]` scikit-learn giữ nguyên vì mọi điểm trích dẫn mới nằm sau lần xuất hiện của nó.

### 2.9 Các mục nhỏ còn lại

- Ch5 ghi chú mục 5.5 (dòng 131): `load_benchmark_metrics` đọc `results/rq2_ghep_svm_orig_to_orig_s42/metrics.json` → đọc `results/rq3_ghep_svm_orig_to_orig_s42/metrics.json`, nếu không có thì dùng bản sao trong `reference/` của gói mã nguồn (thư mục `rq2_ghep_svm_orig_to_orig_s42` không tồn tại trong kho). Bằng chứng: `src/inference_demo.py` dòng 288–292.
- Ch5 ghi chú mục 5.4 (dòng 130): bỏ "chặn trường hợp chép lệch ô như từng xảy ra với bảng RQ3" (lịch sử sửa lỗi).
- Phụ lục A.2: "(kernel v3)" → kernel huấn luyện `ductrannguyen/cxr-inference-demo` phiên bản 3 (bước S5-06); câu HTTP 200 thêm "tại thời điểm nộp". Bằng chứng: `docs/roadmap.md` hàng S5-06, `kaggle/inference_demo/kernel-metadata.json`.
- Phụ lục A.6: bỏ "(quy ước D4)".
- Phụ lục B.1: sửa dòng `slides/` thành "Chỗ để slide thuyết trình, mới có `.gitkeep` giữ chỗ"; thêm hàng **Tổng cộng 322**.
- Ch2 ghi chú: `outputs/split_check/*.json` giờ được track (xem 2.10); bỏ các tham chiếu "cell 5", "cell 6", "cell 3" (giữ tên notebook).
- A.4 "Repo của đề tài ở chế độ private": giữ nguyên (đúng về cơ chế triển khai); nêu rủ trong mô tả PR để người dùng xử lý theo quy định học phần.

### 2.10 Theo dõi hai tệp nguồn đang bị `.gitignore` chặn

`.gitignore` hiện có `outputs/`. Thêm ngoại lệ có kiểm soát để chỉ track hai tệp JSON mà ghi chú Chương 2 đang trích dẫn:

```
outputs/
!outputs/split_check/
outputs/split_check/*
!outputs/split_check/duplicates_summary.json
!outputs/split_check/cross_split_hamming_report.json
```

`git add -f` không cần nếu ngoại lệ đúng; kiểm `git status` chỉ còn hai tệp được thêm (không lọt `split_v1.csv` 3,4 MB và PNG).

### 2.11 Hàng rào kiểm thử mới

- `tests/test_report_tables_match_sources.py`: B.1 — thêm kiểm hàng tổng bằng tổng các dòng và bằng số tệp trong `git ls-files`; thêm kiểm mọi thư mục cấp một trong `git ls-files` đều có mặt trong bảng (đầy đủ).
- `tests/test_report_consistency.py`: thêm các phép:
  1. Bảng A.1 (Thông số mô hình đóng băng) xuất hiện trước Bảng A.2 (Biến môi trường) trong `08_phu_luc_a_c.md`; hàng `CXR_MODEL_SHA256` trỏ đúng bảng.
  2. Câu trọng số lớp ở C.1 nhắc đúng `balanced_subsample` và trọng số mẫu, không còn cụm "cân bằng bằng `weights='distance'`", không còn "cổng H3" ở Phụ lục C.
  3. Tóm tắt/Abstract chứa 0,0723 và 0,2084, và hai số này khớp Bảng 4.1 của Chương 4.
  4. Danh mục tài liệu: `[1]`–`[13]` liên tiếp, hai mục cuối khớp nguyên văn với danh mục cuối Chương 5.
- `tests/test_val_near_duplicate_subset.py`: thêm một phép cho CI của hiệu số (xem 2.6).

### 2.12 Đồng bộ số bộ kiểm thử sau khi thêm hàng rào

Sinh lại Bảng B.2 bằng `scripts/report_appendix_b.py` trên `.venv-demo`; cập nhật mọi vị trí ghi số phép/số module: Chương 5 (thân bài và ghi chú), Phụ lục A.1, tóm tắt (cả hai bản và ghi chú nguồn), `docs/report_standards.md` mục 3.3, `report/README.md` (các hàng nhắc số). Sinh lại mục lục.

## 3. Xác minh trước khi mở PR

- `pytest` toàn bộ trên tập module đã track trong worktree, bằng `.venv-demo` của cây chính (đường dẫn tuyệt đối): kỳ vọng số thu thập = 344 + số phép mới, 1 bỏ qua, còn lại pass.
- Script đối chiếu tổng hợp từng điểm senior (viết mới cho vòng này): mỗi mục N1–N7 và mục nhỏ một tiêu chí; TẤT CẢ PASS.
- `grep` sạch: không còn số trích dẫn cũ (`[7]`, `[8]` ở vị trí cũ), không còn "341/340/27 module", không còn "cổng H3" trong Phụ lục C, không dấu gạch dài trong câu mới.
- Hai script sinh (`report_appendix_b.py`, `report_frontmatter.py`) idempotent: chạy lại không làm đổi tệp.
- Không stage `results/report_rq*/bootstrap_config.json`; không đụng `slides/`, `demo/requirements.txt`.

## 4. Thứ tự thi công

1. Phụ lục A (N3 + kernel v3 + HTTP 200 + D4).
2. Phụ lục B (dòng slides, hàng tổng) — sinh lại sau khi có test mới.
3. Phụ lục C (N1, N2, N7, câu chênh số trích đặc trưng).
4. N6: mở rộng script, chạy, cập nhật Ch2 mục 2.5, Ch6 giới hạn 1, ghi chú.
5. Ch6: thêm giới hạn 12, cập nhật ghi chú mục 6.2.
6. Ch5: ghi chú (đường dẫn `load_benchmark_metrics`, bỏ lịch sử lỗi, câu mốc Kaggle).
7. Trích dẫn: Ch1 (ba điểm), Ch2 ([11]), Ch5 ([12], [13]), 07, README, note Ch1.
8. Tóm tắt/Abstract: N4, N5, các mục nhỏ.
9. Hàng rào mới (2.11).
10. Sinh lại B.1/B.2, mục lục; đồng bộ mọi vị trí số bộ kiểm thử (2.12).
11. Xác minh (mục 3), commit theo nhóm, push, mở PR (người dùng tự merge).

## 5. Rủi ro đã biết và cách xử lý

- Đổi số trích dẫn chạm nhiều tệp: chặn bằng grep toàn kho và hàng rào đối chiếu danh mục (2.11 mục 4).
- Bootstrap trên tập con có lớp 4 ảnh: CI xấp xỉ, ghi rõ trong báo cáo, kèm so recall từng lớp.
- `.gitignore` ngoại lệ sai có thể lọt tệp lớn: kiểm `git status` trước khi commit, chỉ được thêm hai tệp JSON.
- Cây làm việc chính đang ở nhánh slides: mọi sửa trong worktree; không chuyển nhánh ở cây chính.
