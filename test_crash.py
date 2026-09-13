import cv2
from PIL import Image
import imagehash
from backend.document_ai.ocr import get_ocr_engine

img_path = 'data/processed/invoices_images/DOC_INV_0ec0ad4b.png'

print("1. PIL ImageHash")
img_pil = Image.open(img_path)
h = imagehash.phash(img_pil)
print("Hash done:", h)

print("2. CV2 OCR Engine")
ocr_engine = get_ocr_engine('tesseract')
ocr_result = ocr_engine.extract(img_path)
print("OCR done. len:", len(ocr_result['raw_text']))
