# Ghi chép thiết lập môi trường Kaggle (Kaggle Setup Notes)

Tài liệu này ghi nhận kết quả chạy kiểm tra môi trường Kaggle CPU qua Kaggle CLI `[Theo biên bản họp 16/10/2026 mục 3.8: không dùng GPU, phiên CPU không giới hạn giờ]`.

---

## 1. Các lệnh Kaggle CLI đã sử dụng

```powershell
# 1. Cài đặt Kaggle CLI vào môi trường ảo
.\.venv\Scripts\python -m pip install kaggle

# 2. Kiểm tra phiên bản và xác thực tài khoản
.\.venv\Scripts\kaggle.exe --version
.\.venv\Scripts\kaggle.exe kernels list --user ductrannguyen

# 3. Kiểm tra danh mục file trong dataset từ xa
.\.venv\Scripts\kaggle.exe datasets files tawsifurrahman/covid19-radiography-database

# 4. Đẩy notebook chạy kiểm tra môi trường lên Kaggle CPU (chạy CPU do enable_gpu false)
.\.venv\Scripts\kaggle.exe kernels push -p kaggle/setup_check

# 5. Theo dõi trạng thái kernel định kỳ (~30 giây/lần)
.\.venv\Scripts\kaggle.exe kernels status ductrannguyen/cxr-setup-check

# 6. Kéo kết quả và log về máy cục bộ
$env:PYTHONUTF8=1
.\.venv\Scripts\kaggle.exe kernels output ductrannguyen/cxr-setup-check -p outputs/setup_check --force
```

---

## 2. Cấu hình `kernel-metadata.json`

```json
{
  "id": "ductrannguyen/cxr-setup-check",
  "title": "cxr-setup-check",
  "code_file": "00_setup_check.ipynb",
  "language": "python",
  "kernel_type": "notebook",
  "is_private": true,
  "enable_gpu": false,
  "enable_internet": false,
  "dataset_sources": [
    "tawsifurrahman/covid19-radiography-database"
  ]
}
```

---

## 3. Cấu hình môi trường Kaggle CPU (đầu ra setup_check)

`[Theo đầu ra notebooks/00_setup_check.ipynb trên Kaggle CPU]`

* **Python:** `3.12.13 (GCC 11.4.0)`
* **Hệ điều hành:** `Linux 6.18.48+` (`posix`)
* **CPU:** `4` (`CPU Count: 4`)
* **RAM:** `32869448 kB` (khoảng 31,3 GiB)
* **Dung lượng đĩa `/kaggle/working`:**
  * Tổng dung lượng: **19.52 GB**
  * Đã sử dụng: **0.00 GB**
  * Khả dụng: **19.50 GB**
* **Phiên bản 7 thư viện chính:**
  * `numpy==2.0.2`
  * `pandas==2.3.3`
  * `scikit-learn==1.6.1`
  * `scikit-image==0.25.2`
  * `opencv-python-headless==4.13.0.92`
  * `pillow==11.3.0`
  * `gradio==5.50.0`
  * Cả 7 gói import OK; KẾT QUẢ: ĐẠT.

---

## 4. Kết quả kiểm tra Dataset (`COVID-19 Radiography Database`)

* **Thư mục gốc tìm thấy:** `/kaggle/input/datasets/tawsifurrahman/covid19-radiography-database/COVID-19_Radiography_Dataset`
* **Lưu ý:** Đường dẫn dataset trên Kaggle có dạng `/kaggle/input/datasets/<owner>/<tên-dataset>`; notebook `setup_check` dò động nên không phụ thuộc đường dẫn cố định.
* **Cấu trúc thư mục:** Mỗi lớp bệnh đều chứa 2 thư mục con là `images` và `masks`.
* **Đối chiếu số lượng file:**

| Tên thư mục lớp tìm thấy | Thư mục con | Số ảnh quan sát | Số ảnh đặc tả | Số mask quan sát | Đánh giá đối chiếu |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `COVID` | `images`, `masks` | **3.616** | 3.616 | 3.616 | **Khớp 100%** |
| `Lung_Opacity` | `images`, `masks` | **6.012** | 6.012 | 6.012 | **Khớp 100%** |
| `Normal` | `images`, `masks` | **10.192** | 10.192 | 10.192 | **Khớp 100%** |
| `Viral Pneumonia` | `images`, `masks` | **1.345** | 1.345 | 1.345 | **Khớp 100%** |
| **TỔNG CỘNG** | — | **21.165** | **21.165** | **21.165** | **Khớp 100%** |

---

## 5. Ghi chú về trọng số huấn luyện sẵn

* Không dùng trọng số huấn luyện sẵn (ngoài phạm vi ML cổ điển theo quy định giảng viên và biên bản họp 16/10/2026).
* Thiết lập `"enable_internet": false` giữ nguyên.

---

## 6. Hạn mức tài nguyên

* **Chế độ tính toán:** Thuần CPU (không dùng GPU theo biên bản họp 16/10/2026 mục 3.8).
* **Hạn mức CPU:** theo xác nhận của nhóm trong biên bản họp 16/10/2026 mục 3.8, phiên CPU không giới hạn giờ (chưa kiểm trên trang usage của Kaggle).
* **Trạng thái kết nối mạng:** `Internet off` (`"enable_internet": false`).

---

## 7. Ghi chú kỹ thuật: tệp xác thực Kaggle và phép tách nguồn ảnh Normal

Nhật ký kỹ thuật, không thuộc nội dung báo cáo. Nguồn số liệu tương ứng trong báo cáo ghi ở mục "Ghi chú kỹ thuật" của `report/03_ket_qua_rq1_rq2.md` (mục 3.4).

* **Tệp `kaggle.json`** dùng để tùy chọn tải metadata nằm ở `~/.kaggle/`, đã nằm trong `.gitignore`, không vào repo.
* **Lệnh tải metadata tách nguồn lớp Normal:**

```powershell
.\.venv\Scripts\kaggle.exe datasets download tawsifurrahman/covid19-radiography-database -f COVID-19_Radiography_Dataset/Normal.metadata.xlsx -p outputs/normal_metadata --force
```

* **Sinh `results/eda/normal_source_labels.csv`:**

```powershell
.\.venv\Scripts\python.exe -m src.source_labels --xlsx <tep vừa tải>
```

  Đầu ra 10.192 dòng: 8.851 `rsna` và 1.341 `mooney`, khớp với `docs/dataset_provenance.md` mục 2.1–2.2.

* **Vì sao không thêm `openpyxl`:** tệp xlsx không nằm trong repo (W4: kho chỉ giữ CSV và JSON đã chốt), nên `src/source_labels.py` đọc bằng thư viện chuẩn (`zipfile` + `xml.etree`) thay vì thêm một phụ thuộc mới chỉ để dùng một lần. Bộ kiểm thử `tests/test_source_labels.py` tự dựng một xlsx giả nên parser được kiểm trên CI.

* **Chưa đưa vào báo cáo (việc cần làm, không phải nguồn số liệu):** thời gian huấn luyện của từng bộ phân loại, chỉ số theo từng seed riêng lẻ, và phân tích lỗi theo mức độ tin cậy chi tiết hơn.
