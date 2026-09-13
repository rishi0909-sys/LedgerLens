import pytest
import pandas as pd
from datetime import datetime
import json
import os
from backend.ml.transaction_dataset import build_dataset

def test_chronological_split(tmp_path):
    # Dummy data
    data = [
        {"transaction_id": "1", "timestamp": datetime(2023, 1, 1), "source_account": "A", "destination_account": "B", "amount": 100, "transaction_type": "TRANSFER"},
        {"transaction_id": "2", "timestamp": datetime(2023, 10, 15), "source_account": "A", "destination_account": "B", "amount": 100, "transaction_type": "TRANSFER"},
        {"transaction_id": "3", "timestamp": datetime(2023, 12, 1), "source_account": "A", "destination_account": "B", "amount": 100, "transaction_type": "TRANSFER"},
    ]
    df = pd.DataFrame(data)
    
    raw_path = tmp_path / "transactions.parquet"
    df.to_parquet(raw_path)
    
    gt = {"anomalous_transactions": ["3"], "anomalous_invoices": []}
    gt_path = tmp_path / "ground_truth.json"
    with open(gt_path, "w") as f:
        json.dump(gt, f)
        
    out_dir = tmp_path / "ml"
    
    build_dataset(str(raw_path), str(gt_path), str(out_dir))
    
    train = pd.read_parquet(out_dir / "train.parquet")
    val = pd.read_parquet(out_dir / "val.parquet")
    test = pd.read_parquet(out_dir / "test.parquet")
    
    # Check splits
    assert len(train) == 1
    assert train.iloc[0]['transaction_id'] == "1"
    
    assert len(val) == 1
    assert val.iloc[0]['transaction_id'] == "2"
    
    assert len(test) == 1
    assert test.iloc[0]['transaction_id'] == "3"
    
    # Check labels
    assert test.iloc[0]['is_anomalous'] == 1
    assert train.iloc[0]['is_anomalous'] == 0
    
    # Check no 'is_anomaly' leaking from raw
    assert 'is_anomaly' not in train.columns
