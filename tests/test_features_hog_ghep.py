"""Bộ kiểm thử cho module src/features_hog_ghep.py.

Bao gồm đúng 14 ca kiểm thử (T1 đến T14) kiểm tra tính đúng đắn toán học,
đáp án tính tay, kiểm tra khớp skimage gọi trực tiếp, chuẩn hoá L2-Hys, kiểm tra đầu vào,
các nhóm đặc trưng kết hợp, trích xuất hàng loạt theo khối và tích hợp với CXRDataset.
"""

import itertools
import logging
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from PIL import Image
import pytest
from skimage.feature import hog

from src.dataset import CXRDataset
from src.features_hist_glcm_lbp import (
    GLCM_DIM,
    HIST_DIM,
    LBP_DIM,
    extract_glcm,
    extract_histogram,
    extract_lbp,
)
from src.features_hog_ghep import (
    GHEP_DIM,
    GLCMLBP_DIM,
    GROUP_NAMES,
    HOG_DIM,
    extract_ghep,
    extract_glcmlbp,
    extract_group,
    extract_groups,
    extract_hog,
    hog_dim,
)


def test_t1_hog_shape_299x299():
    """T1: Kích thước HOG trên ảnh 299x299.

    Lý do kỳ vọng:
    - Ảnh ngẫu nhiên uint8 kích thước 299x299 có số ô là (299 // 16) x (299 // 16) = 18 x 18 ô.
    - Số khối là (18 - 1) x (18 - 1) = 17 x 17 = 289 khối.
    - Mỗi khối gồm 2x2 ô, 9 hướng nên có 2 x 2 x 9 = 36 giá trị.
    - Tổng số chiều HOG là 289 x 36 = 10404 (bằng HOG_DIM).
    - Dtype là float64, mọi phần tử hữu hạn và không âm.
    """
    rng = np.random.default_rng(1001)
    img = rng.integers(0, 256, (299, 299), dtype=np.uint8)
    vec = extract_hog(img)
    assert vec.shape == (HOG_DIM,)
    assert vec.shape == (10404,)
    assert vec.dtype == np.float64
    assert np.all(np.isfinite(vec))
    assert np.all(vec >= 0.0)


def test_t2_hog_dim_formula_and_extraction():
    """T2: Kích thước HOG theo công thức (đáp án tính tay) và trích xuất thực tế.

    Đáp án tính tay:
    - Số ô theo mỗi chiều là H // 16 và W // 16.
    - Số khối trượt là (số ô hàng - 1) x (số ô cột - 1).
    - Mỗi khối có 2 x 2 x 9 = 36 giá trị:
      + (32, 32): 2x2 ô -> 1x1 khối -> 1 x 36 = 36.
      + (48, 64): 3x4 ô -> 2x3 khối -> 6 x 36 = 216.
      + (100, 70): 6x4 ô -> 5x3 khối -> 15 x 36 = 540.
      + (299, 299): 18x18 ô -> 17x17 khối -> 289 x 36 = 10404.
    - Cạnh nhỏ hơn 32 như (31, 32) và (32, 31) phải báo lỗi ValueError.
    """
    assert hog_dim(32, 32) == 36
    assert hog_dim(48, 64) == 216
    assert hog_dim(100, 70) == 540
    assert hog_dim(299, 299) == 10404

    rng = np.random.default_rng(1002)
    for h, w in [(32, 32), (48, 64), (100, 70), (299, 299)]:
        img = rng.integers(0, 256, (h, w), dtype=np.uint8)
        vec = extract_hog(img)
        assert vec.shape == (hog_dim(h, w),)

    with pytest.raises(ValueError):
        hog_dim(31, 32)
    with pytest.raises(ValueError):
        hog_dim(32, 31)


