# Thiết kế S6-03: Bộ slide bảo vệ cuối kỳ

- **Ngày:** 12/11/2026
- **Trạng thái:** ĐÃ DUYỆT (12/11/2026) — chuyển sang viết kế hoạch thực thi. Chưa dựng slide.
- **Đường dẫn phân loại:** Architectural — sản phẩm mới trong `slides/`, ảnh hưởng tới S6-05 (kịch bản) và S6-04 (rà soát)
- **Căn cứ:** `slides/README.md`; `docs/roadmap.md` (S6-03, DoD); `docs/report_standards.md`; `report/README.md` và 6 chương trong `report/`; `results/` (số liệu gốc)

---

## 1. Mục tiêu và tiêu chí thành công

Bộ slide 16:9 dùng để bảo vệ đề tài trước hội đồng, thời lượng **30 phút trình bày + Q&A riêng**, dựng hoàn toàn từ số liệu có thật trong `results/`.

Một bản được coi là đạt khi:

1. Đúng **28 slide trình bày + 6 slide dự phòng**, khớp cấu trúc 6 chương của báo cáo.
2. Mọi con số trên slide truy về được một tệp trong `results/`, `splits/` hoặc `report/figures/`; không có số nào gõ cứng, kể cả số trong tiêu đề — tiêu đề có số cũng sinh từ `slides/data.py`.
3. Biểu đồ sinh lại được bằng script từ CSV/JSON gốc, không chụp lại từ báo cáo.
4. Không có ảnh nào thuộc split `test`; ảnh minh hoạ đều là `val` và ghi kèm `image_id`.
5. Câu chữ theo `docs/academic_writing_guide.md`: tiêu đề là câu khẳng định, không sáo ngữ, không danh từ hoá rườm rà.
6. Quy tắc D4 giữ nguyên văn ở mọi chỗ nói về chênh lệch val–test.
7. Xuất được `deck_bao_ve.pdf` 34 trang (28 + 6), kiểm toán hình học và cỡ chữ đạt.

## 2. Ràng buộc và nguồn chuẩn

| Nguồn | Ràng buộc áp dụng |
| :--- | :--- |
| `slides/README.md` | 16:9, tương phản tốt khi chiếu, số liệu từ `results/`, có nhãn trục và chú thích |
| `docs/report_standards.md` | Thông tin bìa CTUT/CICT, GVHD, MSSV; trích dẫn IEEE; cổng H2, H7; D4 |
| `report/README.md` | Bản đồ nguồn số liệu; test 3.176 ảnh; val 3.174 ảnh; 349 lỗi val; 427 lỗi test |
| Bourne (2007, *PLoS Comput Biol* 3(4): e77) | Tối đa 1 hình cho mỗi phút nói; người nghe nhớ 3 điểm; bớt chữ |
| Alley, *assertion–evidence* | Tiêu đề là câu khẳng định; bằng chứng là hình, không phải danh sách bullet |
| Quy tắc kiểm toán deck giữa kỳ | Chữ ≥ 14 pt (trừ chân trang), hình cách mép ≥ 0,5 in, không chồng lấn, không tràn chữ |

**Hệ quả số học:** 30 phút → trần 30 hình theo Bourne. 28 slide trình bày nằm dưới trần; 6 slide dự phòng không tính vì chỉ mở khi hội đồng hỏi.

## 3. Quyết định thiết kế đã chốt

