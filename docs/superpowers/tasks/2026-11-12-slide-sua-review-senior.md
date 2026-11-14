# Nhiệm vụ: sửa deck S6-03 theo đánh giá senior (12/11/2026)

Checklist làm việc. Đánh dấu `[x]` khi xong và đã kiểm lại.

## A. Nội dung sai / gây hiểu sai

- [ ] **A1 · Slide 6** — tiêu đề và ô B0 nói sai. A0 = metadata tệp (không phải độ sáng); B0 = đoán toàn bộ là Normal.
- [ ] **A2 · Slide 8 và 12** — bỏ khẳng định "chi phí đi theo cỡ chiều"; thay bằng số đo: HOG 10.404 chiều 0,0201 s/ảnh, GLCM+LBP 88 chiều 0,0552 s/ảnh.
- [ ] **A3 · Slide 4 và 9** — "mỗi bộ ba seed" sai (chỉ DT, RF, GB); "SVM một tham số duy nhất" sai (lưới 4 ứng viên); thêm 5-fold StratifiedGroupKFold; quy ước Δ ≥ 0,005 **và** CI không chứa 0, ghi là quy ước nhóm.
- [ ] **A4 · Slide 18** — viết lại cột phải: không còn "điều kiện bác bỏ" mà là "dự đoán nếu giả thuyết đúng" + "bằng chứng cần có" + trạng thái đã xảy ra; ba giả thuyết khớp `report/04_hoc_loi_tat_rq3.md` mục 4.3; sửa "tụng xuống" → "tụt xuống".
- [ ] **A5 · Slide 15 và 16** — "Che phổi làm mất 0,0535" gọi nhầm kịch bản (đó là lung_to_lung: giữ phổi, che ngoài phổi); tiêu đề slide 16 tách rõ CI chứa 0 là của hiệu `orig − out`; thêm quy ước "A → B".
- [ ] **A6 · Slide 4, 14, 16, 24, 25** — hạ câu hỏi RQ3 về đúng phạm vi: `che/cắt theo mask có làm đổi macro-F1 không`; slide 24 không hứa "mô hình nhìn gì".
- [ ] **A7 · Slide 17** — thêm bằng chứng mạnh nhất RQ3: `lung_to_lung − out_to_out` = −0,0431, CI [−0,0582; −0,0281] không chứa 0.
- [ ] **A8 · Slide 17** — sửa "GLCM mới lên tiếng"; ghi rõ GLCM cao nhất khi chỉ nhìn trong phổi (0,4960); không xếp hạng LBP 0,3590 vs GLCM 0,3526 (chênh 0,0064 < std 10 lần xáo trộn); ghi chưa chuẩn hóa theo cỡ khối.
- [ ] **A9 · Slide 25 và 26** — "không có giá trị" → "chưa được đánh giá"; thêm giới hạn R5: val vừa chọn mô hình vừa báo cáo nên hơi lạc quan.
- [ ] **A10 · Slide 27** — T1 ghi rõ 0,8714 là test, hai mốc nền đo trên validation; T2 ghi nhãn validation; bỏ cụm "Thay hệ cỡ mẫu".
- [ ] **A11 · Slide B5** — "lỗi ở cả ba seed" sai: đồng thuận = SVM sai **và** GB, RF sai (GB, RF theo đa số 2/3 seed); SVM chỉ 1 seed.
- [ ] **A12 · Slide 23** — ghi rõ 0,132 s đo trên laptop i5-13420H (không phải máy deploy); sửa "luỗt" → "lượt".
- [ ] **A13 · Slide 11 và 13** — giải thích hai số RF: 0,8599 (RQ1, RF cố định 500 cây) và 0,8582 (RQ2, RF chọn siêu tham số bằng CV).
- [ ] **A14 · Slide 5** — 18.479 ảnh thuộc Rahman et al. 2021 (bộ COVQU), không phải Chowdhury 2020; "ít nhất hai nguồn" → đủ số kho thật; viết rõ câu "một tệp nguồn".

## B. Nguồn dẫn sai

- [ ] **B1** — D4: `results/threshold_v3.md (D4)` → `results/final_test/r5_gioi_han.md` (slide 18, 21, 26).
- [ ] **B2** — slide 9: `r2_bootstrap_vs_reference.csv` → `results/report_rq2/r1_bootstrap_vs_reference.csv`.
- [ ] **B3** — slide 7: bỏ dẫn `outputs/` (nằm trong .gitignore) → `splits/README.md`.
- [ ] **B4** — slide B2: `report_rq1/r1_per_seed.csv` → `results/report_rq2/r1_per_seed.csv`.
- [ ] **B5** — slide 25: đường dẫn `results/rq3_mask_check/..r5_gioi_han.md` bị cắt → `results/report_rq3/r5_gioi_han.md`.
- [ ] **B6** — slide 18: `report/04 mục 4.3` → `report/04_hoc_loi_tat_rq3.md` mục 4.3.

## C. Chính tả / thuật ngữ

- [ ] **C1** — slide 4: "không mạng tích hợp" → "không Deep Learning (mạng nơ-ron)".
- [ ] **C2** — "tụng xuống" → "tụt xuống".
- [ ] **C3** — slide B3: "phôi đào tạo" → "tập huấn luyện".
- [ ] **C4** — slide 13 và hình `fig_rq2_ci`: "mốc nền: RF" → "tham chiếu: RF" (trùng thuật ngữ với B0/A0).

## D. Trình bày

- [ ] **D1** — slide 6, 21, 23, 24: chân trang / chú thích không đè lên nội dung.
- [ ] **D2** — slide B1 và B6: hết chồng chữ.
- [ ] **D3** — slide 12: nhãn trục làm tròn sai (0,025 hiện thành 0,02; −0,025 thành −0,03) → ba chữ số thập phân.
- [ ] **D4t** — slide 16: dải mask lớn hơn, nhãn không chồng (thay bằng bộ ba ô gốc · chỉ phổi · ngoài phổi của một ảnh val).
- [ ] **D5** — slide 23: ảnh chụp app lớn hơn, đọc được.

## E. Slide cuối

- [ ] **E1** — `huggingface.co/duc16/cxr-svm-demo` đổi nhãn thành "Artifact mô hình" (đã xác nhận là model repo, không phải app).
- [ ] **E2** — thêm link demo thật: `https://covid-xray-classifier.streamlit.app/` (đã mở thử, app chạy, hiển thủ công 0,9024 / 0,8714 / −0,0310).
- [ ] **E3** — giữ link GitHub (bạn xác nhận repo công khai).

## F. Xuất bản lại

- [ ] **F1** — `python -m slides.make_assets` → `python -m slides.figures` → `python -m slides.build_deck` → `python -m slides.export` → `python -m slides.audit` đạt 0 vi phạm.
- [ ] **F2** — `pytest tests/test_slides_data.py` đạt.
- [ ] **F3** — duyệt bằng mắt 34 ảnh `slides/render/`.
- [ ] **F4** — cập nhật `slides/README.md` và ghi chú trạng thái; commit.
