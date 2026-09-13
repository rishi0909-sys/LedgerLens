import os
import json
import pandas as pd
import numpy as np
import xgboost as xgb

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
os.environ["OMP_NUM_THREADS"] = "1"
from sklearn.metrics import precision_recall_curve, f1_score, precision_score, recall_score, roc_auc_score

from backend.ml.transaction_anomaly import compute_metrics
from backend.document_ai.document_features import process_documents

def run_document_pipeline():
    # 1. Run Extraction if features not present
    feat_path = 'data/processed/ml/document_features.parquet'
    if not os.path.exists(feat_path):
        print("Running document extraction pipeline...")
        # We need ledger_df with vendor names
        df_inv = pd.read_parquet('data/processed/invoices.parquet')
        with open('data/processed/entities.json') as f:
            entities = json.load(f)
            
        entity_map = {e['id']: e['name'] for e in entities if 'name' in e}
        df_inv['vendor_name'] = df_inv['vendor_id'].map(entity_map)
        
        process_documents(
            image_dir='data/processed/invoices_images',
            metadata_path='data/processed/invoices_images/documents_metadata.json',
            ledger_df=df_inv,
            output_dir='data/processed/ml/'
        )
        
    df_doc = pd.read_parquet(feat_path)
    
    # Define features
    structured_cols = ['amount_mismatch', 'vendor_mismatch', 'date_mismatch', 'arithmetic_error']
    cv_cols = ['duplicate_similarity']
    nlp_cols = [c for c in df_doc.columns if c.startswith('nlp_emb_')]
    
    # 2. Setup Evaluation Splitting
    # We should split based on invoice_id just like transactions, but let's do a simple chronological or randomized split for now.
    # To prevent leakage, train/test split should ideally match the transaction split.
    # We can load the phase 2 test set transaction_ids or just randomly split invoices.
    
    df_doc = df_doc.sample(frac=1, random_state=42).reset_index(drop=True)
    n = len(df_doc)
    train_idx = int(n * 0.7)
    val_idx = int(n * 0.85)
    
    df_train = df_doc.iloc[:train_idx]
    df_val = df_doc.iloc[train_idx:val_idx]
    df_test = df_doc.iloc[val_idx:]
    
    y_train = df_train['is_document_anomaly'].astype(int)
    y_val = df_val['is_document_anomaly'].astype(int)
    y_test = df_test['is_document_anomaly'].astype(int)
    
    def train_and_eval(X_train, X_val, X_test, name):
        if X_train.shape[1] == 0:
            return {"PR-AUC": 0.0}
            
        pos_count = y_train.sum()
        scale_pos_weight = (len(y_train) - pos_count) / max(1.0, pos_count)
        
        model = xgb.XGBClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.1,
            scale_pos_weight=scale_pos_weight, random_state=42, eval_metric='logloss'
        )
        
        # XGBoost fails if data is empty or completely uniform sometimes, but we assume it's fine
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False, early_stopping_rounds=10)
        
        probs = model.predict_proba(X_test)[:, 1]
        preds = model.predict(X_test)
        
        if len(np.unique(y_test)) > 1:
            metrics = compute_metrics(y_test, probs, preds)
        else:
            metrics = {"PR-AUC": 0.0}
            
        print(f"{name} PR-AUC: {metrics['PR-AUC']:.4f}")
        return metrics

    results = {}
    
    print("\n--- Document Baseline Experiments ---")
    
    # A. Structured Only
    X_train_struct = df_train[structured_cols].values
    X_val_struct = df_val[structured_cols].values
    X_test_struct = df_test[structured_cols].values
    results['Document_Structured'] = train_and_eval(X_train_struct, X_val_struct, X_test_struct, "Document Structured Fields")
    
    # B. Structured + CV
    X_train_cv = df_train[structured_cols + cv_cols].values
    X_val_cv = df_val[structured_cols + cv_cols].values
    X_test_cv = df_test[structured_cols + cv_cols].values
    results['Document_Structured_CV'] = train_and_eval(X_train_cv, X_val_cv, X_test_cv, "Document Structured + CV (Duplicates)")
    
    # C. Structured + NLP
    X_train_nlp = df_train[structured_cols + nlp_cols].values
    X_val_nlp = df_val[structured_cols + nlp_cols].values
    X_test_nlp = df_test[structured_cols + nlp_cols].values
    results['Document_Structured_NLP'] = train_and_eval(X_train_nlp, X_val_nlp, X_test_nlp, "Document Structured + NLP")
    
    # D. Full Document Modality
    all_doc_cols = structured_cols + cv_cols + nlp_cols
    X_train_full = df_train[all_doc_cols].values
    X_val_full = df_val[all_doc_cols].values
    X_test_full = df_test[all_doc_cols].values
    results['Document_All'] = train_and_eval(X_train_full, X_val_full, X_test_full, "Document All Evidence")
    
    with open('data/ml/document_baseline_results.json', 'w') as f:
        json.dump(results, f, indent=2)
        
if __name__ == "__main__":
    run_document_pipeline()
