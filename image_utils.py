from typing import Optional, Tuple

import numpy as np
import streamlit as st
from PIL import Image, ImageEnhance


# ------------------- HÀM CŨ (GIỮ NGUYÊN) -------------------
def load_image(uploaded_file) -> Image.Image:
    """Trả về ảnh PIL dạng RGB từ file upload."""
    try:
        return Image.open(uploaded_file).convert("RGB")
    except Exception as error:
        st.error(f"Lỗi khi đọc ảnh: {error}")
        return None


def load_and_normalize(uploaded_file, max_size: int = 1024) -> Optional[np.ndarray]:
    """Resize ảnh giữ tỉ lệ và chuẩn hóa về mảng numpy [0, 1]."""
    try:
        image = Image.open(uploaded_file).convert("RGB")
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        img_array = np.array(image)
        return img_array / 255.0
    except Exception as error:
        st.error(f"Lỗi khi xử lý ảnh: {error}")
        return None


# ------------------- HÀM MỚI: KIỂM TRA -------------------
def validate_image(image: Image.Image) -> Tuple[bool, str]:
    """Kiểm tra tính hợp lệ của ảnh PIL trước khi đưa vào OCR."""
    if image is None:
        return False, "Ảnh rỗng (None)"

    width, height = image.size
    if width < 50 or height < 50:
        return False, f"Ảnh quá nhỏ ({width}x{height}), cần ít nhất 50x50 pixel"

    if image.mode not in ["RGB", "L"]:
        return False, f"Định dạng màu {image.mode} không được hỗ trợ, cần RGB hoặc grayscale"

    return True, "OK"


def is_valid_uploaded_file(uploaded_file) -> bool:
    """Kiểm tra file upload có phải ảnh hợp lệ không."""
    if uploaded_file is None:
        return False

    allowed_extensions = ["jpg", "jpeg", "png", "bmp", "tiff", "webp"]
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        st.warning(f"File {uploaded_file.name} có đuôi không hỗ trợ. Hỗ trợ: {', '.join(allowed_extensions)}")
        return False

    if hasattr(uploaded_file, "type") and uploaded_file.type:
        if not uploaded_file.type.startswith("image/"):
            st.warning(f"File {uploaded_file.name} không phải định dạng ảnh (MIME: {uploaded_file.type})")
            return False
    return True


# ------------------- HÀM MỚI: LOAD TỪ ĐƯỜNG DẪN -------------------
def load_image_from_path(file_path: str) -> Optional[Image.Image]:
    """Tải ảnh từ đường dẫn local."""
    try:
        image = Image.open(file_path).convert("RGB")
        return image
    except FileNotFoundError:
        st.error(f"Không tìm thấy file: {file_path}")
    except Exception as error:
        st.error(f"Lỗi khi đọc ảnh từ {file_path}: {error}")
    return None


# ------------------- HÀM MỚI: TIỀN XỬ LÝ CHO OCR -------------------
def preprocess_for_ocr(image: Image.Image, grayscale: bool = True, enhance_contrast: float = 1.5) -> Image.Image:
    """Tiền xử lý ảnh để tăng chất lượng OCR."""
    if image is None:
        return None

    if grayscale and image.mode != "L":
        image = image.convert("L")
    elif not grayscale and image.mode != "RGB":
        image = image.convert("RGB")

    if enhance_contrast != 1.0:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(enhance_contrast)

    return image


def get_image_info(image: Image.Image) -> dict:
    """Lấy thông tin cơ bản của ảnh."""
    if image is None:
        return {}
    return {
        "size": image.size,
        "mode": image.mode,
        "format": image.format,
        "width": image.width,
        "height": image.height,
    }
