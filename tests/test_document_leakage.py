import pytest
import pandas as pd
import json

def test_document_leakage():
    # Load document features
    df = pd.read_parquet('data/processed/ml/document_features.parquet')
    
    # 1. Label leakage check
    # Document features should not have direct access to 'is_anomalous' or 'is_document_anomaly' during training,
    # except when acting as the target variable. We must ensure no feature correlates perfectly with the label.
    
    # For Document-only baseline, we use nlp_emb_*, amount_mismatch, vendor_mismatch, date_mismatch, arithmetic_error, duplicate_similarity
    nlp_cols = [c for c in df.columns if c.startswith('nlp_emb_')]
    struct_cols = ['amount_mismatch', 'vendor_mismatch', 'date_mismatch', 'arithmetic_error']
    features = nlp_cols + struct_cols + ['duplicate_similarity']
    
    # Ensure none of these perfectly predict the label on their own (1.0 correlation)
    if 'is_document_anomaly' in df.columns:
        corrs = df[features].corrwith(df['is_document_anomaly'])
        # None should be 1.0 or -1.0
        assert not any(abs(corrs) >= 0.99)
        
    # 2. Chronological Split Check
    # Ensure test set documents have timestamps AFTER train set documents
    train_tx = pd.read_parquet('data/processed/ml/train.parquet')
    test_tx = pd.read_parquet('data/processed/ml/test.parquet')
    
    train_max_time = train_tx['timestamp'].max()
    test_min_time = test_tx['timestamp'].min()
    
    assert test_min_time >= train_max_time, "Temporal leakage: test data occurs before train data ends!"

def test_multimodal_registry_metadata():
    with open('data/ml/models/xgb-multimodal-v1_metadata.json') as f:
        meta = json.load(f)
        
    assert 'model_id' in meta
    assert 'test_metrics' in meta
    assert 'PR-AUC' in meta['test_metrics']
