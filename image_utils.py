from PIL import Image, ImageEnhance
import numpy as np
from typing import Tuple, Optional, Union
import streamlit as st

# ------------------- HÀM CŨ (GIỮ NGUYÊN) -------------------
def load_image(uploaded_file) -> Image.Image:
    """
    HÀM CŨ: Trả về ảnh PIL dạng RGB từ file upload.
    """
    try:
        return Image.open(uploaded_file).convert("RGB")
    except Exception as e:
        st.error(f"Lỗi khi đọc ảnh: {e}")
        return None

def load_and_normalize(uploaded_file, max_size: int = 1024) -> Optional[np.ndarray]:
    """
    HÀM CŨ: Resize ảnh giữ tỉ lệ và chuẩn hóa về mảng numpy [0, 1].
    """
    try:
        image = Image.open(uploaded_file).convert("RGB")
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        img_array = np.array(image)
        normalized_array = img_array / 255.0
        return normalized_array
    except Exception as e:
        st.error(f"Lỗi khi xử lý ảnh: {e}")
        return None

# ------------------- HÀM MỚI: KIỂM TRA -------------------
def validate_image(image: Image.Image) -> Tuple[bool, str]:
    """
    Kiểm tra tính hợp lệ của ảnh PIL trước khi đưa vào OCR.
    Trả về (True, "OK") nếu hợp lệ, ngược lại (False, "Lý do").
    """
    if image is None:
        return False, "Ảnh rỗng (None)"
    
    # Kiểm tra kích thước tối thiểu (tránh ảnh quá nhỏ)
    width, height = image.size
    if width < 50 or height < 50:
        return False, f"Ảnh quá nhỏ ({width}x{height}), cần ít nhất 50x50 pixel"
    
    # Kiểm tra số kênh màu (chỉ chấp nhận RGB hoặc grayscale)
    if image.mode not in ["RGB", "L"]:
        return False, f"Định dạng màu {image.mode} không được hỗ trợ, cần RGB hoặc grayscale"
    
    return True, "OK"

def is_valid_uploaded_file(uploaded_file) -> bool:
    """
    Kiểm tra file upload có phải ảnh hợp lệ không (dựa trên tên và loại MIME).
    """
    if uploaded_file is None:
        return False
    # Kiểm tra extension
    allowed_extensions = ["jpg", "jpeg", "png", "bmp", "tiff", "webp"]
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        st.warning(f"File {uploaded_file.name} có đuôi không hỗ trợ. Hỗ trợ: {', '.join(allowed_extensions)}")
        return False
    
    # Kiểm tra MIME type (nếu có)
    if hasattr(uploaded_file, 'type') and uploaded_file.type:
        if not uploaded_file.type.startswith("image/"):
            st.warning(f"File {uploaded_file.name} không phải định dạng ảnh (MIME: {uploaded_file.type})")
            return False
    return True

# ------------------- HÀM MỚI: LOAD TỪ ĐƯỜNG DẪN -------------------
def load_image_from_path(file_path: str) -> Optional[Image.Image]:
    """
    Tải ảnh từ đường dẫn local (dùng cho batch xử lý hoặc test).
    """
    try:
        image = Image.open(file_path).convert("RGB")
        return image
    except FileNotFoundError:
        st.error(f"Không tìm thấy file: {file_path}")
    except Exception as e:
        st.error(f"Lỗi khi đọc ảnh từ {file_path}: {e}")
    return None

# ------------------- HÀM MỚI: TIỀN XỬ LÝ CHO OCR -------------------
def preprocess_for_ocr(image: Image.Image, 
                       grayscale: bool = True, 
                       enhance_contrast: float = 1.5) -> Image.Image:
    """
    Tiền xử lý ảnh để tăng chất lượng OCR.
    - grayscale: Chuyển sang ảnh xám (giảm nhiễu màu).
    - enhance_contrast: Tăng độ tương phản (hệ số > 1).
    """
    if image is None:
        return None
    
    # Chuyển sang grayscale nếu cần
    if grayscale and image.mode != "L":
        image = image.convert("L")
    elif not grayscale and image.mode != "RGB":
        image = image.convert("RGB")
    
    # Tăng độ tương phản
    if enhance_contrast != 1.0:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(enhance_contrast)
    
    return image

def get_image_info(image: Image.Image) -> dict:
    """
    Lấy thông tin cơ bản của ảnh (để hiển thị lên UI hoặc log).
    """
    if image is None:
        return {}
    return {
        "size": image.size,
        "mode": image.mode,
        "format": image.format,
        "width": image.width,
        "height": image.height,
    }
