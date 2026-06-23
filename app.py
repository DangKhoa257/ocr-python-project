import streamlit as st

from image_utils import load_image
from preprocess import ImagePreprocessor
from ocr_engine import extract_text
from text_utils import clean_text, text_statistics
from export_utils import create_download_button


st.set_page_config(page_title="OCR Python App", layout="centered")

st.title("Ứng dụng OCR nhận diện văn bản từ ảnh")
st.write("Tải lên ảnh tài liệu hoặc hóa đơn, sau đó bấm nút để nhận diện văn bản.")

uploaded_file = st.file_uploader(
    "Chọn ảnh cần nhận diện",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is None:
    st.info("Vui lòng tải lên một ảnh định dạng PNG, JPG hoặc JPEG để bắt đầu.")
else:
    try:
        original_image = load_image(uploaded_file)

        st.subheader("Ảnh gốc")
        st.image(original_image, caption="Ảnh vừa tải lên", use_container_width=True)

        # Tiền xử lý ảnh để hỗ trợ OCR đọc văn bản tốt hơn
        preprocessor = ImagePreprocessor()
        processed_image = preprocessor.apply_light_preprocessing(original_image)

        st.subheader("Ảnh sau tiền xử lý")
        st.image(processed_image, caption="Ảnh đã tiền xử lý", use_container_width=True)

        if st.button("Nhận diện văn bản"):
            try:
                with st.spinner("Đang nhận diện văn bản..."):
                    raw_text = extract_text(processed_image)
                    final_text = clean_text(raw_text)

                st.subheader("Kết quả OCR")

                if final_text:
                    st.text_area("Văn bản nhận diện được", final_text, height=300)

                    stats = text_statistics(final_text)

                    st.subheader("Thống kê")
                    st.write("Số ký tự:", stats["characters"])
                    st.write("Số từ:", stats["words"])
                    st.write("Số dòng:", stats["lines"])

                    create_download_button(final_text)
                else:
                    st.warning("Không nhận diện được văn bản nào trong ảnh.")

            except Exception as error:
                st.error("Đã có lỗi khi nhận diện văn bản. Vui lòng thử lại với ảnh khác.")
                st.exception(error)

    except Exception as error:
        st.error("Đã có lỗi khi đọc hoặc tiền xử lý ảnh.")
        st.exception(error)