# Nhật ký công việc: sửa review senior vòng cuối (N1–N7 + mục nhỏ)

- **Ngày:** 2026-11-12 (thi công 2026-11-13)
- **Nhánh:** `report/sua-review-vong-cuoi` từ `origin/main` (`cec8a8a`), worktree riêng.
- **Spec:** `docs/superpowers/specs/2026-11-12-sua-review-vong-cuoi-design.md`
- **Kế hoạch:** `docs/superpowers/plans/2026-11-12-sua-review-vong-cuoi.md`

## Phạm vi

Sửa toàn bộ điểm review senior vòng cuối trên sáu chương, tài liệu tham khảo, ba phụ lục và tóm tắt; thêm một phép đo mới (bootstrap CI cho hiệu macro-F1 giữa hai tập con gần trùng); thêm hàng rào kiểm thử; đồng bộ số bộ kiểm thử.

## Thay đổi chính

| Điểm review | Thay đổi | Tệp |
| :--- | :--- | :--- |
| N3 (A.2 logic đảo, bảng A, "mặc định") | Đảo câu điều kiện, đánh số lại Bảng A.1/A.2, bỏ "mặc định của Streamlit Community Cloud", ghi rõ kernel huấn luyện v3 và "tại thời điểm nộp", bỏ "(quy ước D4)" | `08` |
| Phụ lục B | Hàng `outputs/` (2 tệp JSON track), hàng **Tổng cộng**, mô tả `slides/` đúng thực tế; hàng rào B.1 kiểm hàng tổng và tính đầy đủ | `08`, `scripts/report_appendix_b.py`, `tests/test_report_tables_match_sources.py` |
| N1 (C.1 trọng số lớp) | Câu đúng cơ chế từng bộ: LR/DT/SVM `balanced`, RF `balanced_subsample`, GB trọng số mẫu, knn `weights='distance'` là trọng số khoảng cách | `08` |
| N2 (C.2 "cổng H3", cấu hình rf) | Bỏ mã hiệu nội bộ, "tất định về nhãn dự đoán", rf là cấu hình chọn bằng CV khác RQ1 | `08` |
| N7 (biên lưới) | Câu biên lưới ở C.1 (5/6 bộ), hạng 12 ở Chương 6 | `08`, `06` |
| Chênh 0,0568↔0,0780 | Câu phân biệt hai lần đo (RQ1 kernel v5, RQ2 kernel v3) ở C.3 | `08` |
| N6 (khoảng tin cậy hiệu 0,0051) | Bootstrap 2.000 lần lấy mẫu lại độc lập trong từng tập con, seed 42: CI [−0,0462; 0,0386] chứa 0; recall từng lớp lệch hai hướng; cảnh báo xấp xỉ (Viral Pneumonia chỉ 4 ảnh) | `scripts/val_near_duplicate_subset.py`, `02`, `06` |
| N4/N5 (tóm tắt) | Đủ 5 kịch bản RQ3 (0,0723 / 0,2084), câu kết đúng phạm vi, "trả lời ba câu hỏi", độ trễ "khi chạy liên tiếp" | `09` |
| Trích dẫn | 13 tài liệu: [7] Haralick, [8] Ojala, [9] Dalal-Triggs (1.2), [10] Efron (1.3), [11] Platt (2.7); Ch5 đổi [7]→[12], [8]→[13]; pHash ghi chú thư viện `imagehash` | `01`, `02`, `05`, `07`, `README` |
| Mục nhỏ | Ghi chú Ch5: đường dẫn `load_benchmark_metrics` (`rq3_...`), bỏ lịch sử lỗi chép lệch ô, "đo ở phiên kernel khác"; Ch2 bỏ tham chiếu "cell N"; track 2 JSON `outputs/split_check` | `05`, `02`, `.gitignore` |

## Số đo mới (sinh bằng script)

- `python scripts/val_near_duplicate_subset.py` ghi thêm vào `results/val_near_duplicate_subset/val_near_duplicate_subset.json`: `bootstrap_ci` (n_boot 2000, seed 42, lo −0,0462, hi 0,0386, boot_mean −0,0002, boot_median 0,0047, chứa 0), `recall_subset`, `recall_complement`.
- Bộ kiểm thử track: 351 phép / 28 module; `pytest -q` cho 350 pass + 1 bỏ qua (skip `nbformat` như trước).

