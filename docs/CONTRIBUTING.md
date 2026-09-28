# Hướng dẫn đóng góp & Quy ước làm việc nhóm

Tài liệu này quy định các nguyên tắc và quy chuẩn bắt buộc cho tất cả thành viên trong nhóm 6 người trong suốt 12 tuần thực hiện dự án.

---

## 1. Quy ước đặt tên nhánh (Branching Convention)

- Mỗi thành viên làm việc trên nhánh tính năng riêng được tạo từ nhánh `main`:
  ```text
  feat/<ten_thanh_vien>-<ten_cong_viec>
  ```
- Ví dụ:
  - `feat/duc-setup-data`
  - `feat/nam-densenet121`
  - `feat/linh-gradcam-eval`

---

## 2. Quy trình gộp nhánh qua Pull Request (PR)

- Mọi thay đổi đều phải được gộp vào nhánh chính `main` thông qua **Pull Request**.
- **Cơ chế duyệt chéo (Peer Review trong cặp):** Mỗi PR bắt buộc phải có ít nhất một thành viên trong cặp xem xét, chạy thử nghiệm kiểm tra và phê duyệt (Approve) trước khi tiến hành Merge.
- Sử dụng đúng checklist trong template PR tại `.github/pull_request_template.md`.

---

## 3. Tuyệt đối KHÔNG đưa dữ liệu và checkpoint lên Git

- Dữ liệu thô (`data/`, `input/`), file giải nén, file zip.
- Checkpoint mô hình, file trọng số (`*.pt`, `*.pth`, `*.ckpt`).
- Thông tin nhạy cảm, API keys, token Kaggle (`kaggle.json`, `.env`).
- Tất cả các mẫu trên đã được cấu hình trong `.gitignore`. Thành viên cần luôn kiểm tra `git status` trước khi commit để đảm bảo không vô tình theo dõi các file này.

---

## 4. Quy tắc khoá tập Test (Strict Test Isolation)

- Tập dữ liệu kiểm thử (Test set) sẽ được chia và **KHOÁ NGHIÊM NGẶT từ Tuần 3**.
- **Quy tắc tuyệt đối:** Không được sử dụng tập test trong bất kỳ bước huấn luyện, tinh chỉnh siêu tham số (hyperparameter tuning), hay lựa chọn mô hình nào.
- Tập test chỉ được phép mở ra để đánh giá **DUY NHẤT 1 LẦN tại Tuần 10** trên mô hình tối ưu cuối cùng của nhóm để đảm bảo tính khách quan và khoa học của kết quả.

---

## 5. Quy ước đặt tên Run thực nghiệm (Experiment Run Naming)

Mỗi lần chạy thực nghiệm huấn luyện mô hình cần được đặt tên định danh thống nhất theo cú pháp:

```text
<rq>_<backbone>_<strategy>_<imb>_s<seed>
```

Trong đó:
- `<rq>`: Mã câu hỏi nghiên cứu hoặc mốc thực nghiệm (`baseline`, `rq1`, `rq2`, `rq3`).
- `<backbone>`: Tên kiến trúc backbone (`densenet121`, `efficientnet_b0`, ...).
- `<strategy>`: Chiến lược huấn luyện (`scratch`, `frozen`, `finetune`).
- `<imb>`: Kỹ thuật xử lý mất cân bằng lớp (`none`, `weighted_ce`, `focal`, `oversampling`).
- `s<seed>`: Seed ngẫu nhiên sử dụng (`s42`, `s43`, `s44`).

**Ví dụ:**
- `baseline_densenet121_frozen_none_s42`
- `rq1_efficientnet_b0_finetune_none_s43`
- `rq2_densenet121_finetune_focal_s42`
