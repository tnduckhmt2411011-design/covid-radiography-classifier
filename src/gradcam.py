"""Module gradcam.py

Trách nhiệm:
- Trích xuất bản đồ nhiệt kích hoạt Grad-CAM (Gradient-weighted Class Activation Mapping) từ tầng tích chập cuối.
- Chồng lớp bản đồ nhiệt (heatmap overlay) lên ảnh X-quang gốc để trực quan hóa giải thích mô hình (Explainable AI).
- Hỗ trợ đối chiếu vùng tập trung của mô hình với mặt nạ phổi (lung mask) để đánh giá sự tập trung vào vùng phổi (lung attention).
"""

# TODO: Xây dựng hàm generate_gradcam(model, input_tensor, target_layer, target_class=None)
# TODO: Xây dựng hàm overlay_heatmap(img_path, cam_mask, alpha=0.5)
# TODO: Xây dựng hàm compute_lung_attention_ratio(cam_mask, lung_mask)