def test_t3_hog_constant_image():
    """T3: HOG trên ảnh hằng có gradient bằng 0.

    Đáp án tính tay:
    - Ảnh hằng 64x64 toàn giá trị 100 có 4x4 ô, 3x3 = 9 khối, 9 x 36 = 324 giá trị.
    - Vì cường độ pixel đồng nhất, độ dốc (gradient) tại mọi điểm đều bằng 0.
    - Kết quả trích xuất vector phải có shape (324,) và toàn bộ phần tử bằng 0.0.
    """
    img = np.full((64, 64), 100, dtype=np.uint8)
    vec = extract_hog(img)
    assert vec.shape == (324,)
    np.testing.assert_allclose(vec, 0.0, atol=1e-12)


def test_t4_hog_matches_skimage_direct():
    """T4: HOG khớp kết quả gọi trực tiếp từ skimage.feature.hog.

    Lý do kỳ vọng:
    - extract_hog cấu hình đúng 5 tham số: orientations=9, pixels_per_cell=(16, 16),
      cells_per_block=(2, 2), block_norm='L2-Hys', feature_vector=True.
    - Kết quả phải khớp chính xác với hàm gốc của skimage trong sai số 1e-12.
    """
    rng = np.random.default_rng(1004)
    img = rng.integers(0, 256, (64, 64), dtype=np.uint8)
    vec_ours = extract_hog(img)
    vec_expected = hog(
        img,
        orientations=9,
        pixels_per_cell=(16, 16),
        cells_per_block=(2, 2),
        block_norm="L2-Hys",
        feature_vector=True,
    )
    np.testing.assert_allclose(vec_ours, vec_expected, atol=1e-12)


def test_t5_hog_l2_hys_normalization():
    """T5: Chuẩn hoá L2-Hys của từng khối trong vector HOG.

    Đáp án tính tay:
    - Ảnh ngẫu nhiên 64x64 có 9 khối (mỗi khối 36 giá trị).
    - Sau khi chuẩn hoá L2-Hys, chuẩn L2 của từng hàng (khối) phải bằng 1.0 (sai số 1e-6).
    - Mọi phần tử đều không âm.
    """
    rng = np.random.default_rng(1005)
    img = rng.integers(0, 256, (64, 64), dtype=np.uint8)
    vec = extract_hog(img)
    blocks = vec.reshape(-1, 36)
    assert blocks.shape == (9, 36)
    norms = np.linalg.norm(blocks, axis=1)
    np.testing.assert_allclose(norms, 1.0, atol=1e-6)
    assert np.all(vec >= 0.0)


def test_t6_hog_input_validation():
    """T6: Kiểm tra đầu vào của hàm extract_hog.

    Lý do kỳ vọng:
    - Mảng 3 chiều, mảng 2 chiều float64, mảng 1 chiều uint8 phải báo ValueError
      với thông báo lỗi chứa cả hai từ 'ndim' và 'dtype'.
    - Mảng 2 chiều uint8 có kích thước nhỏ hơn 32x32 ((31, 31) hoặc (16, 100)) phải báo ValueError.
    """
    for arr in [
        np.zeros((4, 4, 3), dtype=np.uint8),
        np.zeros((8, 8), dtype=np.float64),
        np.zeros(8, dtype=np.uint8),
    ]:
        with pytest.raises(ValueError) as exc_info:
            extract_hog(arr)
        msg = str(exc_info.value)
        assert "ndim" in msg
        assert "dtype" in msg

    for shape in [(31, 31), (16, 100)]:
        with pytest.raises(ValueError):
            extract_hog(np.zeros(shape, dtype=np.uint8))


def test_t7_extract_ghep():
    """T7: Nhóm đặc trưng ghép histogram + GLCM + LBP (152 chiều).

    Đáp án tính tay:
    - histogram có 64 chiều, GLCM có 60 chiều, LBP có 28 chiều.
    - Tổng 64 + 60 + 28 = 152 chiều (bằng GHEP_DIM).
    - [0:64] bằng extract_histogram(img), [64:124] bằng vector GLCM, [124:152] bằng vector LBP.
    - Số trả về bằng nan_count của extract_glcm(img).
    """
    rng = np.random.default_rng(1007)
    img = rng.integers(0, 256, (64, 64), dtype=np.uint8)
    vec_ghep, nan_count = extract_ghep(img)
    assert vec_ghep.shape == (GHEP_DIM,)
    assert vec_ghep.shape == (152,)

    vec_hist = extract_histogram(img)
    vec_glcm, expected_nan = extract_glcm(img)
    vec_lbp = extract_lbp(img)

    assert np.array_equal(vec_ghep[0:64], vec_hist)
    assert np.array_equal(vec_ghep[64:124], vec_glcm)
    assert np.array_equal(vec_ghep[124:152], vec_lbp)
    assert nan_count == expected_nan
    assert HIST_DIM + GLCM_DIM + LBP_DIM == 152


