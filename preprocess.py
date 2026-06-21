from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from typing import Union, Tuple

class ImagePreprocessor:
    MAX_SIZE = 1024
    
    def __init__(self, max_size: int = 1024):
        self.max_size = max_size
    
    @staticmethod
    def load_image(uploaded_file) -> Image.Image:
        return Image.open(uploaded_file).convert("RGB")
    
    def load_and_normalize(self, uploaded_file) -> np.ndarray:
        image = self.load_image(uploaded_file)
        image.thumbnail((self.max_size, self.max_size), Image.Resampling.LANCZOS)
        
        img_array = np.array(image)
        normalized_array = img_array / 255.0
        
        return normalized_array
    
    @staticmethod
    def denoise(image: Image.Image) -> Image.Image:
        # Lọc nhiễu bằng bộ lọc hạt (MedianFilter) của PIL
        return image.filter(ImageFilter.MedianFilter(size=3))
    
    @staticmethod
    def enhance_contrast(image: Image.Image, factor: float = 1.5) -> Image.Image:
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def enhance_brightness(image: Image.Image, factor: float = 1.1) -> Image.Image:
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def enhance_sharpness(image: Image.Image, factor: float = 2.0) -> Image.Image:
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def apply_gaussian_blur(image: Image.Image, radius: int = 1) -> Image.Image:
        return image.filter(ImageFilter.GaussianBlur(radius=radius))
    
    @staticmethod
    def convert_to_grayscale(image: Image.Image) -> Image.Image:
        return image.convert("L")
    
    def apply_full_preprocessing(self, image: Image.Image) -> Image.Image:
        # Bước 1: Khử nhiễu
        image = self.denoise(image)
        
        # Bước 2: Tăng độ nét
        image = self.enhance_sharpness(image, factor=1.5)
        
        # Bước 3: Chuyển sang ảnh xám
        image = self.convert_to_grayscale(image)
        
        # Bước 4: Tăng độ tương phản
        image = self.enhance_contrast(image, factor=1.3)
        
        return image
    
    def apply_light_preprocessing(self, image: Image.Image) -> Image.Image:
        # Chuyển sang ảnh xám
        image = self.convert_to_grayscale(image)
        
        # Tăng độ tương phản
        image = self.enhance_contrast(image, factor=1.2)
        
        # Tăng độ nét
        image = self.enhance_sharpness(image, factor=1.3)
        
        return image

# Các hàm gọi ngoài để tương thích với app.py của nhóm
def load_and_normalize(uploaded_file, max_size=1024) -> np.ndarray:
    preprocessor = ImagePreprocessor(max_size=max_size)
    return preprocessor.load_and_normalize(uploaded_file)

def load_image(uploaded_file) -> Image.Image:
    return ImagePreprocessor.load_image(uploaded_file)