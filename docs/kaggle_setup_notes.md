# Ghi chép thiết lập môi trường Kaggle (Kaggle Setup Notes)

Tài liệu này ghi nhận kết quả chạy thử nghiệm và kiểm tra môi trường Kaggle qua Kaggle CLI (đã xác thực Phone Verification và kích hoạt GPU).

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

# 4. Đẩy notebook chạy thử nghiệm lên Kaggle GPU T4
.\.venv\Scripts\kaggle.exe kernels push -p kaggle/setup_check --accelerator NvidiaTeslaT4

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
  "enable_gpu": true,
  "enable_internet": false,
  "dataset_sources": [
    "tawsifurrahman/covid19-radiography-database"
  ]
}
```

---

## 3. Phần cứng & Môi trường quan sát được (Phiên GPU chính thức)

* **Python:** `3.12.13 (GCC 11.4.0)`
* **PyTorch:** `2.10.0+cu128` (CUDA 12.8 support)
* **Torchvision:** `0.25.0+cu128`
* **GPU quan sát được:**
  * `cuda_available`: **`True`** ✅
  * `gpu_count`: **`2`** (Hệ thống cấp phát cấu hình GPU kép: **GPU T4 × 2**)
  * `gpu_names`: `["Tesla T4", "Tesla T4"]`
  * Bộ nhớ mỗi GPU: **15.360 MiB (~15 GB VRAM/GPU)**, tổng cộng 30 GB VRAM.
  * Driver Version: `580.159.04`, CUDA Version: `13.0`
* **Dung lượng đĩa `/kaggle/working`:**
  * Tổng dung lượng: **19.52 GB**
  * Đã sử dụng: `0.00 GB`
  * Khả dụng: **19.50 GB**
* **Thời gian chạy thực tế:** **~2 phút 30 giây** trên GPU (nhanh gấp hơn 4 lần so với CPU 10m25s).

---

## 4. Kết quả kiểm tra Dataset (`COVID-19 Radiography Database`)

* **Thư mục gốc tìm thấy:** `/kaggle/input/datasets/tawsifurrahman/covid19-radiography-database/COVID-19_Radiography_Dataset`
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

## 5. Kết quả kiểm tra tải trọng số Pretrained (ImageNet)

* **Trạng thái:** **`FAILED`**
* **Thông báo lỗi quan sát được:**
  ```text
  TẢI TRỌNG SỐ THẤT BẠI (có thể do internet tắt)
  Chi tiết lỗi: <urlopen error [Errno -3] Temporary failure in name resolution>
  ```
* **Phân tích:** Thiết lập `"enable_internet": false` hoạt động đúng như mong đợi, ngăn chặn tải ra ngoài mạng internet.
* **Phương án giải quyết của nhóm:**
  1. *Lựa chọn 1 (Bật Internet):* Đổi `"enable_internet": true` khi cần tải tự động trọng số torchvision.
  2. *Lựa chọn 2 (Gắn Dataset trọng số offline - Khuyên dùng):* Thêm Kaggle Dataset chứa sẵn các file `.pth` của backbone (DenseNet121, EfficientNet-B0) vào `dataset_sources` của notebook để nạp trực tiếp offline.

---

## 6. Hạn mức tài nguyên xác nhận từ giao diện người dùng

* **Hạn mức GPU hàng tuần:** **30 giờ / tuần** (hiện tại còn nguyên `30.0 / 30.0 hrs`).
* **Loại Accelerator mặc định:** `GPU T4 x2`.
* **Trạng thái kết nối mạng:** `Internet off`.
