# Bộ slide bảo vệ cuối kỳ (S6-03)

Sản phẩm: **28 slide trình bày + 6 slide dự phòng** cho buổi bảo vệ 30 phút
(21/11/2026), nền **ppt-master** (`https://github.com/hugohe3/ppt-master.git`,
commit `e2820d3`, cài ở `D:\Tools\ppt-master`), phong cách `academic-research`
và layout `report_core`.

- `deck_bao_ve.pptx` — bản chính, 34 trang, khung 13,333 × 7,5 in.
- `deck_bao_ve.pdf` — bản để nộp và in (xuất bằng WPS Presentation COM).
- `render/` — ảnh PNG từng trang, dùng để duyệt bằng mắt.

```
python -m slides.make_assets   # cắt ảnh val, bộ ba chế độ mask, logo, kiểm cổng H2
python -m slides.figures       # sinh 8 biểu đồ từ CSV/JSON trong results/
python -m slides.build_deck    # sinh 34 SVG vào dự án ppt-master
python -m slides.export        # kiểm toán → PPTX → PDF → PNG
python -m slides.audit         # bảy nhóm kiểm: đáy trống, chồng lấn (kể cả ô chân trang),
                               # cỡ chữ, lề 0,5 in, nguồn, cổng H2, D4, cụm từ cấm
python -m slides.render        # alias của export --skip-render + vẽ PNG
pytest tests/test_slides_data.py
```

Cách dựng trang: mỗi slide là một tệp SVG trong
`s6_03_bao_ve_cuoi_ky_ppt169_20261112/svg_output/`, gắn Master/Layout đã khai
báo; nền và đường kẻ giữ trên Master. **Không id nào lặp lại** trong toàn bộ
deck (mỗi id mang tiền tố số trang) và các vùng gốc không chồng lấn — hai điều
kiện bắt buộc của ppt-master. Cổng chồng lấn của `audit.py` đối chiếu cả ô
placeholder chân trang, vì ppt-master chỉ so chồng lấn giữa các vùng nội dung.
Phông ghi trong SVG là Segoe UI; sau khi xuất, một bước vá ghi tường minh
`typeface="Segoe UI"` vào XML slide vì WPS bỏ qua tham chiếu `+mj-lt`/`+mn-lt`
của theme.

**Cổng dữ liệu:** mọi con số đọc từ `slides/data.py`, đọc trực tiếp CSV/JSON
tại thời điểm dựng; không có số nào gõ cứng, kể cả số trong tiêu đề. Ngay cả
ngưỡng quy ước Δ ≥ 0,005, cỡ lưới siêu tham số của SVM và tên CPU cũng đọc từ
`results/threshold_v3.md`, `results/rq2_ghep_svm_s42/config.yaml` và
`results/demo_latency_sustained/latency.json`. Ảnh minh hoạ đều là ảnh `val`
(`COVID-1006.png`, `Normal-9540.png`, bộ ba chế độ mask của `COVID-1006.png`),
không mở ảnh thuộc split `test`.

**Link trên slide cuối:** mã nguồn GitHub, demo Streamlit Community Cloud
(`covid-xray-classifier.streamlit.app`, đã mở thật và thấy app chạy) và kho
artifact trên Hugging Face (`huggingface.co/duc16/cxr-svm-demo` — là *model
repo*, không phải app, nên ghi rõ là artifact).

**Nhất quán với các sprint khác:** S6-05 giữ kịch bản nói riêng; bản S6-03 này
không nhúng speaker notes. Demo dùng **Streamlit** (`demo/streamlit_app.py`),
không phải Gradio; ảnh chụp màn hình được lấy từ phiên Streamlit chạy thật
(`slides/capture_demo.py`).

**Cấu trúc 28 slide:** 3 hồi — Nền tảng (Ch.1–2, slide 1–9), Kết quả
(Ch.3–4, slide 10–18), Kiểm chứng và triển khai (Ch.5–6, slide 19–28). Điểm
mang về T1–T3 lặp lại ở slide 2, 20 và 27. Nếu bị rút còn 20 phút, bỏ 8 slide:
2, 5, 6, 9, 17, 23, 25, 26.

## Sửa sau đánh giá senior (12/11/2026)

