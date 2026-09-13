import json
import torch
import numpy as np
import xgboost as xgb
from torch_geometric.utils import degree, to_networkx
import networkx as nx

from backend.ml.graph.graph_training import load_graphs
from backend.ml.transaction_anomaly import compute_metrics

def compute_graph_summary_features(g):
    # g is a PyG Data object
    # existing node features: g.x (7 features)
    # Let's compute topological features
    
    # 1. Degree
    deg = degree(g.edge_index[0], num_nodes=g.num_nodes).numpy()
    in_deg = degree(g.edge_index[1], num_nodes=g.num_nodes).numpy()
    
    # We can also compute clustering coeff using networkx
    nx_g = to_networkx(g, to_undirected=True)
    clustering = np.array(list(nx.clustering(nx_g).values()))
    
    # Combine features
    summary_features = np.column_stack([deg, in_deg, clustering])
    
    # Total features: original 7 + 3 summary = 10
    features = np.column_stack([g.x.numpy(), summary_features])
    return features

def prepare_xgb_data(graphs):
    X_list = []
    y_list = []
    
    for g in graphs:
        X_feat = compute_graph_summary_features(g)
        X_list.append(X_feat)
        y_list.append(g.y.numpy())
        
    X = np.vstack(X_list)
    y = np.concatenate(y_list)
    return X, y

def train_eval_summary_baseline():
    train_graphs = load_graphs('train')
    val_graphs = load_graphs('val')
    test_graphs = load_graphs('test')
    
    X_train, y_train = prepare_xgb_data(train_graphs)
    X_val, y_val = prepare_xgb_data(val_graphs)
    X_test, y_test = prepare_xgb_data(test_graphs)
    
    print(f"Train Shape: {X_train.shape}, Val Shape: {X_val.shape}, Test Shape: {X_test.shape}")
    
    # Weighted ratio for XGBoost
    pos_count = y_train.sum()
    scale_pos_weight = (len(y_train) - pos_count) / max(1.0, pos_count)
    
    import os
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
    
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric='logloss',
        early_stopping_rounds=10,
        n_jobs=1
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    
    # Test Evaluation
    probs = model.predict_proba(X_test)[:, 1]
    preds = model.predict(X_test)
    
    metrics = compute_metrics(y_test, probs, preds)
    print(f"XGBoost + Graph Summary Test PR-AUC: {metrics['PR-AUC']:.4f}")
    
    with open('data/ml/graph_summary_results.json', 'w') as f:
        json.dump(metrics, f, indent=2)

if __name__ == "__main__":
    train_eval_summary_baseline()
