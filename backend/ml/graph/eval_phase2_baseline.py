import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
import json
import torch
import pandas as pd
import numpy as np
import xgboost as xgb

from backend.ml.graph.graph_training import load_graphs
from backend.ml.transaction_anomaly import compute_metrics

def evaluate_phase2_on_nodes():
    # Load test graphs to get the exact same targets and evaluation period
    test_graphs = load_graphs('test')
    
    if len(test_graphs) == 0:
        print("No test graphs found.")
        return
        
    # We only have one test snapshot but let's loop
    y_true_all = []
    y_pred_probs_all = []
    
    # Load Phase 2 model
    model_dir = 'data/ml/models'
    phase2_model_path = os.path.join(model_dir, 'xgb-transaction-v1.json')
    if not os.path.exists(phase2_model_path):
        print(f"Phase 2 model not found at {phase2_model_path}")
        return
        
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
    xgb_model = xgb.XGBClassifier(n_jobs=1)
    xgb_model.load_model(phase2_model_path)
    
    with open(os.path.join(model_dir, 'xgb-transaction-v1_metadata.json')) as f:
        p2_meta = json.load(f)
    features = p2_meta['features']
    
    # Load raw transactions to get historical features
    df = pd.read_parquet('data/processed/ml/test.parquet') # test set transactions for phase 2
    # Wait, we need the transactions up to `cutoff` for the graph. The graph cutoff might be inside the test period.
    # Actually, we can just load the full df with features already computed
    # To be perfectly causal, we can't use transactions after `cutoff` to score the node.
    full_df = pd.read_parquet('data/processed/transactions.parquet')
    from backend.ml.transaction_features import construct_features
    full_df = construct_features(full_df)
    
    for g in test_graphs:
        cutoff_time = pd.to_datetime(g.cutoff)
        
        # Historical data for Phase 2 scoring
        hist_df = full_df[full_df['timestamp'] <= cutoff_time]
        
        # We need the node IDs to map back to entities
        # Since g doesn't store the entity names directly (except we put global_ids),
        # Wait, we can re-extract entities the exact same way as graph_dataset.py
        entities = pd.concat([hist_df['source_account'], hist_df['destination_account']]).unique()
        
        # Ensure it matches the graph size
        assert len(entities) == g.y.size(0)
        
        # Predict all historical transactions
        if len(hist_df) > 0:
            X_hist = hist_df[features].values
            hist_probs = xgb_model.predict_proba(X_hist)[:, 1]
            hist_df = hist_df.copy()
            hist_df['xgb_prob'] = hist_probs
        else:
            hist_df = pd.DataFrame(columns=['source_account', 'destination_account', 'xgb_prob'])
            
        # Aggregate max probability for each entity
        src_max = hist_df.groupby('source_account')['xgb_prob'].max()
        dst_max = hist_df.groupby('destination_account')['xgb_prob'].max()
        
        node_probs = []
        for ent in entities:
            p_src = src_max.get(ent, 0.0)
            p_dst = dst_max.get(ent, 0.0)
            node_probs.append(max(p_src, p_dst))
            
        y_true_all.extend(g.y.numpy())
        y_pred_probs_all.extend(node_probs)
        
    y_true = np.array(y_true_all)
    y_probs = np.array(y_pred_probs_all)
    y_preds = (y_probs >= 0.5).astype(int)
    
    if len(np.unique(y_true)) > 1:
        metrics = compute_metrics(y_true, y_probs, y_preds)
    else:
        metrics = {"PR-AUC": 0.0}
        
    print(f"Phase 2 XGBoost (Node Aggregated) Test PR-AUC: {metrics['PR-AUC']:.4f}")
    
    with open('data/ml/graph_phase2_baseline_results.json', 'w') as f:
        json.dump(metrics, f, indent=2)

if __name__ == "__main__":
    evaluate_phase2_on_nodes()