Bản đã xuất lần đầu bị chê ở bốn nhóm; các lỗi đã sửa và kiểm lại:

- **Nội dung sai:** A0 là metadata tệp (không phải độ sáng), B0 là bộ đoán toàn
  bộ Normal; chi phí trích đặc trưng không đi theo số chiều (HOG 10.404 chiều
  0,0201 s/ảnh, GLCM+LBP 88 chiều 0,0552 s/ảnh); “mỗi bộ ba seed” chỉ đúng với
  DT, RF, GB; SVM có lưới 4 ứng viên và chạy một lần vì tất định; quy ước
  Δ ≥ 0,005 phải kèm “CI không chứa 0”; “Che phổi làm mất 0,0535” là kịch bản
  `lung_to_lung` (giữ phổi, che ngoài phổi); slide 18 viết lại thành dự đoán và
  bằng chứng kèm trạng thái; thêm bằng chứng `lung_to_lung − out_to_out` =
  −0,0431 [−0,0582; −0,0281].
- **Nguồn dẫn:** D4 nằm ở `results/final_test/r5_gioi_han.md`; bỏ dẫn
  `outputs/` (nằm trong `.gitignore`) để dẫn `splits/README.md`; đúng tên
  `r1_bootstrap_vs_reference.csv`; slide dự phòng B2 dẫn đúng
  `report_rq2/r1_per_seed.csv`.
- **Thuật ngữ:** “không Deep Learning (mạng nơ-ron)”, “tụt xuống”, “tập huấn
  luyện”, “tham chiếu: RF” thay cho “mốc nền: RF”.
- **Trình bày:** nhãn trục của slide 12 ba chữ số thập phân; chú thích không
  còn đè lên chân trang ở slide 6, 9, 18, 23, 24 và hai slide dự phòng B1, B6;
  slide 16 thay dải mask bằng bộ ba ô (gốc · chỉ phổi · ngoài phổi) của một
  ảnh val; slide 23 ghi rõ CPU đo và ảnh chụp lớn hơn.

## Nâng sàn cỡ chữ lên 18 pt (12/11/2026)

Sàn chữ của bộ slide kế thừa từ quy chuẩn văn bản .docx (14,25 pt) là quá nhỏ
cho phòng trình chiếu. Căn cứ: PLOS Computational Biology “Ten simple rules for
effective presentation slides”, MIT CommKit Slide Design, Penn State
(accessibility), Minnesota ODA, Old Dominion University, WUSTL Presentation
Accessibility Tips, quy định của ĐH Văn Hiến (tiêu đề 44 pt, nội dung 32 pt) và
hướng dẫn SoICT Bách khoa Hà Nội — chữ trên slide nên ≥ 18–24 pt.

- Sàn áp dụng: **mọi chữ hiện trên slide ≥ 18 pt (24 px)**, chỉ miễn dòng nguồn
  ở chân trang và số trang. Cỡ chữ tối thiểu trong `svgkit.py` (`SIZE_SMALL`)
  là 24 px; bản đồ cỡ chữ cũ → mới: 19→24, 20→24, 21→28, 22→28, 26→30 px, bề
  dòng 24→28, 26→30, 28→32, 30→34, 34→38, 36→40 px.
- `audit.py` nâng `MIN_BODY_PT` từ 14,0 lên 18,0 và chỉ miễn hai ô cuối trang.
- **Biểu đồ (`slides/figures.py`)** sinh PNG đúng kích thước ô ghép trên slide
  (ghép 1:1, không co), nên cỡ chữ matplotlib quy ra pt slide bằng nhân tố 2,085.
  Sàn 8,63 pt matplotlib ứng với 18 pt slide; mọi hằng cỡ chữ trong tệp đều
  ≥ 9,5 pt (≥ 19,7 pt hiệu dụng). Nhãn trục, tên trục, số trên thanh và dòng
  chú thích trong hình đều nằm trên mức đó. Hình có 6 thanh (RQ2, xáo trộn)
  cao 270–272 px để mỗi hàng đủ chỗ cho nhãn 26 px.
- Bố cục của 16 trang viết lại cho vừa chữ 18 pt: 1, 2, 3, 4, 5, 6, 8, 9, 16,
  18, 20, 22, 24, 25, 26, 27 và bốn slide dự phòng B1, B4, B5, B6.
