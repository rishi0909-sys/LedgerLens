import pandas as pd
import numpy as np
import os
import pickle
import xgboost as xgb
from sklearn.linear_model import LogisticRegression

def train_fusion_models():
    print("Training Evidence Fusion Models...")
    data_dir = 'data/processed/ml/multimodal'
    train_ev = pd.read_parquet(os.path.join(data_dir, 'train_calibrated.parquet'))
    val_ev = pd.read_parquet(os.path.join(data_dir, 'val_calibrated.parquet'))
    
    # Define features for fusion
    # We use calibrated scores and availability flags
    base_features = [
        'cal_tx', 'tx_available',
        'cal_doc', 'doc_available',
        'cal_seq', 'seq_available',
        'cal_graph', 'graph_available'
    ]
    
    # Add conflict/disagreement features for XGBoost
    train_ev['conflict_tx_doc'] = np.abs(train_ev['cal_tx'] - train_ev['cal_doc'])
    train_ev['conflict_tx_seq'] = np.abs(train_ev['cal_tx'] - train_ev['cal_seq'])
    val_ev['conflict_tx_doc'] = np.abs(val_ev['cal_tx'] - val_ev['cal_doc'])
    val_ev['conflict_tx_seq'] = np.abs(val_ev['cal_tx'] - val_ev['cal_seq'])
    
    xgb_features = base_features + ['conflict_tx_doc', 'conflict_tx_seq']
    
    y_train = train_ev['is_anomalous'].astype(int)
    y_val = val_ev['is_anomalous'].astype(int)
    
    # 1. Logistic Fusion
    log_reg = LogisticRegression(class_weight='balanced', random_state=42)
    log_reg.fit(train_ev[base_features], y_train)
    
    with open('data/ml/models/fusion-logistic-v1.pkl', 'wb') as f:
        pickle.dump(log_reg, f)
        
    # 2. XGBoost Fusion
    pos_count = y_train.sum()
    scale_pos_weight = (len(y_train) - pos_count) / max(1.0, pos_count)
    
    xgb_fusion = xgb.XGBClassifier(
        n_estimators=100, max_depth=3, learning_rate=0.05,
        scale_pos_weight=scale_pos_weight, random_state=42, eval_metric='logloss',
        early_stopping_rounds=10
    )
    
    xgb_fusion.fit(
        train_ev[xgb_features], y_train,
        eval_set=[(val_ev[xgb_features], y_val)],
        verbose=False
    )
    
    xgb_fusion.save_model('data/ml/models/fusion-xgb-v1.json')
    print("Fusion models trained and saved.")

if __name__ == "__main__":
    train_fusion_models()
