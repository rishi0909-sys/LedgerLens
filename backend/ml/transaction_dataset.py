import os
import json
import pandas as pd
from datetime import datetime
from backend.ml.transaction_features import construct_features

def build_dataset(
    raw_transactions_path: str,
    ground_truth_path: str,
    output_dir: str
):
    print("Loading raw transactions...")
    df = pd.read_parquet(raw_transactions_path)
    
    with open(ground_truth_path, 'r') as f:
        ground_truth = json.load(f)
        
    print("Constructing causal features...")
    df = construct_features(df)
    
    print("Attaching ground truth labels...")
    anomalous_ids = set(ground_truth.get('anomalous_transactions', []))
    df['is_anomalous'] = df['transaction_id'].isin(anomalous_ids).astype(int)
    
    # We drop the boolean `is_anomaly` because we replaced it with integer `is_anomalous`
    # We KEEP `anomaly_type` for error analysis, but it MUST NOT be used as a feature in ML.
    if 'is_anomaly' in df.columns:
        df = df.drop(columns=['is_anomaly'])
    
    print("Splitting dataset chronologically...")
    train_end = pd.to_datetime('2023-09-30 23:59:59')
    val_end = pd.to_datetime('2023-11-15 23:59:59')
    
    train_mask = df['timestamp'] <= train_end
    val_mask = (df['timestamp'] > train_end) & (df['timestamp'] <= val_end)
    test_mask = df['timestamp'] > val_end
    
    train_df = df[train_mask].copy()
    val_df = df[val_mask].copy()
    test_df = df[test_mask].copy()
    
    os.makedirs(output_dir, exist_ok=True)
    
    train_df.to_parquet(os.path.join(output_dir, 'train.parquet'))
    val_df.to_parquet(os.path.join(output_dir, 'val.parquet'))
    test_df.to_parquet(os.path.join(output_dir, 'test.parquet'))
    
    metadata = {
        "dataset_version": "1.0",
        "feature_schema_version": "1.0",
        "target_definition": "is_anomalous",
        "train_start": str(train_df['timestamp'].min()),
        "train_end": str(train_df['timestamp'].max()),
        "validation_start": str(val_df['timestamp'].min()),
        "validation_end": str(val_df['timestamp'].max()),
        "test_start": str(test_df['timestamp'].min()),
        "test_end": str(test_df['timestamp'].max()),
        "train_count": len(train_df),
        "val_count": len(val_df),
        "test_count": len(test_df),
        "total_anomalies": int(df['is_anomalous'].sum()),
        "positive_prevalence": float(df['is_anomalous'].mean())
    }
    
    with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Dataset generated. Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

if __name__ == "__main__":
    build_dataset(
        'data/processed/transactions.parquet',
        'data/processed/ground_truth.json',
        'data/processed/ml'
    )
