import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


class ImagePreprocessor:
    MAX_SIZE = 1024

    def __init__(self, max_size: int = 1024):
        self.max_size = max_size

    @staticmethod
    def load_image(uploaded_file) -> Image.Image:
        # Load ảnh upload sang định dạng RGB.
        return Image.open(uploaded_file).convert("RGB")

    def load_and_normalize(self, uploaded_file) -> np.ndarray:
        # Resize ảnh và chuẩn hóa pixel về khoảng [0.0, 1.0].
        image = self.load_image(uploaded_file)
        image.thumbnail((self.max_size, self.max_size), Image.Resampling.LANCZOS)
        img_array = np.array(image)
        return img_array / 255.0

    @staticmethod
    def denoise(image: Image.Image, size: int = 3) -> Image.Image:
        # Khử nhiễu bằng MedianFilter.
        return image.filter(ImageFilter.MedianFilter(size=size))

    @staticmethod
    def enhance_contrast(image: Image.Image, factor: float = 1.5) -> Image.Image:
        # Tăng độ tương phản để chữ rõ hơn.
        return ImageEnhance.Contrast(image).enhance(factor)

    @staticmethod
    def enhance_brightness(image: Image.Image, factor: float = 1.1) -> Image.Image:
        # Điều chỉnh độ sáng.
        return ImageEnhance.Brightness(image).enhance(factor)

    @staticmethod
    def enhance_sharpness(image: Image.Image, factor: float = 2.0) -> Image.Image:
        # Tăng độ sắc nét cho viền chữ.
        return ImageEnhance.Sharpness(image).enhance(factor)

    @staticmethod
    def apply_gaussian_blur(image: Image.Image, radius: int = 1) -> Image.Image:
        # Làm mờ nhẹ nếu cần.
        return image.filter(ImageFilter.GaussianBlur(radius=radius))

    @staticmethod
    def convert_to_grayscale(image: Image.Image) -> Image.Image:
        # Chuyển ảnh sang ảnh xám.
        return image.convert("L")

    @staticmethod
    def apply_sharpen(image: Image.Image) -> Image.Image:
        # Áp dụng bộ lọc SHARPEN có sẵn của PIL.
        return image.filter(ImageFilter.SHARPEN)

    def apply_full_preprocessing(self, image: Image.Image) -> Image.Image:
        # Luồng xử lý đầy đủ.
        image = self.denoise(image, size=3)
        image = self.convert_to_grayscale(image)
        image = self.enhance_contrast(image, factor=1.3)
        return self.enhance_sharpness(image, factor=1.5)

    def apply_light_preprocessing(self, image: Image.Image) -> Image.Image:
        # Luồng xử lý nhẹ và nhanh.
        image = self.convert_to_grayscale(image)
        image = self.enhance_contrast(image, factor=1.2)
        return self.enhance_sharpness(image, factor=1.3)

    def process_invoice_image(self, image: Image.Image, target_size: int = 960) -> Image.Image:
        # Luồng nhanh cho OCR hàng loạt dataset SROIE.
        image.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        image = self.convert_to_grayscale(image)
        image = self.enhance_contrast(image, factor=1.25)
        image = self.enhance_sharpness(image, factor=1.2)
        return image

    def process_invoice_image_aggressive(self, image: Image.Image, target_size: int = 1280) -> Image.Image:
        # Luồng mạnh cho hóa đơn mờ hoặc thiếu sáng.
        image.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        image = self.convert_to_grayscale(image)
        image = self.enhance_contrast(image, factor=1.6)
        image = self.enhance_sharpness(image, factor=2.2)
        image = self.denoise(image, size=5)
        return self.enhance_contrast(image, factor=1.3)
