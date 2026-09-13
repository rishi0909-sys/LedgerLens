import os
import json
import pandas as pd
import numpy as np
from tqdm import tqdm

from backend.document_ai.preprocessing import preprocess_image_for_ocr
from backend.document_ai.ocr import get_ocr_engine
from backend.document_ai.extraction import DocumentExtractor
from backend.document_ai.reconciliation import reconcile_document_to_ledger
from backend.document_ai.embeddings import DocumentEmbedder, get_image_hash, compare_hashes

def process_documents(image_dir: str, metadata_path: str, ledger_df: pd.DataFrame, output_dir: str):
    """
    Process all document images and generate features.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
        
    ocr_engine = get_ocr_engine('tesseract')
    extractor = DocumentExtractor()
    embedder = DocumentEmbedder()
    
    features = []
    
    # Pre-compute hashes to detect duplicates
    print("Computing perceptual hashes...")
    doc_hashes = {}
    for meta in tqdm(metadata):
        img_path = os.path.join(image_dir, f"{meta['document_id']}.png")
        if os.path.exists(img_path):
            doc_hashes[meta['document_id']] = get_image_hash(img_path)
            
    print("Extracting features from documents...")
    for meta in tqdm(metadata):
        doc_id = meta['document_id']
        invoice_id = meta['invoice_id']
        img_path = os.path.join(image_dir, f"{doc_id}.png")
        
        if not os.path.exists(img_path):
            continue
            
        # 1. OCR (Using raw image since our synthetic docs are clean enough, or preprocessed)
        ocr_result = ocr_engine.extract(img_path)
        raw_text = ocr_result['raw_text']
        
        # 2. Extraction
        extracted = extractor.extract_fields(raw_text)
        extracted['invoice_id'] = invoice_id # ensure we map correctly even if OCR failed
        
        # 3. Reconciliation
        # Find ledger record
        ledger_record_series = ledger_df[ledger_df['invoice_id'] == invoice_id]
        if len(ledger_record_series) > 0:
            ledger_record = ledger_record_series.iloc[0].to_dict()
            # Need to convert date column to string for exact matching if it's datetime
            if hasattr(ledger_record['date_issued'], 'strftime'):
                ledger_record['date_issued'] = ledger_record['date_issued'].strftime('%Y-%m-%d')
                
            # For vendor matching, we need the vendor name. The ledger DF might only have vendor_id.
            # Assuming ledger_df was joined with entities, or we just rely on amount for now.
            # If not, the reconciliation vendor match will fail, which is fine for the baseline.
            reconciliation = reconcile_document_to_ledger(extracted, ledger_record)
        else:
            reconciliation = {
                "amount_match": False, "vendor_match": False, "date_match": False, "arithmetic_consistency": False
            }
            
        # 4. Embeddings
        text_emb = embedder.get_text_embedding(raw_text)
        
        # 5. Duplicate Detection (Similarity to other documents)
        min_hamming = 999
        my_hash = doc_hashes.get(doc_id)
        for other_id, other_hash in doc_hashes.items():
            if other_id != doc_id:
                dist = compare_hashes(my_hash, other_hash)
                if dist < min_hamming:
                    min_hamming = dist
                    
        duplicate_similarity = 1.0 - (min_hamming / 64.0) # imagehash length is 64 bits
        
        # Build feature dict
        feat_dict = {
            'document_id': doc_id,
            'invoice_id': invoice_id,
            'amount_mismatch': 1 if not reconciliation['amount_match'] else 0,
            'vendor_mismatch': 1 if not reconciliation['vendor_match'] else 0,
            'date_mismatch': 1 if not reconciliation['date_match'] else 0,
            'arithmetic_error': 1 if not reconciliation['arithmetic_consistency'] else 0,
            'duplicate_similarity': duplicate_similarity,
            'is_document_anomaly': meta.get('is_document_anomaly', False),
            'document_anomaly_type': meta.get('document_anomaly_type', 'none')
        }
        
        # Add embedding dimensions
        for i, val in enumerate(text_emb):
            feat_dict[f'nlp_emb_{i}'] = float(val)
            
        features.append(feat_dict)
        
    df_features = pd.DataFrame(features)
    out_path = os.path.join(output_dir, 'document_features.parquet')
    df_features.to_parquet(out_path)
    print(f"Saved document features to {out_path}")
    
    return df_features
