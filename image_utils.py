from PIL import Image
import numpy as np

def load_and_normalize(uploaded_file, max_size=1024):
    # Đọc và Resize ảnh
    image = Image.open(uploaded_file).convert("RGB")
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    # Chuyển sang Numpy array
    img_array = np.array(image)
    
    # Chuẩn hóa giá trị pixel về khoảng [0.0, 1.0]
    normalized_array = img_array / 255.0
    
    return normalized_array