| # | Quyết định | Lý do |
| :-: | :--- | :--- |
| D1 | 28 slide trình bày, 3 hồi: Nền tảng (Ch.1–2), Kết quả (Ch.3–4), Kiểm chứng và triển khai (Ch.5–6) | Bám thứ tự báo cáo để hội đồng đối chiếu, nhưng chia hồi để có nhịp |
| D2 | Mỗi slide có kicker ghi số chương (`CHƯƠNG 3 · KẾT QUẢ RQ1 VÀ RQ2`) | Giữ ưu thế cấu trúc báo cáo; hội đồng tra được mục |
| D3 | Tiêu đề là câu khẳng định có nội dung, không phải nhãn chủ đề | Theo assertion–evidence; buộc mỗi slide phải có ý |
| D4 | Nền giấy sáng cho slide nội dung; nền tối cho bìa, 3 slide mở hồi, slide số test và slide cảm ơn | Biểu đồ matplotlib nền trắng ghép tự nhiên; tối dùng làm điểm nhấn, không lạm dụng |
| D5 | Đúng một slide tối toàn phần cho con số test 0,8714 | Cao trào của buổi bảo vệ |
| D6 | Không animation, không hiệu ứng chuyển slide | Tránh phân tâm và lỗi khi chiếu máy lạ |
| D7 | Demo trình bày bằng ảnh chụp màn hình + số đo latency, không demo live | Không phụ thuộc mạng hội trường |
| D8 | Ví dụ input → output dùng **hai** ca: một đúng, một sai, đều thuộc `val` | Tránh cáo buộc chọn ca đẹp; ca sai là bằng chứng của RQ3 |
| D9 | Số trên slide lấy từ `slides/data.py` đọc trực tiếp CSV/JSON lúc dựng; không hard-code | Chặn lỗi gõ số và lệch sau khi báo cáo sửa |
| D10 | Không nhúng speaker notes trong bản S6-03 | Kịch bản là S6-05; tránh hai nguồn lời thoại lệch nhau |
| D11 | Cập nhật `slides/README.md`: 28 + 6 slide, sửa “Gradio” thành “Streamlit” | README hiện ghi 15–20 slide và demo Gradio, cả hai đều sai |

**Ba điểm mang về** (lặp ở slide 2, 20 và 27):

- **T1:** 152 đặc trưng thủ công + SVM RBF đạt macro-F1 **0,8714** trên 3.176 ảnh test, vượt xa hai mốc B0 = 0,1627 và A0 = 0,2397.
- **T2:** Mô hình chỉ nhìn vùng **ngoài** phổi vẫn đạt **0,8921**, chênh với ảnh gốc +0,0103 nhưng khoảng tin cậy chứa 0 — chưa đủ để nói vùng phổi là nguồn tín hiệu duy nhất.
- **T3:** Kết quả chỉ có giá trị trong phạm vi bộ dữ liệu này; không dùng cho bất kỳ quyết định y tế nào.

## 4. Kiến trúc sản phẩm và đường dẫn tệp

```
slides/
├── README.md                     # cập nhật theo D11
├── deck_bao_ve.pptx              # sản phẩm chính, 34 slide
├── deck_bao_ve.pdf               # bản xuất để nộp và in
├── __init__.py                   # để chạy python -m slides.*
├── data.py                       # đọc CSV/JSON, định dạng số kiểu Việt Nam
├── texts.py                      # câu nguyên văn: D4, disclaimer của app
├── figures.py                    # sinh toàn bộ biểu đồ vào figures/
├── make_assets.py                # cắt ảnh val, contact sheet mask, logo, manifest
├── layout.py                     # primitive pptx: nền, kicker, tiêu đề, chân trang, bảng
├── slides_act1.py                # slide 1–9
├── slides_act2.py                # slide 10–18
├── slides_act3.py                # slide 19–28
├── slides_backup.py              # B1–B6
├── build_deck.py                 # ráp 34 slide từ data.py + figures/ + assets/
├── audit.py                      # kiểm toán hình học, cỡ chữ, nguồn, ảnh test
├── render.ps1                    # render từng slide và xuất PDF qua WPS COM
├── figures/                      # 8 biểu đồ sinh tự động
└── assets/
    ├── logo_ctut.png
    ├── screenshot_demo.png       # ảnh chụp Streamlit, ca đúng
    ├── case_correct.png          # crop 299×299 từ val
    └── case_error.png            # crop 299×299 từ val
```

Ngoài `slides/`, chỉ thêm một tệp kiểm thử `tests/test_slides_data.py`. Không sửa `report/`, `results/`, `src/`, `demo/`.

## 5. Hệ thị giác

### 5.1 Bảng màu

| Token | Mã | Dùng cho |
| :--- | :--- | :--- |
| `paper` | `#F7F4EE` | nền slide nội dung |
| `ink` | `#161D26` | chữ chính, nền slide tối |
| `ink_soft` | `#4A5560` | chú thích, nhãn phụ |
| `teal` | `#0F766E` | điểm nhấn, cột chính, số quan trọng |
| `amber` | `#B45309` | ca sai, cảnh báo, đường mốc B0/A0 |
| `line` | `#D8D2C4` | đường kẻ mảnh, khung bảng |
| `paper_on_dark` | `#F2EFE7` | chữ trên nền tối |

