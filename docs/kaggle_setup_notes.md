# Ghi chép thiết lập môi trường Kaggle (Kaggle Setup Notes)

Tài liệu này ghi nhận kết quả chạy thử nghiệm và kiểm tra môi trường Kaggle headless qua Kaggle CLI vào ngày 28/09/2026.

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

# 4. Đẩy notebook chạy thử nghiệm lên Kaggle GPU
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

## 3. Phần cứng & Môi trường quan sát được

* **Python:** `3.12.13 (GCC 11.4.0)`
* **PyTorch:** `2.10.0+cpu`
* **Torchvision:** `0.25.0+cpu`
* **GPU quan sát được:**
  * `cuda_available`: **`False`**
  * `gpu_count`: **`0`**
  * `gpu_names`: `[]`
  * `nvidia_smi`: `Error [Errno 2] No such file or directory: 'nvidia-smi'`
  * *Lưu ý quan trọng:* Dù lệnh push có tham số `--accelerator NvidiaTeslaT4` và metadata có `"enable_gpu": true`, phiên chạy thực tế được Kaggle cấp phát môi trường **CPU**.
  * *Nguyên nhân:* Tài khoản Kaggle cần hoàn tất **xác thực số điện thoại (Phone Verification)** tại `kaggle.com/settings` để được cấp quyền sử dụng GPU (thường là 30 giờ/tuần).
* **Dung lượng đĩa `/kaggle/working`:**
  * Tổng dung lượng: **19.52 GB**
  * Đã sử dụng: `0.00 GB`
  * Khả dụng: **19.50 GB**
* **Thời gian chạy thực tế:** **10 phút 25 giây (~625 giây)** (bao gồm thời gian container duyệt và đếm toàn bộ 42.330 file ảnh và mask trên ổ đĩa gắn ngoài bằng CPU).

---

## 4. Kết quả kiểm tra Dataset (`COVID-19 Radiography Database`)

* **Thư mục gốc tìm thấy:** `/kaggle/input/datasets/tawsifurrahman/covid19-radiography-database/COVID-19_Radiography_Dataset`
* **Cấu trúc thư mục:** Mỗi lớp bệnh đều chứa 2 thư mục con là `images` và `masks`.
* **Đối chiếu số lượng file:**

| Tên thư mục lớp tìm thấy | Số ảnh quan sát | Số ảnh đặc tả | Số mask quan sát | Đánh giá đối chiếu |
| :--- | :---: | :---: | :---: | :---: |
| `COVID` | 3.616 | 3.616 | 3.616 | **Khớp 100%** |
| `Lung_Opacity` | 6.012 | 6.012 | 6.012 | **Khớp 100%** |
| `Normal` | 10.192 | 10.192 | 10.192 | **Khớp 100%** |
| `Viral Pneumonia` | 1.345 | 1.345 | 1.345 | **Khớp 100%** |
| **TỔNG CỘNG** | **21.165** | **21.165** | **21.165** | **Khớp 100%** |

---

## 5. Kết quả kiểm tra tải trọng số Pretrained (ImageNet)

* **Trạng thái:** **`FAILED`**
* **Thông báo lỗi quan sát được:**
  ```text
  TẢI TRỌNG SỐ THẤT BẠI (có thể do internet tắt)
  Chi tiết lỗi: <urlopen error [Errno -3] Temporary failure in name resolution>
  ```
* **Phân tích:** Do thiết lập `"enable_internet": false`, container không thể phân giải tên miền `download.pytorch.org` để tải trọng số `resnet18-f37072fd.pth`.
* **Các phương án giải quyết để nhóm lựa chọn:**
  1. *Lựa chọn 1 (Bật Internet):* Đổi `"enable_internet": true` trong `kernel-metadata.json` khi chạy trên Kaggle để PyTorch tự tải trọng số qua mạng.
  2. *Lựa chọn 2 (Offline Dataset/Model - Khuyên dùng trong thi đấu/học thuật):* Tải trước file trọng số `.pth` hoặc gắn các bộ weights của Torchvision/Timm có sẵn trên Kaggle dưới dạng Dataset (`dataset_sources`), sau đó nạp offline.

---

## 6. Các điểm chưa xác minh

* **Hạn mức GPU hàng tuần (Weekly Quota):** **KHÔNG XÁC MINH ĐƯỢC** (do phiên chạy vừa rồi nhận môi trường CPU, cần kiểm tra trực tiếp trên giao diện Kaggle Account).
* **Thời lượng tối đa của một phiên (Session timeout):** **KHÔNG XÁC MINH ĐƯỢC** (thực tế chỉ đo được phiên này chạy trong 10m25s).
