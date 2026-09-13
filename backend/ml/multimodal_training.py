import os
import json
import pandas as pd
import numpy as np
import xgboost as xgb
from datetime import datetime

from backend.ml.transaction_anomaly import compute_metrics, FEATURES as TX_FEATURES

def train_multimodal_model(X_train, y_train, X_val, y_val, X_test, y_test, features_list, name):
    if len(features_list) == 0:
        return {"PR-AUC": 0.0}
        
    pos_count = y_train.sum()
    scale_pos_weight = (len(y_train) - pos_count) / max(1.0, pos_count)
    
    model = xgb.XGBClassifier(
        n_estimators=100, max_depth=4, learning_rate=0.1,
        scale_pos_weight=scale_pos_weight, random_state=42, eval_metric='logloss',
        early_stopping_rounds=10
    )
    
    model.fit(
        X_train[features_list], y_train,
        eval_set=[(X_val[features_list], y_val)],
        verbose=False
    )
    
    probs = model.predict_proba(X_test[features_list])[:, 1]
    preds = model.predict(X_test[features_list])
    
    metrics = compute_metrics(y_test, probs, preds)
    print(f"{name} PR-AUC: {metrics['PR-AUC']:.4f}")
    return metrics, model

def run_multimodal_pipeline():
    print("Loading data for multimodal fusion...")
    data_dir = 'data/processed/ml'
    
    train_tx = pd.read_parquet(os.path.join(data_dir, 'train.parquet'))
    val_tx = pd.read_parquet(os.path.join(data_dir, 'val.parquet'))
    test_tx = pd.read_parquet(os.path.join(data_dir, 'test.parquet'))
    
    df_doc = pd.read_parquet(os.path.join(data_dir, 'document_features.parquet'))
    
    # Merge document features on invoice_id (which already exists in train_tx)
    train_f = train_tx.merge(df_doc, on='invoice_id', how='left').fillna(0)
    val_f = val_tx.merge(df_doc, on='invoice_id', how='left').fillna(0)
    test_f = test_tx.merge(df_doc, on='invoice_id', how='left').fillna(0)
    
    y_train = train_f['is_anomalous'].astype(int)
    y_val = val_f['is_anomalous'].astype(int)
    y_test = test_f['is_anomalous'].astype(int)
    
    structured_cols = ['amount_mismatch', 'vendor_mismatch', 'date_mismatch', 'arithmetic_error']
    cv_cols = ['duplicate_similarity']
    nlp_cols = [c for c in df_doc.columns if c.startswith('nlp_emb_')]
    
    results = {}
    print("\n--- Multimodal Fusion Experiments ---")
    
    # A. Transaction Only (Phase 2 equivalent)
    res_a, _ = train_multimodal_model(train_f, y_train, val_f, y_val, test_f, y_test, TX_FEATURES, "A - Transaction Only")
    results['Transaction_Only'] = res_a
    
    # B. Transaction + Document Structured
    feat_b = TX_FEATURES + structured_cols
    res_b, _ = train_multimodal_model(train_f, y_train, val_f, y_val, test_f, y_test, feat_b, "B - Transaction + Doc Structured")
    results['Transaction_DocStruct'] = res_b
    
    # C. Transaction + Document NLP
    feat_c = TX_FEATURES + nlp_cols
    res_c, _ = train_multimodal_model(train_f, y_train, val_f, y_val, test_f, y_test, feat_c, "C - Transaction + Doc NLP")
    results['Transaction_DocNLP'] = res_c
    
    # D. Full Multimodal
    feat_d = TX_FEATURES + structured_cols + cv_cols + nlp_cols
    res_d, model_d = train_multimodal_model(train_f, y_train, val_f, y_val, test_f, y_test, feat_d, "D - Full Multimodal Fusion")
    results['Multimodal_All'] = res_d
    
    with open('data/ml/phase5_multimodal_benchmark.json', 'w') as f:
        json.dump(results, f, indent=2)
        
    # Save the multimodal model
    model_id = "xgb-multimodal-v1"
    model_dir = "data/ml/models"
    model_path = os.path.join(model_dir, f"{model_id}.json")
    model_d.save_model(model_path)
    
    registry_entry = {
        "model_id": model_id,
        "model_type": "xgboost",
        "dataset_version": "1.0",
        "feature_schema_version": "1.0",
        "training_seed": 42,
        "test_metrics": res_d,
        "artifact_path": model_path,
        "created_at": datetime.utcnow().isoformat(),
    }
    with open(os.path.join(model_dir, f"{model_id}_metadata.json"), 'w') as f:
        json.dump(registry_entry, f, indent=2)
        
    print("Phase 5 Multimodal Models trained and saved.")

if __name__ == "__main__":
    run_multimodal_pipeline()
