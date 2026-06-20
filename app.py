import streamlit as st

from image_utils import load_image
from ocr_engine import extract_text
from text_utils import clean_text, count_characters, count_lines
from export_utils import create_download_button

st.set_page_config(page_title="OCR Python App", layout="centered")

st.title("Ứng dụng OCR nhận diện văn bản từ ảnh")
st.write("Chọn ảnh có chứa văn bản, chương trình sẽ nhận diện chữ và xuất kết quả ra file .txt.")

uploaded_file = st.file_uploader(
    "Chọn ảnh cần nhận diện",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = load_image(uploaded_file)

    st.subheader("Ảnh đã chọn")
    st.image(image, caption="Ảnh đầu vào", use_container_width=True)

    if st.button("Nhận diện văn bản"):
        with st.spinner("Đang nhận diện văn bản..."):
            raw_text = extract_text(image)
            final_text = clean_text(raw_text)

        st.subheader("Kết quả OCR")
        st.text_area("Văn bản nhận diện được", final_text, height=300)

        st.write("Số dòng:", count_lines(final_text))
        st.write("Số ký tự:", count_characters(final_text))

        create_download_button(final_text)
else:
    st.info("Vui lòng chọn một ảnh để bắt đầu.")
    