Không dùng đỏ–xanh lá cạnh nhau để phân biệt dữ liệu; teal và amber đủ tương phản cho người mù màu đỏ–xanh.

### 5.2 Chữ

- Phông **Segoe UI** toàn bộ (đã dùng ở deck giữa kỳ, đủ dấu tiếng Việt).
- Tiêu đề slide: 30–34 pt, đậm, tối đa 2 dòng.
- Kicker: 14 pt, in hoa, màu teal.
- Thân: 15–18 pt; nhãn số lớn: 72–110 pt.
- Chân trang và số trang: 11 pt, `ink_soft`.
- Không chữ nào dưới 14 pt, trừ chân trang và số trang (chrome).

### 5.3 Lưới và chrome

- Khung 13,333 × 7,5 in; lề trái/phải 0,85 in; tiêu đề ở y = 0,55 in; nội dung 2,05–6,35 in; chân trang y = 6,66 in.
- Kicker trên trái; chân trang trái ghi nguồn (`Nguồn: results/report_rq1/r1_summary.csv`); số trang `11 / 28` trên phải.
- Đường kẻ ngang 0,75 pt màu `line` dưới tiêu đề.
- Slide tối đảo màu, giữ nguyên lưới.

### 5.4 Biểu đồ

- Sinh bằng matplotlib, `facecolor` trùng nền slide, 300 DPI, không viền trên/phải.
- Cột teal, thanh CI màu ink, nhãn giá trị đặt trên đỉnh cột.
- Đường mốc B0 và A0 nét đứt màu amber, có nhãn ở đầu đường; không bao giờ vẽ mốc mà không ghi số.
- Chú thích đơn vị và cỡ mẫu ngay trên hình (`n = 3.174 ảnh val`).
- Delta và CI ghi thành một dòng dưới hình, không nhồi vào tiêu đề.

## 6. Đặc tả 28 slide

Ký hiệu loại: **S** = nền sáng, **T** = nền tối, **TT** = tối toàn phần.