def test_t8_extract_glcmlbp():
    """T8: Nhóm đặc trưng kết hợp GLCM + LBP (88 chiều).

    Đáp án tính tay:
    - GLCM có 60 chiều và LBP có 28 chiều, tổng là 88 chiều (bằng GLCMLBP_DIM).
    - [0:60] bằng vector của extract_glcm(img), [60:88] bằng extract_lbp(img).
    - Số trả về bằng nan_count của extract_glcm(img).
    """
    rng = np.random.default_rng(1008)
    img = rng.integers(0, 256, (64, 64), dtype=np.uint8)
    vec_glcmlbp, nan_count = extract_glcmlbp(img)
    assert vec_glcmlbp.shape == (GLCMLBP_DIM,)
    assert vec_glcmlbp.shape == (88,)

    vec_glcm, expected_nan = extract_glcm(img)
    vec_lbp = extract_lbp(img)

    assert np.array_equal(vec_glcmlbp[0:60], vec_glcm)
    assert np.array_equal(vec_glcmlbp[60:88], vec_lbp)
    assert nan_count == expected_nan


def test_t9_extract_group():
    """T9: Hàm extract_group theo từng tên nhóm hợp lệ và tên không hợp lệ.

    Lý do kỳ vọng:
    - 'hist': trả về (extract_histogram(img), 0).
    - 'glcmlbp': trả về extract_glcmlbp(img).
    - 'hog': trả về (extract_hog(img), 0).
    - 'ghep': trả về extract_ghep(img).
    - Tên không hợp lệ 'xyz' báo ValueError.
    """
    rng = np.random.default_rng(1009)
    img = rng.integers(0, 256, (64, 64), dtype=np.uint8)

    # hist
    vec_h, nan_h = extract_group(img, "hist")
    assert np.array_equal(vec_h, extract_histogram(img))
    assert nan_h == 0

    # glcmlbp
    vec_gl, nan_gl = extract_group(img, "glcmlbp")
    exp_vec_gl, exp_nan_gl = extract_glcmlbp(img)
    assert np.array_equal(vec_gl, exp_vec_gl)
    assert nan_gl == exp_nan_gl

    # hog
    vec_hg, nan_hg = extract_group(img, "hog")
    assert np.array_equal(vec_hg, extract_hog(img))
    assert nan_hg == 0

    # ghep
    vec_gh, nan_gh = extract_group(img, "ghep")
    exp_vec_gh, exp_nan_gh = extract_ghep(img)
    assert np.array_equal(vec_gh, exp_vec_gh)
    assert nan_gh == exp_nan_gh

    # Ten khong hop le
    with pytest.raises(ValueError):
        extract_group(img, "xyz")


def test_t10_extract_groups_generator_and_rows():
    """T10: extract_groups khớp từng hàng cho iterable generator.

    Lý do kỳ vọng:
    - Generator 3 ảnh 64x64 được trích xuất cho 4 nhóm với thứ tự GROUP_NAMES.
    - Số hàng là 3, số cột tương ứng là 64, 88, 324, 152.
    - Từng hàng khớp chính xác với kết quả extract_group trên từng ảnh.
    - info có n_images = 3, glcm_nan_images = 0, chunk_size = 64.
    """
    rng = np.random.default_rng(1010)
    img_list = [rng.integers(0, 256, (64, 64), dtype=np.uint8) for _ in range(3)]
    gen = (img for img in img_list)

    features, info = extract_groups(gen, chunk_size=64)

    assert list(features.keys()) == list(GROUP_NAMES)
    assert features["hist"].shape == (3, 64)
    assert features["glcmlbp"].shape == (3, 88)
    assert features["hog"].shape == (3, 324)
    assert features["ghep"].shape == (3, 152)

    for g in GROUP_NAMES:
        for i in range(3):
            exp_vec, _ = extract_group(img_list[i], g)
            assert np.array_equal(features[g][i], exp_vec)

    assert info["n_images"] == 3
    assert info["glcm_nan_images"] == 0
    assert info["chunk_size"] == 64


