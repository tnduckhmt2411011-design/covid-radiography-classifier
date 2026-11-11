# Demo suy luận S6-02 (Streamlit)

Ứng dụng web tối giản để chạy thử mô hình SVM đã đóng băng trên một ảnh X-quang ngực do người
dùng tải lên. Ứng dụng chỉ dùng học máy truyền thống, không huấn luyện lại và không đọc ảnh của
split `test`.

## Mô hình đóng băng

| Thành phần | Giá trị |
|---|---|
| Đặc trưng | 152 chiều: Histogram 64 + GLCM 60 + LBP 28 |
| Ảnh đầu vào | Xám, 299×299, ảnh gốc (không mask) |
| Bộ phân loại | `SVC(kernel="rbf", C=10.0, gamma="scale", class_weight="balanced", probability=True, random_state=42)` |
| Tiền xử lý | `StandardScaler` fit chỉ trên split `train` (14 815 ảnh) |
| Lớp | COVID, Lung_Opacity, Normal, Viral Pneumonia |
| Artifact | `cxr_inference_model_cache.joblib` (kernel v3) |
| SHA-256 | `3e14bd570c734d9d8f39a2d340b176a40a41c9559cc2da0ef67bbd8e15735058` |

Artifact không nằm trong git (`.gitignore` chặn `*.joblib`). Ứng dụng tải artifact từ một kho
Hugging Face công khai và kiểm SHA-256 trước khi gọi `joblib.load`; sau đó kiểm thêm băm split,
phiên bản scikit-learn, số mẫu train, siêu tham số SVM và băm mã trích đặc trưng.

## Chạy cục bộ

Yêu cầu Python 3.12 (cùng phiên bản với Streamlit Community Cloud mặc định và môi trường đã chạy
kiểm thử). Cài đúng phiên bản:

```bash
python -m venv .venv-demo
.venv-demo\Scripts\activate        # Windows
pip install -r demo/requirements.txt
```

Chạy với artifact cục bộ (không cần mạng):

```bash
set CXR_MODEL_PATH=outputs\k_v3_out\cxr_inference_model_cache.joblib
streamlit run demo/streamlit_app.py
```

Hoặc chạy với kho Hugging Face:

```bash
set CXR_MODEL_REPO=<tai-khoan>/<ten-kho>
set CXR_MODEL_FILE=cxr_inference_model_cache.joblib
set CXR_MODEL_REVISION=main
set CXR_MODEL_SHA256=3e14bd570c734d9d8f39a2d340b176a40a41c9559cc2da0ef67bbd8e15735058
streamlit run demo/streamlit_app.py
```

## Cấu hình

| Biến môi trường / khóa secrets | Bắt buộc | Ý nghĩa |
|---|---|---|
| `CXR_MODEL_PATH` | Không | Đường dẫn artifact cục bộ; nếu đặt thì bỏ qua tải mạng |
| `CXR_MODEL_REPO` | Có, nếu không có `CXR_MODEL_PATH` | Kho Hugging Face dạng `tai-khoan/ten-kho` |
| `CXR_MODEL_FILE` | Không | Tên tệp trong kho, mặc định `cxr_inference_model_cache.joblib` |
| `CXR_MODEL_REVISION` | Không | Nhánh/tag/commit của kho, mặc định nhánh mặc định |
| `CXR_MODEL_SHA256` | Không | Băm kỳ vọng, mặc định băm đã công bố ở trên |
| `HF_TOKEN` | Không | Chỉ cần nếu kho mô hình là private |

Với Streamlit Community Cloud, khai báo trong **App settings → Secrets** (tệp
`.streamlit/secrets.toml` đã được `.gitignore` chặn):

```toml
CXR_MODEL_REPO = "tai-khoan/ten-kho"
CXR_MODEL_FILE = "cxr_inference_model_cache.joblib"
CXR_MODEL_REVISION = "main"
CXR_MODEL_SHA256 = "3e14bd570c734d9d8f39a2d340b176a40a41c9559cc2da0ef67bbd8e15735058"
# HF_TOKEN = "..."   # chỉ khi kho private
```

## Đưa artifact lên Hugging Face

1. Tạo model repo công khai, ví dụ `tai-khoan/cxr-svm-demo`.
2. Tạo token có quyền ghi (**Settings → Access Tokens**) rồi đăng nhập:
   `hf auth login`.
3. Tải tệp lên: `hf upload tai-khoan/cxr-svm-demo outputs/k_v3_out/cxr_inference_model_cache.joblib`.
4. Đặt `CXR_MODEL_REPO` trỏ tới repo đó. Không commit token vào repo.

## Triển khai trên Streamlit Community Cloud

1. Đẩy nhánh chứa thay đổi lên GitHub và mở pull request (chưa merge cũng được).
2. Đăng nhập <https://share.streamlit.io> bằng tài khoản GitHub có quyền với repo.
3. **Create app** → chọn repo, branch, entrypoint `demo/streamlit_app.py`.
4. Chọn Python **3.12**; Streamlit Cloud tự dùng `demo/requirements.txt` đặt cạnh entrypoint.
5. Dán secrets như trên rồi **Deploy**.
6. Kiểm tra log khởi động không có lỗi tải/kiểm băm; thử một ảnh val để xác nhận app trả nhãn.

Repo hiện là private: tài khoản triển khai cần quyền admin với repo và cấp OAuth scope `repo`.
Người triển khai phải là chủ tài khoản Streamlit; PR này không tự triển khai.

## Cổng tương đương

Chạy 200 ảnh val (seed 42), đối chiếu nhãn với `results/rq3_ghep_svm_orig_to_orig_s42/preds_val.csv`:

```bash
python demo/verify_model_equivalence.py --dataset-root D:\cxr_data\COVID-19_Radiography_Dataset
```

Kỳ vọng: `file_hash MD5 khớp: 200/200` và `NHÃN KHỚP: 200/200`, mã thoát 0. Cổng chỉ đọc split
`val`, không đọc ảnh `test`.

## Kiểm thử

```bash
pytest -q tests/test_model_artifact.py tests/test_streamlit_app.py
```

Test dùng ảnh giả lập trong bộ nhớ, không đọc ảnh thật, không gọi mạng. Bộ test kiểm tra: giải mã
và đổi cỡ ảnh, từ chối tệp rỗng/quá lớn/sai định dạng/không phải ảnh, cổng H2 theo tên tệp, không
ghi ảnh tải lên xuống đĩa, không import framework học sâu, không đọc split `test`, số đo đọc từ
JSON, và sự hiện diện của cảnh báo y tế.

## Giới hạn và an toàn

- **Không dùng để chẩn đoán.** Đây là demo học thuật, không phải thiết bị y tế và chưa kiểm định
  lâm sàng.
- Chỉ tải ảnh X-quang đã ẩn danh. Không tải ảnh bệnh nhân thật hoặc ảnh có thông tin định danh.
- Ảnh được xử lý trong bộ nhớ của phiên; ứng dụng không ghi ảnh tải lên xuống đĩa và không ghi nội
  dung ảnh vào log.
- Ảnh khác 299×299 được đổi cỡ kèm cảnh báo; mô hình chỉ được kiểm chứng trên ảnh 299×299 của bộ
  dữ liệu COVID-19 Radiography.
- Chênh lệch số đo val–test chỉ là quan sát. Mọi giải thích là giả thuyết chưa được kiểm chứng,
  không nêu nguyên nhân (D4); xem `results/rq3_shortcut_learning_conclusion.md`.
- Demo không kèm ảnh mẫu từ bộ dữ liệu.
