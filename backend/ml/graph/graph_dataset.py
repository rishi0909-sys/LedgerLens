import os
import json
import pandas as pd
import numpy as np
import torch
from torch_geometric.data import Data
from backend.ml.transaction_features import construct_features

def get_snapshot_intervals():
    # Train intervals (monthly cutoffs)
    train_cutoffs = [
        ('2023-01-31 23:59:59', '2023-02-28 23:59:59'),
        ('2023-02-28 23:59:59', '2023-03-31 23:59:59'),
        ('2023-03-31 23:59:59', '2023-04-30 23:59:59'),
        ('2023-04-30 23:59:59', '2023-05-31 23:59:59'),
        ('2023-05-31 23:59:59', '2023-06-30 23:59:59'),
        ('2023-06-30 23:59:59', '2023-07-31 23:59:59'),
        ('2023-07-31 23:59:59', '2023-08-31 23:59:59'),
        ('2023-08-31 23:59:59', '2023-09-30 23:59:59')
    ]
    # Validation
    val_cutoffs = [
        ('2023-09-30 23:59:59', '2023-11-15 23:59:59')
    ]
    # Test
    test_cutoffs = [
        ('2023-11-15 23:59:59', '2023-12-31 23:59:59')
    ]
    return train_cutoffs, val_cutoffs, test_cutoffs

def build_graph_snapshot(df, cutoff_time, horizon_time, anomalous_ids, global_node_map, accounts_df):
    cutoff_time = pd.to_datetime(cutoff_time)
    horizon_time = pd.to_datetime(horizon_time)
    
    # 1. Historical data strictly <= cutoff_time
    hist_df = df[df['timestamp'] <= cutoff_time].copy()
    
    if len(hist_df) == 0:
        return None
        
    # Entities seen up to cutoff
    entities = pd.concat([hist_df['source_account'], hist_df['destination_account']]).unique()
    
    # Map entities to local node indices for this graph
    node_mapping = {ent: i for i, ent in enumerate(entities)}
    
    # 2. Node Features
    # features: [transaction_count, total_inflow, total_outflow, avg_amount, is_company, is_employee, is_vendor]
    node_features = np.zeros((len(entities), 7), dtype=np.float32)
    
    # Calculate stats
    outflow_stats = hist_df.groupby('source_account')['amount'].agg(['count', 'sum', 'mean']).reindex(entities, fill_value=0)
    inflow_stats = hist_df.groupby('destination_account')['amount'].agg(['count', 'sum', 'mean']).reindex(entities, fill_value=0)
    
    node_features[:, 0] = outflow_stats['count'].values + inflow_stats['count'].values # transaction_count
    node_features[:, 1] = inflow_stats['sum'].values # total_inflow
    node_features[:, 2] = outflow_stats['sum'].values # total_outflow
    node_features[:, 3] = np.where(node_features[:, 0] > 0, (node_features[:, 1] + node_features[:, 2]) / node_features[:, 0], 0) # avg_amount
    
    # Map account types
    if accounts_df is not None:
        type_mapping = accounts_df.set_index('id')['account_type'].to_dict()
        for i, ent in enumerate(entities):
            atype = type_mapping.get(ent, 'unknown')
            if atype == 'company':
                node_features[i, 4] = 1.0
            elif atype == 'employee':
                node_features[i, 5] = 1.0
            elif atype == 'vendor':
                node_features[i, 6] = 1.0
    
    x = torch.tensor(node_features, dtype=torch.float)
    
    # 3. Edge Index and Edge Features
    source_indices = hist_df['source_account'].map(node_mapping).values
    dest_indices = hist_df['destination_account'].map(node_mapping).values
    
    edge_index = torch.tensor(np.vstack((source_indices, dest_indices)), dtype=torch.long)
    
    # Edge features: amount, time_since_cutoff
    # We can use (cutoff_time - timestamp).dt.days as a feature
    time_since = (cutoff_time - hist_df['timestamp']).dt.total_seconds() / 86400.0
    edge_attr = torch.tensor(np.column_stack((hist_df['amount'].values, time_since.values)), dtype=torch.float)
    
    # 4. Target construction
    # Node is anomalous if it participated in an anomalous transaction in (cutoff, horizon]
    future_df = df[(df['timestamp'] > cutoff_time) & (df['timestamp'] <= horizon_time)]
    future_anom = future_df[future_df['transaction_id'].isin(anomalous_ids)]
    
    anomalous_entities = set(future_anom['source_account']).union(set(future_anom['destination_account']))
    
    y = np.zeros(len(entities), dtype=np.float32)
    for i, ent in enumerate(entities):
        if ent in anomalous_entities:
            y[i] = 1.0
            
    y = torch.tensor(y, dtype=torch.float)
    
    # Store global node IDs to help with mapping if needed
    global_ids = [global_node_map.get(e, -1) for e in entities]
    
    data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr, y=y)
    data.global_ids = torch.tensor(global_ids, dtype=torch.long)
    data.cutoff = str(cutoff_time)
    
    return data

def build_graph_datasets(raw_tx_path, gt_path, accounts_path, output_dir):
    print("Loading data...")
    df = pd.read_parquet(raw_tx_path)
    with open(gt_path, 'r') as f:
        gt = json.load(f)
        
    with open(accounts_path, 'r') as f:
        accounts_data = json.load(f)
    accounts_df = pd.DataFrame(accounts_data)
        
    anomalous_ids = set(gt.get('anomalous_transactions', []))
    
    # Build global node map for robust entity tracking
    all_entities = pd.concat([df['source_account'], df['destination_account']]).unique()
    global_node_map = {ent: i for i, ent in enumerate(all_entities)}
    
    train_cutoffs, val_cutoffs, test_cutoffs = get_snapshot_intervals()
    
    os.makedirs(output_dir, exist_ok=True)
    
    for split_name, cutoffs in zip(['train', 'val', 'test'], [train_cutoffs, val_cutoffs, test_cutoffs]):
        print(f"Building {split_name} snapshots...")
        snapshots = []
        for cutoff, horizon in cutoffs:
            data = build_graph_snapshot(df, cutoff, horizon, anomalous_ids, global_node_map, accounts_df)
            if data is not None:
                snapshots.append(data)
                
        torch.save(snapshots, os.path.join(output_dir, f'{split_name}_graphs.pt'))
        print(f"Saved {len(snapshots)} snapshots for {split_name}.")
        
if __name__ == "__main__":
    build_graph_datasets(
        'data/processed/transactions.parquet',
        'data/processed/ground_truth.json',
        'data/processed/accounts.json',
        'data/processed/ml/graph'
    )
