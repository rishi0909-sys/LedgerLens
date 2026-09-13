import pandas as pd
import json
import xgboost as xgb
import numpy as np
import os
from sklearn.metrics import precision_recall_curve, auc, f1_score, recall_score, precision_score, roc_auc_score

def compute_metrics(y_true, y_prob, y_pred):
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = auc(recall, precision)
    f1 = f1_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    
    return {
        'PR-AUC': float(pr_auc),
        'F1': float(f1),
        'Recall': float(rec),
        'Precision': float(prec)
    }

print("Loading document features...")
df_doc = pd.read_parquet('data/processed/ml/document_features.parquet')

# Document-only baseline (using NLP embeddings + extracted structural mismatch)
nlp_cols = [c for c in df_doc.columns if c.startswith('nlp_emb_')]
struct_cols = ['amount_mismatch', 'vendor_mismatch', 'date_mismatch', 'arithmetic_error']
doc_features = nlp_cols + struct_cols + ['duplicate_similarity']

df_doc = df_doc.sample(frac=1, random_state=42).reset_index(drop=True)
n = len(df_doc)
train_idx = int(n * 0.7)
val_idx = int(n * 0.85)

train_doc = df_doc.iloc[:train_idx]
val_doc = df_doc.iloc[train_idx:val_idx]
test_doc = df_doc.iloc[val_idx:]

X_train, y_train = train_doc[doc_features], train_doc['is_document_anomaly'].astype(int)
X_val, y_val = val_doc[doc_features], val_doc['is_document_anomaly'].astype(int)
X_test, y_test = test_doc[doc_features], test_doc['is_document_anomaly'].astype(int)

# In case there are no anomalies in this split (due to small size), ensure it works
if y_train.sum() == 0:
    scale_pos_weight = 1
else:
    scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()

model = xgb.XGBClassifier(
    n_estimators=100, max_depth=4, learning_rate=0.1,
    scale_pos_weight=scale_pos_weight, random_state=42
)

model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

test_probs = model.predict_proba(X_test)[:, 1]
test_preds = model.predict(X_test)
metrics = compute_metrics(y_test, test_probs, test_preds)
print("Document-Only Baseline Metrics:", metrics)

with open('data/ml/document_baseline_results.json', 'w') as f:
    json.dump(metrics, f)

# Also run Multimodal Training script which is already fixed
print("Running Multimodal Training...")
