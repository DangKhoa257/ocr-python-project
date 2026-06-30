import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

from export_utils import format_ocr_data_to_csv, format_ocr_data_to_txt
from image_utils import load_image
from ocr_engine import extract_text
from preprocess import ImagePreprocessor
from receipt_extractor import extract_address, extract_company, extract_date, extract_total
from text_utils import clean_text, text_statistics


IMAGE_TYPES = ["png", "jpg", "jpeg"]
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg")
BATCH_TABLE_COLUMNS = ["image_name", "company", "date", "total", "status"]


st.set_page_config(
    page_title="OCR Receipt App",
    page_icon="🧾",
    layout="wide",
)


st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #f7f9ff 0%, #eef2f8 100%);
            color: #172033;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1180px;
        }

        .hero {
            padding: 30px 32px;
            border-radius: 18px;
            background: linear-gradient(135deg, #2563eb 0%, #6d5dfc 55%, #7c3aed 100%);
            color: white;
            box-shadow: 0 16px 38px rgba(37, 99, 235, 0.22);
            margin-bottom: 22px;
        }

        .hero h1 {
            margin: 0 0 8px 0;
            font-size: 2.15rem;
            line-height: 1.2;
            font-weight: 800;
        }

        .hero p {
            margin: 0 0 18px 0;
            font-size: 1.02rem;
            color: rgba(255, 255, 255, 0.9);
        }

        .badge-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .badge {
            padding: 7px 12px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.16);
            border: 1px solid rgba(255, 255, 255, 0.28);
            font-size: 0.9rem;
            font-weight: 650;
        }

        .mode-card {
            padding: 16px 18px;
            border-radius: 14px;
            background: #ffffff;
            border: 1px solid #e4e9f5;
            box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
            margin: 12px 0 18px 0;
        }

        .mode-card h3 {
            margin: 0 0 6px 0;
            color: #1d2b53;
            font-size: 1.05rem;
        }

        .mode-card p {
            margin: 0;
            color: #5d6b82;
            line-height: 1.55;
        }

        .info-card {
            padding: 15px 16px;
            border-radius: 14px;
            background: #ffffff;
            border: 1px solid #e4e9f5;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
            margin-bottom: 12px;
            min-height: 92px;
        }

        .info-label {
            color: #64748b;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            margin-bottom: 6px;
        }

        .info-value {
            color: #0f172a;
            font-size: 1rem;
            font-weight: 750;
            word-break: break-word;
        }

        .small-note {
            color: #64748b;
            font-size: 0.92rem;
            line-height: 1.5;
        }

        div.stButton > button {
            border-radius: 12px;
            border: 0;
            background: linear-gradient(135deg, #2563eb, #5b5ff5);
            color: white;
            font-weight: 750;
            min-height: 42px;
            box-shadow: 0 8px 18px rgba(37, 99, 235, 0.18);
        }

        div.stButton > button:hover {
            color: white;
            background: linear-gradient(135deg, #1d4ed8, #4f46e5);
            box-shadow: 0 10px 22px rgba(37, 99, 235, 0.24);
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e4e9f5;
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
        }

        div[data-testid="stDataFrame"] {
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid #e4e9f5;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
        }

        section[data-testid="stSidebar"] {
            background: #111827;
        }

        section[data-testid="stSidebar"] * {
            color: #e5e7eb;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_preprocessor():
    """Dùng lại bộ tiền xử lý ảnh."""
    return ImagePreprocessor()


def render_mode_card(title, description):
    """Hiển thị mô tả ngắn cho từng chế độ."""
    st.markdown(
        f"""
        <div class="mode-card">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_card(label, value):
    """Hiển thị một ô thông tin hóa đơn."""
    value = value if value else "Chưa nhận diện"
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-label">{label}</div>
            <div class="info-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def image_to_result(image_name, ocr_text, status="success", error_message=""):
    """Tạo dict kết quả theo cấu trúc thống nhất."""
    final_text = clean_text(ocr_text)
    stats = text_statistics(final_text)

    return {
        "image_name": image_name,
        "company": extract_company(final_text),
        "date": extract_date(final_text),
        "address": extract_address(final_text),
        "total": extract_total(final_text),
        "ocr_text": final_text,
        "num_characters": stats["characters"],
        "num_words": stats["words"],
        "num_lines": stats["lines"],
        "status": status,
        "error_message": error_message,
    }


def error_result(image_name, error):
    """Tạo kết quả khi một ảnh bị lỗi."""
    return {
        "image_name": image_name,
        "company": "",
        "date": "",
        "address": "",
        "total": "",
        "ocr_text": "",
        "num_characters": 0,
        "num_words": 0,
        "num_lines": 0,
        "status": "error",
        "error_message": str(error),
    }


def process_single_image(image, image_name):
    """OCR một ảnh và trích xuất thông tin hóa đơn."""
    try:
        preprocessor = get_preprocessor()
        processed_image = preprocessor.process_invoice_image(image.copy())
        raw_text = extract_text(processed_image)
        return image_to_result(image_name, raw_text)
    except Exception as error:
        return error_result(image_name, error)


def process_uploaded_files(uploaded_files):
    """OCR nhiều ảnh upload cùng lúc."""
    results = []
    total = len(uploaded_files)
    progress_bar = st.progress(0)
    status_text = st.empty()

    for index, uploaded_file in enumerate(uploaded_files, start=1):
        status_text.info(f"Đang xử lý {index}/{total}: {uploaded_file.name}")

        try:
            image = load_image(uploaded_file)
            results.append(process_single_image(image, uploaded_file.name))
        except Exception as error:
            results.append(error_result(uploaded_file.name, error))

        progress_bar.progress(index / total)

    status_text.success("Hoàn thành")
    return results


def process_local_folder(folder_path):
    """OCR tất cả ảnh trong một thư mục local."""
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        st.error("Thư mục không tồn tại. Vui lòng kiểm tra lại đường dẫn.")
        return []

    image_paths = sorted(
        path for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )

    if not image_paths:
        st.warning("Không tìm thấy ảnh .png, .jpg hoặc .jpeg trong thư mục này.")
        return []

    results = []
    total = len(image_paths)
    progress_bar = st.progress(0)
    status_text = st.empty()

    for index, image_path in enumerate(image_paths, start=1):
        status_text.info(f"Đang xử lý {index}/{total}: {image_path.name}")

        try:
            image = Image.open(image_path).convert("RGB")
            results.append(process_single_image(image, image_path.name))
        except Exception as error:
            results.append(error_result(image_path.name, error))

        progress_bar.progress(index / total)

    status_text.success("Hoàn thành")
    return results


def process_zip_file(zip_file):
    """OCR ảnh nằm trong file ZIP."""
    results = []

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = temp_path / "images.zip"
        zip_path.write_bytes(zip_file.getvalue())

        try:
            with zipfile.ZipFile(zip_path, "r") as archive:
                archive.extractall(temp_path)
        except zipfile.BadZipFile:
            st.error("File ZIP không hợp lệ.")
            return []

        image_paths = sorted(
            path for path in temp_path.rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        )

        if not image_paths:
            st.warning("File ZIP không chứa ảnh .png, .jpg hoặc .jpeg.")
            return []

        total = len(image_paths)
        progress_bar = st.progress(0)
        status_text = st.empty()

        for index, image_path in enumerate(image_paths, start=1):
            relative_name = str(image_path.relative_to(temp_path))
            status_text.info(f"Đang xử lý {index}/{total}: {relative_name}")

            try:
                image = Image.open(image_path).convert("RGB")
                results.append(process_single_image(image, relative_name))
            except Exception as error:
                results.append(error_result(relative_name, error))

            progress_bar.progress(index / total)

        status_text.success("Hoàn thành")

    return results


def show_single_result(result_dict, original_image=None, processed_image=None, image_name=""):
    """Hiển thị kết quả OCR một ảnh."""
    if result_dict.get("status") == "error":
        st.error(f"Lỗi xử lý ảnh: {result_dict.get('error_message', '')}")
        return

    left_col, right_col = st.columns([1, 1.1], gap="large")

    with left_col:
        st.subheader("Ảnh hóa đơn")
        if original_image is not None:
            st.image(original_image, caption=image_name or "Ảnh gốc", use_container_width=True)
        if processed_image is not None:
            st.image(processed_image, caption="Ảnh sau tiền xử lý", use_container_width=True)

    with right_col:
        st.subheader("Thông tin trích xuất")
        card_col_1, card_col_2 = st.columns(2)
        with card_col_1:
            render_info_card("Company", result_dict["company"])
            render_info_card("Date", result_dict["date"])
        with card_col_2:
            render_info_card("Total", result_dict["total"])
            render_info_card("Address", result_dict["address"])

        st.subheader("Thống kê văn bản")
        metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
        metric_col_1.metric("Số ký tự", result_dict["num_characters"])
        metric_col_2.metric("Số từ", result_dict["num_words"])
        metric_col_3.metric("Số dòng", result_dict["num_lines"])

        with st.expander("Xem văn bản OCR đầy đủ"):
            st.text_area("OCR text", result_dict["ocr_text"], height=260)

        download_col_1, download_col_2 = st.columns(2)
        with download_col_1:
            st.download_button(
                label="⬇️ Tải TXT",
                data=format_ocr_data_to_txt(result_dict),
                file_name="ket_qua_ocr.txt",
                mime="text/plain",
            )
        with download_col_2:
            st.download_button(
                label="⬇️ Tải CSV",
                data=format_ocr_data_to_csv(result_dict),
                file_name="ket_qua_ocr.csv",
                mime="text/csv",
            )


def show_batch_results(results_list):
    """Hiển thị bảng kết quả OCR nhiều ảnh."""
    if not results_list:
        return

    df = pd.DataFrame(results_list)
    total_images = len(df)
    success_images = int((df["status"] == "success").sum())
    error_images = total_images - success_images

    st.success(f"Đã xử lý xong {total_images} ảnh")

    metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
    metric_col_1.metric("Tổng ảnh", total_images)
    metric_col_2.metric("Ảnh thành công", success_images)
    metric_col_3.metric("Ảnh lỗi", error_images)

    st.subheader("Bảng kết quả tổng hợp")
    display_columns = [column for column in BATCH_TABLE_COLUMNS if column in df.columns]
    st.dataframe(df[display_columns], use_container_width=True, hide_index=True)

    csv_data = format_ocr_data_to_csv(results_list)
    st.download_button(
        label="⬇️ Tải kết quả batch CSV",
        data=csv_data,
        file_name="ket_qua_ocr_batch.csv",
        mime="text/csv",
    )

    with st.expander("Xem dữ liệu đầy đủ"):
        st.dataframe(df, use_container_width=True)


def show_single_image_tab():
    render_mode_card(
        "📷 OCR một ảnh",
        "Tải lên một ảnh hóa đơn, xem ảnh sau tiền xử lý và trích xuất company, date, address, total.",
    )

    uploaded_file = st.file_uploader(
        "Chọn một ảnh hóa đơn",
        type=IMAGE_TYPES,
        key="single_image",
    )

    if uploaded_file is None:
        st.info("Vui lòng tải ảnh hoặc chọn nguồn dữ liệu để bắt đầu OCR.")
        return

    try:
        original_image = load_image(uploaded_file)
        preprocessor = get_preprocessor()
        processed_image = preprocessor.process_invoice_image(original_image.copy())
    except Exception as error:
        st.error("Không đọc được ảnh. Vui lòng thử ảnh khác.")
        st.exception(error)
        return

    if st.button("Nhận diện hóa đơn", key="run_single"):
        with st.spinner("Đang OCR hóa đơn..."):
            result = process_single_image(original_image, uploaded_file.name)
        show_single_result(result, original_image, processed_image, uploaded_file.name)
    else:
        preview_col_1, preview_col_2 = st.columns(2)
        with preview_col_1:
            st.image(original_image, caption="Ảnh gốc", use_container_width=True)
        with preview_col_2:
            st.image(processed_image, caption="Ảnh sau tiền xử lý", use_container_width=True)


def show_multi_upload_tab():
    render_mode_card(
        "🖼️ OCR nhiều ảnh upload",
        "Upload nhiều ảnh cùng lúc và xuất một file CSV tổng hợp. Xử lý nhiều ảnh có thể mất thời gian.",
    )

    uploaded_files = st.file_uploader(
        "Chọn nhiều ảnh hóa đơn",
        type=IMAGE_TYPES,
        accept_multiple_files=True,
        key="multi_images",
    )

    if not uploaded_files:
        st.info("Vui lòng tải ảnh hoặc chọn nguồn dữ liệu để bắt đầu OCR.")

    if st.button("Xử lý nhiều ảnh", key="run_multi"):
        if not uploaded_files:
            st.warning("Vui lòng chọn ít nhất một ảnh.")
            return

        with st.spinner("Đang OCR nhiều ảnh..."):
            results = process_uploaded_files(uploaded_files)
        show_batch_results(results)


def show_local_folder_tab():
    render_mode_card(
        "📁 OCR folder local",
        "Nhập đường dẫn thư mục ảnh trên máy cá nhân.",
    )

    folder_path = st.text_input(
        "Nhập đường dẫn thư mục ảnh local",
        placeholder=r"D:\archive\SROIE2019\train\img",
    )

    if not folder_path:
        st.info("Vui lòng tải ảnh hoặc chọn nguồn dữ liệu để bắt đầu OCR.")

    if st.button("Quét thư mục", key="run_folder"):
        if not folder_path.strip():
            st.warning("Vui lòng nhập đường dẫn thư mục.")
            return

        with st.spinner("Đang OCR thư mục ảnh..."):
            results = process_local_folder(folder_path.strip())
        show_batch_results(results)


def show_zip_tab():
    render_mode_card(
        "📦 OCR file ZIP",
        "Upload một file ZIP chứa nhiều ảnh hóa đơn. App sẽ giải nén tạm và xử lý từng ảnh.",
    )

    zip_file = st.file_uploader(
        "Chọn file ZIP chứa ảnh",
        type=["zip"],
        key="zip_file",
    )

    if zip_file is None:
        st.info("Vui lòng tải ảnh hoặc chọn nguồn dữ liệu để bắt đầu OCR.")

    if st.button("Xử lý file ZIP", key="run_zip"):
        if zip_file is None:
            st.warning("Vui lòng chọn một file ZIP.")
            return

        with st.spinner("Đang giải nén và OCR file ZIP..."):
            results = process_zip_file(zip_file)
        show_batch_results(results)


def render_sidebar():
    """Hiển thị sidebar giới thiệu project."""
    with st.sidebar:
        st.title("OCR Receipt App")
        st.write("Mini dashboard OCR hóa đơn bằng Streamlit và EasyOCR.")

        st.markdown("---")
        st.subheader("Pipeline")
        st.write("1. Upload ảnh")
        st.write("2. Tiền xử lý")
        st.write("3. OCR bằng EasyOCR")
        st.write("4. Trích xuất thông tin")
        st.write("5. Xuất CSV/TXT")

        st.markdown("---")
        st.subheader("Lưu ý")
        st.write("- Xử lý nhiều ảnh có thể mất thời gian.")
        st.write("- Folder local chỉ dùng khi chạy trên máy cá nhân.")


def render_header():
    """Hiển thị hero header."""
    st.markdown(
        """
        <div class="hero">
            <h1>🧾 OCR Receipt Information Extraction</h1>
            <p>Nhận diện văn bản và trích xuất thông tin chính từ ảnh hóa đơn</p>
            <div class="badge-row">
                <span class="badge">1 ảnh</span>
                <span class="badge">Nhiều ảnh</span>
                <span class="badge">Folder local</span>
                <span class="badge">ZIP batch</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


render_sidebar()
render_header()

single_tab, multi_tab, folder_tab, zip_tab = st.tabs([
    "📷 Một ảnh",
    "🖼️ Nhiều ảnh",
    "📁 Folder local",
    "📦 File ZIP",
])

with single_tab:
    show_single_image_tab()

with multi_tab:
    show_multi_upload_tab()

with folder_tab:
    show_local_folder_tab()

with zip_tab:
    show_zip_tab()
