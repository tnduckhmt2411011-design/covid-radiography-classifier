"""Module trích xuất đặc trưng HOG và dựng các nhóm đặc trưng ghép.

Trách nhiệm:
- Phụ trách nhiệm vụ S3-08 (RQ1) theo kế hoạch phát triển dự án.
- Tính toán số chiều đặc trưng HOG theo kích thước ảnh.
- Trích xuất đặc trưng HOG chuẩn hoá L2-Hys.
- Dựng nhóm đặc trưng glcmlbp kết hợp GLCM và LBP (88 chiều).
- Dựng nhóm đặc trưng ghép gồm histogram, GLCM và LBP (152 chiều).
- Trích xuất đặc trưng theo từng nhóm riêng lẻ hoặc hàng loạt theo khối ảnh.
"""

import logging
import time
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

import numpy as np
from skimage.feature import hog

from src.features_hist_glcm_lbp import (
    GLCM_DIM,
    HIST_DIM,
    LBP_DIM,
    extract_glcm,
    extract_histogram,
    extract_lbp,
)

# Khởi tạo logger cho module
logger = logging.getLogger(__name__)

# Các hằng số công khai theo đặc tả S3-08 và results/threshold_v3.md
HOG_ORIENTATIONS: int = 9
HOG_PIXELS_PER_CELL: Tuple[int, int] = (16, 16)
HOG_CELLS_PER_BLOCK: Tuple[int, int] = (2, 2)
HOG_BLOCK_NORM: str = "L2-Hys"
HOG_MIN_SIZE: int = 32
HOG_DIM: int = 10404
GLCMLBP_DIM: int = 88
GHEP_DIM: int = 152
GROUP_NAMES: Tuple[str, ...] = ("hist", "glcmlbp", "hog", "ghep")
GROUP_DIMS: Dict[str, int] = {
    "hist": 64,
    "glcmlbp": 88,
    "hog": 10404,
    "ghep": 152,
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
            f"Ảnh đầu vào phải là mảng NumPy 2 chiều kiểu uint8. "
            f"Nhận được ndim={received_ndim}, dtype={received_dtype}."
        )


