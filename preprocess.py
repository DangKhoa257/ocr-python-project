import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Union

class ImagePreprocessor:
    MAX_SIZE = 1024
    
    def __init__(self, max_size: int = 1024):
        self.max_size = max_size
    
    @staticmethod
    def load_image(uploaded_file) -> Image.Image:
        # Load ảnh từ file upload sang định dạng RGB
        return Image.open(uploaded_file).convert("RGB")
    
    def load_and_normalize(self, uploaded_file) -> np.ndarray:
        # Load, resize tự động và chuẩn hóa pixel về khoảng [0.0, 1.0]
        image = self.load_image(uploaded_file)
        image.thumbnail((self.max_size, self.max_size), Image.Resampling.LANCZOS)
        img_array = np.array(image)
        return img_array / 255.0
    
    @staticmethod
    def denoise(image: Image.Image, size: int = 3) -> Image.Image:
        # Khử nhiễu bằng MedianFilter (giữ nguyên độ nét viền chữ)
        return image.filter(ImageFilter.MedianFilter(size=size))
    
    @staticmethod
    def enhance_contrast(image: Image.Image, factor: float = 1.5) -> Image.Image:
        # Tăng độ tương phản (làm chữ tách biệt khỏi nền)
        return ImageEnhance.Contrast(image).enhance(factor)
    
    @staticmethod
    def enhance_brightness(image: Image.Image, factor: float = 1.1) -> Image.Image:
        # Điều chỉnh độ sáng
        return ImageEnhance.Brightness(image).enhance(factor)
    
    @staticmethod
    def enhance_sharpness(image: Image.Image, factor: float = 2.0) -> Image.Image:
        # Tăng độ sắc nét cho viền chữ
        return ImageEnhance.Sharpness(image).enhance(factor)
    
    @staticmethod
    def apply_gaussian_blur(image: Image.Image, radius: int = 1) -> Image.Image:
        # Làm mờ (tùy chọn)
        return image.filter(ImageFilter.GaussianBlur(radius=radius))
    
    @staticmethod
    def convert_to_grayscale(image: Image.Image) -> Image.Image:
        # Chuyển đổi sang ảnh xám
        return image.convert("L")
    
    @staticmethod
    def apply_sharpen(image: Image.Image) -> Image.Image:
        # Áp dụng bộ lọc SHARPEN có sẵn của PIL
        return image.filter(ImageFilter.SHARPEN)
    
    def apply_full_preprocessing(self, image: Image.Image) -> Image.Image:
        # Luồng xử lý tiêu chuẩn đầy đủ các bước
        image = self.denoise(image, size=3)
        image = self.convert_to_grayscale(image)
        image = self.enhance_contrast(image, factor=1.3)
        return self.enhance_sharpness(image, factor=1.5)
    
    def apply_light_preprocessing(self, image: Image.Image) -> Image.Image:
        # Luồng xử lý nhẹ và nhanh (bỏ qua bước khử nhiễu)
        image = self.convert_to_grayscale(image)
        image = self.enhance_contrast(image, factor=1.2)
        return self.enhance_sharpness(image, factor=1.3)
    
    def process_invoice_image(self, image: Image.Image, target_size: int = 1280) -> Image.Image:
        # Luồng TỐI ƯU cho dataset hóa đơn SROIE
        image.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        image = self.convert_to_grayscale(image)
        image = self.enhance_contrast(image, factor=1.4)
        image = self.enhance_sharpness(image, factor=1.8)
        return self.denoise(image, size=3)
    
    def process_invoice_image_aggressive(self, image: Image.Image, target_size: int = 1280) -> Image.Image:
        # Luồng CỰC MẠNH dùng cho hóa đơn mờ, nhòe, thiếu sáng nặng
        image.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        image = self.convert_to_grayscale(image)
        image = self.enhance_contrast(image, factor=1.6)
        image = self.enhance_sharpness(image, factor=2.2)
        image = self.denoise(image, size=5)
        return self.enhance_contrast(image, factor=1.3)