| # | Loại | Tiêu đề (câu khẳng định) | Bằng chứng và bố cục | Nguồn |
| :-: | :-: | :--- | :--- | :--- |
| 1 | T | Phân loại ảnh X-quang lồng ngực bằng học máy cổ điển và đánh giá nguy cơ shortcut learning trên bộ dữ liệu COVID-19 Radiography | Bìa dùng **nguyên văn tên đề tài trong báo cáo**, không viết lại: CTUT · Khoa CNTT & Truyền thông; GVHD TS. Lê Anh Nhã Uyên; 6 họ tên + MSSV; Lớp KHMT 2024 — Nhóm 10; Học kỳ 1, 2026–2027; Cần Thơ, 11/2026; logo trái trên | `report/00a_trang_bia_va_loi.md`, `docs/OWNERS.md` |
| 2 | S | Ba câu hỏi, sáu chương, ba điểm mang về | Cột trái: 6 khối chương; cột phải: T1–T3; không bullet dài | `report/README.md` |
| 3 | S | 21.165 ảnh, bốn lớp, lớp đông nhất gấp 7,6 lần lớp hiếm nhất | Bốn thanh ngang kèm số và %; chú thích B0 = 0,1627 nếu chỉ đoán Normal | `splits/split_v1.csv`, `threshold_v3.md` |
| 4 | S | Ba câu hỏi và một ranh giới: chỉ học máy cổ điển | Ba khối RQ1–RQ3 + dải H7; bốn đóng góp viết thành một dòng mỗi ý | `threshold_v3.md`, `tests/` |
| 5 | S | Nhãn lớp không độc lập với nguồn ảnh | Sơ đồ ba nguồn: Chowdhury 18.479; Mooney 1.345 Viral Pneumonia + 1.341 Normal; nhánh COVID đa nguồn | `report/02` mục 2.1 |
| 6 | S | Độ sáng và metadata chỉ chạm tới 0,2397 | Biểu đồ phân bố độ sáng 4 lớp; hai số: AUC COVID 0,6585; A0 0,2397 | `results/eda/brightness_by_class.csv`, `a0_shortcut/metrics.json` |
| 7 | S | Trùng tuyệt đối bị chặn, gần trùng thì không | 178 nhóm/401 ảnh; 14.815/3.174/3.176; 735 cặp (325/335/75; 229 khác nhãn); SHA-256 | `split_v1.csv`, `docs/roadmap.md`, `report/02` mục 2.3–2.5 |
| 8 | S | 152 chiều thủ công, chuẩn hóa chỉ trên train | Năm trạm: 299×299 → 4 nhóm đặc trưng → 152 → scaler fit 14.815 → SVM; HOG 10.404 đo riêng | `src/features_*`, `report/02` mục 2.6–2.7 |
| 9 | S | Sáu bộ phân loại, một thước đo duy nhất | Sáu tên + giao thức: 5-fold, bootstrap 2.000 lần, ngưỡng Δ ≥ 0,005, tham chiếu RF | `report_rq2/r1_bootstrap_vs_reference.csv` |
| 10 | T | Chương 3 — Kết quả trên 3.174 ảnh validation | Mở hồi: ba câu hỏi của chương, không số | — |
| 11 | S | Nhóm ghép dẫn đầu với 0,8599 ± 0,0030 | Bốn cột kèm CI: 0,8599 / 0,8156 / 0,7829 / 0,7625; hai đường B0, A0 | `report_rq1/r1_summary.csv` |
| 12 | S | Chỉ nói “tốt hơn” khi khoảng tin cậy không chứa 0 | Ba thanh Δ: ghép−hist +0,0770 [0,0611; 0,0925]; GLCM+LBP−hist +0,0328; HOG−hist −0,0203 [−0,0419; +0,0014]; dòng chi phí 42,5× | `r1_bootstrap_vs_reference.csv`, `rq1_cost_rank_record.md` |
| 13 | S | SVM RBF 0,9024, hơn RF 0,0442 | Sáu cột kèm CI; dòng Δ SVM−RF +0,0442 [0,0320; 0,0580]; dòng 349 lỗi val, 268 lỗi cặp Normal–Lung_Opacity | `report_rq2/r1_summary.csv`, `error_analysis_summary.md` |
| 14 | T | Chương 4 — Mô hình nhìn vào đâu để phân loại? | Mở hồi: câu hỏi RQ3, không số | — |
| 15 | S | Che phổi làm mất 0,0535 macro-F1 | Năm cột: 0,9024 / 0,8490 / 0,8921 / 0,2084 / 0,0723; đường B0, A0; Δ lung−orig −0,0535 [−0,0691; −0,0392] | `report_rq3/r1_summary.csv` |
| 16 | S | Che sạch phổi vẫn còn 0,8921 — và khoảng tin cậy chứa 0 | Hai cột lớn: 0,9024 và 0,8921; Δ +0,0103 [−0,0017; +0,0220]; dòng “chưa đủ kết luận”; kèm bốn ảnh contact sheet mask (mỗi lớp một ảnh) | `rq3_shortcut_learning_conclusion.md`, `rq3_mask_check` |
| 17 | S | Khi buộc nhìn trong phổi, GLCM mới lên tiếng | Thanh permutation 10 khối: chỉ-phổi GLCM 0,4960; ngoài-phổi LBP 0,3590, GLCM 0,3526, hist 0,2656 | `rq3_permutation_importance.csv` |
| 18 | S | Ba giả thuyết, bốn điều kiện bác bỏ | Trái: tuổi nhi, ký hiệu thiết bị, covariate shift (đều gắn nhãn “chưa kiểm chứng”); phải: 4 điều kiện phản chứng — Δ CI chứa 0; test nằm ngoài CI val; permutation importance khối ngoài phổi về 0; mô hình ngoài phổi xuống dưới A0 | `report/04` mục 4.3, `threshold_v3.md` R3 |
| 19 | T | Chương 5 — Một lần mở khóa, ba lớp kiểm chứng | Ba lớp: băm split, băm artifact, bộ kiểm thử (334 phép/26 module); kèm `UNLOCK_RECORD.json` | `final_test/UNLOCK_RECORD.json`, `report/05` mục 5.4 |
| 20 | TT | 0,8714 trên 3.176 ảnh test | Số lớn giữa slide; CI [0,8579; 0,8840]; accuracy 86,56%; n = 3.176 | `final_test_report.json` |
| 21 | S | Val 0,9024, test 0,8714: chênh 0,0310 — chỉ là quan sát | Hai mốc + dải chênh; nguyên văn D4 in nghiêng, không thêm chữ “nguyên nhân” | `final_test_report.json`, `threshold_v3.md` D4 |
| 22 | S | 427 lỗi, 304 lỗi nằm giữa Normal và Lung_Opacity | Ma trận 4×4; ô 142 và 162 tô amber; 71,19%; precision Lung_Opacity 0,8013 thấp nhất | `final_test/metrics.json` |
| 23 | S | Demo chạy 0,132 giây một ảnh | Ảnh chụp Streamlit (ca đúng); ba số: decode 0,0033 s, đặc trưng 0,1192 s, suy luận 0,0092 s | `demo_latency_sustained/latency.json`, `screenshot_demo.png` |
| 24 | S | Một ca đúng, một ca sai: mô hình nhìn gì | Hai cặp ảnh + xác suất: COVID-1006 → COVID 0,9979; Normal-9540 → Lung_Opacity 0,9700; mask bên cạnh ca sai | `preds_val.csv`, `D:\cxr_data` (val) |
| 25 | S | Giới hạn: 735 cặp gần trùng và không có patient_id | Bốn khối: gần trùng; thiếu patient_id; nguồn và tuổi chưa xác minh; ngoại suy ngoài bộ dữ liệu | `r5_gioi_han.md`, `report/06` mục 6.2 |
| 26 | S | Không dùng để chẩn đoán | Trích nguyên văn disclaimer của app; D4; phạm vi ngoại suy (khác nguồn, khác tiền xử lý thì kết quả không có giá trị đánh giá) | `demo/streamlit_app.py` dòng 60–64 |
| 27 | S | Ba điểm mang về và việc còn lại | T1–T3 + ba hướng phát triển gắn với ba giới hạn | tổng hợp |
| 28 | T | Cảm ơn — mời hội đồng đặt câu hỏi | Logo, tên nhóm; hai URL dạng chữ, không QR: `github.com/tnduckhmt2411011-design/covid-radiography-classifier` và `huggingface.co/duc16/cxr-svm-demo` | `git remote -v`, `demo/README.md` |