def test_t11_extract_groups_cpu_timer(caplog: pytest.LogCaptureFixture):
    """T11: Đo thời gian CPU với đồng hồ giả và kiểm tra log.

    Đáp án tính tay:
    - 5 ảnh chia thành 3 khối với chunk_size=2: (2, 2, 1) ảnh.
    - 4 nhóm đặc trưng, mỗi nhóm được đo 1 cặp t0, t1 -> 2 lần gọi timer cho mỗi (khối, nhóm).
    - Tổng số lần gọi timer là 3 khối x 4 nhóm x 2 = 24 lần.
    - Mỗi lần gọi timer tăng 1.0 giây, nên mỗi (khối, nhóm) mất đúng 1.0 giây CPU.
    - Mỗi nhóm qua 3 khối có cpu_seconds = 3.0.
    - Lần gọi tiếp theo của bộ đếm trả về 24.0.
    - Caplog ghi đúng dòng log thời gian CPU cho nhóm hog là 3.000 giây.
    """
    caplog.set_level(logging.INFO)
    rng = np.random.default_rng(1011)
    imgs = [rng.integers(0, 256, (64, 64), dtype=np.uint8) for _ in range(5)]

    counter = itertools.count(0.0, 1.0)

    def mock_timer() -> float:
        return float(next(counter))

    _, info = extract_groups(imgs, chunk_size=2, timer=mock_timer)

    assert info["cpu_seconds"] == {
        "hist": 3.0,
        "glcmlbp": 3.0,
        "hog": 3.0,
        "ghep": 3.0,
    }
    assert next(counter) == 24.0
    assert info["n_images"] == 5
    assert info["chunk_size"] == 2
    assert "Thoi gian trich (giay CPU) nhom hog: 3.000" in caplog.text


