"""Module trích xuất đặc trưng histogram, GLCM, LBP.

Trách nhiệm:
- Phụ trách nhiệm vụ S3-07 (RQ1) theo kế hoạch phát triển dự án.
- Trích xuất đặc trưng histogram mức xám 64 bin chuẩn hoá tổng bằng 1.
- Trích xuất đặc trưng ma trận đồng hiện mức xám (GLCM) 32 mức với 5 thuộc tính (60 chiều).
- Trích xuất đặc trưng mẫu nhị phân cục bộ (LBP) uniform đa bán kính (28 chiều).
- Cung cấp hàm trích xuất hàng loạt (batch) cho danh sách ảnh đầu vào.
"""

import logging
import math
from typing import Dict, Iterable, Sequence, Tuple

import numpy as np
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern

# Khởi tạo logger cho module
logger = logging.getLogger(__name__)

# Các hằng số công khai theo đặc tả S3-07 và results/threshold_v3.md
HIST_BINS: int = 64
GLCM_LEVELS: int = 32
GLCM_DISTANCES: Tuple[int, ...] = (1, 3, 5)
GLCM_ANGLES: Tuple[float, ...] = (0.0, math.pi / 4, math.pi / 2, 3 * math.pi / 4)
GLCM_PROPS: Tuple[str, ...] = (
    "contrast",
    "dissimilarity",
    "homogeneity",
    "energy",
    "correlation",
)
LBP_PARAMS: Tuple[Tuple[int, int], ...] = ((8, 1), (16, 2))
HIST_DIM: int = 64
GLCM_DIM: int = 60
LBP_DIM: int = 28

# Danh sách tên đặc trưng hợp lệ và số chiều tương ứng
_VALID_FEATURE_NAMES: Tuple[str, ...] = ("hist", "glcm", "lbp")
_DIM_MAPPING: Dict[str, int] = {
    "hist": HIST_DIM,
    "glcm": GLCM_DIM,
    "lbp": LBP_DIM,
}


def _validate_image_input(img: np.ndarray) -> None:
    """Kiểm tra tính hợp lệ của mảng ảnh đầu vào.

    Args:
        img: Mảng ảnh cần kiểm tra.

    Raises:
        ValueError: Nếu ảnh không phải mảng NumPy 2 chiều kiểu uint8.
    """
    if not isinstance(img, np.ndarray) or img.ndim != 2 or img.dtype != np.uint8:
        received_ndim = getattr(img, "ndim", None)
        received_dtype = getattr(img, "dtype", None)
        raise ValueError(
            f"Ảnh đầu vào phải là mảng 2 chiều kiểu uint8. "
            f"Nhận được ndim={received_ndim}, dtype={received_dtype}"
        )


def extract_histogram(img: np.ndarray) -> np.ndarray:
    """Trích xuất vector đặc trưng histogram 64 bin chuẩn hoá tổng bằng 1.

    np.histogram trên khoảng (0, 256) chia thành 64 bin (mỗi bin rộng 4 mức xám:
    0-3, 4-7, ..., 252-255). Kết quả chia cho tổng số phần tử để tổng bằng 1.

    Args:
        img: Mảng ảnh xám 2 chiều kiểu uint8.

    Returns:
        np.ndarray: Vector đặc trưng histogram kích thước (64,) kiểu float64 có tổng bằng 1.
    """
    _validate_image_input(img)
    hist, _ = np.histogram(img, bins=HIST_BINS, range=(0, 256))
    hist_float = hist.astype(np.float64)
    total = np.sum(hist_float)
    if total > 0:
        hist_float = hist_float / total
    return hist_float


def extract_glcm(img: np.ndarray) -> Tuple[np.ndarray, int]:
    """Trích xuất vector đặc trưng GLCM 60 chiều và đếm số giá trị correlation NaN.

    Giảm mức xám về 32 mức (img // 8, giá trị từ 0 đến 31).
    Tính GLCM với các khoảng cách (1, 3, 5), 4 hướng góc (0, pi/4, pi/2, 3pi/4),
    symmetric=True, normed=True.
    Trích xuất 5 thuộc tính theo thứ tự: contrast, dissimilarity, homogeneity,
    energy, correlation. Mỗi thuộc tính làm phẳng theo thứ tự C (khoảng cách chính,
    góc phụ) thành 12 giá trị, nối lại thành vector 60 chiều.
    Riêng thuộc tính correlation: các phần tử NaN được thay bằng 0.0 và đếm số lượng.

    Args:
        img: Mảng ảnh xám 2 chiều kiểu uint8.

    Returns:
        Tuple[np.ndarray, int]:
            - Vector đặc trưng GLCM kích thước (60,) kiểu float64.
            - Số lượng phần tử correlation NaN đã thay thế bằng 0.0 (từ 0 đến 12).
    """
    _validate_image_input(img)
    levels_img = img // 8
    glcm = graycomatrix(
        levels_img,
        distances=list(GLCM_DISTANCES),
        angles=list(GLCM_ANGLES),
        levels=GLCM_LEVELS,
        symmetric=True,
        normed=True,
    )

    feature_blocks = []
    nan_count = 0

    for prop in GLCM_PROPS:
        vals = graycoprops(glcm, prop)
        flat_vals = vals.ravel().astype(np.float64)
        if prop == "correlation":
            is_nan_element = np.isnan(flat_vals)
            nan_count = int(np.sum(is_nan_element))
            flat_vals = np.where(is_nan_element, 0.0, flat_vals)
        feature_blocks.append(flat_vals)

    glcm_vector = np.concatenate(feature_blocks).astype(np.float64)
    return glcm_vector, nan_count


