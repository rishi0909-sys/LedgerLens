import json
import pandas as pd
import numpy as np

def run_verification():
    print("--- Phase 5 Verification ---")
    data_dir = 'data/processed/ml'
    
    train_tx = pd.read_parquet(f'{data_dir}/train.parquet')
    test_tx = pd.read_parquet(f'{data_dir}/test.parquet')
    df_doc = pd.read_parquet(f'{data_dir}/document_features.parquet')
    
    train_f = train_tx.merge(df_doc, on='invoice_id', how='left').fillna(0)
    test_f = test_tx.merge(df_doc, on='invoice_id', how='left').fillna(0)
    
    y_test = test_f['is_anomalous'].astype(int)
    
    print("\n1. Anomaly Prevalence & Baseline")
    prevalence = y_test.mean()
    print(f"Total Test Samples: {len(y_test)}")
    print(f"Test Anomalies: {y_test.sum()} ({prevalence:.4%})")
    print(f"Random PR-AUC Baseline (Prevalence): {prevalence:.4f}")
    
    print("\n2. Feature Dimensionality")
    from backend.ml.transaction_anomaly import FEATURES as TX_FEATURES
    structured_cols = ['amount_mismatch', 'vendor_mismatch', 'date_mismatch', 'arithmetic_error']
    cv_cols = ['duplicate_similarity']
    nlp_cols = [c for c in df_doc.columns if c.startswith('nlp_emb_')]
    
    print(f"A (Transaction Only): {len(TX_FEATURES)} features")
    print(f"B (Transaction + Doc Struct): {len(TX_FEATURES + structured_cols)} features")
    print(f"C (Transaction + Doc NLP): {len(TX_FEATURES + nlp_cols)} features")
    print(f"D (Full Multimodal): {len(TX_FEATURES + structured_cols + cv_cols + nlp_cols)} features")
    
    print("\n3. Why are predictions identical?")
    # Let's check how many documents are actually associated with anomalous transactions
    test_f_anom = test_f[test_f['is_anomalous'] == 1]
    docs_in_anom = test_f_anom['invoice_id'].notna() & (test_f_anom['invoice_id'] != 0)
    print(f"Anomalous transactions in test set: {len(test_f_anom)}")
    print(f"Anomalous transactions with documents: {docs_in_anom.sum()}")
    
    with open('data/ml/phase5_multimodal_benchmark.json') as f:
        metrics = json.load(f)
        
    print("\nBenchmark Results:")
    for k, v in metrics.items():
        print(f"{k} PR-AUC: {v['PR-AUC']:.4f}")

if __name__ == "__main__":
    run_verification()
