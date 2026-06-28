import streamlit as st
import csv
import io
from typing import Union, List, Dict, Any

# ------------------- HÀM CŨ (GIỮ NGUYÊN) -------------------
def create_download_button(text: str):
    """
    Tạo nút tải xuống file .txt với tên mặc định.
    """
    if not text or not text.strip():
        st.warning("Không có dữ liệu để tải xuống!")
        return

    st.download_button(
        label="📥 Tải kết quả về file .txt",
        data=text,
        file_name="ket_qua_ocr.txt",
        mime="text/plain"
    )

def create_download_button_custom(text: str, filename: str):
    """
    Tạo nút tải xuống file với tên tuỳ chỉnh.
    """
    if not text or not text.strip():
        st.warning("Không có dữ liệu để tải xuống!")
        return

    st.download_button(
        label=f"📥 Tải {filename}",
        data=text,
        file_name=filename,
        mime="text/plain"
    )

# ------------------- HÀM MỚI: CHUẨN HÓA DỮ LIỆU -------------------
def _normalize_data(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Chuyển đầu vào thành list các dict chứa các trường:
    image_name, ocr_text, company, date, address, total.
    """
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    return []

# ------------------- HÀM MỚI: ĐỊNH DẠNG CHUỖI -------------------
def format_ocr_data_to_txt(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
    """
    Chuyển dữ liệu OCR thành chuỗi văn bản TXT.
    """
    records = _normalize_data(data)
    if not records:
        return ""

    lines = []
    for idx, rec in enumerate(records, 1):
        lines.append(f"Hóa đơn #{idx}")
        lines.append(f"Tên ảnh    : {rec.get('image_name', '')}")
        lines.append(f"Công ty     : {rec.get('company', '')}")
        lines.append(f"Ngày        : {rec.get('date', '')}")
        lines.append(f"Địa chỉ     : {rec.get('address', '')}")
        lines.append(f"Tổng tiền   : {rec.get('total', '')}")
        lines.append(f"Văn bản OCR :\n{rec.get('ocr_text', '')}")
        lines.append("---")
    return "\n".join(lines)

def format_ocr_data_to_csv(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
    """
    Chuyển dữ liệu OCR thành chuỗi CSV (có header).
    """
    records = _normalize_data(data)
    if not records:
        return ""

    output = io.StringIO()
    fieldnames = ["image_name", "company", "date", "address", "total", "ocr_text"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for rec in records:
        row = {field: rec.get(field, "") for field in fieldnames}
        writer.writerow(row)
    return output.getvalue()

# ------------------- HÀM MỚI: NÚT TẢI XUỐNG TRONG STREAMLIT -------------------
def create_download_button_txt(data: Union[Dict[str, Any], List[Dict[str, Any]]],
                               filename: str = "ket_qua_ocr.txt"):
    """
    Tạo nút tải TXT từ dữ liệu OCR.
    """
    text = format_ocr_data_to_txt(data)
    if not text.strip():
        st.warning("Không có dữ liệu để tải xuống!")
        return
    st.download_button(
        label=f"📥 Tải {filename}",
        data=text,
        file_name=filename,
        mime="text/plain"
    )

def create_download_button_csv(data: Union[Dict[str, Any], List[Dict[str, Any]]],
                               filename: str = "ket_qua_ocr.csv"):
    """
    Tạo nút tải CSV từ dữ liệu OCR.
    """
    csv_data = format_ocr_data_to_csv(data)
    if not csv_data.strip():
        st.warning("Không có dữ liệu để tải xuống!")
        return
    st.download_button(
        label=f"📥 Tải {filename}",
        data=csv_data,
        file_name=filename,
        mime="text/csv"
    )

# ------------------- HÀM TỔNG QUÁT (TIỆN LỢI) -------------------
def create_download_button_general(data: Union[Dict[str, Any], List[Dict[str, Any]]],
                                   format_type: str = "txt",
                                   filename: str = None):
    """
    Tạo nút tải với định dạng được chỉ định ('txt' hoặc 'csv').
    """
    if format_type.lower() == "txt":
        if filename is None:
            filename = "ket_qua_ocr.txt"
        create_download_button_txt(data, filename)
    elif format_type.lower() == "csv":
        if filename is None:
            filename = "ket_qua_ocr.csv"
        create_download_button_csv(data, filename)
    else:
        st.error("Định dạng không hỗ trợ. Chỉ hỗ trợ 'txt' hoặc 'csv'.")

# ------------------- (TUỲ CHỌN) TEST NHANH -------------------
if __name__ == "__main__":
    # Chạy thử nếu file được thực thi trực tiếp
    test_data = {
        "image_name": "test.jpg",
        "ocr_text": "Đây là văn bản OCR",
        "company": "Công ty XYZ",
        "date": "01/01/2025",
        "address": "Hà Nội",
        "total": "1,000,000 VND"
    }
    print("--- TXT ---")
    print(format_ocr_data_to_txt(test_data))
    print("\n--- CSV ---")
    print(format_ocr_data_to_csv(test_data))
