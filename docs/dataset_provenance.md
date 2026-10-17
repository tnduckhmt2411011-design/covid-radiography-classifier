# Hồ sơ Nguồn gốc và Kiểm chứng Bộ dữ liệu (Dataset Provenance)

> **Tài liệu:** Kiểm chứng độc lập nguồn gốc bộ dữ liệu `COVID-19 Radiography Database` từ hai bài báo gốc (P1, P2), siêu dữ liệu Kaggle CLI và kho mã nguồn dự án.  
> **Ngày thực hiện:** 09/10/2026  
> **Nguyên tắc biên soạn:** Mọi thông tin đều được phân loại rõ ràng theo 3 mức độ xác thực: `[Nêu rõ trong bài]`, `[Suy ra từ số liệu]`, hoặc `[Chưa xác minh]`, kèm vị trí truy vết cụ thể (mục, bảng, trang hoặc tên file). Tuyệt đối không dùng kết quả của bài báo làm ngưỡng hay mục tiêu cho đồ án.

---

## 1. Nguồn tài liệu đã đọc và Phiên bản

Thực hiện đúng quy trình truy cập ưu tiên trang nhà xuất bản trước, sau đó đến kho lưu trữ preprint arXiv:

1. **Bài báo P1 — Chowdhury và cộng sự (2020):**
   - **Thông tin thư mục:** Muhammad E. H. Chowdhury và cộng sự, *"Can AI Help in Screening Viral and COVID-19 Pneumonia?"*, tạp chí *IEEE Access*, Tập 8, trang 132665–132676, xuất bản ngày 20/07/2020, DOI: `10.1109/ACCESS.2020.3010287`.
   - **Kết quả truy cập trang nhà xuất bản (`https://ieeexplore.ieee.org/document/9144185`, ngày 09/10/2026):** Trang trả về khung HTML kèm đối tượng siêu dữ liệu `xplGlobal.document.metadata` (chứa tiêu đề, danh sách tác giả, tóm tắt, số trang, DOI và trường `_value: "CCBY"`), nhưng phần thân bài báo tải động qua ứng dụng AngularJS nên không trích xuất trực tiếp được toàn văn từ HTTP tĩnh `[Nêu rõ trong bài — Metadata IEEE Xplore]`. Lưu ý: nhãn `CCBY` trên trang IEEE Xplore là giấy phép xuất bản mở của **bài báo**, không phải giấy phép của bộ dữ liệu.
   - **Bản đã đọc toàn văn:** Bản preprint **`arXiv:2003.13145v3`** (gồm 12 trang, định dạng bản thảo hai cột của IEEE Access), tải từ `https://arxiv.org/pdf/2003.13145.pdf`, truy cập ngày **09/10/2026**. **Ghi chú trạng thái:** *Chỉ đọc toàn văn bản preprint v3, chưa đối chiếu toàn văn bản chính thức trên nhà xuất bản (ngoại trừ phần Abstract và thông tin thư mục khớp với metadata trên IEEE Xplore).*

2. **Bài báo P2 — Rahman và cộng sự (2021):**
   - **Thông tin thư mục:** Tawsifur Rahman và cộng sự, *"Exploring the effect of image enhancement techniques on COVID-19 detection using chest X-ray images"*, tạp chí *Computers in Biology and Medicine*, Tập 132, Mã bài 104319, năm 2021, DOI: `10.1016/j.compbiomed.2021.104319`.
   - **Kết quả truy cập trang nhà xuất bản (`https://www.sciencedirect.com/science/article/pii/S001048252100113X`, ngày 09/10/2026):** Máy chủ ScienceDirect từ chối truy cập tự động với mã lỗi **`HTTP 403 Forbidden`**.
   - **Bản đã đọc toàn văn:** Bản preprint **`arXiv:2012.02238v1`** (gồm 34 trang, dòng chân trang ghi bản thảo gửi nhà xuất bản Elsevier ngày 25/11/2020), tải từ `https://arxiv.org/pdf/2012.02238.pdf`, truy cập ngày **09/10/2026**. **Ghi chú trạng thái:** *Chưa đối chiếu bản chính thức trên nhà xuất bản.*

3. **Trang Dataset trên Kaggle và Siêu dữ liệu qua Kaggle CLI:**
   - **Định danh bộ dữ liệu:** `tawsifurrahman/covid19-radiography-database` (`datasetId: 576013`).
   - **Công cụ truy vấn:** `Kaggle CLI 2.2.4` (phát hành ngày `23/07/2026` trên PyPI, đi kèm `kagglesdk 0.1.37`), truy cập ngày **09/10/2026** bằng lệnh chỉ đọc `kaggle datasets files` và `kaggle datasets metadata`.
   - **Các tệp siêu dữ liệu nhỏ đã tải riêng về thư mục tạm ngoài repo để kiểm tra (không tải ảnh và mask):**
     - `dataset-metadata.json` (`8.105` bytes)
     - `README.md.txt` (`3.348` bytes)
     - `COVID.metadata.xlsx` (`87.027` bytes)
     - `Lung_Opacity.metadata.xlsx` (`141.103` bytes)
     - `Normal.metadata.xlsx` (`234.106` bytes)
     - `Viral Pneumonia.metadata.xlsx` (`38.215` bytes)

4. **Tài liệu nội bộ của nhóm trên nhánh `origin/main` (commit `d9e40bf`):**
   - Đã đọc và đối chiếu nguyên trạng: [`README.md`](../README.md), [`splits/README.md`](../splits/README.md), [`docs/roadmap.md`](roadmap.md) (Mục 5), và [`splits/manifest.csv`](../splits/manifest.csv) (`21.165` bản ghi).

---

## 2. Thành phần Bộ dữ liệu, Kiểm chứng H1–H6 và Kiểm tra Số học

### 2.1. Bảng thành phần 4 lớp trong bộ dữ liệu (`21.165` ảnh)

Bộ dữ liệu được nhóm tác giả phát hành qua nhiều giai đoạn: bản đầu tiên gồm `219` ảnh COVID-19, `1.341` ảnh Normal và `1.345` ảnh Viral Pneumonia; bản cập nhật thứ nhất nâng lớp COVID-19 lên `1.200` ảnh (trong P1 sử dụng phiên bản trung gian gồm `423` COVID-19, `1.579` Normal, `1.485` Viral Pneumonia); bản cập nhật thứ hai (hiện hành trên Kaggle) gồm **`21.165` ảnh** chia thành 4 lớp kèm mặt nạ phổi `[Nêu rõ trong bài — dataset-metadata.json; README.md.txt dòng 3; P1 Mục II.A tr. 3]`.

