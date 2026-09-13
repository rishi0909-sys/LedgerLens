import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch_geometric.data import DataLoader as PyGDataLoader # For batches of graphs, though we can just iterate
from sklearn.metrics import precision_recall_curve
import numpy as np

from backend.ml.graph.graph_models import BasicGraphSAGE, EdgeGraphSAGE
from backend.ml.transaction_anomaly import compute_metrics

def set_seed(seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)

def load_graphs(split_name, data_dir='data/processed/ml/graph'):
    path = os.path.join(data_dir, f'{split_name}_graphs.pt')
    if os.path.exists(path):
        return torch.load(path, weights_only=False)
    return []

def train_model(model, train_graphs, val_graphs, epochs, lr, device, use_edge_attr=False):
    # Calculate pos_weight
    num_pos = sum((g.y == 1).sum().item() for g in train_graphs)
    num_total = sum(g.y.size(0) for g in train_graphs)
    num_neg = num_total - num_pos
    pos_weight = torch.tensor([num_neg / max(1.0, num_pos)]).to(device)
    
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    
    best_val_f1 = 0.0
    best_state = None
    best_threshold = 0.5
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for g in train_graphs:
            g = g.to(device)
            optimizer.zero_grad()
            if use_edge_attr:
                logits = model(g.x, g.edge_index, g.edge_attr)
            else:
                logits = model(g.x, g.edge_index)
            loss = criterion(logits, g.y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            
        # Validation
        model.eval()
        val_logits = []
        val_targets = []
        with torch.no_grad():
            for g in val_graphs:
                g = g.to(device)
                if use_edge_attr:
                    logits = model(g.x, g.edge_index, g.edge_attr)
                else:
                    logits = model(g.x, g.edge_index)
                val_logits.extend(logits.cpu().numpy())
                val_targets.extend(g.y.cpu().numpy())
                
        val_probs = torch.sigmoid(torch.tensor(val_logits)).numpy()
        val_targets = np.array(val_targets)
        
        # Guard against zero variance targets
        if len(np.unique(val_targets)) > 1:
            precisions, recalls, thresholds = precision_recall_curve(val_targets, val_probs)
            f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
            best_idx = np.argmax(f1_scores)
            epoch_thresh = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
            epoch_f1 = f1_scores[best_idx] if len(f1_scores) > 0 else 0.0
        else:
            epoch_thresh = 0.5
            epoch_f1 = 0.0
            
        print(f"Epoch {epoch+1}/{epochs} | Loss: {train_loss/len(train_graphs):.4f} | Val F1: {epoch_f1:.4f}")
        
        if epoch_f1 >= best_val_f1:
            best_val_f1 = epoch_f1
            best_threshold = epoch_thresh
            best_state = model.state_dict().copy()
            
    if best_state is not None:
        model.load_state_dict(best_state)
        
    return model, best_threshold

def evaluate_model(model, test_graphs, threshold, device, use_edge_attr=False):
    model.eval()
    test_logits = []
    test_targets = []
    with torch.no_grad():
        for g in test_graphs:
            g = g.to(device)
            if use_edge_attr:
                logits = model(g.x, g.edge_index, g.edge_attr)
            else:
                logits = model(g.x, g.edge_index)
            test_logits.extend(logits.cpu().numpy())
            test_targets.extend(g.y.cpu().numpy())
            
    test_probs = torch.sigmoid(torch.tensor(test_logits)).numpy()
    test_targets = np.array(test_targets)
    test_preds = (test_probs >= threshold).astype(int)
    
    if len(np.unique(test_targets)) > 1:
        metrics = compute_metrics(test_targets, test_probs, test_preds)
    else:
        metrics = {"PR-AUC": 0.0}
    return metrics

def run_graph_pipeline():
    set_seed(42)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    train_graphs = load_graphs('train')
    val_graphs = load_graphs('val')
    test_graphs = load_graphs('test')
    
    in_channels = 7 # Features
    hidden_channels = 64
    out_channels = 1
    edge_channels = 2
    
    results = {}
    
    # 1. Topology Only
    print("\n--- Training Topology-Only GraphSAGE ---")
    model_top = BasicGraphSAGE(in_channels, hidden_channels, out_channels).to(device)
    model_top, thresh_top = train_model(model_top, train_graphs, val_graphs, epochs=20, lr=1e-3, device=device, use_edge_attr=False)
    metrics_top = evaluate_model(model_top, test_graphs, thresh_top, device, use_edge_attr=False)
    results['GraphSAGE_Topology'] = metrics_top["PR-AUC"]
    print(f"Topology Test PR-AUC: {metrics_top['PR-AUC']:.4f}")
    
    # 2. Topology + Edge Attributes
    print("\n--- Training Edge-Aware GraphSAGE ---")
    model_edge = EdgeGraphSAGE(in_channels, hidden_channels, out_channels, edge_channels).to(device)
    model_edge, thresh_edge = train_model(model_edge, train_graphs, val_graphs, epochs=20, lr=1e-3, device=device, use_edge_attr=True)
    metrics_edge = evaluate_model(model_edge, test_graphs, thresh_edge, device, use_edge_attr=True)
    results['GraphSAGE_Topology+Edge'] = metrics_edge["PR-AUC"]
    print(f"Topology+Edge Test PR-AUC: {metrics_edge['PR-AUC']:.4f}")
    
    # Save the edge model
    model_dir = 'data/ml/models'
    os.makedirs(model_dir, exist_ok=True)
    
    torch.save(model_edge.state_dict(), os.path.join(model_dir, 'graphsage-edge-v1.pt'))
    with open(os.path.join(model_dir, 'graphsage-edge-v1_metadata.json'), 'w') as f:
        json.dump({
            "model_id": "graphsage-edge-v1",
            "model_type": "graphsage_edge",
            "dataset_version": "1.0",
            "hyperparameters": {"hidden_channels": 64},
            "test_metrics": metrics_edge,
            "threshold": float(thresh_edge),
            "artifact_path": os.path.join(model_dir, 'graphsage-edge-v1.pt')
        }, f, indent=2)
        
    print("\n--- Results ---")
    print(json.dumps(results, indent=2))
    with open('data/ml/graph_ablation_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_graph_pipeline()
