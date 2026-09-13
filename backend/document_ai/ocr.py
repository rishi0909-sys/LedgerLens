import pytesseract
from typing import Protocol, Dict, Any
import cv2
import numpy as np

class OCREngine(Protocol):
    def extract(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text from an image.
        Returns a dict containing:
        - raw_text: str
        - data: list of dicts with bounding boxes and confidences (if supported)
        """
        ...

class TesseractOCR:
    def __init__(self, config: str = '--psm 6'):
        self.config = config
        
    def extract(self, image_path: str) -> Dict[str, Any]:
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found at {image_path}")
            
        # Get raw text
        raw_text = pytesseract.image_to_string(img, config=self.config)
        
        # Get structured data (bounding boxes, confidences)
        # Using dict output
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=self.config)
        
        # Filter out empty text blocks
        structured_data = []
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if text:
                structured_data.append({
                    'text': text,
                    'left': data['left'][i],
                    'top': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'conf': data['conf'][i]
                })
                
        h, w = img.shape[:2]
        return {
            'raw_text': raw_text,
            'data': structured_data,
            'dimensions': {'width': w, 'height': h}
        }

# Factory function to get OCR engine
def get_ocr_engine(engine_name: str = 'tesseract') -> OCREngine:
    if engine_name.lower() == 'tesseract':
        return TesseractOCR()
    raise ValueError(f"Unknown OCR engine: {engine_name}")
