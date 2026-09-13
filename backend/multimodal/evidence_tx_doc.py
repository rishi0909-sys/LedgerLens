import os
import pandas as pd
import xgboost as xgb
import numpy as np

def generate_tx_doc_evidence():
    print("Generating TX & Doc Evidence...")
    data_dir = 'data/processed/ml'
    
    for split in ['train', 'val', 'test']:
        tx_df = pd.read_parquet(os.path.join(data_dir, f'{split}.parquet'))
        df = pd.DataFrame({'transaction_id': tx_df['transaction_id'], 'is_anomalous': tx_df['is_anomalous']})
        
        # Transaction
        from backend.ml.transaction_anomaly import FEATURES as TX_FEATURES
        tx_model = xgb.XGBClassifier()
        tx_model.load_model('data/ml/models/xgb-transaction-v1.json')
        df['score_tx'] = tx_model.predict_proba(tx_df[TX_FEATURES])[:, 1]
        df['tx_available'] = 1
        
        # Document
        doc_model = xgb.XGBClassifier()
        doc_model.load_model('data/ml/models/xgb-document-v1.json')
        doc_df = pd.read_parquet(os.path.join(data_dir, 'document_features.parquet'))
        
        tx_doc = tx_df[['transaction_id', 'invoice_id']].merge(doc_df, on='invoice_id', how='left')
        nlp_cols = [c for c in doc_df.columns if c.startswith('nlp_emb_')]
        struct_cols = ['amount_mismatch', 'vendor_mismatch', 'date_mismatch', 'arithmetic_error']
        doc_features = nlp_cols + struct_cols + ['duplicate_similarity']
        
        doc_avail = tx_doc['invoice_id'].notna() & (tx_doc['invoice_id'] != 0) & (tx_doc['document_id'].notna())
        doc_X = tx_doc[doc_features].fillna(0)
        
        df['score_doc'] = np.where(doc_avail.values, doc_model.predict_proba(doc_X)[:, 1], 0.0)
        df['doc_available'] = doc_avail.astype(int).values
        
        os.makedirs('data/processed/ml/multimodal', exist_ok=True)
        df.to_parquet(f'data/processed/ml/multimodal/{split}_tx_doc.parquet')

if __name__ == '__main__':
    generate_tx_doc_evidence()
