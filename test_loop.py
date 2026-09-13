import os
import json
from backend.document_ai.ocr import get_ocr_engine
from backend.document_ai.embeddings import DocumentEmbedder

metadata_path = 'data/processed/invoices_images/documents_metadata.json'
with open(metadata_path, 'r') as f:
    metadata = json.load(f)

print("Loading OCR Engine...")
ocr_engine = get_ocr_engine('tesseract')
print("Loading Embedder...")
embedder = DocumentEmbedder()

print("Processing doc 0...")
doc_id = metadata[0]['document_id']
img_path = f"data/processed/invoices_images/{doc_id}.png"

print("1. Extracting OCR...")
ocr_result = ocr_engine.extract(img_path)
print("OCR done. raw text len:", len(ocr_result['raw_text']))

print("2. Extracting Embeddings...")
emb = embedder.get_text_embedding(ocr_result['raw_text'])
print("Emb done. len:", len(emb))
print("All done!")
