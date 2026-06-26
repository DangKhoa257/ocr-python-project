
# OCR Python Project - Receipt Information Extraction

## Đề tài
Xây dựng hệ thống OCR trích xuất và phân tích thông tin từ ảnh hóa đơn bán hàng bằng Python.

## Dataset
Sử dụng SROIE2019 dataset.

Cấu trúc dataset:
- train/img: ảnh hóa đơn
- train/entities: thông tin đúng gồm company, date, address, total
- train/box: text và tọa độ chữ

## Pipeline
Ảnh hóa đơn → Tiền xử lý ảnh → OCR bằng EasyOCR → Lưu kết quả CSV → Trích xuất thông tin → Đánh giá kết quả → Demo bằng Streamlit.

## Cấu trúc project
- app.py: giao diện Streamlit
- preprocess.py: tiền xử lý ảnh
- ocr_engine.py: chạy OCR
- batch_ocr.py: OCR nhiều ảnh
- receipt_extractor.py: trích xuất thông tin hóa đơn
- evaluate_results.py: đánh giá kết quả
- analysis.py: phân tích và vẽ biểu đồ