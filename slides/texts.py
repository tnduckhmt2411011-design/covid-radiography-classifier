"""Câu chữ nguyên văn dùng ở nhiều slide.

Không viết lại các câu này ở tầng nội dung: mọi chỗ xuất hiện đều lấy từ đây để
một thay đổi ở nguồn gốc không tạo ra hai dị bản trên slide.
"""

from __future__ import annotations

# Quy tắc D4 — giữ nguyên văn, không thêm bớt.
D4 = (
    "Mọi lời giải thích về sự khác biệt giữa val và test đều là giả thuyết "
    "chưa kiểm chứng, không nêu nguyên nhân."
)

# Nhãn đánh dấu cho mọi nội dung chưa được kiểm chứng trong đề tài.
UNVERIFIED = "chưa kiểm chứng"

TITLE = (
    "Phân loại ảnh X-quang lồng ngực bằng học máy cổ điển và đánh giá nguy cơ "
    "shortcut learning trên bộ dữ liệu COVID-19 Radiography"
)

SCHOOL = "Trường Đại học Kỹ thuật – Công nghệ Cần Thơ (CTUT)"
FACULTY = "Khoa Công nghệ Thông tin và Truyền thông"
COURSE = "Báo cáo bài tập lớn – Môn Học máy"
SUPERVISOR = "GVHD: TS. Lê Anh Nhã Uyên"
CLASS = "Lớp Khoa học máy tính 2024 — Nhóm 10"
PLACE = "Cần Thơ, tháng 11/2026"
SEMESTER = "Học kỳ 1, năm học 2026–2027"

MEMBERS = [
    ("Trần Nguyễn Đức", "KHMT2411011", "Nhóm trưởng"),
    ("Lê Hải Lý", "KHMT2411021", ""),
    ("Phạm Lê Minh", "KHMT2411003", ""),
    ("Nguyễn Vũ Thương", "KHMT2411022", ""),
    ("Nguyễn Trần Minh Thuận", "KHMT2411014", ""),
    ("Hàng Thái Tú", "KHMT2411046", ""),
]

DISCLAIMER = (
    "KHÔNG DÙNG ĐỂ CHẨN ĐOÁN. Đây là demo học thuật của mô hình học máy truyền "
    "thống, không phải thiết bị y tế và chưa được kiểm định lâm sàng. Không dùng "
    "kết quả để đưa ra quyết định điều trị hay bất kỳ quyết định y tế nào."
)

REPO_URL = "github.com/tnduckhmt2411011-design/covid-radiography-classifier"
DEMO_URL = "huggingface.co/duc16/cxr-svm-demo"

# Ba điểm mang về, lặp ở slide 2, 20 và 27.
TAKEAWAYS = {
    "T1": "152 đặc trưng thủ công với SVM RBF đạt macro-F1 vượt xa hai mốc nền.",
    "T2": "Mô hình chỉ nhìn ngoài phổi vẫn giữ được phần lớn năng lực phân loại.",
    "T3": "Kết quả chỉ có giá trị trong phạm vi bộ dữ liệu này, không dùng để chẩn đoán.",
}
