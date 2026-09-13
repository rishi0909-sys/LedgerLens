import os
import json
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_recall_curve, auc, f1_score, recall_score, precision_score, roc_auc_score, confusion_matrix
import pickle
import time
from datetime import datetime

# FEATURES must be explicitly defined to avoid leakage
FEATURES = [
    'amount', 'hour', 'day_of_week', 'day_of_month', 'month',
    'is_salary', 'is_invoice_payment', 'is_transfer', 'is_reimbursement',
    'time_since_previous', 'rolling_txn_count', 'rolling_avg_amount', 
    'amount_deviation', 'amount_deviation_ratio', 'unique_counterparty_count'
]

def load_data(data_dir: str):
    train = pd.read_parquet(os.path.join(data_dir, 'train.parquet'))
    val = pd.read_parquet(os.path.join(data_dir, 'val.parquet'))
    test = pd.read_parquet(os.path.join(data_dir, 'test.parquet'))
    return train, val, test

def compute_metrics(y_true, y_prob, y_pred, k_values=[10, 50, 100]):
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = auc(recall, precision)
    roc_auc = roc_auc_score(y_true, y_prob)
    f1 = f1_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    
    metrics = {
        'PR-AUC': float(pr_auc),
        'ROC-AUC': float(roc_auc),
        'F1': float(f1),
        'Recall': float(rec),
        'Precision': float(prec),
        'FPR': float(fpr),
        'ConfusionMatrix': {'TN': int(tn), 'FP': int(fp), 'FN': int(fn), 'TP': int(tp)}
    }
    
    # Ranking metrics
    sorted_indices = np.argsort(y_prob)[::-1]
    sorted_true = y_true.values[sorted_indices] if isinstance(y_true, pd.Series) else y_true[sorted_indices]
    
    for k in k_values:
        if len(sorted_true) >= k:
            top_k_true = sorted_true[:k]
            metrics[f'Precision@{k}'] = float(np.sum(top_k_true) / k)
            metrics[f'Recall@{k}'] = float(np.sum(top_k_true) / max(1, np.sum(y_true)))
            
    return metrics

def train_statistical_baseline(val_df, test_df):
    print("--- Statistical Baseline ---")
    # Rule: amount_deviation_ratio > threshold
    
    # Find best threshold on validation
    best_f1 = 0
    best_thresh = 1.0
    for thresh in np.linspace(1.5, 10.0, 50):
        val_preds = (val_df['amount_deviation_ratio'] > thresh).astype(int)
        f1 = f1_score(val_df['is_anomalous'], val_preds)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = thresh
            
    # Test evaluation
    test_probs = val_df['amount_deviation_ratio'] / best_thresh # Pseudo prob
    test_preds = (test_df['amount_deviation_ratio'] > best_thresh).astype(int)
    # Using deviation ratio as score for PR-AUC
    test_scores = test_df['amount_deviation_ratio'].fillna(0).replace([np.inf, -np.inf], 0)
    
    metrics = compute_metrics(test_df['is_anomalous'], test_scores, test_preds)
    print(f"Stat Baseline Threshold: {best_thresh}")
    print(f"Stat Baseline Metrics: {metrics}\n")
    return metrics

def train_isolation_forest(train_df, val_df, test_df, model_dir):
    print("--- Isolation Forest ---")
    X_train = train_df[FEATURES].fillna(0)
    X_val = val_df[FEATURES].fillna(0)
    X_test = test_df[FEATURES].fillna(0)
    
    # Train
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X_train)
    
    # Isolation forest returns -1 for anomaly, 1 for normal
    # decision_function gives lower scores for anomalies
    val_scores = -model.decision_function(X_val) 
    
    # Threshold selection on Val
    best_f1 = 0
    best_thresh = 0
    for thresh in np.percentile(val_scores, np.linspace(50, 99, 50)):
        val_preds = (val_scores > thresh).astype(int)
        f1 = f1_score(val_df['is_anomalous'], val_preds)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = thresh
            
    test_scores = -model.decision_function(X_test)
    test_preds = (test_scores > best_thresh).astype(int)
    
    metrics = compute_metrics(test_df['is_anomalous'], test_scores, test_preds)
    print(f"IForest Threshold: {best_thresh}")
    print(f"IForest Metrics: {metrics}\n")
    
    # Save model
    with open(os.path.join(model_dir, 'iforest.pkl'), 'wb') as f:
        pickle.dump({'model': model, 'threshold': best_thresh}, f)
        
    return metrics

