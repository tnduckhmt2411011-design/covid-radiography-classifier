"""Module dataset.py

Trách nhiệm:
- Quản lý nạp dữ liệu từ thư mục ảnh hoặc file manifest (CSV).
- Định nghĩa lớp PyTorch Dataset cho bài toán phân loại 4 nhóm ảnh X-quang ngực (COVID-19 Radiography Database).
- Cài đặt các phép biến đổi tiền xử lý ảnh (Resize, Normalization) và các kỹ thuật tăng cường dữ liệu (Data Augmentation).
- Tạo DataLoader cho các tập train, val và test.
"""

# TODO: Định nghĩa lớp Custom Dataset kế thừa torch.utils.data.Dataset
# TODO: Xây dựng hàm get_transforms(img_size, is_train=True)
# TODO: Cài đặt hàm build_dataloaders(data_dir_or_csv, batch_size, num_workers)