## 7. Sáu slide dự phòng

Đặt sau slide 28, không đánh số `/28`, tiêu đề bắt đầu bằng `DỰ PHÒNG`.

| # | Nội dung | Nguồn |
| :-: | :--- | :--- |
| B1 | RQ1 từng seed và CI của từng nhóm | `report_rq1/r1_per_seed.csv` |
| B2 | RQ2 đầy đủ 6 bộ, siêu tham số đã chọn | `rq2_classifier_selection_record.md`, `report_rq2/r1_summary.csv` |
| B3 | RQ3 đủ 5 kịch bản: CI, accuracy, recall từng lớp | `report_rq3/r1_summary.csv`, `r4_sampling_error.csv` |
| B4 | 735 cặp gần trùng: phân bố theo cặp split và nhãn | `docs/roadmap.md`, `report/02` mục 2.5 |
| B5 | Ma trận nhầm lẫn validation, 349 lỗi, 240 lỗi đồng thuận, 138 lỗi p ≥ 0,80 | `results/error_analysis/*` |
| B6 | Latency chi tiết 3 lượt × 200 ảnh + metadata artifact | `demo_latency_sustained/latency.json`, `model_artifact.py` |

## 8. Sinh hình và chặn lệch số

`slides/data.py` là nguồn số duy nhất:

- `load_rq1()`, `load_rq2()`, `load_rq3()`, `load_test()`, `load_latency()`, `load_dataset()` đọc CSV/JSON bằng `pandas`/`json`.
- `fmt(x, digits=4)` định dạng dấu phẩy thập phân; `fmt_pct()` cho phần trăm; `fmt_delta()` luôn kèm dấu.
- Không hàm nào nhận tham số số; mọi giá trị đọc từ tệp.

`slides/figures.py` sinh 8 hình, mỗi hình khai báo rõ tệp nguồn trong docstring:

