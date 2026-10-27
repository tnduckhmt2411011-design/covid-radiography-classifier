"""Bộ kiểm thử cho module src/features_hist_glcm_lbp.py.

Bao gồm đúng 14 ca kiểm thử (T1 đến T14) kiểm tra tính đúng đắn toán học,
đáp án tính tay, kiểm tra khớp skimage gọi trực tiếp, xử lý NaN, kiểm tra đầu vào,
trích xuất hàng loạt (batch) và tích hợp với lớp CXRDataset.
"""

import logging
import math
from pathlib import Path
from typing import Any, Tuple

import numpy as np
import pandas as pd
from PIL import Image
import pytest
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern

from src.dataset import CXRDataset
from src.features_hist_glcm_lbp import (
    GLCM_ANGLES,
    GLCM_DIM,
    GLCM_DISTANCES,
    GLCM_LEVELS,
    GLCM_PROPS,
    HIST_BINS,
    HIST_DIM,
    LBP_DIM,
    LBP_PARAMS,
    extract_batch,
    extract_glcm,
    extract_histogram,
    extract_lbp,
)


def test_t1_histogram_shape_and_sum():
    """T1: Kích thước và tổng của histogram trên ảnh ngẫu nhiên 299x299.

    Lý do kỳ vọng:
    - Ảnh ngẫu nhiên uint8 kích thước 299x299 khi trích histogram 64 bin chuẩn hoá
      phải tạo ra vector có shape (64,), kiểu float64 và tổng bằng 1.0 (sai số < 1e-12).
    """
    rng = np.random.default_rng(101)
    img = rng.integers(0, 256, (299, 299)).astype(np.uint8)

    feat = extract_histogram(img)
    assert feat.shape == (HIST_DIM,)
    assert feat.dtype == np.float64
    assert abs(float(np.sum(feat)) - 1.0) < 1e-12


def test_t2_histogram_bin_locations_manual():
    """T2: Vị trí bin theo đáp án tính tay trên các ảnh 10x10.

    Đáp án tính tay:
    - Mỗi bin rộng 4 mức xám (bin 0: 0-3, bin 1: 4-7, ..., bin 63: 252-255).
    - Ảnh toàn 0: toàn bộ rơi vào bin 0 -> hist[0] = 1.0, các bin khác = 0.
    - Ảnh toàn 3: 3 nằm trong khoảng [0, 3] -> hist[0] = 1.0, các bin khác = 0.
    - Ảnh toàn 4: 4 nằm trong khoảng [4, 7] -> hist[1] = 1.0, các bin khác = 0.
    - Ảnh toàn 255: 255 nằm trong bin cuối -> hist[63] = 1.0, các bin khác = 0.
    - Ảnh nửa trên 0 nửa dưới 255: 50% ở bin 0, 50% ở bin 63 -> hist[0] = 0.5, hist[63] = 0.5.
    """
    # 1. Ảnh toàn 0
    img_0 = np.zeros((10, 10), dtype=np.uint8)
    h0 = extract_histogram(img_0)
    assert h0[0] == 1.0
    assert np.all(h0[1:] == 0.0)

    # 2. Ảnh toàn 3
    img_3 = np.full((10, 10), 3, dtype=np.uint8)
    h3 = extract_histogram(img_3)
    assert h3[0] == 1.0
    assert np.all(h3[1:] == 0.0)

    # 3. Ảnh toàn 4
    img_4 = np.full((10, 10), 4, dtype=np.uint8)
    h4 = extract_histogram(img_4)
    assert h4[1] == 1.0
    assert h4[0] == 0.0
    assert np.all(h4[2:] == 0.0)

    # 4. Ảnh toàn 255
    img_255 = np.full((10, 10), 255, dtype=np.uint8)
    h255 = extract_histogram(img_255)
    assert h255[63] == 1.0
    assert np.all(h255[:63] == 0.0)

    # 5. Nửa trên 0 nửa dưới 255
    img_half = np.zeros((10, 10), dtype=np.uint8)
    img_half[5:, :] = 255
    h_half = extract_histogram(img_half)
    assert h_half[0] == 0.5
    assert h_half[63] == 0.5
    assert np.all(h_half[1:63] == 0.0)


