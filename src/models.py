"""Module models.py

Trách nhiệm:
- Định nghĩa và khởi tạo kiến trúc các mô hình học sâu cho bài toán phân loại ảnh X-quang 4 lớp.
- Hỗ trợ tải các kiến trúc pretrained backbone (DenseNet121, EfficientNet-B0, ...).
- Thay thế classifier head phù hợp với 4 lớp đầu ra (Normal, COVID-19, Lung Opacity, Viral Pneumonia).
- Cung cấp cơ chế đóng băng (freeze) hoặc mở khóa (unfreeze) các tầng mạng phục vụ transfer learning / fine-tuning.
"""

# TODO: Xây dựng hàm get_model(model_name, num_classes=4, pretrained=True)
# TODO: Hỗ trợ các backbone DenseNet121 và EfficientNet-B0
# TODO: Cài đặt logic thay đổi classifier head và tùy chọn freeze feature extractor
