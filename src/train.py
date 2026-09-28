"""Module train.py

Trách nhiệm:
- Điều khiển vòng lặp huấn luyện (train loop) và kiểm định (validation loop) cho mô hình.
- Quản lý hàm mất mát (Loss function), bộ tối ưu hóa (Optimizer), và bộ điều chỉnh tốc độ học (LR Scheduler).
- Hỗ trợ lưu checkpoint (best checkpoint, latest checkpoint) và khôi phục trạng thái huấn luyện (resume training).
- Ghi log quá trình huấn luyện phục vụ theo dõi và phân tích (loss, accuracy, F1-score theo từng epoch).
"""

# TODO: Xây dựng hàm train_one_epoch(model, dataloader, criterion, optimizer, device)
# TODO: Xây dựng hàm validate(model, dataloader, criterion, device)
# TODO: Cài đặt logic lưu checkpoint và resume training từ file .pt
# TODO: Xây dựng hàm main_train(config) điều phối toàn bộ pipeline huấn luyện