def train_xgboost(train_df, val_df, test_df, model_dir):
    print("--- XGBoost ---")
    X_train = train_df[FEATURES]
    y_train = train_df['is_anomalous']
    X_val = val_df[FEATURES]
    y_val = val_df['is_anomalous']
    X_test = test_df[FEATURES]
    y_test = test_df['is_anomalous']
    
    # Handle Class Imbalance
    pos_weight = (len(y_train) - y_train.sum()) / max(1, y_train.sum())
    
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        scale_pos_weight=pos_weight,
        random_state=42,
        eval_metric='logloss',
        early_stopping_rounds=10
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    
    val_probs = model.predict_proba(X_val)[:, 1]
    
    # Threshold selection
    precisions, recalls, thresholds = precision_recall_curve(y_val, val_probs)
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
    best_idx = np.argmax(f1_scores)
    best_thresh = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
    
    test_probs = model.predict_proba(X_test)[:, 1]
    test_preds = (test_probs >= best_thresh).astype(int)
    
    metrics = compute_metrics(y_test, test_probs, test_preds)
    
    # Error analysis by subtype
    if 'anomaly_type' in test_df.columns:
        test_df = test_df.copy()
        test_df['pred'] = test_preds
        print("XGBoost Error Analysis by Subtype:")
        for subtype in test_df['anomaly_type'].dropna().unique():
            sub_df = test_df[test_df['anomaly_type'] == subtype]
            if len(sub_df) > 0:
                rec = (sub_df['pred'] == 1).mean()
                print(f"  {subtype}: Recall = {rec:.2f}")
                metrics[f'Recall_{subtype}'] = float(rec)
    
    print(f"XGBoost Threshold: {best_thresh}")
    print(f"XGBoost Metrics: {metrics}\n")
    
    # Feature Importance
    importance = model.feature_importances_
    feat_imp = {FEATURES[i]: float(importance[i]) for i in range(len(FEATURES))}
    
    # Save model and registry
    model_id = f"xgb-transaction-v1"
    model_path = os.path.join(model_dir, f'{model_id}.json')
    model.save_model(model_path)
    
    registry_entry = {
        "model_id": model_id,
        "model_type": "xgboost",
        "dataset_version": "1.0",
        "feature_schema_version": "1.0",
        "training_seed": 42,
        "hyperparameters": {"n_estimators": 100, "max_depth": 4, "learning_rate": 0.1},
        "test_metrics": metrics,
        "threshold": float(best_thresh),
        "artifact_path": model_path,
        "created_at": datetime.utcnow().isoformat(),
        "feature_importance": feat_imp
    }
    
    with open(os.path.join(model_dir, f'{model_id}_metadata.json'), 'w') as f:
        json.dump(registry_entry, f, indent=2)
        
    return metrics, registry_entry

def run_pipeline():
    data_dir = 'data/processed/ml'
    model_dir = 'data/ml/models'
    os.makedirs(model_dir, exist_ok=True)
    
    train, val, test = load_data(data_dir)
    
    print(f"Train: {len(train)} | Val: {len(val)} | Test: {len(test)}")
    
    stat_metrics = train_statistical_baseline(val, test)
    if_metrics = train_isolation_forest(train, val, test, model_dir)
    xgb_metrics, xgb_registry = train_xgboost(train, val, test, model_dir)
    
    # Save a final report data file
    with open('data/ml/phase2_benchmark.json', 'w') as f:
        json.dump({
            "Statistical": stat_metrics,
            "IsolationForest": if_metrics,
            "XGBoost": xgb_metrics
        }, f, indent=2)
    
    print("Phase 2 Models trained and saved.")

if __name__ == "__main__":
    run_pipeline()