def test_t3_histogram_independent_formula():
    """T3: Đối chiếu histogram bằng công thức độc lập trên ảnh 64x64.

    Lý do kỳ vọng:
    - Vì mỗi bin có độ rộng 4 mức xám liên tiếp, ánh xạ pixel bằng img // 4
      rồi tính tần suất qua np.bincount / img.size phải cho kết quả tương đương
      với np.histogram(img, bins=64, range=(0, 256)) trong phạm vi sai số 1e-12.
    """
    rng = np.random.default_rng(202)
    img = rng.integers(0, 256, (64, 64)).astype(np.uint8)

    feat = extract_histogram(img)
    expected = np.bincount((img // 4).ravel(), minlength=64).astype(np.float64) / img.size

    np.testing.assert_allclose(feat, expected, atol=1e-12)


def test_t4_glcm_general():
    """T4: Đặc trưng GLCM tổng quát trên ảnh ngẫu nhiên 64x64.

    Lý do kỳ vọng:
    - Vector trả về có shape (60,), kiểu float64, mọi phần tử hữu hạn.
    - Với ảnh mức xám ngẫu nhiên đầy đủ, số phần tử NaN correlation bằng 0 (kiểu int).
    - Tính toán phải tất định (kết quả hai lần gọi liên tiếp giống nhau hoàn toàn).
    """
    rng = np.random.default_rng(303)
    img = rng.integers(0, 256, (64, 64)).astype(np.uint8)

    feat1, count1 = extract_glcm(img)
    feat2, count2 = extract_glcm(img)

    assert feat1.shape == (GLCM_DIM,)
    assert feat1.dtype == np.float64
    assert np.all(np.isfinite(feat1))
    assert isinstance(count1, int)
    assert count1 == 0

    np.testing.assert_array_equal(feat1, feat2)
    assert count1 == count2


def test_t5_glcm_constant_image():
    """T5: GLCM trên ảnh hằng (toàn 100, 64x64).

    Đáp án tính tay và phân tích toán học:
    - 100 // 8 = 12 nên mọi pixel chuyển về mức 12, ma trận GLCM chỉ có ô (12, 12) = 1.0.
    - Contrast và dissimilarity tính hiệu bình phương và độ lệch tuyệt đối giữa các mức xám,
      do đó vector[0:24] hoàn toàn bằng 0.0.
    - Homogeneity và energy đạt giá trị tối đa 1.0 trên toàn bộ cặp (vector[24:48] toàn 1.0).
    - Mọi phần tử đều hữu hạn.
    - Số lượng correlation NaN thuộc tập {0, 12}; nếu bằng 12 thì vector[48:60] toàn 0.0.
    """
    img = np.full((64, 64), 100, dtype=np.uint8)
    feat, nan_count = extract_glcm(img)

    assert feat.shape == (GLCM_DIM,)
    assert feat.dtype == np.float64
    assert np.all(np.isfinite(feat))

    # Contrast và dissimilarity toàn 0.0
    np.testing.assert_allclose(feat[0:24], 0.0, atol=1e-12)
    # Homogeneity và energy toàn 1.0
    np.testing.assert_allclose(feat[24:48], 1.0, atol=1e-12)

    assert nan_count in (0, 12)
    if nan_count == 12:
        np.testing.assert_allclose(feat[48:60], 0.0, atol=1e-12)


def test_t6_glcm_layout_matches_skimage():
    """T6: Bố cục vector GLCM so với scikit-image gọi trực tiếp trên ảnh 64x64.

    Lý do kỳ vọng:
    - 5 thuộc tính sắp xếp theo thứ tự: contrast, dissimilarity, homogeneity,
      energy, correlation.
    - Mỗi thuộc tính (3 khoảng cách x 4 góc) được trải phẳng theo thứ tự hàng C
      khớp chính xác với graycoprops(glcm, prop).ravel().
    """
    rng = np.random.default_rng(404)
    img = rng.integers(0, 256, (64, 64)).astype(np.uint8)

    feat, _ = extract_glcm(img)

    levels_img = img // 8
    g = graycomatrix(
        levels_img,
        distances=list(GLCM_DISTANCES),
        angles=list(GLCM_ANGLES),
        levels=GLCM_LEVELS,
        symmetric=True,
        normed=True,
    )

    for i, prop in enumerate(GLCM_PROPS):
        expected_prop = graycoprops(g, prop).ravel()
        if prop == "correlation":
            expected_prop = np.nan_to_num(expected_prop, nan=0.0)
        actual_block = feat[12 * i : 12 * (i + 1)]
        np.testing.assert_allclose(actual_block, expected_prop, atol=1e-12)


def test_t7_glcm_nan_replacement(monkeypatch):
    """T7: Thay thế NaN của correlation bằng monkeypatch hàm giả.

    Đáp án tính tay:
    - Hàm giả trả về mảng shape (3, 4) bằng 2.0 cho thuộc tính khác correlation.
    - Cho correlation: trả về 0.5 với hai vị trí NaN tại [0, 0] và [2, 3].
    - Thứ tự làm phẳng C:
      * [0, 0] tương ứng chỉ số phẳng 0 -> vector[48 + 0] = 0.0
      * [2, 3] tương ứng chỉ số phẳng 2 * 4 + 3 = 11 -> vector[48 + 11] = vector[59] = 0.0
    - Các phần tử correlation còn lại bằng 0.5.
    - Số phần tử NaN thay thế đếm được bằng 2.
    """
    def fake_graycoprops(glcm: np.ndarray, prop: str, *args: Any, **kwargs: Any) -> np.ndarray:
        if prop != "correlation":
            return np.full((3, 4), 2.0)
        corr_arr = np.full((3, 4), 0.5)
        corr_arr[0, 0] = np.nan
        corr_arr[2, 3] = np.nan
        return corr_arr

    monkeypatch.setattr("src.features_hist_glcm_lbp.graycoprops", fake_graycoprops)

    dummy_img = np.zeros((32, 32), dtype=np.uint8)
    feat, nan_count = extract_glcm(dummy_img)

    assert feat.shape == (GLCM_DIM,)
    np.testing.assert_allclose(feat[0:48], 2.0, atol=1e-12)
    assert feat[48] == 0.0
    assert feat[59] == 0.0
    # Các ô correlation còn lại (10 ô) bằng 0.5
    remaining_indices = [idx for idx in range(48, 60) if idx not in (48, 59)]
    np.testing.assert_allclose(feat[remaining_indices], 0.5, atol=1e-12)
    assert nan_count == 2


def test_t8_lbp_general():
    """T8: Đặc trưng LBP tổng quát trên ảnh ngẫu nhiên 64x64.

    Lý do kỳ vọng:
    - Vector LBP trả về có shape (28,), kiểu float64, không có phần tử âm.
    - Vector gồm hai phần: 10 bin đầu của (8,1) có tổng bằng 1.0,
      18 bin sau của (16,2) có tổng bằng 1.0 (sai số < 1e-12).
    """
    rng = np.random.default_rng(505)
    img = rng.integers(0, 256, (64, 64)).astype(np.uint8)

    feat = extract_lbp(img)

    assert feat.shape == (LBP_DIM,)
    assert feat.dtype == np.float64
    assert np.all(feat >= 0.0)
    assert abs(float(np.sum(feat[:10])) - 1.0) < 1e-12
    assert abs(float(np.sum(feat[10:])) - 1.0) < 1e-12


def test_t9_lbp_matches_skimage():
    """T9: LBP so với scikit-image gọi trực tiếp trên ảnh 64x64.

    Lý do kỳ vọng:
    - Khớp chính xác với việc tự gọi local_binary_pattern(img, P, R, method='uniform')
      và tính histogram qua np.bincount chia cho code.size theo đúng thứ tự (8,1) rồi (16,2).
    """
    rng = np.random.default_rng(606)
    img = rng.integers(0, 256, (64, 64)).astype(np.uint8)

    feat = extract_lbp(img)

    code1 = local_binary_pattern(img, 8, 1, method="uniform")
    h1 = np.bincount(code1.astype(np.int64).ravel(), minlength=10).astype(np.float64) / code1.size

    code2 = local_binary_pattern(img, 16, 2, method="uniform")
    h2 = np.bincount(code2.astype(np.int64).ravel(), minlength=18).astype(np.float64) / code2.size

    expected = np.concatenate([h1, h2])
    np.testing.assert_allclose(feat, expected, atol=1e-12)


def test_t10_input_validation():
    """T10: Kiểm tra xác thực đầu vào cho các hàm trích và extract_batch.

    Lý do kỳ vọng:
    - Mọi hàm trích đơn lẻ (histogram, glcm, lbp) đều yêu cầu mảng 2 chiều uint8.
    - Mảng 3 chiều uint8 (4, 4, 3), mảng 2 chiều float64 (8, 8), mảng 1 chiều uint8 (8,)
      đều phải kích hoạt ngoại lệ ValueError (thông báo có ndim và dtype).
    - extract_batch với names=() hoặc names chứa tên lạ như ('hist', 'xyz') phải ném ValueError.
    """
    invalid_inputs = [
        np.zeros((4, 4, 3), dtype=np.uint8),
        np.zeros((8, 8), dtype=np.float64),
        np.zeros((8,), dtype=np.uint8),
    ]

    extraction_funcs = [extract_histogram, extract_glcm, extract_lbp]

    for func in extraction_funcs:
        for bad_inp in invalid_inputs:
            with pytest.raises(ValueError) as exc_info:
                func(bad_inp)
            msg = str(exc_info.value)
            assert "ndim" in msg and "dtype" in msg

    # Kiểm tra extract_batch với names rỗng hoặc tên lạ
    dummy_imgs = [np.zeros((16, 16), dtype=np.uint8)]
    with pytest.raises(ValueError):
        extract_batch(dummy_imgs, names=())

    with pytest.raises(ValueError):
        extract_batch(dummy_imgs, names=("hist", "xyz"))


def test_t11_extract_batch_fake_glcm(monkeypatch, caplog):
    """T11: extract_batch với hàm giả extract_glcm trên 4 ảnh 32x32.

    Lý do kỳ vọng:
    - Monkeypatch extract_glcm của module trả về số NaN k lần lượt là [0, 2, 0, 1].
    - Thứ tự khóa trong dict kết quả phải là ('hist', 'glcm', 'lbp') với shape tương ứng
      (4, 64), (4, 60), (4, 28).
    - Số ảnh có k > 0 là 2 ảnh (lần gọi 2 có k=2, lần gọi 4 có k=1).
    - Log mức INFO có chứa chuỗi 'GLCM correlation NaN: 2/4'.
    - Khi chỉ trích xuất names=('hist',): chỉ có khóa 'hist', số trả về bằng 0.
    """
    caplog.set_level(logging.INFO)

    k_seq = iter([0, 2, 0, 1])

    def fake_extract_glcm(img: np.ndarray) -> Tuple[np.ndarray, int]:
        return np.zeros(GLCM_DIM, dtype=np.float64), next(k_seq)

    monkeypatch.setattr("src.features_hist_glcm_lbp.extract_glcm", fake_extract_glcm)

    rng = np.random.default_rng(707)
    imgs = [rng.integers(0, 256, (32, 32)).astype(np.uint8) for _ in range(4)]

    res, nan_imgs = extract_batch(imgs, names=("hist", "glcm", "lbp"))

    assert list(res.keys()) == ["hist", "glcm", "lbp"]
    assert res["hist"].shape == (4, HIST_DIM)
    assert res["glcm"].shape == (4, GLCM_DIM)
    assert res["lbp"].shape == (4, LBP_DIM)
    assert nan_imgs == 2
    assert "GLCM correlation NaN: 2/4" in caplog.text

    # Gọi thêm với names=('hist',)
    res_hist_only, nan_hist_only = extract_batch(imgs, names=("hist",))
    assert list(res_hist_only.keys()) == ["hist"]
    assert res_hist_only["hist"].shape == (4, HIST_DIM)
    assert nan_hist_only == 0


def test_t12_extract_batch_real():
    """T12: extract_batch thật trên 3 ảnh 32x32 và trên generator rỗng.

    Lý do kỳ vọng:
    - Từng hàng của mảng kết quả bằng đúng kết quả gọi trực tiếp từng hàm trích trên từng ảnh.
    - Với dữ liệu ngẫu nhiên phong phú, số ảnh NaN trả về là 0.
    - Với generator / iterable rỗng, mỗi mảng có shape (0, dim) tương ứng (0, 64), (0, 60), (0, 28).
    """
    rng = np.random.default_rng(808)
    imgs = [rng.integers(0, 256, (32, 32)).astype(np.uint8) for _ in range(3)]

    res, nan_count = extract_batch(imgs)

    assert nan_count == 0
    for i in range(3):
        expected_hist = extract_histogram(imgs[i])
        expected_glcm, _ = extract_glcm(imgs[i])
        expected_lbp = extract_lbp(imgs[i])

        np.testing.assert_array_equal(res["hist"][i], expected_hist)
        np.testing.assert_array_equal(res["glcm"][i], expected_glcm)
        np.testing.assert_array_equal(res["lbp"][i], expected_lbp)

    # Trường hợp images rỗng
    empty_res, empty_nan = extract_batch([])
    assert empty_nan == 0
    assert empty_res["hist"].shape == (0, HIST_DIM)
    assert empty_res["glcm"].shape == (0, GLCM_DIM)
    assert empty_res["lbp"].shape == (0, LBP_DIM)


def test_t13_feature_shapes_299x299():
    """T13: Kích thước các vector trích xuất trên ảnh độ phân giải 299x299.

    Lý do kỳ vọng:
    - Ảnh 299x299 đúng độ phân giải chuẩn của bộ dữ liệu CXR.
    - Các vector trích xuất có shape khớp đúng HIST_DIM (64,), GLCM_DIM (60,),
      LBP_DIM (28,) và tất cả các phần tử đều hữu hạn.
    """
    rng = np.random.default_rng(909)
    img = rng.integers(0, 256, (299, 299)).astype(np.uint8)

    h_vec = extract_histogram(img)
    g_vec, g_nan = extract_glcm(img)
    l_vec = extract_lbp(img)

    assert h_vec.shape == (HIST_DIM,)
    assert g_vec.shape == (GLCM_DIM,)
    assert l_vec.shape == (LBP_DIM,)

    assert np.all(np.isfinite(h_vec))
    assert np.all(np.isfinite(g_vec))
    assert np.all(np.isfinite(l_vec))


def test_t14_cxr_dataset_integration(tmp_path: Path):
    """T14: Tích hợp với CXRDataset dùng transform=extract_histogram.

    Lý do kỳ vọng:
    - CXRDataset đọc ảnh PNG màu RGB, tự ép về đơn sắc 2D không resize.
    - Khi truyền transform=extract_histogram, mỗi lần truy cập dataset[i]
      sẽ trả về (vector_histogram shape (64,) có tổng 1, nhãn số nguyên int).
    """
    rng = np.random.default_rng(1010)

    # Tạo 2 tệp PNG RGB 40x40 ngẫu nhiên trong tmp_path
    img1_arr = rng.integers(0, 256, (40, 40, 3)).astype(np.uint8)
    img2_arr = rng.integers(0, 256, (40, 40, 3)).astype(np.uint8)

    path1 = tmp_path / "cxr_sample_1.png"
    path2 = tmp_path / "cxr_sample_2.png"

    Image.fromarray(img1_arr).save(path1)
    Image.fromarray(img2_arr).save(path2)

    split_df = pd.DataFrame([
        {
            "image_id": "cxr_sample_1.png",
            "label": "COVID",
            "rel_image_path": "cxr_sample_1.png",
            "split": "train",
        },
        {
            "image_id": "cxr_sample_2.png",
            "label": "Normal",
            "rel_image_path": "cxr_sample_2.png",
            "split": "train",
        },
    ])

    dataset = CXRDataset(
        split_df_or_path=split_df,
        split="train",
        data_root=tmp_path,
        transform=extract_histogram,
    )

    assert len(dataset) == 2

    vec0, label0 = dataset[0]
    assert isinstance(vec0, np.ndarray)
    assert vec0.shape == (HIST_DIM,)
    assert abs(float(np.sum(vec0)) - 1.0) < 1e-12
    assert isinstance(label0, int)
    assert label0 == 0  # "COVID" có index 0

    vec1, label1 = dataset[1]
    assert isinstance(vec1, np.ndarray)
    assert vec1.shape == (HIST_DIM,)
    assert abs(float(np.sum(vec1)) - 1.0) < 1e-12
    assert isinstance(label1, int)
    assert label1 == 2  # "Normal" có index 2
