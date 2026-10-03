# Ke hoach va Bang theo doi tien do do an (Scrum rut gon)

Tai lieu theo doi tien do thuc hien do an mon Hoc may trong 12 tuan, ap dung mo hinh Scrum rut gon danh cho nhom 6 sinh vien beginner. Toan bo tien do duoc dong bo voi trang thai thuc te tren GitHub repository.

---

## Muc 1. Cach doc tai lieu

### 1.1. He thong 5 trang thai cong viec

Moi cong viec trong backlog chi nhan dung 1 trong 5 trang thai sau, gan chat voi hoat dong tren GitHub:

- **Chua lam:** Mac dinh cho tat ca cac cong viec chua bat dau hoac chua tim thay bang chung xac thuc tren GitHub/repo.
- **Dang lam:** Co nhanh tinh nang `feat/<ten>-<viec>` dang mo tren repo, dang duoc phat trien va chua tao Pull Request.
- **Cho duyet:** Da mo Pull Request tren GitHub, dang trong qua trinh kiem tra va cho thanh vien trong cap duyet (Approve), chua merge vao main.
- **Xong:** Pull Request da duoc merge vao nhanh main VA dat day du tieu chi nghiem thu cua viec do. Doi voi cac viec khong qua Pull Request (vi du: gui cau hoi cho giang vien), bat buoc can leader xac nhan bang van ban.
- **Bi chan:** Cong viec khong the tiep tuc do vuong mac ve ky thuat, thieu thong tin, hoac phu thuoc chua hoan thanh. Bat buoc phai co dong giai thich nguyen nhan tai Muc 5.

### 1.2. Quy uoc uoc luong do lon (Size)

Do lon cong viec duoc uoc luong tho theo gio lam viec thuc te de nhom sinh vien de phan bo thoi gian (nhom co the tinh chinh o buoi Sprint Planning):

- **S (Small):** Nho hon hoac bang 2 gio lam viec.
- **M (Medium):** Tu 3 den 5 gio lam viec.
- **L (Large):** Tu 6 den 10 gio lam viec.

### 1.3. Cot Bang chung

