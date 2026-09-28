"""Module utils.py

Trách nhiệm:
- Cung cấp các hàm tiện ích dùng chung trong toàn bộ dự án.
"""

import os
import random
import numpy as np
import torch


def set_seed(seed: int = 42) -> None:
    """Thiết lập seed ngẫu nhiên cho các thư viện để đảm bảo khả năng tái lập kết quả thực nghiệm.

    Args:
        seed (int): Giá trị seed cần thiết lập (mặc định là 42).
    """
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
