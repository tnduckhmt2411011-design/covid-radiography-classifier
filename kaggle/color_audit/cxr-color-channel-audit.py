"""Kiểm tra kênh màu thực tế trên 140 ảnh RGB của lớp Viral Pneumonia."""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image

def run_audit():
    print("=== BẮT ĐẦU ĐO ĐẠC KÊNH MÀU TRÊN KAGGLE CPU ===")
    input_root = Path("/kaggle/input")
    
    # 1. Định vị manifest.csv
    manifest_path = None
    for p in input_root.rglob("manifest.csv"):
        manifest_path = p
        break
    
    if manifest_path is None or not manifest_path.exists():
        raise FileNotFoundError("Không tìm thấy manifest.csv trong /kaggle/input!")
        
    print(f"Đọc manifest từ: {manifest_path}")
    df = pd.read_csv(manifest_path)
    
    # Lọc 140 ảnh RGB của Viral Pneumonia
    rgb_viral = df[(df["label"] == "Viral Pneumonia") & (df["color_mode"] == "RGB")].copy()
    print(f"Tổng số ảnh Viral Pneumonia có color_mode == 'RGB': {len(rgb_viral)}")
    assert len(rgb_viral) == 140, f"Kỳ vọng 140 ảnh, tìm thấy {len(rgb_viral)}"
    
    # 2. Định vị thư mục ảnh gốc
    img_root = None
    for p in input_root.rglob("COVID-19_Radiography_Dataset"):
        if p.is_dir():
            img_root = p
            break
            
    if img_root is None:
        for p in input_root.rglob("Viral Pneumonia"):
            if p.is_dir():
                img_root = p.parent
                break
                
    print(f"Thư mục ảnh gốc: {img_root}")
    
    records = []
    num_diff_images = 0
    num_diff_pixels_total = 0
    
    for idx, row in rgb_viral.iterrows():
        rel_path = row["rel_image_path"]
        candidate = img_root / rel_path if img_root else None
        if not candidate or not candidate.exists():
            # Thử tìm trực tiếp
            found = list(input_root.rglob(row["image_id"]))
            if found:
                candidate = found[0]
            else:
                raise FileNotFoundError(f"Không tìm thấy ảnh {row['image_id']}")
                
        with Image.open(candidate) as img:
            arr_orig = np.array(img)
            
            # Kênh R, G, B
            if arr_orig.ndim == 3 and arr_orig.shape[2] >= 3:
                R = arr_orig[:, :, 0].astype(np.int32)
                G = arr_orig[:, :, 1].astype(np.int32)
                B = arr_orig[:, :, 2].astype(np.int32)
                
                diff_rg = np.abs(R - G)
                diff_gb = np.abs(G - B)
                diff_rb = np.abs(R - B)
                
                max_diff = int(max(np.max(diff_rg), np.max(diff_gb), np.max(diff_rb)))
                mean_diff = float(np.mean([np.mean(diff_rg), np.mean(diff_gb), np.mean(diff_rb)]))
            else:
                max_diff = 0
                mean_diff = 0.0
                
            # So sánh convert("RGB") vs convert("L").convert("RGB")
            img_c1 = img.convert("RGB")
            img_c2 = img.convert("L").convert("RGB")
            
            arr_c1 = np.array(img_c1).astype(np.int32)
            arr_c2 = np.array(img_c2).astype(np.int32)
            
            pixel_diff_mask = np.any(arr_c1 != arr_c2, axis=-1)
            diff_pixel_count = int(np.sum(pixel_diff_mask))
            max_convert_diff = int(np.max(np.abs(arr_c1 - arr_c2))) if diff_pixel_count > 0 else 0
            
            if max_diff > 0:
                num_diff_images += 1
            num_diff_pixels_total += diff_pixel_count
            
            records.append({
                "image_id": row["image_id"],
                "max_diff_channel": max_diff,
                "mean_diff_channel": mean_diff,
                "diff_pixel_count": diff_pixel_count,
                "max_convert_diff": max_convert_diff
            })
            
    max_diffs = [r["max_diff_channel"] for r in records]
    percentiles = {
        "p25": float(np.percentile(max_diffs, 25)),
        "p50": float(np.percentile(max_diffs, 50)),
        "p75": float(np.percentile(max_diffs, 75)),
        "p90": float(np.percentile(max_diffs, 90)),
        "p99": float(np.percentile(max_diffs, 99)),
        "max": int(np.max(max_diffs)),
    }
    
    summary = {
        "total_images": len(records),
        "num_images_channel_diff_gt_zero": num_diff_images,
        "ratio_images_diff": num_diff_images / len(records),
        "mean_max_diff": float(np.mean(max_diffs)),
        "percentiles": percentiles,
        "total_different_pixels": num_diff_pixels_total,
        "all_channels_identical_R_G_B": (num_diff_images == 0)
    }
    
    print("\n" + "="*50)
    print("=== KẾT QUẢ ĐO ĐẠC KÊNH MÀU THỰC TẾ ===")
    print(f"Tổng số ảnh kiểm tra: {summary['total_images']}")
    print(f"Số ảnh có chênh lệch kênh (|R-G|, |G-B|, |R-B| > 0): {summary['num_images_channel_diff_gt_zero']}/{summary['total_images']}")
    print(f"Trung bình max_diff giữa các kênh: {summary['mean_max_diff']:.4f}")
    print(f"Phân vị max_diff: {percentiles}")
    print(f"Tổng số pixel khác nhau giữa convert('RGB') và convert('L').convert('RGB'): {summary['total_different_pixels']}")
    print(f"Kết luận: Tất cả 140 ảnh có R=G=B hoàn toàn? {summary['all_channels_identical_R_G_B']}")
    print("="*50 + "\n")
    
    output_path = Path("/kaggle/working/color_channel_audit.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Đã lưu kết quả tại: {output_path}")

if __name__ == "__main__":
    run_audit()