def extract_lbp(img: np.ndarray) -> np.ndarray:
    """Trích xuất vector đặc trưng LBP uniform 28 chiều.

    Xử lý viền ảnh theo mặc định của scikit-image, không can thiệp.
    Không khẳng định giá trị đệm cụ thể.
    Tính toán tuần tự cho hai bộ tham số (P=8, R=1) và (P=16, R=2) với method='uniform'
    trên ảnh uint8 gốc (không giảm mức xám).
    Với mỗi bộ tham số, tính histogram bằng np.bincount với minlength=P + 2 rồi
    chia cho code.size để tổng bằng 1 (10 bin cho (8,1) và 18 bin cho (16,2)).
    Nối hai histogram thành vector 28 chiều kiểu float64.

    Args:
        img: Mảng ảnh xám 2 chiều kiểu uint8.

    Returns:
        np.ndarray: Vector đặc trưng LBP kích thước (28,) kiểu float64.
    """
    _validate_image_input(img)
    lbp_hist_list = []

    for p, r in LBP_PARAMS:
        code = local_binary_pattern(img, p, r, method="uniform")
        hist = np.bincount(code.astype(np.int64).ravel(), minlength=p + 2).astype(np.float64)
        total_pixels = float(code.size)
        if total_pixels > 0:
            hist = hist / total_pixels
        lbp_hist_list.append(hist)

    return np.concatenate(lbp_hist_list).astype(np.float64)


def extract_batch(
    images: Iterable[np.ndarray],
    names: Sequence[str] = ("hist", "glcm", "lbp"),
) -> Tuple[Dict[str, np.ndarray], int]:
    """Trích xuất đặc trưng hàng loạt từ một iterable các ảnh.

    Duyệt qua iterable ảnh một lần duy nhất (hỗ trợ generator).
    Gọi các hàm extract_histogram, extract_glcm, extract_lbp qua tên ở mức module
    để hỗ trợ việc thay thế kiểm thử bằng monkeypatch.

    Args:
        images: Iterable chứa các mảng ảnh 2 chiều kiểu uint8.
        names: Bộ tên đặc trưng cần trích xuất (mặc định 'hist', 'glcm', 'lbp').

    Returns:
        Tuple[Dict[str, np.ndarray], int]:
            - Dict ánh xạ tên đặc trưng sang mảng kích thước (n, dim) kiểu float64
              theo đúng thứ tự trong names.
            - Số ảnh có ít nhất một phần tử correlation NaN bị thay thế (trả về 0 nếu
              không có 'glcm' trong names).

    Raises:
        ValueError: Nếu names rỗng hoặc chứa tên đặc trưng không hợp lệ.
    """
    if not names:
        raise ValueError("Danh sách tên đặc trưng names không được để rỗng.")

    for name in names:
        if name not in _VALID_FEATURE_NAMES:
            raise ValueError(
                f"Tên đặc trưng '{name}' không hợp lệ. "
                f"Chỉ chấp nhận các tên: {_VALID_FEATURE_NAMES}"
            )

    has_glcm = "glcm" in names
    extracted_features: Dict[str, list] = {name: [] for name in names}
    nan_images_count = 0
    total_images_count = 0

    for img in images:
        total_images_count += 1
        glcm_nan_found = False

        for name in names:
            if name == "hist":
                feat = extract_histogram(img)
                extracted_features["hist"].append(feat)
            elif name == "glcm":
                feat, nan_count = extract_glcm(img)
                extracted_features["glcm"].append(feat)
                if nan_count > 0:
                    glcm_nan_found = True
            elif name == "lbp":
                feat = extract_lbp(img)
                extracted_features["lbp"].append(feat)

        if glcm_nan_found:
            nan_images_count += 1

    result_arrays: Dict[str, np.ndarray] = {}
    for name in names:
        dim = _DIM_MAPPING[name]
        if total_images_count == 0:
            result_arrays[name] = np.zeros((0, dim), dtype=np.float64)
        else:
            result_arrays[name] = np.array(extracted_features[name], dtype=np.float64)

    if has_glcm:
        logger.info(
            "GLCM correlation NaN: %d/%d anh",
            nan_images_count,
            total_images_count,
        )
        return result_arrays, nan_images_count

    return result_arrays, 0