| Lớp (Class) | Số ảnh (`manifest.csv` & `.xlsx`) | Nguồn gốc thành phần và Số lượng chi tiết | Mức chắc chắn & Vị trí truy vết |
| :--- | :---: | :--- | :--- |
| **COVID** (`COVID-19`) | **3.616** | **Theo văn bản P2 & `README.md.txt` (tổng cộng ra 3.615):**<br>• `2.473` ảnh từ bộ `BIMCV-COVID19+` (`bimcv.cipf.es` `[67]`, trong `README.md.txt` dòng 9 ghi nhầm tên là *padchest*)<br>• `183` ảnh từ kho ảnh của một trường y tại Đức (`github.com/ml-workgroup/covid-19-image-repository` `[68]`)<br>• `559` ảnh gộp từ `SIRM`, `GitHub` (`ieee8023`), `Eurorad`, `Kaggle` & `Twitter/Figshare` `[69–72]`<br>• `400` ảnh từ kho `COVID-CXNet` (`github.com/armiro/COVID-CXNet` `[73]`)<br><br>**Theo tệp `COVID.metadata.xlsx` thực tế (đủ 3.616 dòng):**<br>• `2.474` dòng từ `bimcv.cipf.es/...` (**nhiều hơn văn bản P2 đúng 1 ảnh**)<br>• `400` dòng từ `github.com/armiro/COVID-CXNet`<br>• `258` dòng từ `eurorad.org`<br>• `183` dòng từ `github.com/ml-workgroup/covid-19-image-repository`<br>• `182` dòng từ `github.com/ieee8023/covid-chestxray-dataset`<br>• `119` dòng từ `sirm.org/category/senza-categoria/covid-19/`<br>*(Ghi chú: $258 + 182 + 119 = 559$ ảnh, khớp đúng cụm 559 ảnh trong văn bản P2)* | • `[Nêu rõ trong bài]` Tổng `3.616` và 4 nguồn con với số lượng `2.473`, `183`, `559`, `400` tại **P2 Mục 3.1.5 (tr. 18–19), Bảng 1 (tr. 20)** và **`README.md.txt` (dòng 8–12)**.<br>• `[Nêu rõ trong bài]` Phân rã chính xác đủ `3.616` dòng (`2.474` ảnh BIMCV và `258 + 182 + 119 = 559` ảnh cụm SIRM/GitHub/Eurorad) tại **`COVID.metadata.xlsx` (cột `URL`)**.<br>• `[Suy ra từ số liệu]` Sự chênh lệch 1 ảnh giữa tổng 4 nguồn trong lời văn P2 (`3.615`) và con số công bố (`3.616`) là do văn bản P2 ghi nguồn BIMCV là `2.473` thay vì `2.474` như trong file `COVID.metadata.xlsx`. |
| **Normal** | **10.192** | Gồm 2 nguồn cộng lại ($8.851 + 1.341 = 10.192$):<br>• `8.851` ảnh từ cuộc thi `RSNA Pneumonia Detection Challenge` (`kaggle.com/c/rsna-pneumonia-detection-challenge/data`)<br>• `1.341` ảnh từ bộ `Chest X-Ray Images (Pneumonia)` của Paul Mooney (`kaggle.com/paultimothymooney/chest-xray-pneumonia`) | • `[Nêu rõ trong bài]` Con số `8.851` ảnh Normal từ RSNA được nêu tại **P2 Abstract (tr. 2), Mục 3.1.4 (tr. 18), Bảng 1 (tr. 20)**; con số `1.341` ảnh Normal từ bộ Kaggle Pneumonia được nêu tại **P1 Mục II.A (tr. 4, cột phải)**.<br>• `[Nêu rõ trong bài]` Phép gộp `10.192 = 8.851 (RSNA) + 1.341 (Kaggle)` được ghi trực tiếp trong **`README.md.txt` (dòng 15–19)** và khớp 100% với cột `URL` của **`Normal.metadata.xlsx`** (`8.851` dòng RSNA + `1.341` dòng Mooney). |
| **Lung_Opacity** | **6.012** | • Toàn bộ `6.012` ảnh lấy từ các ca mờ phổi không do COVID (*non-COVID ground glass lung opacity*) thuộc cuộc thi `RSNA Pneumonia Detection Challenge` | • `[Nêu rõ trong bài]` Nêu trực tiếp tại **P2 Abstract (tr. 2), Mục 3.1.4 (tr. 18), Bảng 1 (tr. 20)**, **`README.md.txt` (dòng 22–24)** và xác nhận 100% (`6.012/6.012` dòng) trong **`Lung_Opacity.metadata.xlsx` (cột `URL`)**. |
| **Viral Pneumonia** | **1.345** | • Toàn bộ `1.345` ảnh lấy từ lớp viêm phổi do virus của bộ dữ liệu Kaggle `Chest X-Ray Images (Pneumonia)` (Paul Mooney) | • `[Nêu rõ trong bài]` Nêu trực tiếp tại **P1 Mục II.A (tr. 4, cột phải)**, **`README.md.txt` (dòng 26–28)**, **`dataset-metadata.json`** và xác nhận 100% (`1.345/1.345` dòng) trong **`Viral Pneumonia.metadata.xlsx` (cột `URL`)**.<br>• `[Suy ra từ số liệu]` Nhiều khả năng toàn bộ `1.345` ảnh này (cùng `1.341` ảnh Normal lấy từ cùng nguồn Mooney) là ảnh X-quang bệnh nhi 1–5 tuổi từ nghiên cứu gốc của Kermany và cộng sự (2018), dù P1 và P2 không ghi trực tiếp độ tuổi bệnh nhi tại mục mô tả dữ liệu. |
| **TỔNG CỘNG** | **21.165** | • `18.479` ảnh thuộc bộ `COVQU` trong P2 (`3.616` COVID + `6.012` Lung Opacity + `8.851` Normal RSNA)<br>• `2.686` ảnh từ bộ Kaggle `Chest X-Ray Images (Pneumonia)` (`1.345` Viral Pneumonia + `1.341` Normal) | • `[Nêu rõ trong bài]` Tổng số `18.479` ảnh của bộ `COVQU` nêu tại **P2 Abstract (tr. 2), Mục 3.1 (tr. 16)**; tổng số `21.165` ảnh của toàn bộ 4 lớp nêu tại **`dataset-metadata.json`**, **`README.md.txt`** và khớp 100% với [`splits/manifest.csv`](../splits/manifest.csv). |

---

### 2.2. Kết quả kiểm tra chi tiết từ Kaggle CLI (Giấy phép & 4 tệp `.metadata.xlsx`)

1. **Giấy phép bộ dữ liệu (Dataset License):**
   - Trong tệp `dataset-metadata.json` lấy qua lệnh `kaggle datasets metadata`, trường `licenses` ghi: **`[{"name": "copyright-authors"}]`** `[Nêu rõ trong bài — dataset-metadata.json]`.
   - Trong phần `description` của `dataset-metadata.json`, nhóm tác giả ghi dòng quy định quyền truy cập và sử dụng: **`DATA ACCESS AND USE: Academic/Non-Commercial Use`** và yêu cầu trích dẫn hai bài báo P1, P2 (trường `licenses` ghi nhãn `[{"name": "copyright-authors"}]`; điều khoản chi tiết chưa xác minh) `[Nêu rõ trong bài — dataset-metadata.json]`.
   - Lưu ý phân biệt: Nhãn `CCBY` xuất hiện trong siêu dữ liệu trang IEEE Xplore của P1 và giấy phép `CC BY 4.0` trên trang arXiv của P2 là **giấy phép bản quyền của bài báo**, không phải giấy phép của bộ ảnh X-quang trên Kaggle.

2. **Cấu trúc cột và nội dung 4 tệp `.metadata.xlsx`:**
   Cả 4 tệp Excel đều có đúng **4 cột**: `['FILE NAME', 'FORMAT', 'SIZE', 'URL']` `[Nêu rõ trong bài — 4 tệp *.metadata.xlsx]`.

| Tệp Metadata trên Kaggle | Dung lượng (Bytes) | Số dòng dữ liệu | Giá trị cột `FORMAT` | Giá trị cột `SIZE` ghi trong Excel | Kích thước ảnh thực tế (`manifest.csv`) | Phân bố cột `URL` (Nguồn ảnh) |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `COVID.metadata.xlsx` | 87.027 | **3.616** | `PNG` (3.616) | `256*256` (3.616) | `299×299` (3.616) | • `bimcv.cipf.es/...`: 2.474<br>• `github.com/armiro/COVID-CXNet`: 400<br>• `eurorad.org`: 258<br>• `github.com/ml-workgroup/...`: 183<br>• `github.com/ieee8023/...`: 182<br>• `sirm.org/...`: 119 |
| `Lung_Opacity.metadata.xlsx` | 141.103 | **6.012** | `PNG` (6.012) | `256*256` (6.012) | `299×299` (6.012) | • `kaggle.com/c/rsna-pneumonia-detection-challenge/data`: 6.012 |
| `Normal.metadata.xlsx` | 234.106 | **10.192** | `PNG` (10.192) | `256*256` (10.192) | `299×299` (10.192) | • `kaggle.com/c/rsna-pneumonia-detection-challenge/data`: 8.851<br>• `kaggle.com/paultimothymooney/chest-xray-pneumonia`: 1.341 |
| `Viral Pneumonia.metadata.xlsx` | 38.215 | **1.345** | `PNG` (1.345) | `256*256` (1.345) | `299×299` (1.345) | • `kaggle.com/paultimothymooney/chest-xray-pneumonia`: 1.345 |
| **TỔNG CỘNG** | **500.451** | **21.165** | **`PNG` (21.165)** | **`256*256` (21.165)** | **`299×299` (21.165)** | **Khớp 100% số lượng từng lớp** |

---

### 2.3. Bảng kiểm tra số học bằng Script và đối chiếu [`splits/manifest.csv`](../splits/manifest.csv)

Kết quả chạy script kiểm tra số học tự động đối chiếu số liệu trong bài báo, tệp `.metadata.xlsx` và [`splits/manifest.csv`](../splits/manifest.csv):

| Hạng mục kiểm tra số học | Phép tính chi tiết | Kết quả tính | Số đối chiếu | Độ lệch & Nhận xét |
| :--- | :--- | :---: | :---: | :--- |
| **1. Tổng 4 nguồn COVID nêu trong lời văn P2 & `README.md.txt`** | $2.473 + 183 + 559 + 400$ | **3.615** | 3.616 | **Lệch $-1$ ảnh** `[Suy ra từ số liệu]`: Lời văn P2 (Mục 3.1.5, tr. 18) ghi nguồn BIMCV là `2.473`, trong khi `COVID.metadata.xlsx` có `2.474` dòng BIMCV ($2.474 + 183 + 559 + 400 = 3.616$). |
| **2. Tổng 5 nguồn COVID của phiên bản đầu trong P1** | $94 + 134 + 60 + 32 + 103$ | **423** | 423 | **Khớp tuyệt đối ($0$)** `[Nêu rõ trong bài — P1 Mục II.A, tr. 3–4]`. |
| **3. Tổng ảnh lớp `Normal` từ RSNA và Kaggle Mooney** | $8.851 + 1.341$ | **10.192** | 10.192 | **Khớp tuyệt đối ($0$)** với `Normal.metadata.xlsx`, `README.md.txt` (dòng 17–19) và `splits/manifest.csv`. |
| **4. Tổng ảnh bộ `COVQU` (3 lớp trong P2)** | $3.616 + 6.012 + 8.851$ | **18.479** | 18.479 | **Khớp tuyệt đối ($0$)** với P2 Abstract (tr. 2), Mục 3.1 (tr. 16) và Bảng 1 (tr. 20). |
| **5. Tổng toàn bộ dataset (`COVQU` + phần từ Kaggle Mooney)** | $18.479 + 1.345 + 1.341$ | **21.165** | 21.165 | **Khớp tuyệt đối ($0$)**; phần chênh lệch $21.165 - 18.479 = 2.686$ ảnh chính là $1.345$ ảnh `Viral Pneumonia` + $1.341$ ảnh `Normal` từ bộ Kaggle của Paul Mooney. |
| **6. Đối chiếu số lượng ảnh & mask trong `splits/manifest.csv`** | `COVID`: 3.616<br>`Lung_Opacity`: 6.012<br>`Normal`: 10.192<br>`Viral Pneumonia`: 1.345 | **21.165 ảnh**<br>**21.165 mask** | 21.165 ảnh<br>21.165 mask | **Khớp 100% về số lượng file**; tuy nhiên `mask_match_size = False` trên cả `21.165/21.165` cặp vì ảnh gốc có kích thước `299×299` còn mask có kích thước `256×256`. |

---

