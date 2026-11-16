# Tài liệu tham khảo

Danh mục này gộp toàn bộ tài liệu được trích dẫn trong sáu chương, đánh số theo chuẩn IEEE `[n]` theo thứ tự xuất hiện đầu tiên trong quyển báo cáo. Mười tài liệu đầu xuất hiện ở Chương 1 (mục 1.1 đến 1.3); một tài liệu xuất hiện ở Chương 2 (nội suy Platt, mục 2.7); hai tài liệu cuối xuất hiện ở Chương 5 (mục 5.5.1 và 5.5.2). Chương 3, 4 và 6 chỉ dùng lại các tài liệu đã có số thứ tự nên không phát sinh số mới. Chú thích chân trang `[^covid-src]` thuộc Chương 2; chú thích `[^mooney]` xuất hiện ở Chương 1 (mục 1.1) và được dùng lại ở Chương 2 (mục 2.1); cả hai không nằm trong danh mục này và khi chuyển sang Word được chèn thành footnote tại chỗ như ở bản thảo các chương.

[1] M. E. H. Chowdhury, T. Rahman, A. Khandakar, R. Mazhar, M. A. Kadir, Z. B. Mahbub, K. R. Islam, M. S. Khan, A. Iqbal, N. Al-Emadi, M. B. I. Reaz, and M. T. Islam, "Can AI help in screening viral and COVID-19 pneumonia?," *IEEE Access*, vol. 8, pp. 132665–132676, 2020, doi: 10.1109/ACCESS.2020.3010287.

[2] T. Rahman, A. Khandakar, Y. Qiblawey, A. Tahir, S. Kiranyaz, S. B. A. Kashem, M. T. Islam, S. Al Maadeed, S. M. Zughaier, M. S. Khan, and M. E. H. Chowdhury, "Exploring the effect of image enhancement techniques on COVID-19 detection using chest X-ray images," *Computers in Biology and Medicine*, vol. 132, p. 104319, 2021, doi: 10.1016/j.compbiomed.2021.104319.

[3] D. S. Kermany, M. Goldbaum, W. Cai, et al., "Identifying medical diagnoses and treatable diseases by image-based deep learning," *Cell*, vol. 172, no. 5, pp. 1122–1131.e9, 2018.

[4] R. Geirhos, J.-H. Jacobsen, C. Michaelis, R. Zemel, W. Brendel, M. Bethge, and F. A. Wichmann, "Shortcut learning in deep neural networks," *Nature Machine Intelligence*, vol. 2, no. 11, pp. 665–673, 2020, doi: 10.1038/s42256-020-00257-z.

[5] J. R. Zech, M. A. Badgeley, M. Liu, A. B. Costa, J. J. Titano, and E. K. Oermann, "Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study," *PLOS Medicine*, vol. 15, no. 11, e1002683, 2018, doi: 10.1371/journal.pmed.1002683.

[6] F. Pedregosa, G. Varoquaux, A. Gramfort, et al., "Scikit-learn: Machine learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.

[7] R. M. Haralick, K. Shanmugam, and I. Dinstein, "Textural features for image classification," *IEEE Trans. Syst., Man, Cybern.*, vol. SMC-3, no. 6, pp. 610–621, 1973.

[8] T. Ojala, M. Pietikäinen, and D. Harwood, "A comparative study of texture measures with classification based on featured distributions," *Pattern Recognit.*, vol. 29, no. 1, pp. 51–59, 1996.

[9] N. Dalal and B. Triggs, "Histograms of oriented gradients for human detection," in *Proc. IEEE Comput. Soc. Conf. Comput. Vis. Pattern Recognit. (CVPR)*, 2005, pp. 886–893.

[10] B. Efron, "Bootstrap methods: Another look at the jackknife," *Ann. Statist.*, vol. 7, no. 1, pp. 1–26, 1979.

[11] J. Platt, "Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods," in *Advances in Large Margin Classifiers*, A. J. Smola, Ed. Cambridge, MA: MIT Press, 1999, pp. 61–74.

[12] Nhóm 10, Lớp Khoa học máy tính 2024, "cxr-svm-demo: artifact bộ phân loại CXR bốn lớp," Hugging Face Hub, 2026. [Online]. Available: https://huggingface.co/duc16/cxr-svm-demo. [Accessed: 12-11-2026].

[13] Streamlit, "Streamlit documentation," 2026. [Online]. Available: https://docs.streamlit.io/. [Accessed: 12-11-2026].

---

## Ghi chú kỹ thuật

- Nguồn: ba danh mục riêng ở cuối Chương 1 (`[1]`–`[10]`, tệp `report/01_gioi_thieu.md`), cuối Chương 2 (`[11]`, tệp `report/02_du_lieu_va_phuong_phap.md`) và cuối Chương 5 (`[12]`, `[13]`, tệp `report/05_ket_qua_test_va_trien_khai.md`), ghép nguyên văn không sửa. Chương 3, 4 và 6 không có trích dẫn mới; Chương 3 không trích dẫn tài liệu ngoài.
- pHash (mục 1.2, 2.3) là kỹ thuật băm nhận thức không có một bài báo gốc duy nhất; bản dùng trong đề tài tính bằng thư viện mã nguồn mở `imagehash`, nên không đưa vào danh mục.
- Trích dẫn `van der Walt và cộng sự (2014)` ghi trong đề cương ban đầu của `report/README.md` không còn xuất hiện trong sáu chương đã viết, nên danh mục này không đưa vào; nếu về sau có chương cần, đánh số tiếp từ `[14]`.
- Thứ tự xuất hiện: `[1]`, `[2]`, `[3]`, `[4]`, `[5]`, `[6]` ở mục 1.1; `[7]`, `[8]`, `[9]` ở mục 1.2; `[10]` ở mục 1.3; `[11]` ở mục 2.7; `[12]` ở mục 5.5.1; `[13]` ở mục 5.5.2.
