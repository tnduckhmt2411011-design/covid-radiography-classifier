# Phep do tren tap validation co anh gan trung o tap khac

| Hang muc | Gia tri |
| :--- | ---: |
| So anh validation co anh gan trung (train hoac test) | 273 |
| Ty le trong 3.174 anh validation | 8.6% |
| Macro-F1 toan bo validation | 0.9024 |
| Macro-F1 tren 273 anh co anh gan trung | 0.9068 |
| Macro-F1 tren 2901 anh con lai | 0.9017 |
| Khoang tin cay 95% cho hieu macro-F1 (tap con tru phan con lai) | [-0.0462; 0.0386] |
| Bootstrap (n_boot / seed) | 2000 / 42 |
| Recall tung lop tren tap con | {'COVID': 0.9531, 'Lung_Opacity': 0.7317, 'Normal': 0.9329, 'Viral Pneumonia': 1.0} |
| Recall tung lop tren phan con lai | {'COVID': 0.9577, 'Lung_Opacity': 0.855, 'Normal': 0.8778, 'Viral Pneumonia': 0.9397} |

Dem lai tu `splits/split_v1.csv` (cot `phash`), khoang cach Hamming 2 hoac 4 giua cac tap; ket qua khop so da cong bo: 735 cap, 325/335/75 theo cap tap, 229 cap lech nhan, 273 anh validation va 243 anh test. Khoang tin cay lay mau lai doc lap trong tung tap con (2000 lan, seed 42), chi dung du doan co san, khong huan luyen lai.
