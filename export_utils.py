import streamlit as st

def create_download_button(text):
    st.download_button(
        label="Tải kết quả về file .txt",
        data=text,
        file_name="ket_qua_ocr.txt",
        mime="text/plain"
    )