- Kiểm lại bằng mắt toàn bộ 34 trang từ `render/p01.png`–`p34.png`; hai cổng
  (ppt-master `svg_quality_checker` và `slides.audit`) đều 0 lỗi chặn.

## Rà soát từng điểm ảnh (13–14/11/2026)

Hai cổng tự động chỉ so khung vùng và `data-pptx-bounds`; chúng không thấy phần
mực thật của chữ Việt (dấu mũ, dấu thanh vượt khung) và không thấy chữ nằm sát
mép thẻ. Vòng rà soát này đo trực tiếp:

- Chồng lấn giữa các vùng lấy từ `data-pptx-bounds`; sau đó render từng dòng
  chữ bằng PIL với `segoeui.ttf`/`seguibl.ttf` để lấy hộp mực thật (đỉnh =
  baseline − 0,88·cỡ chữ; đáy = baseline + 0,42·cỡ chữ cho dòng cuối).
- Cờ: khe mực giữa hai khối khác nhau < 6 px; chữ nằm trong thẻ mà cách mép
  < 3 px; đáy thẻ > 622 px (vạch chân trang ở 628 px).
- Biểu đồ: kiểm ảnh có bị cắt (nhãn trục, số cuối thanh) và ảnh có đúng tỷ lệ
  ô ghép.

Các sửa chính:

- Bề dòng tiêu đề 45→50 px để hai dòng tiêu đề không chạm nhau; tiêu đề hai
  dòng có ngắt tường minh ở slide 3, 12, 21 (`Page._title_lines` trong
  `svgkit.py`).
- Slide 3: thanh và số không còn chồng. Slide 8: ba mũi tên là ba đoạn thẳng
  vector trong khe 18 px (glyph "→" bị cắt); ô trạm 1 ghi `299×299` kèm chú
  thích "một kênh xám, không resize lại". Slide 11: bỏ nhãn trùng
  `ghép`/`rules`. Slide 12: chú thích CI tách dòng đúng. Slide 13: tiêu đề lấy
  từ dữ liệu (`SVM RBF 0,9024, hơn Random Forest 0,0442`). Slide 15: số đứng
  trước quy ước. Slide 17: biểu đồ hoán vị xếp lại thành dumbbell, chú giải lên
  trên trục. Slide 22: nhãn trục rút còn `COVID / Lung / Normal / Viral`.
  Slide 23: ảnh chụp canh giữa. Slide 27: `ngoài phổi − gốc = −0,0103`.
- Slide dự phòng: B1–B6 canh lại đáy thẻ và bề dòng; B2 chú thích lấy từ dữ
  liệu; B3 sửa `huần luyện` → `huấn luyện`; B4 hàng thứ hai đổi sang số lớn +
  nhãn (`Hamming = 4` 665, `Hamming = 2` 70, `Cặp khác nhãn` 229); B5 tiêu đề
  `349 lỗi validation, 138 lỗi tự tin ≥ 0,80`.
- Hình: nền trắng (`PAPER = #FFFFFF`) vì mọi hình nằm trong thẻ trắng;
  `_frame` chừa ≥ 118 px cho nhãn trục; trục dùng dấu trừ Unicode;
  `fig_test_gap` đổi sang forest plot hai hàng; `fig_brightness` bỏ chú thích
  trong hình, đường IQR dày 11; `fig_rq3_scenarios` in B0/A0 ngay trong hình.

Sau khi dựng lại: ppt-master 0 lỗi chặn (`With errors: 0 (0%)`),
`slides.audit` ĐẠT 34 trang, kiểm khe mực 0 lỗi, kiểm thẻ 0 lỗi (không thẻ nào
vượt 622 px hay ra ngoài khung 82..1198 / 197..720), kiểm thanh 0 lỗi, kiểm
widow còn 2 dòng đã chấp nhận (đường dẫn nguồn kết thúc bằng `/`; nhãn
`GLCM +`/`LBP` ngắt ở toán tử). PPTX/PDF/34 PNG đã xuất lại; postflight
`passed-with-warnings` với 45 cảnh báo không chặn.

