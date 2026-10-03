# COVID-19 Radiography Classifier

Dự án bài tập lớn môn Học máy (Machine Learning) thực hiện phân loại 4 nhóm ảnh X-quang ngực:
- **Normal** (Bình thường)
- **COVID-19**
- **Lung Opacity** (Mờ phổi / Tổn thương phổi không do COVID)
- **Viral Pneumonia** (Viêm phổi do virus)

Dữ liệu sử dụng: [COVID-19 Radiography Database](https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database).

> [!CAUTION]
> **CẢNH BÁO:** Chỉ phục vụ mục đích học thuật, không dùng để chẩn đoán hay hỗ trợ quyết định y khoa.

---

## 1. Cấu trúc thư mục dự án

```text
├── .github/
│   └── pull_request_template.md  # Mẫu checklist khi tạo Pull Request
├── configs/
│   └── base.yaml                 # Cấu hình mặc định (kích thước ảnh, seeds, tỉ lệ split)
├── demo/                         # Ứng dụng demo suy luận (Gradio)
├── docs/
│   ├── CONTRIBUTING.md           # Quy định làm việc nhóm, quy ước nhánh và commit
│   ├── OWNERS.md                 # Phân công trách nhiệm module cho 6 thành viên
│   └── roadmap.md                # Kế hoạch chi tiết 12 tuần thực hiện dự án
├── kaggle/                       # Scripts và cấu hình phục vụ chạy trên Kaggle
├── notebooks/                    # 12 notebooks nghiên cứu và thực nghiệm
├── report/                       # Báo cáo bài tập lớn
├── results/                      # Lưu trữ bảng số liệu, biểu đồ kết quả
├── slides/                       # Slide thuyết trình bảo vệ đề tài
├── splits/                       # Lưu file manifest phân chia tập train/val/test
├── src/                          # Mã nguồn Python tái sử dụng
│   ├── dataset.py                # Xử lý dữ liệu và Data Augmentation
│   ├── gradcam.py                # Trực quan hóa Grad-CAM và vùng chú ý phổi
│   ├── metrics.py                # Đánh giá độ đo (F1, Accuracy, Confusion Matrix)
│   ├── models.py                 # Khởi tạo kiến trúc mô hình (DenseNet, EfficientNet, ...)
│   ├── train.py                  # Pipeline huấn luyện mô hình có hỗ trợ resume
│   └── utils.py                  # Các hàm tiện ích dùng chung (set_seed, ...)
├── .gitignore                    # Chặn dữ liệu, checkpoint, file nhạy cảm
├── README.md                     # Tài liệu tổng quan dự án
└── requirements.txt              # Danh sách thư viện phụ thuộc
```

## 2. Theo dõi tiến độ đồ án

Toàn bộ tiến độ thực hiện đồ án 12 tuần được theo dõi chi tiết theo mô hình Scrum rút gọn (6 sprint, trạng thái và bằng chứng kiểm chứng) tại tài liệu [docs/roadmap.md](docs/roadmap.md). Mọi thành viên có thể mở tài liệu này để nắm bắt sprint hiện tại, các việc đã hoàn thành và các vướng mắc đang mở.

---

## 3. Thứ tự thực thi Notebooks

Nhóm thực hiện tuần tự theo quy trình nghiên cứu từ bước 00 đến bước 11:

| STT | Notebook | Mục tiêu chính |
| :---: | :--- | :--- |
| 00 | `00_setup_check.ipynb` | Kiểm tra môi trường GPU, CUDA, thư viện và ghim phiên bản |
| 01 | `01_download_and_eda.ipynb` | Khám phá dữ liệu, phân tích nhãn, kiểm tra mask phổi |
| 02 | `02_duplicates_and_split.ipynb` | Lọc ảnh trùng bằng imagehash, chia tập train/val/test và khoá test |
| 03 | `03_smoke_test_train.ipynb` | Chạy thử nghiệm nhanh luồng huấn luyện nhỏ và kiểm tra tính năng resume |
| 04 | `04_baseline.ipynb` | Huấn luyện mô hình cơ sở, đo thời gian chạy và thiết lập ngưỡng chuẩn |
| 05 | `05_rq1_backbones.ipynb` | Câu hỏi nghiên cứu 1: So sánh các backbone (DenseNet121, EfficientNet-B0) |
| 06 | `06_rq2_imbalance.ipynb` | Câu hỏi nghiên cứu 2: Thử nghiệm các kỹ thuật xử lý mất cân bằng lớp |
| 07 | `07_gradcam_lung_attention.ipynb`| Trực quan hóa Grad-CAM đối chiếu với mask phổi xem mô hình nhìn vào đâu |
| 08 | `08_rq3_masked_eval.ipynb` | Câu hỏi nghiên cứu 3: Đánh giá trên ảnh gốc vs chỉ phổi vs ngoài phổi |
| 09 | `09_error_analysis.ipynb` | Phân tích chi tiết các ca dự đoán sai và nguyên nhân gây nhầm lẫn |
| 10 | `10_final_test_eval.ipynb` | Mở khoá tập test và đánh giá DUY NHẤT 1 LẦN trên mô hình tối ưu |
| 11 | `11_inference_demo.ipynb` | Xây dựng giao diện demo suy luận (Gradio) nhận ảnh X-quang và hiển thị kết quả |

---

## 4. Hướng dẫn chạy trên Kaggle

Dự án được cấu hình và chạy chính trên môi trường Kaggle Linux (GPU Tesla T4 x 2, quota 30 giờ/tuần):

### 4.1. Cấu hình kernel (`kernel-metadata.json`)
Mỗi tác vụ chạy trên Kaggle sử dụng một thư mục riêng kèm metadata chuẩn:
```json
{
  "id": "<username>/<kernel_name>",
  "title": "<kernel_name>",
  "code_file": "<notebook_name>.ipynb",
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

### 4.2. Đường dẫn và dữ liệu trên Kaggle
* **Dữ liệu đầu vào:** `/kaggle/input/datasets/tawsifurrahman/covid19-radiography-database/COVID-19_Radiography_Dataset` (gồm 21.165 ảnh và 21.165 masks trên 4 lớp: COVID, Lung_Opacity, Normal, Viral Pneumonia).
* **Thư mục làm việc & xuất kết quả:** `/kaggle/working` (khoảng 19.5 GB khả dụng để lưu logs và checkpoints).

### 4.3. Các lệnh Kaggle CLI cơ bản
```powershell
# 1. Đẩy notebook chạy trên Kaggle GPU T4
kaggle kernels push -p <thư_mục_kernel> --accelerator NvidiaTeslaT4

# 2. Theo dõi trạng thái thực thi của kernel
kaggle kernels status <username>/<kernel_name>

# 3. Kéo kết quả (outputs, log, checkpoint) về máy cục bộ
kaggle kernels output <username>/<kernel_name> -p <thư_mục_output> --force
```
