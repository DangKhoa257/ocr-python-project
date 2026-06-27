import streamlit as st


def create_download_button(text):
    if not text.strip():
        st.warning("Không có dữ liệu để tải xuống!")
        return

    st.download_button(
        label="📥 Tải kết quả về file .txt",
        data=text,
        file_name="ket_qua_ocr.txt",
        mime="text/plain"
    )


def create_download_button_custom(text, filename):
    if not text.strip():
        st.warning("Không có dữ liệu để tải xuống!")
        return

    st.download_button(
        label=f"📥 Tải {filename}",
        data=text,
        file_name=filename,
        mime="text/plain"
    )