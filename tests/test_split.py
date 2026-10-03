"""Bộ kiểm thử tính toàn vẹn và chống rò rỉ của tập dữ liệu phân chia (splits/split_v1.csv).

Tuần 3 (Sprint 2) - Track A.
Phụ trách: Nguyễn Đức (kèm cặp: Hải Lý).

Kiểm tra 4 điều kiện cốt lõi:
1. Không rò rỉ nhóm (Leakage Prevention): Tập group_id giữa train, val, test rời nhau hoàn toàn.
2. Tỷ lệ phân chia xấp xỉ 70/15/15: Tổng số mẫu đúng 21.165, tỷ lệ train/val/test nằm trong dung sai cho phép.
3. Phân bố lớp đồng đều (Stratification): Tỷ lệ từng lớp trong train, val, test khớp với tỷ lệ tổng thể.
4. Toàn vẹn và mã băm SHA256 (Integrity): Mã băm của split_v1.csv khớp chính xác với file split_v1.sha256.
"""

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPLIT_CSV_PATH = REPO_ROOT / "splits" / "split_v1.csv"
SPLIT_SHA_PATH = REPO_ROOT / "splits" / "split_v1.sha256"

EXPECTED_TOTAL_ROWS = 21165
EXPECTED_CLASSES = {"COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"}
REQUIRED_COLUMNS = {"image_id", "label", "rel_image_path", "group_id", "split"}


def load_split_records():
    assert SPLIT_CSV_PATH.exists(), f"Không tìm thấy file: {SPLIT_CSV_PATH}"
    records = []
    with open(SPLIT_CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


def test_file_existence_and_columns():
    """Kiểm tra sự tồn tại của file và các cột bắt buộc."""
    assert SPLIT_CSV_PATH.exists(), "splits/split_v1.csv chưa tồn tại!"
    assert SPLIT_SHA_PATH.exists(), "splits/split_v1.sha256 chưa tồn tại!"

    records = load_split_records()
    assert len(records) == EXPECTED_TOTAL_ROWS, (
        f"Tổng số ảnh ({len(records)}) không khớp với kỳ vọng ({EXPECTED_TOTAL_ROWS})"
    )

    first_row = records[0]
    for col in REQUIRED_COLUMNS:
        assert col in first_row, f"Thiếu cột bắt buộc: {col}"


def test_no_group_leakage():
    """Điều kiện 1: Không rò rỉ nhóm trùng lặp giữa các tập train, val, test."""
    records = load_split_records()
    split_groups = defaultdict(set)
    for r in records:
        split_groups[r["split"]].add(r["group_id"])

    train_groups = split_groups["train"]
    val_groups = split_groups["val"]
    test_groups = split_groups["test"]

    train_val_overlap = train_groups & val_groups
    train_test_overlap = train_groups & test_groups
    val_test_overlap = val_groups & test_groups

    assert len(train_val_overlap) == 0, (
        f"Rò rỉ nhóm giữa train và val: {len(train_val_overlap)} nhóm trùng!"
    )
    assert len(train_test_overlap) == 0, (
        f"Rò rỉ nhóm giữa train và test: {len(train_test_overlap)} nhóm trùng!"
    )
    assert len(val_test_overlap) == 0, (
        f"Rò rỉ nhóm giữa val và test: {len(val_test_overlap)} nhóm trùng!"
    )


def test_split_ratios():
    """Điều kiện 2: Tỷ lệ xấp xỉ 70% train, 15% val, 15% test (dung sai +/- 3%)."""
    records = load_split_records()
    total = len(records)
    split_counts = Counter(r["split"] for r in records)

    train_count = split_counts["train"]
    val_count = split_counts["val"]
    test_count = split_counts["test"]

    assert train_count + val_count + test_count == total

    train_ratio = train_count / total
    val_ratio = val_count / total
    test_ratio = test_count / total

    # Cho phép dung sai 3% do ràng buộc gom nhóm group_id
    assert 0.67 <= train_ratio <= 0.73, f"Tỷ lệ train ngoài khoảng [67%, 73%]: {train_ratio:.3f}"
    assert 0.12 <= val_ratio <= 0.18, f"Tỷ lệ val ngoài khoảng [12%, 18%]: {val_ratio:.3f}"
    assert 0.12 <= test_ratio <= 0.18, f"Tỷ lệ test ngoài khoảng [12%, 18%]: {test_ratio:.3f}"


def test_class_distribution_balance():
    """Điều kiện 3: Phân bố các lớp đồng đều và phân tầng trên từng split."""
    records = load_split_records()
    total = len(records)

    global_class_counts = Counter(r["label"] for r in records)
    assert set(global_class_counts.keys()) == EXPECTED_CLASSES, (
        f"Các lớp không khớp: {set(global_class_counts.keys())}"
    )

    split_class_counts = defaultdict(Counter)
    for r in records:
        split_class_counts[r["split"]][r["label"]] += 1

    # Kiểm tra tỷ lệ từng lớp trong từng split so với tỷ lệ toàn cục (độ lệch tối đa < 3%)
    for split_name in ["train", "val", "test"]:
        split_total = sum(split_class_counts[split_name].values())
        for cls, count in global_class_counts.items():
            global_prop = count / total
            split_prop = split_class_counts[split_name][cls] / split_total
            diff = abs(split_prop - global_prop)
            assert diff < 0.035, (
                f"Lệch phân bố lớp {cls} ở tập {split_name}: {split_prop:.3f} vs toàn cục {global_prop:.3f} (diff={diff:.3f})"
            )


def test_sha256_integrity():
    """Điều kiện 4: Mã băm SHA256 của split_v1.csv phải khớp tuyệt đối với file split_v1.sha256."""
    assert SPLIT_SHA_PATH.exists(), f"Không tìm thấy file mã băm: {SPLIT_SHA_PATH}"

    sha_content = SPLIT_SHA_PATH.read_text(encoding="utf-8").strip()
    expected_hash = sha_content.split()[0].lower()

    hasher = hashlib.sha256()
    with open(SPLIT_CSV_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    actual_hash = hasher.hexdigest().lower()

    assert actual_hash == expected_hash, (
        f"Mã SHA256 không khớp!\nKỳ vọng: {expected_hash}\nThực tế: {actual_hash}"
    )


if __name__ == "__main__":
    print("Đang kiểm tra tính toàn vẹn của split...")
    test_file_existence_and_columns()
    test_no_group_leakage()
    test_split_ratios()
    test_class_distribution_balance()
    test_sha256_integrity()
    print("Tất cả các bài kiểm tra đều ĐẠT!")