## Hàng rào mới

- `tests/test_report_consistency.py`: +6 (thứ tự bảng A; câu trọng số lớp C.1 đối chiếu `CLASSIFIER_SPECS`; tóm tắt có 0,0723/0,2084; danh mục [1]–[13] liên tục, khớp Ch5 và câu dẫn đúng số; Ch2 không còn "chưa đo mức chênh"; README đếm đúng số hạng mục Ch6).
- `tests/test_val_near_duplicate_subset.py`: +1 (tái lập CI từ JSON).
- `tests/test_report_tables_match_sources.py`: mở rộng B.1 (hàng tổng, tính đầy đủ).

## Rủi ro đã nêu cho người duyệt

- Hai tệp JSON `outputs/split_check/` được track làm nguồn ghi chú Chương 2 (ngoại lệ `.gitignore` có kiểm soát).
- A.4 giữ nguyên câu "Repo ở chế độ private" (đúng cơ chế triển khai); nếu quy định học phần yêu cầu công khai, đổi trước khi nộp.
- Tóm tắt hai bản vẫn trong một trang mỗi bản sau khi thêm mệnh đề RQ3.

## Xác minh (2026-11-13)

- `pytest` toàn bộ module track (kèm artifact cục bộ trong worktree, không commit): **351 collected, 350 passed, 1 skipped** (`test_inference_demo_notebook` thiếu `nbformat`).
- Script đối chiếu 74 mốc (N1–N7, chênh số liệu, mục nhỏ, trích dẫn, số 351/327): **TẤT CA PASS**.
- Idempotent: chạy lại `scripts/report_appendix_b.py` và `scripts/report_frontmatter.py` → `git diff` sạch.
- Quy ước chữ: câu mới không có dấu gạch dài (U+2014); các chỗ còn lại trong `report/` đều là câu cũ, ngoài phạm vi đợt này. Câu mới dùng phẩy thập phân, chấm hàng nghìn.
- Không stage `results/report_rq*/bootstrap_config.json` (pytest ghi lại phiên bản thư viện vào các tệp này; đã khôi phục nguyên trạng).

## Vòng sửa sau review độc lập (2026-11-13)

Reviewer độc lập đọc toàn nhánh, chạy lại pytest và generator, nêu 2 lỗi Important và 5 Minor; đã sửa hết:

1. `05` câu dẫn danh mục ghi "đánh tiếp từ [9]" cạnh `[12]`/`[13]` → sửa thành `[12]`; hàng rào `test_reference_list_contiguous_and_matches_ch5` nay đọc cả câu dẫn và so với số bắt đầu của danh mục Chương 5.
2. `02` mục 2.5 còn câu "Đề tài chưa đo mức chênh này" mâu thuẫn với CI vừa công bố → thay bằng giới hạn thật ("chưa tách được ảnh hưởng của bản gần trùng lúc huấn luyện"); hàng rào mới `test_ch2_near_duplicate_claim_matches_json`.
3. `README` hàng 6.2 ghi "Gồm 11 hạng mục" → "Gồm 12 hạng mục", bổ sung hạng 12; hàng rào mới `test_readme_limit_count_matches_ch6`.
4. Typo "cẩn nang viết" trong `scripts/report_appendix_b.py` và Bảng B.1 → "cẩm nang viết"; sinh lại bảng.
5. Khối `bootstrap_ci` thêm `boot_mean` (−0,0002) và `boot_median` (0,0047) để kiểm độ lệch của phân phối bootstrap; docstring ghi quy ước lớp vắng mặt nhận F1 = 0; phép kiểm tái lập kiểm thêm hai khóa.
6. Bỏ dòng trống giữa hạng 11 và 12 của Chương 6 để danh sách đánh số liền mạch.
7. Câu dẫn danh mục Chương 1 viết lại cho rõ ("các mục còn lại của chương này (1.2, 1.3) và tài liệu của các chương sau…").

Do thêm 2 phép kiểm thử, số bộ kiểm thử đồng bộ lại thành **351 phép / 28 module / 350 pass + 1 bỏ qua** ở Ch5, Phụ lục A/B, tóm tắt, `docs/report_standards.md`, `report/README.md` và mục lục.