def hog_dim(height: int, width: int) -> int:
    """Tính số chiều của vector đặc trưng HOG từ kích thước ảnh.

    Args:
        height: Chiều cao ảnh theo điểm ảnh.
        width: Chiều rộng ảnh theo điểm ảnh.

    Returns:
        int: Số chiều vector đặc trưng HOG.

    Raises:
        ValueError: Nếu chiều cao hoặc chiều rộng nhỏ hơn 32.
    """
    if height < HOG_MIN_SIZE or width < HOG_MIN_SIZE:
        raise ValueError(
            f"Kích thước ảnh phải tối thiểu {HOG_MIN_SIZE}x{HOG_MIN_SIZE}. "
            f"Nhận được height={height}, width={width}."
        )
    return ((height // 16) - 1) * ((width // 16) - 1) * 2 * 2 * 9


def extract_hog(img: np.ndarray) -> np.ndarray:
    """Trích xuất vector đặc trưng HOG từ ảnh xám 2 chiều kiểu uint8.

    Args:
        img: Mảng ảnh xám 2 chiều kiểu uint8.

    Returns:
        np.ndarray: Vector đặc trưng HOG kiểu float64.

    Raises:
        ValueError: Nếu ảnh không đúng mảng 2 chiều uint8 hoặc có cạnh nhỏ hơn 32.
    """
    _validate_image_input(img)
    height, width = img.shape
    if height < HOG_MIN_SIZE or width < HOG_MIN_SIZE:
        raise ValueError(
            f"Kích thước ảnh nhỏ hơn ngưỡng tối thiểu {HOG_MIN_SIZE}x{HOG_MIN_SIZE}. "
            f"Nhận được kích thước {img.shape}."
        )
    feat = hog(
        img,
        orientations=HOG_ORIENTATIONS,
        pixels_per_cell=HOG_PIXELS_PER_CELL,
        cells_per_block=HOG_CELLS_PER_BLOCK,
        block_norm=HOG_BLOCK_NORM,
        feature_vector=True,
    )
    return feat.astype(np.float64)


def extract_glcmlbp(img: np.ndarray) -> Tuple[np.ndarray, int]:
    """Trích xuất nhóm đặc trưng kết hợp GLCM và LBP.

    Args:
        img: Mảng ảnh xám 2 chiều kiểu uint8.

    Returns:
        Tuple[np.ndarray, int]: Vector 88 chiều (GLCM 60 chiều rồi LBP 28 chiều)
        và số lượng thuộc tính GLCM correlation bị NaN.
    """
    _validate_image_input(img)
    vec_glcm, nan_count = extract_glcm(img)
    vec_lbp = extract_lbp(img)
    return np.concatenate([vec_glcm, vec_lbp]).astype(np.float64), nan_count


def extract_ghep(img: np.ndarray) -> Tuple[np.ndarray, int]:
    """Trích xuất nhóm đặc trưng ghép gồm histogram, GLCM và LBP.

    Args:
        img: Mảng ảnh xám 2 chiều kiểu uint8.

    Returns:
        Tuple[np.ndarray, int]: Vector 152 chiều (histogram 64, GLCM 60, LBP 28)
        và số lượng thuộc tính GLCM correlation bị NaN.
    """
    _validate_image_input(img)
    vec_hist = extract_histogram(img)
    vec_glcm, nan_count = extract_glcm(img)
    vec_lbp = extract_lbp(img)
    return (
        np.concatenate([vec_hist, vec_glcm, vec_lbp]).astype(np.float64),
        nan_count,
    )


def extract_group(img: np.ndarray, name: str) -> Tuple[np.ndarray, int]:
    """Trích xuất đặc trưng của một ảnh theo tên nhóm.

    Args:
        img: Mảng ảnh xám 2 chiều kiểu uint8.
        name: Tên nhóm đặc trưng ('hist', 'glcmlbp', 'hog', 'ghep').

    Returns:
        Tuple[np.ndarray, int]: Vector đặc trưng và số thuộc tính GLCM correlation NaN.

    Raises:
        ValueError: Nếu tên nhóm không hợp lệ.
    """
    if name == "hist":
        return extract_histogram(img), 0
    elif name == "glcmlbp":
        return extract_glcmlbp(img)
    elif name == "hog":
        return extract_hog(img), 0
    elif name == "ghep":
        return extract_ghep(img)
    else:
        raise ValueError(
            f"Tên nhóm không hợp lệ: '{name}'. "
            f"Các nhóm hợp lệ: {GROUP_NAMES}."
        )


def extract_groups(
    images: Iterable[np.ndarray],
    groups: Sequence[str] = GROUP_NAMES,
    chunk_size: int = 64,
    timer: Callable[[], float] = time.process_time,
) -> Tuple[Dict[str, np.ndarray], Dict[str, object]]:
    """Trích xuất các nhóm đặc trưng cho tập ảnh theo khối và đo thời gian CPU.

    Args:
        images: Iterable các mảng ảnh xám 2 chiều kiểu uint8.
        groups: Danh sách tên các nhóm đặc trưng cần trích xuất.
        chunk_size: Số lượng ảnh tối đa trong mỗi khối xử lý.
        timer: Hàm đo thời gian CPU (mặc định time.process_time).

    Returns:
        Tuple[Dict[str, np.ndarray], Dict[str, object]]:
            - features: Ánh xạ từ tên nhóm sang mảng đặc trưng float64 shape (n, dim).
            - info: Thông tin thống kê gồm 'n_images', 'glcm_nan_images',
                    'cpu_seconds', 'chunk_size'.

    Raises:
        ValueError: Nếu groups rỗng, chứa tên không hợp lệ hoặc trùng lặp,
                    hoặc chunk_size nhỏ hơn 1.
    """
    if not groups:
        raise ValueError("Danh sách groups không được rỗng.")
    if len(groups) != len(set(groups)):
        raise ValueError("Danh sách groups không được chứa tên trùng lặp.")
    for g in groups:
        if g not in GROUP_NAMES:
            raise ValueError(
                f"Tên nhóm '{g}' không hợp lệ. Các nhóm hợp lệ: {GROUP_NAMES}."
            )
    if chunk_size < 1:
        raise ValueError(
            f"chunk_size phải lớn hơn hoặc bằng 1. Nhận được {chunk_size}."
        )

    cpu_seconds: Dict[str, float] = {g: 0.0 for g in groups}
    all_features: Dict[str, List[np.ndarray]] = {g: [] for g in groups}
    n_images: int = 0
    glcm_nan_images: int = 0

    chunk: List[np.ndarray] = []

    def _process_chunk(chunk_imgs: List[np.ndarray]) -> None:
        nonlocal n_images, glcm_nan_images
        chunk_len = len(chunk_imgs)
        chunk_has_nan = [False] * chunk_len

        for g in groups:
            t0 = timer()
            for i, img in enumerate(chunk_imgs):
                vec, nan_count = extract_group(img, g)
                all_features[g].append(vec)
                if nan_count > 0:
                    chunk_has_nan[i] = True
            t1 = timer()
            cpu_seconds[g] += (t1 - t0)

        glcm_nan_images += sum(chunk_has_nan)
        n_images += chunk_len

    for img in images:
        chunk.append(img)
        if len(chunk) == chunk_size:
            _process_chunk(chunk)
            chunk = []

    if chunk:
        _process_chunk(chunk)

    features: Dict[str, np.ndarray] = {}
    for g in groups:
        if n_images == 0:
            features[g] = np.empty((0, GROUP_DIMS[g]), dtype=np.float64)
        else:
            features[g] = np.array(all_features[g], dtype=np.float64)

    for g in groups:
        logger.info(
            f"Thoi gian trich (giay CPU) nhom {g}: {cpu_seconds[g]:.3f}"
        )

    if "glcmlbp" in groups or "ghep" in groups:
        logger.info(
            f"GLCM correlation NaN: {glcm_nan_images}/{n_images} anh"
        )

    info: Dict[str, object] = {
        "n_images": n_images,
        "glcm_nan_images": glcm_nan_images,
        "cpu_seconds": cpu_seconds,
        "chunk_size": chunk_size,
    }

    return features, info
