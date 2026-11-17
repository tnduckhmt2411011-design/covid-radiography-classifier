# Tài liệu tham khảo

Danh mục này gồm năm tài liệu học thuật cốt lõi được trích dẫn trong báo cáo, đánh số theo chuẩn IEEE `[n]` theo thứ tự xuất hiện đầu tiên trong Chương 1 (mục 1.1 và 1.2). Các chương sau chỉ dùng lại các tài liệu đã có số thứ tự nên không phát sinh số mới. Chú thích chân trang `[^covid-src]` thuộc Chương 2; chú thích `[^mooney]` xuất hiện ở Chương 1 (mục 1.1) và được dùng lại ở Chương 2 (mục 2.1); cả hai không nằm trong danh mục này và khi chuyển sang Word được chèn thành footnote tại chỗ như ở bản thảo các chương.

[1] M. E. H. Chowdhury, T. Rahman, A. Khandakar, R. Mazhar, M. A. Kadir, Z. B. Mahbub, K. R. Islam, M. S. Khan, A. Iqbal, N. Al-Emadi, M. B. I. Reaz, and M. T. Islam, "Can AI help in screening viral and COVID-19 pneumonia?," *IEEE Access*, vol. 8, pp. 132665–132676, 2020, doi: 10.1109/ACCESS.2020.3010287.

[2] T. Rahman, A. Khandakar, Y. Qiblawey, A. Tahir, S. Kiranyaz, S. B. A. Kashem, M. T. Islam, S. Al Maadeed, S. M. Zughaier, M. S. Khan, and M. E. H. Chowdhury, "Exploring the effect of image enhancement techniques on COVID-19 detection using chest X-ray images," *Computers in Biology and Medicine*, vol. 132, p. 104319, 2021, doi: 10.1016/j.compbiomed.2021.104319.

[3] R. Geirhos, J.-H. Jacobsen, C. Michaelis, R. Zemel, W. Brendel, M. Bethge, and F. A. Wichmann, "Shortcut learning in deep neural networks," *Nature Machine Intelligence*, vol. 2, no. 11, pp. 665–673, 2020, doi: 10.1038/s42256-020-00257-z.

[4] J. R. Zech, M. A. Badgeley, M. Liu, A. B. Costa, J. J. Titano, and E. K. Oermann, "Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study," *PLOS Medicine*, vol. 15, no. 11, e1002683, 2018, doi: 10.1371/journal.pmed.1002683.

[5] B. Efron, "Bootstrap methods: Another look at the jackknife," *Ann. Statist.*, vol. 7, no. 1, pp. 1–26, 1979.

---

## Ghi chú kỹ thuật

- Nguồn: danh mục cuối Chương 1 (`[1]`–`[5]`, tệp `report/01_gioi_thieu.md`), giữ nguyên văn từng mục. Các thuật toán/kỹ thuật chuẩn (GLCM, LBP, HOG, SVM, Random Forest, nội suy Platt, pHash) và thư viện/công cụ triển khai (`scikit-learn`, `imagehash`, `Streamlit`, kho artifact `duc16/cxr-svm-demo`) đã nêu rõ tên, tham số và phiên bản trong báo cáo nên được lược khỏi danh mục IEEE để giữ trọng tâm vào các tài liệu nền trực tiếp của bài toán.
- Thứ tự xuất hiện: `[1]`, `[2]`, `[3]`, `[4]` ở mục 1.1; `[5]` ở mục 1.2; Chương 2, 4 và 6 chỉ trích dẫn lại từ `[1]`–`[4]`.