1. `fig_rq1_ci.png` — 4 nhóm, CI, mốc B0/A0.
2. `fig_rq1_delta.png` — 3 thanh Δ kèm CI, đường 0 và ngưỡng +0,005.
3. `fig_rq2_ci.png` — 6 bộ, CI, mốc tham chiếu RF.
4. `fig_rq3_scenarios.png` — 5 kịch bản, CI, mốc B0/A0.
5. `fig_rq3_perm.png` — 10 khối, hai nhóm chỉ-phổi và ngoài-phổi.
6. `fig_brightness.png` — phân bố độ sáng 4 lớp.
7. `fig_test_confusion.png` — ma trận nhầm lẫn test, tô ô Normal↔Lung_Opacity.
8. `fig_test_gap.png` — hai mốc val 0,9024 và test 0,8714, dải chênh, không chú thích nguyên nhân.

Cặp ảnh input → output của slide 24 **không** vẽ trong matplotlib: ảnh X-quang là ảnh thật, ghép trong pptx bằng `layout.add_picture` và thanh xác suất vẽ bằng shape.

Quy tắc chặn lệch:

- Hình không được vẽ lại từ bảng markdown trong `report/`; chỉ đọc CSV/JSON.
- `tests/test_slides_data.py` kiểm tra 6 giá trị neo: 0,8599; 0,9024; 0,8714; 0,8921; 0,0535; 427.
- Nếu CSV đổi, test đổi theo; slide dựng lại sẽ đổi theo vì không hard-code.

## 9. Ảnh minh hoạ và ảnh chụp demo

