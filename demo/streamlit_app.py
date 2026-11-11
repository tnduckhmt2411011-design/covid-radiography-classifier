"""Ứng dụng Streamlit demo suy luận ảnh X-quang với mô hình SVM đóng băng (S6-02).

Ứng dụng chỉ đọc ảnh do người dùng tải lên trong bộ nhớ, chuyển sang ảnh xám 299x299, trích 152
đặc trưng thủ công và gọi mô hình đã đóng băng. Không đọc ảnh của split 'test', không ghi ảnh tải
lên xuống đĩa, không dùng framework học sâu.

Quy ước:
- Cổng H2: tên tệp trùng một image_id thuộc split 'test' bị từ chối trước khi giải mã.
- Cổng H7: chỉ học máy truyền thống (scikit-learn, scikit-image, OpenCV).
- D4: chênh lệch val-test chỉ là quan sát; mọi giải thích là giả thuyết chưa được kiểm chứng,
  không nêu nguyên nhân.
"""

from __future__ import annotations

import base64
import os
import sys
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import cv2  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import streamlit as st  # noqa: E402

from src.inference_demo import (  # noqa: E402
    IMAGE_SIZE,
    ensure_not_heldout_image,
    extract_152_features,
    load_benchmark_metrics,
    plot_probabilities,
    predict_image,
)
from src.model_artifact import (  # noqa: E402
    DEFAULT_MODEL_FILE,
    DEFAULT_MODEL_SHA256,
    ENV_HF_TOKEN,
    ENV_MODEL_FILE,
    ENV_MODEL_PATH,
    ENV_MODEL_REPO,
    ENV_MODEL_REVISION,
    ENV_MODEL_SHA256,
    ModelArtifactError,
    download_and_verify_model,
    load_model_artifact,
)

SPLIT_CSV = REPO_ROOT / "splits" / "split_v1.csv"

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_UPLOAD_MB = MAX_UPLOAD_BYTES // (1024 * 1024)
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

DISCLAIMER = (
    "**KHÔNG DÙNG ĐỂ CHẨN ĐOÁN.** Đây là demo học thuật của mô hình học máy truyền thống, "
    "không phải thiết bị y tế và chưa được kiểm định lâm sàng. Không dùng kết quả để đưa ra "
    "quyết định điều trị hay bất kỳ quyết định y tế nào."
)


def read_setting(name: str, default: Optional[str] = None) -> Optional[str]:
    """Đọc cấu hình từ Streamlit secrets trước, sau đó tới biến môi trường."""
    try:
        if name in st.secrets:
            value = st.secrets[name]
            if value not in (None, ""):
                return str(value)
    except Exception:
        pass  # không có tệp secrets cục bộ là trạng thái hợp lệ
    value = os.environ.get(name, "")
    return value if value else default


def resolve_model_file() -> Path:
    """Trả về đường dẫn artifact: ưu tiên CXR_MODEL_PATH, nếu không thì tải từ Hugging Face.

    Raises:
        ModelArtifactError: Khi thiếu cấu hình kho mô hình hoặc tải/kiểm băm thất bại.
    """
    override = read_setting(ENV_MODEL_PATH)
    if override:
        return Path(str(override)).expanduser()

    repo_id = read_setting(ENV_MODEL_REPO)
    if not repo_id:
        raise ModelArtifactError(
            f"Chưa cấu hình kho mô hình. Đặt biến môi trường {ENV_MODEL_REPO} "
            "(dạng 'tai-khoan/ten-kho') hoặc khóa tương ứng trong Streamlit secrets, "
            f"hoặc trỏ {ENV_MODEL_PATH} tới artifact cục bộ."
        )
    return download_and_verify_model(
        str(repo_id),
        expected_sha256=str(read_setting(ENV_MODEL_SHA256, DEFAULT_MODEL_SHA256)),
        filename=str(read_setting(ENV_MODEL_FILE, DEFAULT_MODEL_FILE)),
        revision=read_setting(ENV_MODEL_REVISION),
        token=read_setting(ENV_HF_TOKEN),
    )


@st.cache_resource(show_spinner=False)
def load_model_cached(artifact_path: str, expected_sha256: str) -> Tuple[Any, Any, Dict[str, Any]]:
    """Nạp artifact một lần cho mỗi cặp (đường dẫn, băm) và giữ trong bộ nhớ tiến trình."""
    return load_model_artifact(artifact_path, expected_sha256=expected_sha256)


