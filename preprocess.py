"""
Preprocessing module for OCR application
Handles image loading and preprocessing to improve OCR accuracy
"""

from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2
from typing import Union, Tuple


class ImagePreprocessor:
    """Class to handle image loading and preprocessing for OCR"""
    
    MAX_SIZE = 1024
    
    def __init__(self, max_size: int = 1024):
        """
        Initialize ImagePreprocessor
        
        Args:
            max_size: Maximum dimension for resizing image
        """
        self.max_size = max_size
    
    @staticmethod
    def load_image(uploaded_file) -> Image.Image:
        """
        Load image from uploaded file
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            PIL Image object in RGB format
        """
        image = Image.open(uploaded_file).convert("RGB")
        return image
    
    def load_and_normalize(self, uploaded_file) -> np.ndarray:
        """
        Load image and normalize pixel values to [0.0, 1.0]
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Normalized numpy array
        """
        image = self.load_image(uploaded_file)
        image.thumbnail((self.max_size, self.max_size), Image.Resampling.LANCZOS)
        
        img_array = np.array(image)
        normalized_array = img_array / 255.0
        
        return normalized_array
    
    @staticmethod
    def denoise(image: Image.Image) -> Image.Image:
        """
        Remove noise from image using bilateral filter
        
        Args:
            image: PIL Image object
            
        Returns:
            Denoised PIL Image
        """
        img_array = np.array(image, dtype=np.uint8)
        
        # Apply bilateral filter to reduce noise while preserving edges
        denoised = cv2.bilateralFilter(img_array, 9, 75, 75)
        
        return Image.fromarray(denoised)
    
    @staticmethod
    def enhance_contrast(image: Image.Image, factor: float = 1.5) -> Image.Image:
        """
        Enhance image contrast for better text visibility
        
        Args:
            image: PIL Image object
            factor: Contrast enhancement factor (>1 increases contrast)
            
        Returns:
            Enhanced PIL Image
        """
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def enhance_brightness(image: Image.Image, factor: float = 1.1) -> Image.Image:
        """
        Adjust image brightness
        
        Args:
            image: PIL Image object
            factor: Brightness factor (>1 brightens, <1 darkens)
            
        Returns:
            Adjusted PIL Image
        """
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def enhance_sharpness(image: Image.Image, factor: float = 2.0) -> Image.Image:
        """
        Sharpen image to make text clearer
        
        Args:
            image: PIL Image object
            factor: Sharpness factor (>1 increases sharpness)
            
        Returns:
            Sharpened PIL Image
        """
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def apply_gaussian_blur(image: Image.Image, radius: int = 1) -> Image.Image:
        """
        Apply Gaussian blur to reduce noise
        
        Args:
            image: PIL Image object
            radius: Blur radius
            
        Returns:
            Blurred PIL Image
        """
        return image.filter(ImageFilter.GaussianBlur(radius=radius))
    
    @staticmethod
    def convert_to_grayscale(image: Image.Image) -> Image.Image:
        """
        Convert image to grayscale
        
        Args:
            image: PIL Image object
            
        Returns:
            Grayscale PIL Image
        """
        return image.convert("L")
    
    @staticmethod
    def binarize(image: Image.Image, threshold: int = 150) -> Image.Image:
        """
        Convert image to black and white (binary) for better OCR
        
        Args:
            image: PIL Image object (should be grayscale)
            threshold: Binary threshold value (0-255)
            
        Returns:
            Binarized PIL Image
        """
        img_array = np.array(image, dtype=np.uint8)
        _, binary = cv2.threshold(img_array, threshold, 255, cv2.THRESH_BINARY)
        
        return Image.fromarray(binary)
    
    @staticmethod
    def deskew(image: Image.Image) -> Image.Image:
        """
        Correct image skew/rotation for better text recognition
        
        Args:
            image: PIL Image object
            
        Returns:
            Deskewed PIL Image
        """
        img_array = np.array(image)
        
        # Convert to grayscale for processing
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return image
        
        # Get largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Fit rectangle and get rotation angle
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[2]
        
        # Rotate image if angle is significant
        if angle < -45:
            angle = 90 + angle
        
        if abs(angle) > 0.5:
            h, w = gray.shape
            center = (w // 2, h // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(img_array, rotation_matrix, (w, h))
            return Image.fromarray(rotated)
        
        return image
    
    def apply_full_preprocessing(self, image: Image.Image) -> Image.Image:
        """
        Apply full preprocessing pipeline for optimal OCR results
        
        Pipeline:
        1. Denoise
        2. Enhance sharpness
        3. Convert to grayscale
        4. Enhance contrast
        5. Deskew
        
        Args:
            image: PIL Image object
            
        Returns:
            Fully preprocessed PIL Image
        """
        # Step 1: Denoise
        image = self.denoise(image)
        
        # Step 2: Enhance sharpness
        image = self.enhance_sharpness(image, factor=1.5)
        
        # Step 3: Convert to grayscale
        image = self.convert_to_grayscale(image)
        
        # Step 4: Enhance contrast
        image = self.enhance_contrast(image, factor=1.3)
        
        # Step 5: Deskew
        image = self.deskew(image)
        
        return image
    
    def apply_light_preprocessing(self, image: Image.Image) -> Image.Image:
        """
        Apply light preprocessing (faster, good for most images)
        
        Pipeline:
        1. Convert to grayscale
        2. Enhance contrast
        3. Enhance sharpness
        
        Args:
            image: PIL Image object
            
        Returns:
            Lightly preprocessed PIL Image
        """
        # Convert to grayscale
        image = self.convert_to_grayscale(image)
        
        # Enhance contrast
        image = self.enhance_contrast(image, factor=1.2)
        
        # Enhance sharpness
        image = self.enhance_sharpness(image, factor=1.3)
        
        return image


# Standalone functions for backward compatibility
def load_and_normalize(uploaded_file, max_size=1024) -> np.ndarray:
    """
    Load and normalize image (legacy function)
    
    Args:
        uploaded_file: Streamlit uploaded file object
        max_size: Maximum dimension for resizing
        
    Returns:
        Normalized numpy array
    """
    preprocessor = ImagePreprocessor(max_size=max_size)
    return preprocessor.load_and_normalize(uploaded_file)


def load_image(uploaded_file) -> Image.Image:
    """
    Load image from uploaded file (legacy function)
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        PIL Image object
    """
    return ImagePreprocessor.load_image(uploaded_file)