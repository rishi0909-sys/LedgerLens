import pandas as pd
import xgboost as xgb
import os

print("Loading document features...")
df_doc = pd.read_parquet('data/processed/ml/document_features.parquet')

nlp_cols = [c for c in df_doc.columns if c.startswith('nlp_emb_')]
struct_cols = ['amount_mismatch', 'vendor_mismatch', 'date_mismatch', 'arithmetic_error']
doc_features = nlp_cols + struct_cols + ['duplicate_similarity']

df_doc = df_doc.sample(frac=1, random_state=42).reset_index(drop=True)
n = len(df_doc)
train_idx = int(n * 0.7)
val_idx = int(n * 0.85)

train_doc = df_doc.iloc[:train_idx]
val_doc = df_doc.iloc[train_idx:val_idx]

X_train, y_train = train_doc[doc_features], train_doc['is_document_anomaly'].astype(int)
X_val, y_val = val_doc[doc_features], val_doc['is_document_anomaly'].astype(int)

scale_pos_weight = (len(y_train) - y_train.sum()) / max(1.0, y_train.sum())

model = xgb.XGBClassifier(
    n_estimators=100, max_depth=4, learning_rate=0.1,
    scale_pos_weight=scale_pos_weight, random_state=42, eval_metric='logloss',
    early_stopping_rounds=10
)
model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

os.makedirs('data/ml/models', exist_ok=True)
model.save_model('data/ml/models/xgb-document-v1.json')
print("Saved xgb-document-v1.json")
