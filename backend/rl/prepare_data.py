import pandas as pd
import numpy as np
import pickle
import xgboost as xgb
import os

def prepare_rl_data():
    print("Preparing RL candidate queues...")
    os.makedirs('data/processed/ml/rl', exist_ok=True)
    
    xgb_fusion = xgb.XGBClassifier()
    xgb_fusion.load_model('data/ml/models/fusion-xgb-v1.json')
    
    base_features = [
        'cal_tx', 'tx_available',
        'cal_doc', 'doc_available',
        'cal_seq', 'seq_available',
        'cal_graph', 'graph_available'
    ]
    xgb_features = base_features + ['conflict_tx_doc', 'conflict_tx_seq']
    
    for split in ['train', 'val', 'test']:
        print(f"Processing {split}...")
        ev = pd.read_parquet(f'data/processed/ml/multimodal/{split}_calibrated.parquet')
        
        ev['conflict_tx_doc'] = np.abs(ev['cal_tx'] - ev['cal_doc'])
        ev['conflict_tx_seq'] = np.abs(ev['cal_tx'] - ev['cal_seq'])
        
        # We need fused risk score (from XGBoost)
        ev['fused_score'] = xgb_fusion.predict_proba(ev[xgb_features])[:, 1]
        
        # We need timestamps to build chronological episodes
        tx_raw = pd.read_parquet(f'data/processed/ml/{split}.parquet')
        
        ev = ev.merge(tx_raw[['transaction_id', 'timestamp']], on='transaction_id', how='left')
        ev['timestamp'] = pd.to_datetime(ev['timestamp'])
        ev = ev.sort_values('timestamp').reset_index(drop=True)
        
        # Select the top N suspicious transactions within weekly windows?
        # The prompt says: Phase 7 explicitly prioritization within a Phase 6 suspicious queue.
        # So we pre-filter the dataset to only cases that have a minimum fused_score?
        # Let's say fused_score > 0.05 to filter out totally normal ones, simulating an investigation queue.
        # But we need episodes. Let's group by 1-week or 1-day windows.
        
        ev['window_id'] = ev['timestamp'].dt.to_period('W').astype(str)
        
        # Save augmented dataframe
        ev.to_parquet(f'data/processed/ml/rl/{split}_rl.parquet')
        
if __name__ == "__main__":
    prepare_rl_data()
