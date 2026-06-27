from PIL import Image
import numpy as np

def load_image(uploaded_file):
    """
    HÀM MỚI BỔ SUNG: Trả về ảnh PIL dạng RGB theo yêu cầu của nhóm
    """
    return Image.open(uploaded_file).convert("RGB")

def load_and_normalize(uploaded_file, max_size=1024):
    """
    HÀM CŨ: Giữ lại để phòng trường hợp sau này cần dùng tới
    """
    image = Image.open(uploaded_file).convert("RGB")
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    img_array = np.array(image)
    normalized_array = img_array / 255.0
    
    return normalized_array