Moi cong viec o trang thai "Xong" hoac "Cho duyet" bat buoc phai ghi ro nguon xac thuc:
- Duong dan hoac ma so Pull Request tren GitHub (vi du: PR #1, PR #2).
- Ma commit, duong dan file trong repository (vi du: splits/manifest.csv).
- Ten kernel va run id tren Kaggle (doi voi kernel chay private).
- Hoac dong chu "leader xac nhan" doi voi cong viec ngoai le khong co code tren Git.

### 1.4. Bang thuat ngu rut gon cho nguoi moi

| Thuat ngu | Y nghia don gian trong do an |
| :--- | :--- |
| **Sprint** | Chu ky lam viec co dinh dai 2 tuan de hoan thanh mot nhom muc tieu nhat dinh. |
| **Sprint Goal** | Muc tieu cot loi nhat ma ca nhom phai dat duoc khi ket thuc mot sprint. |
| **Backlog** | Danh sach tat ca cac cong viec can lam trong du an, duoc chia nho theo tung sprint. |
| **Definition of Done** | Bo tieu chuan bat buoc de mot cong viec duoc cong nhan la hoan thanh thuc su. |
| **Sprint Review** | Buoi hop nganh cuoi sprint de trinh bay va kiem tra cac san pham da hoan thanh. |
| **Retrospective** | Buoi hop rut kinh nghiem cuoi sprint de cai tien cach phoi hop va sua loi cho sprint tiep theo. |

### 1.5. Nhip lam viec de xuat cho nhom

- **Sprint Planning (Dau sprint, khoang 30 phut):** Nhom hop online/offline, leader giao viec theo phan cong trong docs/OWNERS.md, cac cap uoc luong lai Size neu can.
- **Cap nhat tien do hang tuan (Cuoi tuan):** Nguoi phu trach cap nhat trang thai cong viec cua minh ngay trong chinh Pull Request hoac commit cua viec do.
- **Sprint Review va Retrospective (Cuoi sprint, khoang 45 phut):** Danh gia san pham sprint, ghi nhan vao Muc 7 va chot ke hoach sprint tiep theo.

---

## Muc 2. Tong quan tien do

Cap nhat lan cuoi: 03/10/2026

| Sprint | Tuan | Muc tieu sprint | So viec Xong/Tong | Trang thai sprint | Ghi chu |
| :---: | :---: | :--- | :---: | :---: | :--- |
| **S1** | T1-2 | Moi truong chay duoc va hieu du lieu | 5/7 | Dang lam | Da xong setup Kaggle, EDA va manifest; cho leader xac nhan T1-03 va T1-04 |
| **S2** | T3-4 | Khoa test, khung huan luyen chay duoc, co baseline va nguong chap nhan | 5/8 | Dang lam | Hoan tat 100% Tuan 3 (Track A & Track B, khoa test, GPU smoke test pass); chuan bi Tuan 4 baseline |
| **S3** | T5-6 | Hoan tat RQ1 (so sanh backbone va chien luoc fine-tune) | 0/6 | Chua lam | So sanh DenseNet121 va EfficientNet-B0 |
| **S4** | T7-8 | Hoan tat RQ2 (mat can bang lop), chot cau hinh cuoi, Grad-CAM, phan tich loi, bo anh che | 0/7 | Chua lam | Thu nghiem Weighted Loss, Focal Loss, tao mask anh |
| **S5** | T9-10 | RQ3 (shortcut learning), danh gia test MOT lan, notebook suy luan | 0/6 | Chua lam | Danh gia anh che va mo khoa tap test duy nhat mot lan |
| **S6** | T11-12 | Bao cao, slide, demo, du phong, nop, tap bao ve | 0/6 | Chua lam | Hoan thien bao cao tong ket va ung dung Gradio |
| **Tong** | **T1-12** | **Toan bo 6 sprint cua do an** | **10/40** | **Dang trien khai** | **Dat 25.0% tong khoi luong cong viec** |

---

## Muc 3. Backlog chi tiet theo sprint

### Sprint 1 (Tuan 1 - 2): Moi truong chay duoc va hieu du lieu
**Sprint Goal:** Chung minh moi truong tinh toan Kaggle GPU hoat dong on dinh, xac minh tap du lieu 21.165 anh tren 4 lop, xuat file manifest.csv day du mask va phan tich nguy co shortcut learning.

| ID | Tuan | Cong viec | Gan voi | Phu trach | Size | Trang thai | Bang chung | Tieu chi nghiem thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S1-01 | T1 | Kiem tra moi truong Kaggle GPU, ghi chep cau hinh phan cung | Ha tang | Ca nhom | M | Xong | PR #2 da merge, docs/kaggle_setup_notes.md, kernel cxr-setup-check | Chay thanh cong tren 2x Tesla T4, xac dinh torch 2.10.0+cu128 va CUDA 12.8 khong loi |
| S1-02 | T1 | Ghim phien ban thu vien thuc te vao requirements.txt | Ha tang | Ca nhom | S | Xong | PR #2 da merge, commit e7c88b0, docs/kaggle_setup_notes.md | Ghi chep day du torch==2.10.0+cu128, torchvision==0.25.0+cu128 tu log Kaggle |
| S1-03 | T1 | 6/6 thanh vien clone repo ve may va kiem tra moi truong cuc bo | Ha tang | Ca nhom | S | Chua lam | Chua co bang chung, can leader xac nhan | 6/6 nguoi clone repo, chay xong 00_setup_check khong loi |
| S1-04 | T1 | Gui danh sach cau hoi lam ro de tai cho giang vien | Bao cao | Leader | S | Chua lam | Chua co bang chung, can leader xac nhan | Cau hoi cho giang vien da gui bang van ban hoac email |
| S1-05 | T2 | Xay dung notebook 01_download_and_eda.ipynb doc du lieu tu Kaggle | Ha tang | TV1 | M | Xong | PR #1 da merge, notebooks/01_download_and_eda.ipynb, kernel cxr-eda-manifest | Notebook tu dong tim dataset, doc du lieu, khong co loi lap trinh |
| S1-06 | T2 | Tao file manifest.csv, doi chieu so luong anh va mask 4 lop | Chong ro ri | TV1 | M | Xong | PR #1 da merge, splits/manifest.csv, outputs/eda_manifest/manifest.csv | So anh moi lop khop chinh xac so biet (21.165 anh), bao cao mask khop 100% |
| S1-07 | T2 | Thong ke do sang, luoi anh mau va phat hien 54 hash trung lap | Chong ro ri | TV1 | S | Xong | PR #1 da merge, results/eda/brightness_distribution.png, samples_grid.png | Co danh sach nhom anh trung lap, phan tich nghi van shortcut learning ve do sang |

---

### Sprint 2 (Tuan 3 - 4): Khoa test, khung huan luyen, baseline va nguong chap nhan
**Sprint Goal:** Hoan thanh loc trung va chia train/val/test 70/15/15, khoa nghiem ngat tap test; hoan thien khung train.py co checkpoint resume; huan luyen thanh cong mo hinh baseline va chot nguong chap nhan.

| ID | Tuan | Cong viec | Gan voi | Phu trach | Size | Trang thai | Bang chung | Tieu chi nghiem thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S2-01 | T3 | Loc bo 54 anh trung bang imagehash trong 02_duplicates_and_split.ipynb | Chong ro ri | TV1 | M | Xong | PR #4 da merge (commit 83531cc), notebooks/02_duplicates_and_split.ipynb, kernel cxr-duplicates-and-split, splits/README.md | Loc nhom trung pHash nguong T=0 (178 nhom, 401 anh), 0 cap trung khac nhan, khong ro ri nhom giua cac split |
| S2-02 | T3 | Chia tap train/val/test theo ti le 70/15/15 va gan tag test-locked | Chong ro ri | TV1 | M | Xong | PR #4 da merge, splits/split_v1.csv, split_v1.sha256, tag test-locked tro commit e7c0993b, tests/test_split.py pass | Ti le 70/15/15 chuan (do lech < 0.1%), khoa test set v1 bang SHA256 va tag test-locked |
| S2-03 | T3 | Xay dung DataLoader va Data Augmentation co ban trong src/dataset.py | Ha tang | TV4 | M | Xong | PR #5 da merge (commit f5c688b), src/dataset.py, tests/test_resume.py | Dataset doc split_v1.csv, anh xam -> 3 kenh, chuan hoa ImageNet, augment chi cho train (khong lat anh), chan split test bang allow_test |
| S2-04 | T3 | Xay dung pipeline huan luyen src/train.py co ho tro resume | Ha tang | TV2 | L | Xong | PR #5 da merge, commit f5c688b, src/train.py, src/metrics.py, src/models.py, tests/test_metrics.py, tests/test_resume.py | Pipeline mixed precision AMP, luu last.pt va best.pt (macro-F1), ho tro resume tu dong, ten run chuan <rq>_<backbone>_<strategy>_<imb>_s<seed> |
| S2-05 | T3 | Chay smoke test tren 03_smoke_test_train.ipynb | Ha tang | TV2 | S | Xong | PR #5 da merge, notebooks/03_smoke_test_train.ipynb, kernel cxr-smoke-test-train (GPU T4x2), outputs/smoke_test/smoke_test_report.json | 12/12 pytest pass, gia lap ngat phien va resume thanh cong epoch 1 -> 2 tren Kaggle GPU trong 49s |
| S2-06 | T4 | Huan luyen mo hinh co so Baseline tren 04_baseline.ipynb | Ha tang | TV2 | L | Chua lam | Chua co nhanh/PR | Bang baseline co macro-F1 va recall tung lop tren tap validation |
| S2-07 | T4 | Do dac thoi gian chay thuc te moi run va uoc tinh tong GPU-gio | Ha tang | TV2 | S | Chua lam | Chua co nhanh/PR | Co so lieu thoi gian tung epoch va bang uoc tinh tong GPU-gio cho cac tuan sau |
| S2-08 | T4 | Xac lap nguong hieu nang toi thieu chap nhan duoc bang van ban | Bao cao | Leader | S | Chua lam | Chua co nhanh/PR | Nguong chap nhan viet bang loi trong results/, gan lien voi ket qua baseline |

---

### Sprint 3 (Tuan 5 - 6): Hoan tat RQ1 (So sanh backbone va chien luoc fine-tune)
**Sprint Goal:** Hoan thanh so sanh thuc nghiem giua DenseNet121 va EfficientNet-B0 duoi 2 chien luoc (frozen vs fine-tune) tren 3 seed ngau nhien; chon ra 1 cau hinh toi uu nhat dua sang RQ2.

| ID | Tuan | Cong viec | Gan voi | Phu trach | Size | Trang thai | Bang chung | Tieu chi nghiem thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S3-01 | T5 | Cai dat cac kien truc DenseNet121 va EfficientNet-B0 trong src/models.py | RQ1 | TV3 | M | Chua lam | Chua co nhanh/PR | Khoi tao dung kien truc, nap dung pretrained weights ImageNet |
| S3-02 | T5 | Thuc hien cac run huan luyen chien luoc frozen backbone | RQ1 | TV3 | L | Chua lam | Chua co nhanh/PR | It nhat 50% run RQ1 hoan tat, moi run co day du config, log va file best.pt |
| S3-03 | T5 | Thuc hien cac run huan luyen chien luoc full fine-tuning | RQ1 | TV3 | L | Chua lam | Chua co nhanh/PR | Hoan tat cac run fine-tune tren ca 2 backbone voi log va checkpoint |
| S3-04 | T6 | Chay lap lai thuc nghiem tren 3 seed ngau nhien (s42, s43, s44) | RQ1 | TV3 | L | Chua lam | Chua co nhanh/PR | Du so lieu 3 seed cho tung cau hinh de tinh toan thong ke |
| S3-05 | T6 | Tong hop bang ket qua so sanh RQ1 trong 05_rq1_backbones.ipynb | RQ1 | TV3 | M | Chua lam | Chua co nhanh/PR | Bang RQ1 co trung binh cong va do lech chuan qua 3 seed cho macro-F1, recall |
| S3-06 | T6 | Phan tich va chot 1 cau hinh backbone tot nhat tren validation cho RQ2 | RQ1 | TV3 | S | Chua lam | Chua co nhanh/PR | Co bien ban ket luan ro rang dua tren validation metric de chuyen tiep |

---

### Sprint 4 (Tuan 7 - 8): Hoan tat RQ2, chot cau hinh, Grad-CAM, phan tich loi, bo anh che
**Sprint Goal:** Hoan thanh thu nghiem cac giai phap xu ly mat can bang lop (RQ2); dong bang cau hinh toi uu; cai dat Grad-CAM; phan tich loi va tao bo anh che mat na phoi.

| ID | Tuan | Cong viec | Gan voi | Phu trach | Size | Trang thai | Bang chung | Tieu chi nghiem thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S4-01 | T7 | Cai dat Weighted Cross-Entropy va Focal Loss trong src/train.py | RQ2 | TV4 | M | Chua lam | Chua co nhanh/PR | Ham mat mat tinh dung dao ham, ho tro truyen trong so lop |
| S4-02 | T7 | Thu nghiem WeightedRandomSampler va Data Augmentation bo sung | RQ2 | TV4 | M | Chua lam | Chua co nhanh/PR | Sampler can bang ti le lay mau giua lop it (Viral Pneumonia) va lop nhieu (Normal) |
| S4-03 | T7 | Huan luyen so sanh cac chien luoc tren 06_rq2_imbalance.ipynb | RQ2 | TV4 | L | Chua lam | Chua co nhanh/PR | Bang RQ2 ghi ro recall va F1 rieng cho lop Viral Pneumonia va cac lop khac, so voi baseline |
| S4-04 | T8 | Chot cau hinh mo hinh toi uu nhat va dong bang tham so thuc nghiem | Ha tang | Ca nhom | S | Chua lam | Chua co nhanh/PR | Cau hinh cuoi cung duoc ghi nhan van ban va khoa chat che |
| S4-05 | T8 | Cai dat module Grad-CAM trong src/gradcam.py va 07_gradcam_lung_attention.ipynb | RQ3 | TV5 | L | Chua lam | Chua co nhanh/PR | Xuat duoc ban do nhiet Grad-CAM phu tren anh X-quang, doi chieu truc quan voi mask |
| S4-06 | T8 | Phan tich chi tiet cac ca du doan sai tren 09_error_analysis.ipynb | Bao cao | TV5 | M | Chua lam | Chua co nhanh/PR | Lap danh sach cac ca nham lan dien hinh giua COVID, Lung Opacity va Pneumonia |
| S4-07 | T8 | Tao bo anh che thu nghiem (chi giu phoi / che ngoai phoi) | RQ3 | TV5 | M | Chua lam | Chua co nhanh/PR | Bo anh che duoc kiem tra bang mat tren it nhat 20 anh moi lop khong bi lech mask |

---

### Sprint 5 (Tuan 9 - 10): RQ3 (Shortcut Learning), danh gia test MOT lan, suy luan
**Sprint Goal:** Danh gia mo hinh tren bo anh che de do luong do le thuoc vao vung ngoai phoi (RQ3); mo khoa tap test de danh gia duy nhat mot lan; hoan thien notebook suy luan doc lap.

| ID | Tuan | Cong viec | Gan voi | Phu trach | Size | Trang thai | Bang chung | Tieu chi nghiem thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S5-01 | T9 | Danh gia mo hinh tren 3 tap (anh goc, chi phoi, ngoai phoi) trong 08_rq3_masked_eval.ipynb | RQ3 | TV5 | L | Chua lam | Chua co nhanh/PR | Bang RQ3 tren tap validation the hien day du su thay doi do chinh xac tren 3 kieu che |
| S5-02 | T9 | Tinh toan chi so tap trung nang luong Grad-CAM ben trong mask phoi | RQ3 | TV5 | M | Chua lam | Chua co nhanh/PR | Co ti le % nang luong nam trong phoi so voi ngoai phoi |
| S5-03 | T9 | Soan thao ket luan nghien cuu ve nguy co shortcut learning | RQ3 | TV5 | M | Chua lam | Chua co nhanh/PR | Ket luan so bo ve muc do shortcut learning du ket qua co dep hay khong |
| S5-04 | T10 | Mo khoa tap test va thuc hien danh gia DUY NHAT 1 LAN trong 10_final_test_eval.ipynb | Chong ro ri | TV6 | M | Chua lam | Chua co nhanh/PR | Ket qua test ghi dung 1 lan duy nhat kem ma hash file split de dam bao tinh khach quan |
| S5-05 | T10 | Xuat ma tran nham lan (Confusion Matrix) va bang chi so tren test | Bao cao | TV6 | S | Chua lam | Chua co nhanh/PR | Bang ket qua test day du accuracy, macro-F1 va recall tung lop |
| S5-06 | T10 | Xay dung notebook suy luan doc lap 11_inference_demo.ipynb | Ha tang | TV6 | M | Chua lam | Chua co nhanh/PR | Notebook suy luan chay lai duoc tu dau tren mot phien Kaggle moi tinh |

---

### Sprint 6 (Tuan 11 - 12): Bao cao, Demo, Bao ve va Hoan tat
**Sprint Goal:** Hoan thien toan dien bao cao bai tap lon, ung dung demo Gradio, slide thuyet trinh; dien tap bao ve va nop san pham dung han.

| ID | Tuan | Cong viec | Gan voi | Phu trach | Size | Trang thai | Bang chung | Tieu chi nghiem thu |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| S6-01 | T11 | Soan thao bao cao bai tap lon trong thu muc report/ | Bao cao | TV6 | L | Chua lam | Chua co nhanh/PR | Bao cao trinh bay day du RQ1-3, gioi han nghien cuu va canh bao y khoa |
| S6-02 | T11 | Xay dung ung dung demo Gradio tuong tac trong demo/ | Ha tang | TV6 | M | Chua lam | Chua co nhanh/PR | Mot thanh vien khong phu trach phan do chay lai duoc app va suy luan thanh cong |
| S6-03 | T11 | Hoan thien slide thuyet trinh bao ve de tai trong slides/ | Bao cao | Ca nhom | M | Chua lam | Chua co nhanh/PR | Slide ngan gon, day du bieu do thuc nghiem va cau truc de cuong |
| S6-04 | T12 | Ra soat toan bo san pham, code va dinh dang theo yeu cau giang vien | Bao cao | Ca nhom | S | Chua lam | Chua co nhanh/PR | Dung dinh dang file, tieu chuan ky thuat ma giang vien yeu cau |
| S6-05 | T12 | To chuc dien tap thuyet trinh va tra loi cau hoi phan bien | Bao cao | Ca nhom | M | Chua lam | Chua co nhanh/PR | Dien tap thuyet trinh hoan chinh it nhat 1 lan truoc buoi bao ve chinh thuc |
| S6-06 | T12 | Dong goi san pham cuoi ky va nop bai tap lon | Bao cao | Leader | S | Chua lam | Chua co nhanh/PR | Nop bai dung han quy dinh, repo sach se va dong bo |

---

## Muc 4. Definition of Done chung

Mot cong viec chi duoc phep danh dau la **Xong** khi va chi khi thoa man day du 6 dieu kien nghiem ngat sau day:

1. **Pull Request duoc duyet chéo:** Pull Request da duoc it nhat mot thanh vien trong cap xem xet, kiem tra va phe duyet (Approve), sau do duoc merge vao nhanh `main`.
2. **Notebook chay lai duoc:** Tat ca notebook phai chay lai thanh cong tu dau den cuoi (`Run All`) tren moi truong sach khong phat sinh loi.
3. **Ket qua luu dung vi tri:** Bang so lieu, log, checkpoint hoac bieu do phai duoc luu dung thu muc quy dinh (`results/`, `splits/`, `report/`).
4. **Bao mat va sach repo:** Tuyet doi khong co du lieu anh tho, checkpoint trong so lon (`*.pt`, `*.pth`), token bi mat (`kaggle.json`, `.env`) bi commit vao Git.
5. **Dong bo tien do tren roadmap:** Dong cong viec tuong ung trong `docs/roadmap.md` da duoc cap nhat trang thai thanh `Xong` kem link Pull Request hoac bang chung cu the.
6. **Tuan thu khoa test:** Tuyet doi khong dung tap test trong bat ky buoc huan luyen, chon mo hinh hay tinh chinh nao; tap test chi duoc mo ra dung mot lan tai Tuan 10.

---

## Muc 5. Vuong mac va quyet dinh dang mo

Bang tong hop cac van de can giai quyet hoac quyet dinh de tranh bi chan tien do:

| Muc | Loai | Nguoi quyet | Trang thai | Ghi chu |
| :--- | :---: | :---: | :---: | :--- |
| Phuong an tai trong so ImageNet cho kernel huan luyen | Quyet dinh | Leader | Mo | De xuat (bat internet enable_internet: true cho kernel huan luyen hoac gan Kaggle Dataset chua weights), CHUA CHOT. Nguoi quyet: Leader. Can chot truoc khi chay Baseline Tuan 4. |
| Phan cong chu so huu module src/models.py | Quyet dinh | Leader | Mo | src/models.py hien chua co chu so huu trong docs/OWNERS.md. Can Leader phan cong thanh vien phu trach mo rong cac backbone DenseNet121 va EfficientNet-B0. |
| Quyet dinh giu split_v1 hay tao split_v2 | Quyet dinh | Leader | Mo | split_v1 da khoa voi nguong T=0 (178 nhom, 401 anh). Da thong ke 735 cap gan trung (Hamming 1-4) khac split (325 Train-Test, 335 Train-Val, 75 Val-Test; 229 khac nhan, 506 cung nhan). Mo cho toi khi Leader danh gia co can sua nguong hay khong (735 cap gan trung la gioi han da biet). |
| Rubric cham diem chi tiet cua giang vien | Rui ro | Giang vien / Leader | Dang cho | Chua co rubric cham diem chinh thuc; nhom can lien he hoi giang vien de bam sat trong so diem. |
| Hinh thuc san pham nop cuoi ky | Quyet dinh | Giang vien / Leader | Dang cho | Can xac nhan san pham nop gom nhung gi (mo hinh fine-tune, notebook, bao cao, co bat buoc demo app Gradio hay khong). |
| Thong tin nguon goc cua bo du lieu CXR (Shortcut Learning) | Rui ro | Ca nhom | Mo | Dataset tong hop tu nhieu nguon, thieu metadata benh nhan (patient_id) va thiet bi chup; do lech do sang lop COVID cao hon ro ret; can ghi ro gioi han nay trong bao cao va danh gia tai RQ3. |

---

## Muc 6. Quy tac khi tre tien do

Trong qua trinh thuc hien, neu tien do thuc te bi tre hon 1 tuan so voi ke hoach Sprint, nhom se ap dung quy tac cat giam pham vi cong viec theo thu tu uu tien sau day:

1. **Cat giam 1:** Cat bo phan RQ3-C (phan mo rong: huan luyen lai mo hinh tu dau tren tap anh chi chua vung phoi).
2. **Cat giam 2:** Cat bo thu nghiem Focal Loss trong RQ2 (chi giu lai Weighted Cross-Entropy Loss).
3. **Cat giam 3:** Bot di mot kien truc backbone trong RQ1 (chi tap trung vao DenseNet121 hoac EfficientNet-B0).
4. **Cat giam 4:** Giam so luong seed ngau nhien chay lap lai tu 3 seed xuong con 2 seed de tiet kiem thoi gian tinh toan.
5. **Cat giam 5:** Cat bo phan ung dung demo giao dien (Gradio app), chi giu lai notebook suy luan 11_inference_demo.ipynb.

**Cac phan tuyet doi KHONG duoc phep cat giam:**
- Quy tac khoa tap test va cach ly du lieu.
- Mo hinh co so Baseline va nguong chap nhan toi thieu.
- Danh gia Macro-F1 va Recall tren tung lop benh rieng biet.
- RQ3-A va RQ3-B (danh gia tren anh che phoi va truc quan hoa Grad-CAM).
- Phan gioi han nghien cuu va canh bao y khoa trong bao cao bai tap lon.

---

## Muc 7. Sprint Review va Retrospective

Khung theo doi danh gia va rut kinh nghiem cuoi moi sprint (dien noi dung thuc te o buoi hop cuoi sprint, khong tu y bia dat):

### Sprint 1 (Tuan 1 - 2)
- **Da lam duoc:** Chua dien ra (se dien vao cuoi Tuan 2)
- **Chua xong va vi sao:** Chua dien ra
- **Doi gi o sprint sau:** Chua dien ra

### Sprint 2 (Tuan 3 - 4)
- **Da lam duoc:** Hoan thanh chia split 70/15/15 chong ro ri pHash, khoa tap test (tag test-locked), xay dung xong khung huan luyen PyTorch AMP co resume, chay smoke test thanh cong tren Kaggle GPU T4x2 dat 12/12 pytest pass
- **Chua xong va vi sao:** Cac viec Tuan 4 (Baseline, do gio GPU, nguong chap nhan) chua bat dau
- **Doi gi o sprint sau:** Chot phuong an trong so ImageNet voi Leader de chay Baseline

### Sprint 3 (Tuan 5 - 6)
- **Da lam duoc:** Chua dien ra
- **Chua xong va vi sao:** Chua dien ra
- **Doi gi o sprint sau:** Chua dien ra

### Sprint 4 (Tuan 7 - 8)
- **Da lam duoc:** Chua dien ra
- **Chua xong va vi sao:** Chua dien ra
- **Doi gi o sprint sau:** Chua dien ra

### Sprint 5 (Tuan 9 - 10)
- **Da lam duoc:** Chua dien ra
- **Chua xong va vi sao:** Chua dien ra
- **Doi gi o sprint sau:** Chua dien ra

### Sprint 6 (Tuan 11 - 12)
- **Da lam duoc:** Chua dien ra
- **Chua xong va vi sao:** Chua dien ra
- **Doi gi o sprint sau:** Chua dien ra

---

## Muc 8. Lich su thay doi

| Phien ban | Ngay | Nguoi sua | Noi dung thay doi |
| :---: | :---: | :---: | :--- |
| **v1.0** | 28/09/2026 | Ca nhom | Khoi tao khung lo trinh 12 tuan ban dau |
| **v2.0** | 02/10/2026 | Leader va nhom | Nang cap lo trinh sang bang theo doi tien do Scrum rut gon 6 sprint co trang thai va bang chung |
| **v2.1** | 03/10/2026 | Ky su ML & Nhom | Dong bo tien do Sprint 2 (hoan tat Tuan 3 Track A & Track B, khoa test, GPU smoke test pass) va mo lai cac quyet dinh cua Leader |
