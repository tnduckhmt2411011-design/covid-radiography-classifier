# Bộ slide bảo vệ cuối kỳ (S6-03)

Sản phẩm: **28 slide trình bày + 6 slide dự phòng** cho buổi bảo vệ 30 phút
(21/11/2026), nền **ppt-master** (`https://github.com/hugohe3/ppt-master.git`,
commit `e2820d3`, cài ở `D:\Tools\ppt-master`), phong cách `academic-research`
và layout `report_core`.

- `deck_bao_ve.pptx` — bản chính, 34 trang, khung 13,333 × 7,5 in.
- `deck_bao_ve.pdf` — bản để nộp và in (xuất bằng WPS Presentation COM).
- `render/` — ảnh PNG từng trang, dùng để duyệt bằng mắt.

```
python -m slides.make_assets   # cắt ảnh val, dải mask, logo, kiểm cổng H2
python -m slides.figures       # sinh 8 biểu đồ từ CSV/JSON trong results/
python -m slides.build_deck    # sinh 34 SVG vào dự án ppt-master
python -m slides.export        # kiểm toán → PPTX → PDF → PNG
python -m slides.audit         # sáu nhóm kiểm: đáy trống, chồng lấn, cỡ chữ,
                               # lề 0,5 in, nguồn, cổng H2, D4, cụm từ cấm
python -m slides.render        # alias của export --skip-render + vẽ PNG
pytest tests/test_slides_data.py
```

Cách dựng trang: mỗi slide là một tệp SVG trong
`s6_03_bao_ve_cuoi_ky_ppt169_20261112/svg_output/`, gắn Master/Layout đã khai
báo; nền và đường kẻ giữ trên Master. **Không id nào lặp lại** trong toàn bộ
deck (mỗi id mang tiền tố số trang) và các vùng gốc không chồng lấn — hai điều
kiện bắt buộc của ppt-master. Phông ghi trong SVG là Segoe UI; sau khi xuất, một
bước vá ghi tường minh `typeface="Segoe UI"` vào XML slide vì WPS bỏ qua tham
chiếu `+mj-lt`/`+mn-lt` của theme.

**Nhất quán với các sprint khác:** S6-05 giữ kịch bản nói riêng; bản S6-03 này
không nhúng speaker notes. Demo dùng **Streamlit** (`demo/streamlit_app.py`),
không phải Gradio; ảnh chụp màn hình được lấy từ phiên Streamlit chạy thật
(`slides/capture_demo.py`).

**Cấu trúc 28 slide:** 3 hồi — Nền tảng (Ch.1–2, slide 1–9), Kết quả
(Ch.3–4, slide 10–18), Kiểm chứng và triển khai (Ch.5–6, slide 19–28). Điểm
mang về T1–T3 lặp lại ở slide 2, 20 và 27. Nếu bị rút còn 20 phút, bỏ 8 slide:
2, 5, 6, 9, 17, 23, 25, 26.

**Cổng dữ liệu:** mọi con số đọc từ `slides/data.py`, đọc trực tiếp CSV/JSON tại
thời điểm dựng; không có số nào gõ cứng, kể cả số trong tiêu đề. Ảnh minh hoạ
đều là ảnh `val` (`COVID-1006.png`, `Normal-9540.png`, ảnh kiểm tra mask), không
mở ảnh thuộc split `test`.