- Nguồn ảnh: `D:\cxr_data\COVID-19_Radiography_Dataset\...\images\`, đọc qua biến `CXR_DATA_ROOT` (mặc định `D:\cxr_data\COVID-19_Radiography_Dataset`). Trước khi dùng, đối chiếu `splits/split_v1.csv` để chắc `split == "val"`.
- Ca đúng: `COVID-1006.png` (val, dự đoán COVID, xác suất 0,9979).
- Ca sai: `Normal-9540.png` (val, nhãn thật Normal, dự đoán Lung_Opacity, xác suất 0,9700).
- Ảnh chụp demo: chạy `streamlit run demo/streamlit_app.py` với `CXR_MODEL_PATH=outputs\k_v3_out\cxr_inference_model_cache.joblib`, tải `COVID-1006.png`, chụp ở 1600×1000, thấy rõ nhãn dự đoán, bảng xác suất, sidebar số đo và disclaimer.
- Kiểm chứng sau khi chụp: nhãn và xác suất trên màn hình phải khớp `preds_val.csv` (sai số làm tròn 2 chữ số).
- Không mở, không chụp, không trích bất kỳ tệp nào có `image_id` thuộc split `test`; `audit.py` đối chiếu tên tệp với danh sách test và dừng nếu trùng.

## 10. Quy trình dựng và kiểm toán

1. Chạy `python -m slides.figures` sinh 7 hình.
2. Chạy `python -m slides.build_deck` dựng `deck_bao_ve.pptx` (34 slide).
3. Chạy `python -m slides.audit` kiểm 6 nhóm:
   - a) đáy trống > 25% hoặc một cột trống > 30%;
   - b) chồng lấn ngoài ý muốn;
   - c) tràn chữ theo ước lượng, gắn nhãn “cần kiểm lại trong PowerPoint”;
   - d) chữ < 14 pt (trừ chrome);
   - e) hình cách mép < 0,5 in;
   - f) kicker, số trang, chân trang nguồn đồng nhất.
4. Render từng slide qua WPS Presentation COM (`render.ps1`, `Kwpp.Application` — máy dựng bài không có Microsoft PowerPoint), mắt người duyệt 34 ảnh.
5. Xuất PDF, kiểm 34 trang, 960 × 540 pt.

Audit trả mã lỗi khác 0 nếu bất kỳ mục nào không đạt; không có ngoại lệ “tạm bỏ qua”.

## 11. Kiểm thử và nghiệm thu

| Hạng mục | Cách kiểm | Đạt khi |
| :--- | :--- | :--- |
| Số liệu | `pytest tests/test_slides_data.py` | 6 giá trị neo khớp tệp nguồn |
| Bố cục | `python -m slides.audit` | 0 vi phạm a, b, d, e, f |
| Tràn chữ | Render + mắt người | Không có chữ bị cắt ở 34 ảnh |
| Ảnh test | `audit.py` đối chiếu `image_id` | 0 ảnh thuộc split test |
| D4 | Đọc slide 21 và 26 | Có nguyên văn, không có từ “nguyên nhân”, “do đó”, “vì vậy” khi nói chênh lệch |
| Nguồn | Chân trang từng slide | 100% slide dữ liệu có đường dẫn tệp |
| Thời lượng | Bấm giờ bản diễn tập 30 phút | Không vượt 30:00; không slide nào quá 90 giây |

## 12. Rủi ro và xử lý

| Rủi ro | Xử lý |
| :--- | :--- |
| Ảnh chụp Streamlit lệch số do model/artifact khác | Chặn bằng kiểm chứng nhãn + xác suất với `preds_val.csv`; sai thì chụp lại |
| WPS COM không render được trên máy khác | Máy dựng bài chỉ có WPS (`Kwpp.Application`); giữ bản PDF làm chuẩn nộp, render chỉ để duyệt nội bộ. Nếu WPS lỗi COM, mở WPS bằng tay một lần rồi chạy lại `render.ps1` |
| Biểu đồ nhiều số gây rối | Tối đa 6 cột/hình; số phụ chuyển xuống slide dự phòng |
| Hội đồng hỏi ngoài 28 slide | 6 slide dự phòng + báo cáo đã có đủ bảng |
| 30 phút bị rút còn 20 | Đánh dấu 8 slide cắt được (2, 5, 6, 9, 17, 23, 25, 26) trong ghi chú kỹ thuật khi dựng, không xoá khỏi deck; còn 20 slide ≈ 21–22 phút |

## 13. Ngoài phạm vi

- Kịch bản nói, phân vai, tập diễn: S6-05.
- Sửa báo cáo, sửa mã nguồn, sửa demo: không thuộc S6-03.
- Bản tiếng Anh của slide.
- Animation, video, demo live.

## 14. Điều kiện tiên quyết trước khi dựng

1. **Nhánh git:** worktree đang ở `report/mo-dau-quyen` và có thay đổi chưa commit của việc khác. Dựng trên nhánh `slides/s6-03-deck-bao-ve` tạo từ `main`; mang theo `slides/README.md` (đang chưa được theo dõi) và commit cùng deck.
2. **Logo:** dùng `C:\Users\LENOVO\AppData\Local\Temp\opencode\ctut_logo_clean.png`, bản đã dùng ở deck giữa kỳ, để hai bản trình bày cùng một nhận diện.
3. **Nguồn ảnh:** `D:\cxr_data\COVID-19_Radiography_Dataset` phải còn đủ 4 thư mục lớp; nếu thiếu, dừng và báo, không thay bằng ảnh khác nguồn.

---

## 15. Thay đổi sau khi duyệt (12/11/2026): dựng bằng ppt-master

Đặc tả gốc mô tả công cụ dựng là python-pptx. Bản thực tế đã chuyển sang
**ppt-master** (https://github.com/hugohe3/ppt-master.git, commit `e2820d3`, cài
tại `D:\Tools\ppt-master`) vì nó kiểm soát được hợp đồng SVG, kiểm toán hình học
trước khi xuất và xuất khung Master/Layout chuẩn — ba thứ python-pptx không tự
làm được.

Các quyết định trong §3 giữ nguyên; chỉ thay cách thực hiện:

| Hạng mục | Cũ (đã duyệt) | Thực tế |
| :--- | :--- | :--- |
| Công cụ dựng | `layout.py` + python-pptx | `svgkit.py` sinh trang SVG, ppt-master xuất PPTX |
| Kiểm toán | `audit.py` tự đo hình học | ppt-master kiểm hình học/lề/chồng lấn; `audit.py` kiểm thêm cỡ chữ, cổng H2, D4, cụm từ cấm |
| Xuất PDF | `render.ps1` + WPS | `export.py` (kiểm → `svg_to_pptx` → vá phông → WPS → PDF → PNG) |
| Biểu đồ | 7 hình | 8 hình (`fig_test_gap.png` thêm cho slide 21) |
| Ảnh chụp demo | chụp tay | `capture_demo.py` mở Streamlit thật qua Chrome headless và nạp ảnh val qua đúng ô tải tệp |

Hai điểm bắt buộc ppt-master đòi hỏi khi soạn trang: không id nào lặp lại trong
toàn bộ deck, và các vùng gốc không chồng lấn. Hai điều kiện này được `svgkit.py`
đảm bảo bằng tiền tố số trang cho id và bằng việc gói mỗi khối nội dung trong một
`Zone` có `data-pptx-bounds` riêng.
