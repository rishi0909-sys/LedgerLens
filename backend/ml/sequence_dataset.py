import os
import json
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from backend.ml.transaction_features import construct_features

FEATURES = [
    'amount', 'hour', 'day_of_week', 'day_of_month', 'month',
    'is_salary', 'is_invoice_payment', 'is_transfer', 'is_reimbursement',
    'time_since_previous', 'rolling_txn_count', 'rolling_avg_amount', 
    'amount_deviation', 'amount_deviation_ratio', 'unique_counterparty_count'
]

class TransactionSequenceDataset(Dataset):
    def __init__(self, df: pd.DataFrame, seq_len: int = 20):
        # We assume df is already strictly sorted by timestamp.
        # df must contain all features in FEATURES + target + transaction_id + source_account
        self.seq_len = seq_len
        self.features = []
        self.masks = []
        self.targets = []
        self.metadata = []
        
        # Build sequences per account
        for account, group in df.groupby('source_account'):
            # The group is ordered by timestamp
            feature_matrix = group[FEATURES].values
            target_array = group['is_anomalous'].values
            txn_ids = group['transaction_id'].values
            
            n = len(group)
            for i in range(n):
                # For transaction t (index i), history is [max(0, i - seq_len) : i]
                start_idx = max(0, i - seq_len)
                hist_feats = feature_matrix[start_idx:i]
                hist_len = len(hist_feats)
                
                # We need to pad to seq_len
                # Sequence format: [pad, pad, ..., t-2, t-1]
                pad_len = seq_len - hist_len
                
                if pad_len > 0:
                    pad = np.zeros((pad_len, len(FEATURES)))
                    seq_feats = np.vstack([pad, hist_feats]) if hist_len > 0 else pad
                    mask = [True]*pad_len + [False]*hist_len
                else:
                    seq_feats = hist_feats
                    mask = [False]*seq_len
                
                self.features.append(seq_feats)
                self.masks.append(mask)
                self.targets.append(target_array[i])
                self.metadata.append(txn_ids[i])
                
        self.features = np.array(self.features, dtype=np.float32)
        self.masks = np.array(self.masks, dtype=bool)
        self.targets = np.array(self.targets, dtype=np.float32)

    def __len__(self):
        return len(self.targets)
        
    def __getitem__(self, idx):
        return (
            torch.tensor(self.features[idx]), 
            torch.tensor(self.masks[idx]), 
            torch.tensor(self.targets[idx]),
            self.metadata[idx]
        )

def build_sequence_data(raw_transactions_path: str, ground_truth_path: str, output_dir: str, seq_len: int = 20):
    print("Loading raw transactions...")
    df = pd.read_parquet(raw_transactions_path)
    
    with open(ground_truth_path, 'r') as f:
        ground_truth = json.load(f)
        
    print("Constructing causal features...")
    df = construct_features(df)
    
    anomalous_ids = set(ground_truth.get('anomalous_transactions', []))
    df['is_anomalous'] = df['transaction_id'].isin(anomalous_ids).astype(int)
    
    train_end = pd.to_datetime('2023-09-30 23:59:59')
    val_end = pd.to_datetime('2023-11-15 23:59:59')
    
    # We MUST pass the entire df through the sequence generator so that transactions
    # in the validation set can still look back at transactions from the training set.
    # We will build the dataset object and then split it based on the transaction_id timestamp.
    
    dataset = TransactionSequenceDataset(df, seq_len=seq_len)
    
    # Filter arrays into train/val/test
    # To do this correctly, we need the original timestamp of the target transaction
    df_indexed = df.set_index('transaction_id')
    
    train_f, train_m, train_t, train_ids = [], [], [], []
    val_f, val_m, val_t, val_ids = [], [], [], []
    test_f, test_m, test_t, test_ids = [], [], [], []
    
    for i in range(len(dataset)):
        tid = dataset.metadata[i]
        ts = df_indexed.at[tid, 'timestamp']
        if ts <= train_end:
            train_f.append(dataset.features[i])
            train_m.append(dataset.masks[i])
            train_t.append(dataset.targets[i])
            train_ids.append(tid)
        elif ts <= val_end:
            val_f.append(dataset.features[i])
            val_m.append(dataset.masks[i])
            val_t.append(dataset.targets[i])
            val_ids.append(tid)
        else:
            test_f.append(dataset.features[i])
            test_m.append(dataset.masks[i])
            test_t.append(dataset.targets[i])
            test_ids.append(tid)
            
    os.makedirs(output_dir, exist_ok=True)
    
    def save_split(name, f, m, t, ids):
        torch.save({
            'features': np.array(f),
            'masks': np.array(m),
            'targets': np.array(t),
            'metadata': ids
        }, os.path.join(output_dir, f'{name}_seq.pt'))
        
    save_split('train', train_f, train_m, train_t, train_ids)
    save_split('val', val_f, val_m, val_t, val_ids)
    save_split('test', test_f, test_m, test_t, test_ids)
    
    metadata = {
        "dataset_version": "1.0",
        "feature_schema_version": "1.0",
        "sequence_length": seq_len,
        "grouping_key": "source_account",
        "target_definition": "is_anomalous",
        "padding_strategy": "zero_pad_with_boolean_mask"
    }
    with open(os.path.join(output_dir, 'seq_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Sequence datasets generated. Train: {len(train_f)}, Val: {len(val_f)}, Test: {len(test_f)}")

if __name__ == "__main__":
    build_sequence_data(
        'data/processed/transactions.parquet',
        'data/processed/ground_truth.json',
        'data/processed/ml/sequences'
    )