def decode_upload(
    filename: str,
    data: bytes,
    *,
    split_csv: Optional[Path] = None,
) -> Tuple[np.ndarray, bool, Optional[str]]:
    """Kiểm và giải mã ảnh tải lên thành mảng xám uint8 299x299.

    Args:
        filename: Tên tệp do người dùng tải lên (dùng cho cổng H2 theo tên).
        data: Nội dung tệp trong bộ nhớ.
        split_csv: Manifest split; mặc định ``splits/split_v1.csv`` của repo.

    Returns:
        ``(image, resized, warning)``; ``warning`` khác None khi ảnh bị đổi cỡ.

    Raises:
        PermissionError: Nếu tên tệp thuộc split 'test' (cổng H2).
        ValueError: Nếu tệp rỗng, quá lớn, sai định dạng hoặc không giải mã được.
    """
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Chỉ nhận tệp PNG/JPG/JPEG; tệp '{filename}' có đuôi '{suffix}' không hợp lệ."
        )
    if not data:
        raise ValueError("Tệp tải lên rỗng.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError(
            f"Tệp tải lên có kích thước {len(data) / (1024 * 1024):.1f} MB, "
            f"vượt giới hạn {MAX_UPLOAD_MB} MB."
        )

    ensure_not_heldout_image(filename, split_csv or SPLIT_CSV)

    raw = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(raw, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(
            f"Không thể giải mã tệp '{filename}' thành ảnh. Hãy chọn tệp PNG/JPG hợp lệ."
        )

    resized = img.shape != IMAGE_SIZE
    warning: Optional[str] = None
    if resized:
        original_height, original_width = img.shape[:2]
        img = cv2.resize(img, (IMAGE_SIZE[1], IMAGE_SIZE[0]), interpolation=cv2.INTER_AREA)
        warning = (
            f"Ảnh gốc {original_width}×{original_height} đã được đổi cỡ về 299×299 (INTER_AREA). "
            "Mô hình chỉ được kiểm chứng trên ảnh 299×299 của bộ dữ liệu COVID-19 Radiography; "
            "kết quả trên ảnh khác nguồn hoặc khác cách xử lý không có giá trị đánh giá."
        )
    return img, resized, warning


def to_data_url(image: np.ndarray) -> str:
    """Mã hóa ảnh xám thành data URL PNG trong bộ nhớ (không ghi tệp tạm)."""
    ok, buffer = cv2.imencode(".png", image)
    if not ok:
        raise ValueError("Không mã hóa được ảnh thành PNG.")
    return "data:image/png;base64," + base64.b64encode(buffer.tobytes()).decode("ascii")


def build_limitations_text(metrics: Mapping[str, Any]) -> str:
    """Tạo đoạn giới hạn/đạo đức hiển thị trong app, số đo lấy từ JSON đã công bố."""
    val_f1 = float(metrics["val_macro_f1"])
    test_f1 = float(metrics["test_macro_f1"])
    diff = float(metrics["diff"])
    return (
        "**Số đo tham chiếu đã công bố** (đọc trực tiếp từ tệp kết quả, không đọc lại ảnh test):\n\n"
        f"- Macro-F1 trên val: **{val_f1:.4f}**\n"
        f"- Macro-F1 trên test: **{test_f1:.4f}**\n"
        f"- Chênh lệch test − val: **{diff:+.4f}**\n\n"
        "**D4.** Chênh lệch val–test chỉ là quan sát thực nghiệm. Mọi giải thích về chênh lệch "
        "là giả thuyết chưa được kiểm chứng, không nêu nguyên nhân; xem "
        "`results/rq3_shortcut_learning_conclusion.md`.\n\n"
        "Mô hình dùng 152 đặc trưng thủ công (Histogram 64 + GLCM 60 + LBP 28) trên ảnh gốc xám "
        "299×299. Ảnh đầu vào khác phân bố huấn luyện có thể cho kết quả sai lệch."
    )


def render_metrics(metrics: Mapping[str, Any]) -> None:
    """Hiển thị số đo công bố và đoạn giới hạn D4 trong sidebar."""
    st.markdown(build_limitations_text(metrics))


def main() -> None:
    st.set_page_config(
        page_title="CXR SVM demo — S6-02",
        page_icon="🫁",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Demo suy luận ảnh X-quang ngực")
    st.caption(
        "SVM RBF đóng băng trên 152 đặc trưng thủ công (Histogram + GLCM + LBP), "
        "ảnh gốc xám 299×299, 4 lớp: COVID, Lung_Opacity, Normal, Viral Pneumonia."
    )
    st.error(DISCLAIMER)

    metrics: Optional[Dict[str, Any]] = None
    metrics_error: Optional[str] = None
    try:
        metrics = load_benchmark_metrics(REPO_ROOT)
    except Exception as exc:
        metrics_error = f"Không đọc được số đo tham chiếu: {exc}"

    with st.sidebar:
        st.header("Mô hình & số đo")
        st.markdown(
            "- Artifact: `cxr_inference_model_cache.joblib`\n"
            f"- SHA-256: `{str(read_setting(ENV_MODEL_SHA256, DEFAULT_MODEL_SHA256))[:16]}…`\n"
            "- Fit chỉ trên split `train` (14 815 ảnh)\n"
            "- Không huấn luyện lại, không đọc ảnh test"
        )
        if metrics is not None:
            render_metrics(metrics)
        elif metrics_error:
            st.warning(metrics_error)
        st.divider()
        st.warning(
            "Chỉ tải ảnh X-quang đã ẩn danh. Không tải ảnh bệnh nhân thật hoặc ảnh có thông tin "
            "định danh. Ảnh được xử lý trong bộ nhớ của phiên và không được lưu thành tệp."
        )

    try:
        with st.spinner("Đang nạp mô hình đóng băng…"):
            artifact_path = resolve_model_file()
            scaler, clf, meta = load_model_cached(
                str(artifact_path),
                str(read_setting(ENV_MODEL_SHA256, DEFAULT_MODEL_SHA256)),
            )
    except ModelArtifactError as exc:
        st.error(f"Không nạp được mô hình: {exc}")
        st.info(
            "Cấu hình cần thiết: `CXR_MODEL_REPO` (kho Hugging Face công khai) hoặc "
            "`CXR_MODEL_PATH` (artifact cục bộ), tùy chọn `CXR_MODEL_FILE`, "
            "`CXR_MODEL_REVISION`, `CXR_MODEL_SHA256`, `HF_TOKEN`."
        )
        st.stop()
    except Exception as exc:
        st.error(f"Lỗi không mong đợi khi nạp mô hình: {exc}")
        st.stop()

    uploaded = st.file_uploader(
        f"Tải ảnh X-quang ngực (PNG/JPG, tối đa {MAX_UPLOAD_MB} MB)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False,
        help="Ảnh được chuyển sang ảnh xám và đổi cỡ 299×299 nếu cần; không ghi xuống đĩa.",
    )

    if uploaded is None:
        st.info(
            "Chọn một ảnh X-quang để suy luận. Demo không kèm ảnh mẫu từ bộ dữ liệu; "
            "hãy dùng ảnh đã ẩn danh của bạn."
        )
        st.stop()

    try:
        image, _, warning = decode_upload(uploaded.name, uploaded.getvalue())
    except PermissionError as exc:
        st.error(str(exc))
        st.stop()
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    if warning:
        st.warning(warning)

    with st.spinner("Đang trích đặc trưng và suy luận…"):
        features = extract_152_features(image)
        result = predict_image(scaler, clf, features)

    left, right = st.columns([1, 1], gap="large")
    with left:
        st.subheader("Ảnh đầu vào (299×299, xám)")
        st.image(image, caption=uploaded.name, clamp=True)
        data_url = to_data_url(image)
        st.download_button(
            "Tải ảnh đã tiền xử lý (PNG)",
            data=base64.b64decode(data_url.split(",", 1)[1]),
            file_name="cxr_preprocessed_299.png",
            mime="image/png",
            help="Ảnh 299×299 đã dùng để trích đặc trưng; tệp được tạo trong bộ nhớ.",
        )

    with right:
        st.subheader("Kết quả suy luận")
        st.metric("Nhãn dự đoán", str(result["label"]))
        fig = plot_probabilities(result)
        st.pyplot(fig)
        plt.close(fig)
        probs = result["probabilities"]
        st.dataframe(
            {
                "Lớp": list(probs.keys()),
                "Xác suất": [float(v) for v in probs.values()],
            },
            hide_index=True,
            width="stretch",
        )

    st.divider()
    st.caption(
        "Artifact: "
        f"`{artifact_path.name}` · scikit-learn {meta.get('sklearn_version')} · "
        f"n_train={meta.get('n_train')} · split `{str(meta.get('split_sha256'))[:12]}…`"
    )
    st.error(DISCLAIMER)
    st.caption(
        "Không tải ảnh bệnh nhân thật hoặc ảnh có thông tin định danh. "
        "Kết quả chỉ dùng cho mục đích học tập và minh họa phương pháp."
    )


if __name__ == "__main__":
    main()
