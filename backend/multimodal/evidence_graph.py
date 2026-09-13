import os
import torch
import pandas as pd
import numpy as np
from datetime import datetime

def generate_graph_evidence():
    print("Generating Graph Evidence from Node Classifications...")
    from backend.ml.graph.graph_models import EdgeGraphSAGE
    
    # 1. Build Global Node Map exactly as in dataset prep
    df_raw = pd.read_parquet('data/processed/transactions.parquet')
    all_entities = pd.concat([df_raw['source_account'], df_raw['destination_account']]).unique()
    global_node_map = {ent: i for i, ent in enumerate(all_entities)}
    
    # 2. Iterate through splits to get node probabilities per cutoff
    node_probs = {} # dict mapping global_id -> max prob seen
    
    for split in ['train', 'val', 'test']:
        snaps = torch.load(f'data/processed/ml/graph/{split}_graphs.pt', weights_only=False)
        if not snaps:
            continue
            
        node_dim = snaps[0].x.shape[1]
        edge_dim = snaps[0].edge_attr.shape[1]
        
        model = EdgeGraphSAGE(in_channels=node_dim, hidden_channels=64, out_channels=1, edge_channels=edge_dim)
        model.load_state_dict(torch.load('data/ml/models/graphsage-edge-v1.pt', weights_only=True))
        model.eval()
        
        with torch.no_grad():
            for snap in snaps:
                out = model(snap.x, snap.edge_index, snap.edge_attr)
                p = torch.sigmoid(out).numpy().flatten()
                
                # Update max seen prob for each global ID
                for global_id, prob in zip(snap.global_ids.numpy(), p):
                    if global_id not in node_probs:
                        node_probs[global_id] = prob
                    else:
                        node_probs[global_id] = max(node_probs[global_id], prob)
                        
    # 3. Apply to transaction dataframes
    for split in ['train', 'val', 'test']:
        tx_df = pd.read_parquet(f'data/processed/ml/{split}.parquet')
        
        def get_graph_score(row):
            src_id = global_node_map.get(row['source_account'], -1)
            dst_id = global_node_map.get(row['destination_account'], -1)
            p_src = node_probs.get(src_id, 0.0)
            p_dst = node_probs.get(dst_id, 0.0)
            return max(p_src, p_dst)
            
        scores = tx_df.apply(get_graph_score, axis=1)
        
        out_df = pd.DataFrame({'transaction_id': tx_df['transaction_id'], 'score_graph': scores})
        out_df.to_parquet(f'data/processed/ml/multimodal/{split}_graph.parquet')

if __name__ == '__main__':
    generate_graph_evidence()
