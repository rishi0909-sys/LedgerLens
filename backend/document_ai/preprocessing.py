import cv2
import numpy as np
import os

def preprocess_image_for_ocr(image_path: str, output_path: str = None) -> np.ndarray:
    """
    Applies DIP techniques to improve OCR accuracy.
    Includes grayscale conversion, denoising, and thresholding.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")
        
    # 1. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Denoising (remove synthetic noise we added)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # 3. Thresholding (binarization)
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    if output_path:
        cv2.imwrite(output_path, thresh)
        
    return thresh
