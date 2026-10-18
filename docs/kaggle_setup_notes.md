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
* **Thời gian chạy thực tế:** **~2 phút 42 giây** trên CPU.
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

## 5. Kết quả kiểm tra tải trọng số

* Không dùng trọng số huấn luyện sẵn (ngoài phạm vi ML cổ điển theo quy định giảng viên và biên bản họp 16/10/2026).
* Thiết lập `"enable_internet": false` giữ nguyên để đảm bảo môi trường thực thi hoàn toàn ngoại tuyến (offline).

---

## 6. Hạn mức tài nguyên xác nhận từ giao diện người dùng

* **Chế độ tính toán:** Thuần CPU (không dùng GPU theo biên bản họp 16/10/2026 mục 3.8).
* **Hạn mức CPU:** Phiên CPU trên Kaggle không giới hạn quota hàng tuần (theo biên bản họp 16/10/2026 mục 3.8: không dùng GPU, phiên CPU không giới hạn giờ).
* **Trạng thái kết nối mạng:** `Internet off` (`"enable_internet": false`).