### 2.4. Bảng kiểm chứng độc lập các giả thuyết H1 – H6

| Mã | Nội dung điểm cần kiểm tra | Kết luận | Phân loại mức chắc chắn & Vị trí kiểm chứng cụ thể |
| :---: | :--- | :---: | :--- |
| **H1** | `Viral Pneumonia` (`1.345` ảnh) trùng đúng số ảnh viral của bộ Kaggle *"Chest X-Ray Images (Pneumonia)"* nên nhiều khả năng toàn bộ là ảnh bệnh nhi. | **XÁC NHẬN** *(phần số lượng & nguồn Kaggle)* / **SUY RA TỪ NGUỒN GỐC** *(phần bệnh nhi)* | • `[Nêu rõ trong bài]` Con số `1.345` ảnh Viral Pneumonia được lấy từ bộ Kaggle *"Chest X-Ray Images (Pneumonia)"* của P. Mooney (`[67]`) được ghi rõ tại **P1 Mục II.A (tr. 4, cột phải, gạch đầu dòng thứ nhất)**, **`README.md.txt` (dòng 26–28)**, **`dataset-metadata.json`** và **`Viral Pneumonia.metadata.xlsx` (`1.345/1.345` dòng trỏ về URL `paultimothymooney/chest-xray-pneumonia`)**.<br>• `[Suy ra từ số liệu]` Cả P1 và P2 đều **không ghi trực tiếp** tại mục mô tả dữ liệu rằng `1.345` ảnh này là ảnh bệnh nhi (dù ở phần Tổng quan **P1 Mục I, tr. 2, cột phải**, tác giả có trích dẫn bài báo gốc của Kermany và cộng sự `[29]` về chẩn đoán viêm phổi nhi khoa). Vì bộ Kaggle của P. Mooney lấy từ dữ liệu bệnh nhi 1–5 tuổi tại Trung tâm Y tế Phụ nữ và Trẻ em Quảng Châu (Kermany et al., *Cell* 2018), việc suy luận toàn bộ lớp `Viral Pneumonia` là ảnh bệnh nhi có cơ sở rất mạnh từ nguồn dữ liệu gốc nhưng thuộc diện **suy ra ngoài văn bản P1/P2**. |
| **H2** | `Normal` `10.192` = `8.851` (RSNA) + `1.341` (ảnh normal của bộ Kaggle nói trên). | **XÁC NHẬN** | • `[Nêu rõ trong bài]` **P2 Abstract (tr. 2), Mục 3.1.4 (tr. 18) và Bảng 1 (tr. 20)** nêu rõ lấy `8.851` ảnh Normal từ RSNA; **P1 Mục II.A (tr. 4, cột phải)** nêu rõ bộ Kaggle *"Chest X-Ray Images (Pneumonia)"* có `1.341` ảnh Normal.<br>• `[Nêu rõ trong bài]` Tệp **`README.md.txt` (dòng 15–19)** và **`Normal.metadata.xlsx`** trên Kaggle xác nhận trực tiếp lớp `Normal` (`10.192` dòng) gồm đúng `8.851` dòng có URL `rsna-pneumonia-detection-challenge` và `1.341` dòng có URL `paultimothymooney/chest-xray-pneumonia` ($8.851 + 1.341 = 10.192$). |
| **H3** | `Lung Opacity` `6.012` và phần lớn `Normal` đến từ RSNA. `COVID-19` `3.616` gồm `BIMCV-COVID19+` `2.473`, một kho của trường y Đức `183`, `SIRM/GitHub/Kaggle/Twitter` `559`, một kho khác `400`; tổng các nguồn là `3.615`, không phải `3.616`. | **XÁC NHẬN** | • `[Nêu rõ trong bài]` **P2 Mục 3.1.4 (tr. 18) và Bảng 1 (tr. 20)** nêu rõ `6.012` ảnh non-COVID lung opacity và `8.851` ảnh Normal được lấy từ bộ `RSNA Pneumonia Detection Challenge` `[66]`.<br>• `[Nêu rõ trong bài]` **P2 Mục 3.1.5 (tr. 18–19)** và **`README.md.txt` (dòng 8–12)** liệt kê `3.616` ảnh COVID-19 gồm: `2.473` ảnh từ `BIMCV-COVID19+` `[67]`, `183` ảnh từ một trường y tại Đức `[68]`, `559` ảnh từ `SIRM, GitHub, Kaggle & Twitter` `[69–72]`, và `400` ảnh từ một kho COVID-19 CXR khác `[73]`.<br>• `[Suy ra từ số liệu]` Phép cộng 4 con số nêu trong lời văn P2 là $2.473 + 183 + 559 + 400 = 3.615 \neq 3.616$ (thiếu 1 ảnh). Đối chiếu với **`COVID.metadata.xlsx`** cho thấy nguồn `BIMCV-COVID19+` thực tế có **`2.474` dòng** ($2.474 + 183 + 559 + 400 = 3.616$). |
| **H4** | P2 nói `18.479` ảnh thuộc khoảng `15.000` bệnh nhân; P1 và P2 chia theo ảnh (5-fold), không theo bệnh nhân. | **XÁC NHẬN** | • `[Nêu rõ trong bài]` **P2 Mục 3.1 (tr. 16) và Mục 3.1.2 (tr. 17)** ghi rõ bộ dữ liệu `COVQU` gồm `18.479` ảnh CXR thuộc `15.000` ca bệnh nhân (*across 15,000 patient cases*).<br>• `[Nêu rõ trong bài]` **P1 Mục II.B (tr. 5) & Bảng 1 (tr. 5)** và **P2 Mục 3.2 (tr. 20) & Bảng 1 (tr. 20)** đều mô tả quy trình chia `5-fold cross-validation` (80% train / 20% test) dựa thuần túy trên số lượng ảnh của từng lớp (*Count of CXR's/class*), không có bất kỳ bước gom nhóm hay tách tập theo mã định danh bệnh nhân (`patient_id`) nào. |
| **H5** | P2 tự mâu thuẫn về nguồn mask (mask chuẩn do bác sĩ kiểm cho `18.479` ảnh, hay mask sinh bằng U-Net vì không có mask chuẩn); `2.686` ảnh còn lại ($18.479 + 2.686 = 21.165$) không được mô tả. | **XÁC NHẬN** | • `[Nêu rõ trong bài]` **Mâu thuẫn trong P2:** Tại **Mục 3.1.1 (tr. 17) và Mục 3.2.1 (tr. 21)**, P2 viết rằng nhóm tác giả đã tạo mặt nạ phổi chuẩn (*ground truth lung masks*) cho `18.479` ảnh CXR được bác sĩ chẩn đoán hình ảnh kiểm duyệt để huấn luyện (80%) và kiểm thử (20%) mạng Modified U-Net. Thế nhưng tại **Mục 4.1 (tr. 23–24) và Hình 7 (tr. 24)**, P2 lại viết rằng mạng Modified U-Net được đem đi phân đoạn bộ dữ liệu phân loại (gọi là tập hoàn toàn chưa từng thấy) và **không thể đánh giá định lượng trên bộ phân loại vì không có ground truth mask**, nên chỉ kiểm tra định tính bằng mắt.<br>• `[Suy ra từ số liệu]` Phần chênh lệch $21.165 - 18.479 = 2.686$ ảnh (`1.345` Viral Pneumonia + `1.341` Normal từ Kaggle Mooney) hoàn toàn không xuất hiện trong P2 và P1 cũng không dùng lung mask, nên quy trình tạo mask cho `2.686` ảnh này không được mô tả trong cả hai bài báo. |
| **H6** | P2: Score-CAM cho thấy quyết định trên ảnh gốc không luôn nằm trong phổi; ảnh cắt phổi làm độ chính xác giảm nhẹ (`96,29%` xuống `95,11%`). | **XÁC NHẬN** | • `[Nêu rõ trong bài]` Tại **P2 Mục 4.3 (tr. 28–29) và Hình 10 (tr. 28)**, tác giả nhận xét từ bản đồ nhiệt Score-CAM rằng trên ảnh X-quang gốc chưa cắt phổi, vùng đóng góp chính cho quyết định của mạng CNN không phải lúc nào cũng nằm trong vùng phổi (thậm chí trong đa số trường hợp nằm ngoài vùng phổi).<br>• `[Nêu rõ trong bài]` Tại **P2 Abstract (tr. 2), Bảng 3–4 (tr. 25), Bảng 5–6 (tr. 26–27) và Mục 5 (tr. 30)**, mô hình tốt nhất trên ảnh gốc tăng cường Gamma (CheXNet) đạt độ chính xác `96,29%`, còn khi chuyển sang ảnh đã cắt tách vùng phổi tăng cường Gamma (DenseNet201) thì độ chính xác giảm nhẹ xuống `95,11%`, đổi lại vùng chú ý Score-CAM tập trung đúng vào nhu mô phổi. |

---

## 3. Quy trình Gán nhãn, Mặt nạ Phổi (Lung Mask), Thiết bị và Độ tuổi

### 3.1. Cách gán nhãn bệnh lý cho từng lớp
- **Lớp `COVID-19` (`3.616` ảnh):** Được tổng hợp từ các kho dữ liệu công khai và bài báo khoa học (`BIMCV-COVID19+`, trường y tại Đức, `SIRM`, `GitHub ieee8023`, `Eurorad`, `COVID-CXNet`) `[Nêu rõ trong bài — P2 Mục 3.1.5 tr. 18; COVID.metadata.xlsx]`. Trong P1, tác giả ghi nhận một nguồn con tại Tây Ban Nha (`103` ảnh từ Thread Reader) là các ca dương tính `SARS-CoV-2 PCR+` `[Nêu rõ trong bài — P1 Mục II.A tr. 4 & Tài liệu tham khảo [65] tr. 12]`, và tại Mục III.B (tr. 9–10) có 3 bác sĩ chẩn đoán hình ảnh đánh giá lại 3 ảnh COVID-19 bị mô hình phân loại nhầm. Tuy nhiên, đối với toàn bộ `3.616` ảnh ở P2, bài báo **không mô tả quy trình tái thẩm định nhãn độc lập hay tiêu chuẩn vàng đồng nhất (RT-PCR hay CT) cho từng ảnh thành phần** mà kế thừa trực tiếp nhãn từ các kho nguồn `[Chưa xác minh]`.
- **Lớp `Normal` (`10.192` ảnh) và `Lung_Opacity` (`6.012` ảnh):** Kế thừa trực tiếp nhãn từ cuộc thi `RSNA Pneumonia Detection Challenge` (`8.851` ảnh Normal và `6.012` ảnh Non-COVID Lung Opacity) và từ bộ Kaggle `Chest X-Ray Images (Pneumonia)` (`1.341` ảnh Normal) `[Nêu rõ trong bài — P2 Mục 3.1.4 tr. 18; README.md.txt dòng 15–25]`.
- **Lớp `Viral Pneumonia` (`1.345` ảnh):** Kế thừa trực tiếp nhãn từ nhánh viêm phổi do virus của bộ Kaggle `Chest X-Ray Images (Pneumonia)` `[Nêu rõ trong bài — P1 Mục II.A tr. 4; README.md.txt dòng 26–28]`.

### 3.2. Nguồn gốc và đặc điểm kỹ thuật của Mặt nạ Phổi (Lung Masks)
- **Kiến trúc sinh mask trong P2:** Sử dụng mạng **Modified U-Net** gồm 4 khối mã hóa (encoding blocks) và 4 khối giải mã (decoding blocks) với đầu vào kích thước **`256×256` điểm ảnh**, huấn luyện bằng bộ tối ưu Adam (`lr = 0.001`, `batch_size = 4`, tối đa `20` epochs) `[Nêu rõ trong bài — P2 Mục 2.2 & Hình 1 tr. 9; Mục 3.2 tr. 19; Mục 3.2.1 tr. 21]`.
- **Mâu thuẫn về dữ liệu gốc dùng để tạo mask:** Như đã phân tích tại **H5**, P2 tự mâu thuẫn giữa **Mục 3.1.1 (tr. 17) / Mục 3.2.1 (tr. 21)** (khẳng định có `18.479` mask chuẩn do bác sĩ X-quang kiểm duyệt để train/test U-Net) và **Mục 4.1 (tr. 23–24) / Hình 7 (tr. 24)** (khẳng định bộ dữ liệu phân loại không có mask chuẩn nên phải dùng mạng U-Net đã huấn luyện để tự sinh mask rồi kiểm tra định tính bằng mắt) `[Nêu rõ trong bài — P2 tr. 17, 21, 23, 24]`.
- **Khoảng trống thông tin về `2.686` mask còn lại:** Trên Kaggle, cả 4 lớp đều có thư mục `masks/` với tổng cộng `21.165` file PNG khớp 1-1 với `21.165` ảnh X-quang `[Nêu rõ trong bài — outputs/setup_check/setup_report.json & splits/manifest.csv]`. Tuy nhiên, nguồn gốc mặt nạ phổi của `2.686` ảnh ngoài bộ `COVQU` (`1.345` ảnh `Viral Pneumonia` và `1.341` ảnh `Normal` từ bộ Kaggle Mooney) không được đề cập trong P1, P2 hay `README.md.txt` `[Chưa xác minh]`.
- **Độ phân giải thực tế của ảnh và mask:**
  - Tệp `README.md.txt` (dòng 47) và `dataset-metadata.json` ghi tất cả ảnh có định dạng `PNG` và độ phân giải `299×299` pixels `[Nêu rõ trong bài — README.md.txt dòng 47]`.
  - Ngược lại, cả 4 tệp `*.metadata.xlsx` đều ghi cột `SIZE` là `256*256` cho toàn bộ `21.165` dòng `[Nêu rõ trong bài — 4 tệp *.metadata.xlsx]`.
  - Kiểm tra thực tế trong [`splits/manifest.csv`](../splits/manifest.csv) (do notebook `01_download_and_eda.ipynb` quét trực tiếp trên Kaggle): 100% ảnh X-quang (`21.165/21.165` ảnh) có kích thước **`299×299`**, trong khi 100% mặt nạ phổi (`21.165/21.165` mask) có `mask_match_size = False` (kích thước **`256×256`**, đúng bằng kích thước đầu ra của mạng Modified U-Net ở P2 Hình 1 tr. 9) `[Suy ra từ số liệu — splits/manifest.csv & P2 tr. 9, 19]`.

### 3.3. Thiết bị chụp, Tư thế chụp và Nhân khẩu học (Độ tuổi / Giới tính)
- **Tư thế chụp:** P1 nêu rằng bộ dữ liệu sử dụng ảnh X-quang ngực tư thế sau-trước (PA) hoặc trước-sau (AP) `[Nêu rõ trong bài — P1 Mục II.A tr. 3]`.
- **Thiết bị chụp:** P2 chỉ nêu thông tin thiết bị cho duy nhất nguồn `BIMCV-COVID19+` (`2.473` ảnh trong lời văn / `2.474` dòng trong Excel) là được thu nhận từ máy X-quang kỹ thuật số (*digital X-ray - DX*) và X-quang điện toán (*computerized X-ray - CX*) `[Nêu rõ trong bài — P2 Mục 3.1.5 tr. 18–19]`. P1 (Mục II.A tr. 4) chỉ ghi nhận rằng ảnh từ các nguồn có độ phân giải gốc rất khác nhau (ví dụ bộ Kaggle Pneumonia dao động từ `400p` đến `2000p`) tùy thuộc vào máy chụp. Toàn bộ các nguồn còn lại không có thông tin cụ thể về hãng sản xuất máy chụp, bệnh viện hay thông số tia X `[Chưa xác minh]`.
- **Độ tuổi và giới tính bệnh nhân:** Cả P1, P2 và 4 tệp `*.metadata.xlsx` trên Kaggle đều **không cung cấp cột tuổi, giới tính hay mã bệnh nhân (`patient_id`)** `[Chưa xác minh]`. Sự khác biệt về lứa tuổi (bệnh nhi ở nguồn Kaggle Mooney so với người trưởng thành ở nguồn RSNA/BIMCV) được suy ra từ nguồn gốc bộ dữ liệu thành phần `[Suy ra từ số liệu]`.

---

## 4. Bảng So sánh Quy trình Thực nghiệm của Paper (P1, P2) và của Nhóm

| Tiêu chí so sánh | Bài báo P1 (Chowdhury et al., 2020) | Bài báo P2 (Rahman et al., 2021) | Quy trình Đồ án của Nhóm (`origin/main`) |
| :--- | :--- | :--- | :--- |
| **Bài toán & Số lớp** | • Kịch bản 1: 2 lớp (`COVID-19` vs `Normal`)<br>• Kịch bản 2: 3 lớp (`COVID-19`, `Normal`, `Viral Pneumonia`)<br>`[Nêu rõ trong bài — P1 Mục II.A–B tr. 3–5]` | • Phân loại 3 lớp (`COVID-19`, `Non-COVID Lung Opacity`, `Normal`) trên ảnh gốc và ảnh đã cắt vùng phổi.<br>`[Nêu rõ trong bài — P2 Mục 3 tr. 15–16]` | • Phân loại **4 lớp** (`COVID`, `Lung_Opacity`, `Normal`, `Viral Pneumonia`).<br>`[Theo README.md & src/dataset.py]` |
| **Quy mô dữ liệu sử dụng** | Tổng `3.487` ảnh (`423` COVID-19, `1.579` Normal, `1.485` Viral Pneumonia).<br>`[Nêu rõ trong bài — P1 Bảng 1 tr. 5]` | Tổng `18.479` ảnh thuộc bộ `COVQU` (`3.616` COVID-19, `6.012` Lung Opacity, `8.851` Normal).<br>`[Nêu rõ trong bài — P2 Bảng 1 tr. 20]` | Tổng **`21.165` ảnh** (`3.616` COVID, `6.012` Lung Opacity, `10.192` Normal, `1.345` Viral Pneumonia).<br>`[Theo splits/manifest.csv]` |
| **Khử trùng lặp & Gom nhóm** | Chỉ nêu đã đối chiếu thủ công các ảnh thu thập từ bài báo với kho GitHub của Cohen để tránh trùng lặp khi tạo bộ dữ liệu; không lọc trùng bằng hàm băm trên toàn bộ các lớp.<br>`[Nêu rõ trong bài — P1 Mục II.A tr. 4]` | Không đề cập bước khử trùng lặp bằng hàm băm giữa các nguồn.<br>`[Chưa xác minh]` | Quét `MD5` và `pHash` 64-bit DCT toàn bộ `21.165` ảnh; gom cụm `Union-Find` ở ngưỡng $T=0$ (`178` nhóm, `401` ảnh) giữ cùng một split; ghi nhận giới hạn `735` cặp gần trùng $1 \le D \le 4$ khác split.<br>`[Theo splits/README.md]` |
| **Chiến lược chia dữ liệu & Quản lý tập Test** | Stratified `5-fold cross-validation` theo **số lượng ảnh** (80% train / 20% test; trích 10% của tập train làm validation). Cộng dồn kết quả cả 5 fold test.<br>`[Nêu rõ trong bài — P1 Mục II.B & E tr. 5–6]` | `5-fold cross-validation` theo **số lượng ảnh** (80% train / 20% test; trích 20% của tập train làm validation, tức tỷ lệ 64% train / 16% val / 20% test mỗi fold). Không chia theo `patient_id` dù nêu có `15.000` bệnh nhân.<br>`[Nêu rõ trong bài — P2 Mục 3.1 tr. 16 & Mục 3.2 tr. 20]` | Chia cố định 1 lần bằng `StratifiedGroupKFold` theo tỷ lệ **70% Train (`14.815`) / 15% Val (`3.174`) / 15% Test (`3.176`)** tại [`splits/split_v1.csv`](../splits/split_v1.csv). Khóa cứng tập Test bằng mã SHA256, tag `test-locked` và cờ `allow_test=False`; chỉ mở tập Test đúng 1 lần ở Tuần 10.<br>`[Theo splits/README.md & src/dataset.py]` |
| **Tiền xử lý & Tăng cường chất lượng ảnh** | Resize theo kiến trúc mạng (`227×227` cho SqueezeNet, `299×299` cho InceptionV3, `224×224` cho các mạng còn lại) và chuẩn hóa theo chuẩn mô hình pretrained.<br>`[Nêu rõ trong bài — P1 Mục II.B tr. 5]` | Resize (`256×256` cho U-Net, `299×299` cho InceptionV3, `224×224` cho các mạng khác), chuẩn hóa Z-score. Khảo sát 5 phép biến đổi nâng cao chất lượng ảnh: `HE`, `CLAHE`, `Complement`, `Gamma correction`, `BCET`.<br>`[Nêu rõ trong bài — P2 Mục 2.3 tr. 10–14 & Mục 3.2 tr. 19]` | ảnh xám 8-bit 299x299, không resize, không chuẩn hoá theo ImageNet.<br>[Theo results/threshold_v3.md mục 1] |
| **Data Augmentation & Xử lý mất cân bằng lớp** | Nhân bản trước/trong mỗi fold để cân bằng lớp: ở Study 2, ảnh train lớp COVID-19 (`304` ảnh/fold) được tăng cường 6 lần lên `2.128` ảnh/fold bằng xoay $\pm 5^\circ, \pm 10^\circ, \pm 15^\circ$ và dịch chuyển ngang/dọc $\pm 5\%$; lớp Normal và Viral Pneumonia chỉ dịch chuyển 1 lần.<br>`[Nêu rõ trong bài — P1 Bảng 1 & Mục II.C tr. 5]` | Nhân đôi số ảnh train của lớp COVID-19 trong mỗi fold từ `2.314` lên `4.628` ảnh bằng phép xoay ảnh (*image rotation*) để giảm chênh lệch với lớp Normal (`5.664` ảnh/fold); hai lớp còn lại giữ nguyên số lượng.<br>`[Nêu rõ trong bài — P2 Mục 3.2.1 & Bảng 1 tr. 19–20]` | RQ2: so sánh 6 bộ phân loại (Logistic Regression, k-NN, Decision Tree, Random Forest, SVM, Gradient Boosting); trọng số lớp theo H3 của threshold_v3.<br>[Theo results/threshold_v3.md mục 1 và H3] |
| **Kiến trúc CNN khảo sát** | 8 mạng: `MobileNetV2`, `SqueezeNet`, `ResNet18`, `ResNet101`, `DenseNet201` (chạy trên MATLAB 2020a) và `CheXNet`, `InceptionV3`, `VGG19` (chạy trên PyTorch).<br>`[Nêu rõ trong bài — P1 Mục II.B tr. 4]` | 6 mạng trên PyTorch: `ResNet18`, `ResNet50`, `ResNet101`, `InceptionV3`, `DenseNet201`, `CheXNet` (kèm `Modified U-Net` cho phân đoạn phổi).<br>`[Nêu rõ trong bài — P2 Mục 3.2.2 tr. 21]` | RQ1: so sánh 4 nhóm đặc trưng thủ công (histogram, GLCM + LBP, HOG, ghép) với Random Forest cố định, 3 seed 42/43/44.<br>[Theo results/threshold_v3.md mục 1; docs/roadmap.md S3-04] |
| **Siêu tham số huấn luyện** | Bộ tối ưu `SGD` với `momentum = 0.9`, `lr = 0.001`, `batch_size = 16`, `20` epochs.<br>`[Nêu rõ trong bài — P1 Mục II.B tr. 4]` | Bộ tối ưu `Adam`, `lr = 0.001`, `batch_size = 32` (`batch_size = 4` cho U-Net), tối đa `20` epochs, giảm `lr` nếu 3 epochs liên tiếp không cải thiện và dừng sớm sau 6 epochs.<br>`[Nêu rõ trong bài — P2 Mục 3.2.1–3.2.2 tr. 21]` | chạy trên CPU; mỗi run lưu results/<run_id>/{config.yaml, metrics.json, log, preds_val.csv}.<br>[Theo results/threshold_v3.md H1] |
| **Chỉ số đánh giá chính** | `Overall Accuracy` và các chỉ số **trung bình có trọng số (`Weighted Average`)** cho Precision, Sensitivity/Recall, F1-score, Specificity cùng đường cong ROC/AUC.<br>`[Nêu rõ trong bài — P1 Mục II.E tr. 6 & Bảng 2–3 tr. 7–8]` | `Overall Accuracy`, **Weighted** Sensitivity/Recall, Specificity, Precision, F1-score, AUC và thời gian suy luận mỗi ảnh $\delta t$.<br>`[Nêu rõ trong bài — P2 Mục 3.3.2 tr. 22–23]` | **`Macro-F1`** (thước đo chính chọn mô hình, đối xử bình đẳng với lớp thiểu số `Viral Pneumonia`), kèm `Balanced Accuracy`, `Per-class Recall/Precision/F1` và ma trận nhầm lẫn.<br>`[Theo src/metrics.py & docs/roadmap.md]` |
| **Giải thích mô hình & Kiểm tra Shortcut Learning** | Trực quan hóa bản đồ kích hoạt (*feature activation maps*) ở tầng tích chập thứ 1, 14 và 29 của `DenseNet201`.<br>`[Nêu rõ trong bài — P1 Mục II.D tr. 6 & Hình 8 tr. 9]` | Dùng **Score-CAM** so sánh vùng quyết định trên ảnh gốc và ảnh đã cắt vùng phổi bằng U-Net.<br>`[Nêu rõ trong bài — P2 Mục 2.4 tr. 15 & Mục 4.3 tr. 27–29]` | RQ3: đánh giá trên 3 chế độ ảnh (ảnh gốc, chỉ trong phổi, chỉ ngoài phổi) và permutation importance.<br>[Theo results/threshold_v3.md R3; docs/roadmap.md S4-07, S5-01, S5-02] |

---

## 5. Kết quả Thực nghiệm của Paper (Chỉ dùng làm Bối cảnh Tham khảo)

> [!IMPORTANT]
> **TUYÊN BỐ PHƯƠNG PHÁP LUẬN:** Toàn bộ số liệu hiệu năng của P1 và P2 dưới đây chỉ được trích lục để làm bối cảnh học thuật. Nhóm **tuyệt đối không sử dụng các con số này làm ngưỡng chấp nhận tối thiểu hay mục tiêu hiệu năng cho đồ án**, bởi vì bài toán, cách chia dữ liệu và thước đo đánh giá của hai bài báo khác biệt căn bản so với thiết kế chống rò rỉ của nhóm.

### 5.1. Tóm tắt kết quả công bố trong P1 và P2
- **Trong P1 (`arXiv:2003.13145v3`):**
  - **Bài toán 2 lớp (`COVID-19` vs `Normal`, `423` vs `1.579` ảnh):** Khi có tăng cường dữ liệu, mạng `DenseNet201` đạt kết quả trung bình trọng số cao nhất với `Accuracy = 99,70%`, `Precision = 99,70%`, `Sensitivity = 99,70%`, `F1-score = 99,70%`, `Specificity = 99,55%` (khi không tăng cường dữ liệu, `CheXNet` và `ResNet18` đạt `Accuracy = 99,41%`) `[Nêu rõ trong bài — P1 Bảng 2 tr. 7]`.
  - **Bài toán 3 lớp (`COVID-19`, `Normal`, `Viral Pneumonia`, tổng `3.487` ảnh):** Khi có tăng cường dữ liệu, `DenseNet201` dẫn đầu với `Accuracy = 97,94%`, `Precision = 97,95%`, `Sensitivity = 97,94%`, `F1-score = 97,94%`, `Specificity = 98,80%` (khi không tăng cường dữ liệu, `CheXNet` cao nhất với `Accuracy = 97,74%`, `F1-score = 96,61%`) `[Nêu rõ trong bài — P1 Bảng 3 tr. 8]`.
- **Trong P2 (`arXiv:2012.02238v1`):**
  - **Phân đoạn phổi (Modified U-Net trên 5-fold CV):** Đạt `Accuracy = 98,63%`, `IoU = 94,3%`, `Dice = 96,94%` `[Nêu rõ trong bài — P2 Bảng 2 tr. 23]`.
  - **Phân loại 3 lớp trên ảnh X-quang gốc chưa cắt phổi (`18.479` ảnh):** Phép biến đổi `Gamma correction` kết hợp mạng `CheXNet` đạt kết quả cao nhất với `Overall Accuracy = 96,29%`, `Weighted Precision = 96,28%`, `Weighted Recall = 96,29%`, `Weighted F1-score = 96,28%`, `Weighted Specificity = 97,27%` (so với ảnh gốc không tăng cường tương phản tốt nhất là `InceptionV3` đạt `Accuracy = 93,46%`, `F1-score = 93,47%`) `[Nêu rõ trong bài — P2 Bảng 3 & Bảng 4 tr. 25]`.
  - **Phân loại 3 lớp trên ảnh đã cắt vùng phổi (`Segmented Lungs`, `18.479` ảnh):** Phép biến đổi `Gamma correction` kết hợp mạng `DenseNet201` đạt kết quả cao nhất với `Overall Accuracy = 95,11%`, `Weighted Precision = 94,55%`, `Weighted Recall = 94,56%`, `Weighted F1-score = 94,53%`, `Weighted Specificity = 95,59%` (so với ảnh cắt phổi không tăng cường tương phản tốt nhất là `CheXNet` đạt `Accuracy = 93,22%`) `[Nêu rõ trong bài — P2 Bảng 5 & Bảng 6 tr. 26–27]`.

### 5.2. Năm lý do không thể so sánh trực tiếp số liệu của Paper với Đồ án của nhóm
1. **Khác số lượng lớp phân loại:** Cả P1 (2 hoặc 3 lớp, chưa có lớp `Lung_Opacity`) và P2 (3 lớp, bỏ qua lớp `Viral Pneumonia` và `1.341` ảnh `Normal` từ bộ Kaggle Mooney) đều không giải bài toán **4 lớp đầy đủ (`21.165` ảnh)** như đồ án của nhóm `[Suy ra từ số liệu]`.
2. **Chia dữ liệu theo ảnh, không lọc trùng pHash và không tách theo bệnh nhân:** P2 tự nêu `18.479` ảnh thuộc khoảng `15.000` bệnh nhân nhưng lại chia `5-fold` theo ảnh; đồng thời trong bộ dữ liệu tồn tại `178` nhóm trùng khít `pHash` ($T=0$, gồm `401` ảnh). Việc chia ngẫu nhiên theo ảnh khiến các ảnh trùng lặp hoặc chụp cùng một bệnh nhân rơi vào cả tập train lẫn tập test của từng fold, làm điểm số test bị thổi phồng `[Suy ra từ số liệu — P2 tr. 16, 20 & splits/README.md]`.
3. **Khác biệt giữa `Weighted F1` và `Macro-F1`:** P1 và P2 dùng trung bình có trọng số (`Weighted Average`), trong đó lớp đa số (`Normal` chiếm gần metà bộ dữ liệu) chi phối điểm tổng. Ngược lại, nhóm dùng **`Macro-F1`** tính trung bình cộng ngang bằng giữa cả 4 lớp (lớp nhỏ nhất `Viral Pneumonia` chỉ có `1.345` ảnh vẫn chiếm đúng 25% trọng số điểm) `[Theo src/metrics.py & P2 tr. 22]`.
4. **Hiệu ứng Shortcut Learning trên ảnh gốc:** Chính P2 (Mục 4.3, tr. 28) đã chứng minh bằng Score-CAM rằng kết quả `96,29%` trên ảnh gốc có sự đóng góp lớn từ các vùng nằm ngoài phổi; khi cắt bỏ nền ngoài phổi, độ chính xác giảm xuống `95,11%` `[Nêu rõ trong bài — P2 tr. 28]`.
5. **Khác biệt về kiểm soát tập Test:** P1 và P2 báo cáo trung bình cộng 5 fold test cho hàng chục tổ hợp mô hình × kỹ thuật tiền xử lý mà không tách riêng một tập test khóa kín đánh giá một lần duy nhất như [`splits/split_v1.csv`](../splits/split_v1.csv) của nhóm `[Suy ra từ số liệu]`.

### 5.3. Hạn chế do chính nhóm tác giả tự nêu trong P1 và P2
- **Tại P1 (Mục III.B, tr. 9–10 & Hình 9, tr. 10):** Tác giả nêu rõ mạng học sâu gặp thất bại trên các ca COVID-19 giai đoạn rất nhẹ hoặc mới khởi phát khi vùng mờ ở thùy trên hai phổi rất ít, hình ảnh tương tự như phổi bình thường (2 trong 3 ảnh COVID-19 bị mô hình đoán nhầm thành Normal cũng được 3 bác sĩ chẩn đoán hình ảnh nhận định là không có dấu hiệu hoặc dấu hiệu rất mờ nhạt trên X-quang và cần xác nhận bằng phương pháp khác). Ngoài ra, tác giả cũng nêu sự biến thiên lớn của ảnh đầu vào do khác biệt về máy chụp và kỹ năng kỹ thuật viên `[Nêu rõ trong bài — P1 tr. 9–10]`.
- **Tại P2 (Mục 4.1 tr. 24 & Mục 4.3 tr. 28–29):** Tác giả thừa nhận hạn chế không có mặt nạ phổi chuẩn cho bộ phân loại để đánh giá định lượng độ chính xác phân đoạn (tr. 24), và chỉ ra rằng mô hình phân loại trên ảnh X-quang nguyên bản thường xuyên nhìn vào vùng ngoài phổi để ra quyết định (tr. 28) `[Nêu rõ trong bài — P2 tr. 24, 28]`.

---

## 6. Tổng hợp các Mâu thuẫn Nội tại trong Paper và Metadata Kaggle

Quá trình đối chiếu chéo giữa P1, P2, các tệp metadata trên Kaggle và dữ liệu thực tế ghi nhận **7 điểm mâu thuẫn / bất nhất** cần lưu ý khi viết báo cáo:

1. **Mâu thuẫn về sự tồn tại của Ground Truth Lung Masks trong P2:**
   - Tại **P2 Mục 3.1.1 (tr. 17) và Mục 3.2.1 (tr. 21)**: Khẳng định nhóm tác giả đã tạo mặt nạ phổi chuẩn (*ground truth lung masks*) cho toàn bộ `18.479` ảnh CXR có bác sĩ chuyên khoa kiểm duyệt và dùng 80% để huấn luyện, 20% để kiểm thử mạng Modified U-Net.
   - Tại **P2 Mục 4.1 (tr. 23–24) và Hình 7 (tr. 24)**: Lại khẳng định mạng Modified U-Net được đem áp dụng lên bộ dữ liệu phân loại (gọi là tập hoàn toàn chưa từng thấy) và **không thể đánh giá định lượng trên bộ dữ liệu này vì không có ground truth masks**, chỉ có thể đánh giá định tính bằng mắt `[Nêu rõ trong bài — P2 tr. 17, 21, 23, 24]`.

2. **Lệch tổng số ảnh COVID-19 giữa lời văn P2 (`3.615`) và con số công bố (`3.616`):**
   - Tại **P2 Mục 3.1.5 (tr. 18)** và **`README.md.txt` (dòng 8–12)**: Ghi tổng số ảnh COVID-19 là `3.616`, nhưng 4 nguồn thành phần liệt kê ngay sau đó ($2.473 + 183 + 559 + 400$) chỉ cộng được **`3.615`**.
   - Đối chiếu **`COVID.metadata.xlsx`**: Nguồn `BIMCV-COVID19+` thực tế có **`2.474` dòng** (không phải `2.473`), giúp tổng thực tế đạt đúng `3.616` `[Nêu rõ trong bài — P2 tr. 18 & COVID.metadata.xlsx]`.

3. **Ghi nhầm số lượng ảnh COVID-19 thành `3.416` và tên bộ `BIMCV` thành `padchest`:**
   - Tại **P2 Mục 4.1 (tr. 23)**: Tác giả ghi bộ dữ liệu phân loại gồm `8.851` normal, `6.012` lung opacity và **`3.416`** COVID images (lệch thiếu 200 ảnh so với con số `3.616` ở Bảng 1 tr. 20) `[Nêu rõ trong bài — P2 tr. 20, 23]`.
   - Tại **`README.md.txt` (dòng 9)** và **`dataset-metadata.json` (mục Acknowledgments)**: Tác giả gọi nguồn `[1]` (`2.473` ảnh COVID-19) là *"padchest dataset"*, dù đường dẫn `[1]` trỏ trực tiếp tới dự án `BIMCV-COVID19+` `[Nêu rõ trong bài — README.md.txt dòng 9, 35]`.
   - Tại **`README.md.txt` (dòng 17–19)**: Ghi `10.192` ảnh Normal được thu thập từ **"ba"** bộ dữ liệu khác nhau (*three different dataset*), nhưng bên dưới chỉ liệt kê đúng **2** nguồn (`8.851` RSNA và `1.341` Kaggle) `[Nêu rõ trong bài — README.md.txt dòng 17–19]`.

4. **Bất nhất về thông số kích thước ảnh (`256×256` vs `299×299`):**
   - Trong `README.md.txt` (dòng 47) và `dataset-metadata.json`, tác giả ghi toàn bộ ảnh là file `PNG` kích thước **`299×299`**.
   - Trong cả 4 tệp `*.metadata.xlsx`, cột `SIZE` lại ghi **`256*256`** cho toàn bộ `21.165` dòng.
   - Thực tế kiểm tra trong [`splits/manifest.csv`](../splits/manifest.csv): toàn bộ `21.165` ảnh trong thư mục `images/` có kích thước **`299×299`**, còn toàn bộ `21.165` mặt nạ phổi trong thư mục `masks/` có kích thước **`256×256`** `[Nêu rõ trong bài — README.md.txt, *.metadata.xlsx & splits/manifest.csv]`.

5. **Lệch số liệu nhỏ giữa Abstract / Kết luận và các Bảng kết quả trong P2:**
   - Với ảnh gốc + Gamma (CheXNet): **Bảng 3 & 4 (tr. 25)** ghi `Specificity = 97,27%`, nhưng **Abstract (tr. 2)** ghi `96,27%`; **Bảng 3 & 4 (tr. 25)** ghi `Recall = 96,29%`, nhưng **Conclusion (tr. 30)** ghi `96,28%`.
   - Với ảnh cắt phổi + Gamma (DenseNet201): **Abstract (tr. 2) và Bảng 5 & 6 (tr. 26–27)** ghi `F1-score = 94,53%`, nhưng câu văn cuối **trang 27** ghi `F1-score = 94,56%` `[Nêu rõ trong bài — P2 tr. 2, 25, 26, 27, 30]`.

6. **Lỗi biên tập mục lục và trích dẫn trong bản preprint P1 và P2:**
   - Trong **P2**: Mục `2.1` (tr. 8) viết có *"chín"* mạng CNN pretrained nhưng chỉ liệt kê 6 mạng; hai mục liên tiếp (`3.1.2` và `3.1.3`, tr. 17–18) bị nhân đôi nguyên văn cùng tiêu đề *"Image Classification"*; đánh số trùng hai mục `3.2`, hai mục `3.2.1` (tr. 19–20) và hai hình cùng mang số `Figure 2` (tr. 14–15) `[Nêu rõ trong bài — P2 tr. 8, 14–20]`.
   - Trong **P1**: Tại **Mục II.A (tr. 4)**, tác giả mô tả cuộc thi *RSNA-Pneumonia-Detection-Challenge (2018)* kèm trích dẫn `[66]`, nhưng ở danh mục tài liệu tham khảo (**tr. 12**), `[66]` lại là bài báo *ChestX-ray8* (Wang et al., CVPR 2017) `[Nêu rõ trong bài — P1 tr. 4, 12]`.

7. **Sự pha trộn không đồng nhất về kênh màu trong lớp `Viral Pneumonia`:**
   - Mặc dù tài liệu mô tả ảnh X-quang là ảnh mức xám, kiểm tra thực tế từ [`splits/manifest.csv`](../splits/manifest.csv) cho thấy 3 lớp `COVID`, `Lung_Opacity`, `Normal` có 100% ảnh ở chế độ 1 kênh (`mode = L`), riêng lớp `Viral Pneumonia` có `1.205` ảnh `mode = L` và **`140` ảnh lưu ở chế độ 3 kênh (`mode = RGB`)** `[Suy ra từ số liệu — splits/manifest.csv]`.

---

## 7. Hệ quả đối với Đồ án: Rủi ro Kỹ thuật và Các ĐỀ XUẤT

### 7.1. Năm rủi ro kỹ thuật trực tiếp đối với đồ án của nhóm

1. **Rủi ro thiên lệch nguồn dữ liệu và độ tuổi (Demographic & Source Confounding — Shortcut Learning):**
   - Lớp `Viral Pneumonia` (`1.345` ảnh) đến 100% từ bộ dữ liệu của Paul Mooney (vốn là ảnh bệnh nhi 1–5 tuổi), trong khi lớp `Lung_Opacity` (`6.012` ảnh) đến 100% từ RSNA và lớp `COVID` (`3.616` ảnh) đến từ 6 kho dữ liệu khác hoàn toàn (`BIMCV`, Đức, `SIRM`, `Eurorad`, `GitHub`, `COVID-CXNet`).
   - Hệ quả: Mô hình học máy có nguy cơ rất cao phân biệt `Viral Pneumonia` với `COVID` hoặc `Lung_Opacity` dựa vào **hình thái lồng ngực trẻ em** (xương sườn mảnh, bóng tuyến ức, tỷ lệ tim-ngực khác người lớn) hoặc đặc trưng máy chụp thay vì tổn thương viêm phổi thực sự `[Suy ra từ số liệu]`.

2. **Rủi ro rò rỉ cấp độ bệnh nhân (Patient-level Leakage) do thiếu `patient_id`:**
   - P2 xác nhận `18.479` ảnh thuộc khoảng `15.000` bệnh nhân (tức có nhiều bệnh nhân chụp nhiều ảnh theo thời gian), nhưng metadata công bố trên Kaggle không có `patient_id`.
   - Dù nhóm đã lọc trùng khít `pHash` ngưỡng $T=0$ (`178` nhóm, `401` ảnh) trong [`splits/split_v1.csv`](../splits/split_v1.csv), các ảnh chụp cùng một bệnh nhân ở các ngày khác nhau (hoặc một phần trong `506` cặp gần trùng cùng nhãn ở khoảng cách Hamming $1 \le D \le 4$ nằm khác split) vẫn có thể tồn tại giữa Train, Val và Test `[Suy ra từ số liệu — P2 tr. 16 & splits/README.md]`.

3. **Rủi ro sai lệch không gian khi dùng Lung Mask (`256×256` vs `299×299`) và nhiễu biên mask sinh tự động:**
   - Toàn bộ `21.165` mask có kích thước `256×256` trong khi ảnh CXR gốc là `299×299`. Nếu áp dụng mask trực tiếp mà không đồng bộ kích thước hoặc dùng phép nội suy tuyến tính làm nhòe biên nhị phân, mặt nạ phổi sẽ bị lệch vị trí giải phẫu.
   - Hơn nữa, vì mask của bộ dữ liệu phân loại nhiều khả năng được sinh tự động bằng mạng Modified U-Net (như P2 Mục 4.1 tr. 23–24 mô tả), trên các ca mờ phổi nặng (đông đặc phổi sát thành ngực), U-Net có thể cắt thiếu chính vùng tổn thương bệnh lý `[Suy ra từ số liệu — P2 tr. 23–24 & splits/manifest.csv]`.

4. **Rủi ro từ sự mất cân bằng lớp nghiêm trọng kết hợp nguồn pha trộn ở lớp `Normal`:**
   - Lớp `Normal` (`10.192` ảnh) lớn gấp **7,58 lần** lớp `Viral Pneumonia` (`1.345` ảnh) và bao gồm hai quần thể khác nhau (`8.851` ảnh từ RSNA + `1.341` ảnh từ bộ Kaggle Mooney). Nếu dùng Accuracy hoặc Weighted F1 như P1/P2, kết quả tốt trên lớp `Normal` sẽ che lấp hoàn toàn sai số trên lớp `Viral Pneumonia` `[Suy ra từ số liệu]`.

5. **Ràng buộc pháp lý và đạo đức từ nhãn giấy phép `copyright-authors`:**
   - Trong `dataset-metadata.json`, trường `licenses` ghi nhãn `[{"name": "copyright-authors"}]` và phần description có dòng `DATA ACCESS AND USE: Academic/Non-Commercial Use`; điều khoản chi tiết chưa xác minh `[Nêu rõ trong bài — dataset-metadata.json]`.

---

### 7.2. Các ĐỀ XUẤT kỹ thuật và quản trị trình Leader (Nguyễn Đức) xem xét

> [!NOTE]
> Các mục dưới đây chỉ là **ĐỀ XUẤT** dựa trên bằng chứng kiểm chứng, **chưa phải quyết định chính thức**. Mọi thay đổi đối với lộ trình hay tài liệu quản trị đều chờ Leader (Nguyễn Đức) phê duyệt.

1. **`[ĐỀ XUẤT 1 — Cho RQ3 & Phân tích lỗi (Lê Minh & Minh Thuận)]` Kiểm tra định lượng và trực quan hóa độ lệch kích thước ảnh/mask và hiện tượng Shortcut Learning:**
   - Khi viết notebook `08_rq3_masked_eval.ipynb` ở Sprint 4–5, bắt buộc phải resize cả ảnh CXR (`299×299`) và mask (`256×256`) về cùng kích thước chuẩn (sử dụng `InterpolationMode.NEAREST` cho mask để giữ giá trị nhị phân `{0, 1}`).
   - Trong `09_error_analysis.ipynb`, đề xuất đối chiếu kết quả dự đoán của lớp `Normal` tách riêng theo 2 nhóm nguồn con (`8.851` ảnh RSNA vs `1.341` ảnh Mooney dựa theo `Normal.metadata.xlsx`) để kiểm tra xem mô hình có bị nhầm lẫn giữa `Normal (Mooney)` và `Viral Pneumonia (Mooney)` do cùng nguồn ảnh bệnh nhi hay không.

2. **`[ĐỀ XUẤT 2 — Cho Quản lý Split (Nguyễn Đức & Hải Lý)]` Giữ nguyên `split_v1.csv` đã khóa nhưng bổ sung cảnh báo nguồn gốc vào tài liệu báo cáo:**
   - Không mở khóa hay tạo lại `split_v1.csv`, vì dữ liệu gốc trên Kaggle vốn không có `patient_id` nên bất kỳ cách chia lại nào cũng không thể tách theo bệnh nhân 100%.
   - Đề xuất ghi nhận rõ con số **`18.479` ảnh / `15.000` bệnh nhân** của P2 và cấu trúc ghép nguồn (`RSNA` + `Mooney` + `6 nguồn COVID`) vào mục *"Giới hạn của nghiên cứu (Limitations)"* trong báo cáo cuối kỳ (`S6-01`).

3. **`[ĐỀ XUẤT 3 — Cho cập nhật tài liệu nội bộ sau khi PR này được duyệt]`:**
   - Đề xuất cập nhật dòng *"Thông tin nguồn gốc của bộ dữ liệu CXR (Shortcut Learning)"* tại Mục 5 của [`docs/roadmap.md`](roadmap.md#L184) từ trạng thái `Mở` sang `Đã giải quyết` (dẫn chiếu tới `docs/dataset_provenance.md`).
   - Đề xuất bổ sung một đoạn ghi chú ngắn vào Mục 4 của [`splits/README.md`](../splits/README.md#L90-L95) dẫn chiếu tới `docs/dataset_provenance.md` về tỷ lệ `18.479` ảnh / `15.000` bệnh nhân và sự lệch kích thước gốc giữa ảnh (`299×299`) và mask (`256×256`). *(Nhóm nghiên cứu KHÔNG tự ý sửa 2 tệp này trong PR hiện tại).*

---

## 8. Danh sách Trích dẫn Đầy đủ

### 8.1. Hai bài báo gốc và Trang dữ liệu Kaggle
1. **[P1 — Bài báo gốc 1]** M. E. H. Chowdhury, T. Rahman, A. Khandakar, R. Mazhar, M. A. Kadir, Z. B. Mahbub, K. R. Islam, M. S. Khan, A. Iqbal, N. Al-Emadi, M. B. I. Reaz, và M. T. Islam, *"Can AI Help in Screening Viral and COVID-19 Pneumonia?"*, *IEEE Access*, vol. 8, pp. 132665–132676, 2020, doi: `10.1109/ACCESS.2020.3010287`. Bản preprint đã đọc: `arXiv:2003.13145v3` (`https://arxiv.org/abs/2003.13145`).
2. **[P2 — Bài báo gốc 2]** T. Rahman, A. Khandakar, Y. Qiblawey, A. Tahir, S. Kiranyaz, S. B. A. Kashem, M. T. Islam, S. Al Maadeed, S. M. Zughaier, M. S. Khan, và M. E. H. Chowdhury, *"Exploring the effect of image enhancement techniques on COVID-19 detection using chest X-ray images"*, *Computers in Biology and Medicine*, vol. 132, p. 104319, 2021, doi: `10.1016/j.compbiomed.2021.104319`. Bản preprint đã đọc: `arXiv:2012.02238v1` (`https://arxiv.org/abs/2012.02238`).
3. **[Kaggle Dataset]** T. Rahman, M. E. H. Chowdhury, A. Khandakar và cộng sự, *"COVID-19 Radiography Database"*, Kaggle Repository (`https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database`), `datasetId: 576013`, giấy phép: nhãn `copyright-authors` trên Kaggle (description ghi `Academic/Non-Commercial Use`; điều khoản chi tiết chưa xác minh).

### 8.2. Các nguồn dữ liệu gốc thành phần được trích dẫn trong P1, P2 và `README.md.txt`
4. **[Nguồn COVID — BIMCV-COVID19+]** Medical Imaging Databank of the Valencia Region (BIMCV), *"BIMCV-COVID19+: Datasets related to COVID-19's pathology course"*, `https://bimcv.cipf.es/bimcv-projects/bimcv-covid19/#1590858128006-9e640421-6711` (Trích dẫn `[67]` trong P2; `[1]` trong `README.md.txt`).
5. **[Nguồn COVID — Trường Y tại Đức / ML Workgroup]** Institute for Diagnostic and Interventional Radiology, Hannover Medical School (Germany), *"covid-19-image-repository"*, `https://github.com/ml-workgroup/covid-19-image-repository/tree/master/png` (Trích dẫn `[68]` trong P2; `[2]` trong `README.md.txt`).
6. **[Nguồn COVID — SIRM]** Italian Society of Medical and Interventional Radiology (SIRM), *"COVID-19 Database"*, `https://www.sirm.org/category/senza-categoria/covid-19/` (Trích dẫn `[62]` trong P1; `[69]` trong P2; `[3]` trong `README.md.txt`).
7. **[Nguồn COVID — Eurorad]** European Society of Radiology, *"Eurorad Chest Imaging Database"*, `https://www.eurorad.org/` (Trích dẫn `[70]` trong P2; `[4]` trong `README.md.txt`).
8. **[Nguồn COVID — GitHub Cohen et al.]** J. P. Cohen, P. Morrison, và L. Dao, *"COVID-19 Image Data Collection"*, `arXiv:2003.11597`, 2020, GitHub: `https://github.com/ieee8023/covid-chestxray-dataset` (Trích dẫn `[63]` trong P1; `[18], [71]` trong P2; `[5]` trong `README.md.txt`).
9. **[Nguồn COVID — Figshare / Twitter / Radiopaedia]** *"COVID-19 Chest X-Ray Image Repository"*, `https://figshare.com/articles/COVID-19_Chest_X-Ray_Image_Repository/12580328`; Radiopaedia (`https://radiopaedia.org`); Thread Reader (`https://threadreaderapp.com/thread/1243928581983670272.html`) (Trích dẫn `[64], [65]` trong P1; `[6]` trong `README.md.txt`).
10. **[Nguồn COVID — COVID-CXNet]** A. Haghanifar và cộng sự, *"COVID-CXNet Repository"*, `https://github.com/armiro/COVID-CXNet` (Trích dẫn `[73]` trong P2; `[7]` trong `README.md.txt`).
11. **[Nguồn Normal & Lung Opacity — RSNA]** Radiological Society of North America (RSNA), *"RSNA Pneumonia Detection Challenge"*, Kaggle, 2018, `https://www.kaggle.com/c/rsna-pneumonia-detection-challenge/data` (Trích dẫn `[66]` trong P2; `[8]` trong `README.md.txt`).
12. **[Nguồn Normal & Viral Pneumonia — Kaggle Mooney / Kermany et al.]** P. Mooney, *"Chest X-Ray Images (Pneumonia)"*, Kaggle, 2018, `https://www.kaggle.com/paultimothymooney/chest-xray-pneumonia` (Trích dẫn `[67]` trong P1; `[9]` trong `README.md.txt`); bắt nguồn từ nghiên cứu gốc: D. S. Kermany, M. Goldbaum, W. Cai và cộng sự, *"Identifying Medical Diagnoses and Treatable Diseases by Image-Based Deep Learning"*, *Cell*, vol. 172, no. 5, pp. 1122–1131.e9, 2018 (Trích dẫn `[29]` trong P1).

---

## 9. Các Vấn đề Chưa Xác minh và Phương thức Xác minh Tiếp theo

| STT | Nội dung hiện ở trạng thái `[Chưa xác minh]` | Nguyên nhân chưa xác minh được | Cách xác minh cụ thể nếu nhóm cần làm rõ |
| :---: | :--- | :--- | :--- |
| **1** | **Nội dung toàn văn bản xuất bản chính thức của P1 (IEEE Access) và P2 (Elsevier CBM)** | Trang IEEE Xplore tải nội dung bài báo qua AngularJS; trang ScienceDirect của Elsevier chặn truy cập tự động bằng mã lỗi `HTTP 403 Forbidden`, nên hiện mới đọc toàn văn bản preprint `arXiv:2003.13145v3` và `arXiv:2012.02238v1`. | Tải trực tiếp tệp PDF bản xuất bản chính thức qua tài khoản thư viện trường đại học (hoặc mạng nội bộ có quyền truy cập ScienceDirect/IEEE Xplore) để đối chiếu xem các lỗi đánh máy ở Mục 3.1.5 (`2.473` vs `2.474`), Mục 4.1 (`3.416` vs `3.616`) và mâu thuẫn mô tả mask ở Mục 3.1.1 vs 4.1 đã được biên tập lại trong bản in chính thức hay chưa. |
| **2** | **Quy trình tạo mặt nạ phổi cho `2.686` ảnh ngoài bộ `COVQU` (`1.345` Viral Pneumonia + `1.341` Normal)** | P1 không sử dụng mặt nạ phổi; P2 chỉ mô tả việc phân đoạn trên `18.479` ảnh của bộ `COVQU`. Không có tài liệu nào trong dataset mô tả ai hoặc mô hình nào đã tạo mask cho `2.686` ảnh lấy từ bộ Kaggle của Paul Mooney. | Kiểm tra trực quan một mẫu ngẫu nhiên (ví dụ 20–30 cặp ảnh và mask của lớp `Viral Pneumonia` và `Normal` thuộc nguồn Mooney trong `08_rq3_masked_eval.ipynb`) để đánh giá chất lượng khớp biên phổi, đồng thời ghi rõ trong báo cáo rằng nguồn gốc mask của `2.686` ảnh này không được công bố trong bài báo gốc. |
| **3** | **Thông tin nhân khẩu học (độ tuổi, giới tính), mã bệnh nhân (`patient_id`) và thiết bị chụp của từng ảnh** | Các tệp `*.metadata.xlsx` trên Kaggle chỉ cung cấp 4 cột (`FILE NAME`, `FORMAT`, `SIZE`, `URL`), hoàn toàn không lưu mã định danh bệnh nhân hay thông số DICOM gốc. | Đối với nguồn `BIMCV`, `SIRM`, `GitHub ieee8023` và `RSNA`, metadata gốc từng tồn tại trên các kho nguồn nhưng khi tác giả P1/P2 xuất sang ảnh PNG `299×299` và đổi tên theo thứ tự (`COVID-1.png`, `Normal-1.png`, ...) thì liên kết ánh xạ 1-1 tới bản ghi gốc đã bị mất. Do đó, cần ghi nhận đây là giới hạn cố hữu không thể khôi phục của bộ dữ liệu thứ cấp này. |
| **4** | **Tiêu chuẩn vàng chẩn đoán lâm sàng (RT-PCR, CT hay lâm sàng) và người gán nhãn ban đầu của từng nguồn con COVID-19** | P2 gộp `3.616` ảnh COVID-19 từ 6 kho dữ liệu trực tuyến mà không liệt kê tiêu chuẩn chẩn đoán chi tiết của từng kho (ngoài `103` ảnh ở Tây Ban Nha trong P1 được ghi rõ là `SARS-CoV-2 PCR+`). | Tra cứu riêng tài liệu gốc của từng kho thành phần (đặc biệt là bài báo mô tả bộ `BIMCV-COVID19+` chiếm `2.474/3.616` ảnh COVID-19 và bài báo `RSNA Pneumonia Detection Challenge` của Shih et al., 2019) nếu giảng viên yêu cầu thuyết minh sâu hơn về quy trình bác sĩ gán nhãn ở các kho nguồn. |