def test_t12_extract_groups_glcm_nan_count(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    """T12: Đếm số ảnh bị GLCM correlation NaN và ghi log cảnh báo.

    Đáp án tính tay:
    - 4 ảnh có img[0, 0] lần lượt là 0, 1, 2, 3.
    - Hàm giả extract_glcm trả về nan_count theo bảng: 0 -> 0, 1 -> 2, 2 -> 0, 3 -> 1.
    - Ảnh thứ 1 và ảnh thứ 3 có nan_count > 0, mỗi ảnh chỉ tính đúng 1 lần dù gọi ở cả glcmlbp và ghep.
    - Tổng số ảnh có NaN là 2 (glcm_nan_images = 2 trên tổng 4 ảnh).
    - Caplog chứa dòng 'GLCM correlation NaN: 2/4'.
    """
    caplog.set_level(logging.INFO)
    rng = np.random.default_rng(1012)
    imgs = [rng.integers(0, 256, (64, 64), dtype=np.uint8) for _ in range(4)]
    for i in range(4):
        imgs[i][0, 0] = i

    nan_mapping = {0: 0, 1: 2, 2: 0, 3: 1}

    def mock_extract_glcm(img: np.ndarray) -> Tuple[np.ndarray, int]:
        val = int(img[0, 0])
        return np.zeros(60, dtype=np.float64), nan_mapping[val]

    monkeypatch.setattr("src.features_hog_ghep.extract_glcm", mock_extract_glcm)

    _, info = extract_groups(imgs)
    assert info["glcm_nan_images"] == 2
    assert "GLCM correlation NaN: 2/4" in caplog.text


def test_t13_extract_groups_subsets_empty_and_validation(
    caplog: pytest.LogCaptureFixture,
):
    """T13: Kiểm tra tập con nhóm, danh sách rỗng và xác thực tham số đầu vào.

    Lý do kỳ vọng:
    - groups=('hist', 'hog') với 2 ảnh cho đúng 2 khóa theo thứ tự, glcm_nan_images=0,
      không ghi log NaN vì không chứa glcmlbp hay ghep.
    - images=[] trả về mảng rỗng shape (0, dim) đúng chuẩn 299x299 (HOG 10404),
      n_images=0, cpu_seconds toàn 0.0.
    - groups rỗng, chứa tên sai, chứa tên trùng hoặc chunk_size=0 đều báo ValueError.
    """
    caplog.set_level(logging.INFO)
    rng = np.random.default_rng(1013)
    imgs = [rng.integers(0, 256, (64, 64), dtype=np.uint8) for _ in range(2)]

    # Tập con groups
    features_sub, info_sub = extract_groups(imgs, groups=("hist", "hog"))
    assert list(features_sub.keys()) == ["hist", "hog"]
    assert list(info_sub["cpu_seconds"].keys()) == ["hist", "hog"]
    assert info_sub["glcm_nan_images"] == 0
    assert "GLCM correlation NaN" not in caplog.text

    # Danh sách ảnh rỗng
    features_empty, info_empty = extract_groups([])
    assert features_empty["hist"].shape == (0, 64)
    assert features_empty["glcmlbp"].shape == (0, 88)
    assert features_empty["hog"].shape == (0, 10404)
    assert features_empty["ghep"].shape == (0, 152)
    assert info_empty["n_images"] == 0
    assert info_empty["cpu_seconds"] == {
        "hist": 0.0,
        "glcmlbp": 0.0,
        "hog": 0.0,
        "ghep": 0.0,
    }

    # Tham số không hợp lệ
    with pytest.raises(ValueError):
        extract_groups(imgs, groups=())
    with pytest.raises(ValueError):
        extract_groups(imgs, groups=("hist", "xyz"))
    with pytest.raises(ValueError):
        extract_groups(imgs, groups=("hist", "hist"))
    with pytest.raises(ValueError):
        extract_groups(imgs, chunk_size=0)


def test_t14_cxr_dataset_integration(tmp_path: Path):
    """T14: Tích hợp với CXRDataset dùng transform=extract_hog.

    Đáp án tính tay:
    - Tạo 2 ảnh PNG màu RGB kích thước 40x40 ngẫu nhiên trong tmp_path.
    - CXRDataset tự ép ảnh về đơn sắc 2D không resize.
    - Với ảnh 40x40, số ô là 2x2, số khối là (2-1)x(2-1) = 1 khối.
    - 1 khối có 2 x 2 x 9 = 36 giá trị.
    - Mỗi phần tử dataset trả về vector HOG shape (36,) và nhãn kiểu số nguyên int.
    """
    rng = np.random.default_rng(1014)

    img1_arr = rng.integers(0, 256, (40, 40, 3), dtype=np.uint8)
    img2_arr = rng.integers(0, 256, (40, 40, 3), dtype=np.uint8)

    path1 = tmp_path / "cxr_hog_1.png"
    path2 = tmp_path / "cxr_hog_2.png"

    Image.fromarray(img1_arr).save(path1)
    Image.fromarray(img2_arr).save(path2)

    split_df = pd.DataFrame([
        {
            "image_id": "cxr_hog_1.png",
            "label": "COVID",
            "rel_image_path": "cxr_hog_1.png",
            "split": "train",
        },
        {
            "image_id": "cxr_hog_2.png",
            "label": "Normal",
            "rel_image_path": "cxr_hog_2.png",
            "split": "train",
        },
    ])

    dataset = CXRDataset(
        split_df_or_path=split_df,
        split="train",
        data_root=tmp_path,
        transform=extract_hog,
    )

    assert len(dataset) == 2

    vec0, label0 = dataset[0]
    assert isinstance(vec0, np.ndarray)
    assert vec0.shape == (36,)
    assert isinstance(label0, int)

    vec1, label1 = dataset[1]
    assert isinstance(vec1, np.ndarray)
    assert vec1.shape == (36,)
    assert isinstance(label1, int)
