import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from sklearn.metrics import precision_recall_curve, f1_score
from datetime import datetime

from backend.ml.sequence_models import SequenceLSTM, SequenceTransformer
from backend.ml.transaction_anomaly import compute_metrics # reuse metrics logic

def set_seed(seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def load_data(split_name, data_dir='data/processed/ml/sequences'):
    path = os.path.join(data_dir, f'{split_name}_seq.pt')
    data = torch.load(path, weights_only=False)
    dataset = TensorDataset(
        torch.tensor(data['features']),
        torch.tensor(data['masks']),
        torch.tensor(data['targets'])
    )
    return dataset, data['targets'], data['metadata']

def train_model(model, train_loader, val_loader, val_targets, epochs, lr, device, model_name):
    criterion = nn.BCEWithLogitsLoss() # handles class imbalance implicitly if we set pos_weight
    
    # Calculate pos_weight from train_loader
    num_pos = 0
    num_total = 0
    for _, _, targets in train_loader:
        num_pos += targets.sum().item()
        num_total += targets.size(0)
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
        for features, masks, targets in train_loader:
            features, masks, targets = features.to(device), masks.to(device), targets.to(device)
            
            optimizer.zero_grad()
            logits = model(features, mask=masks)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            
        # Validation
        model.eval()
        val_logits = []
        with torch.no_grad():
            for features, masks, targets in val_loader:
                features, masks = features.to(device), masks.to(device)
                logits = model(features, mask=masks)
                val_logits.extend(logits.cpu().numpy())
                
        val_probs = torch.sigmoid(torch.tensor(val_logits)).numpy()
        
        precisions, recalls, thresholds = precision_recall_curve(val_targets, val_probs)
        f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
        best_idx = np.argmax(f1_scores)
        epoch_thresh = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
        epoch_f1 = f1_scores[best_idx] if len(f1_scores) > 0 else 0.0
        
        print(f"[{model_name}] Epoch {epoch+1}/{epochs} | Loss: {train_loss/len(train_loader):.4f} | Val F1: {epoch_f1:.4f}")
        
        if epoch_f1 > best_val_f1:
            best_val_f1 = epoch_f1
            best_threshold = epoch_thresh
            best_state = model.state_dict().copy()
            
    if best_state is not None:
        model.load_state_dict(best_state)
        
    return model, best_threshold

def evaluate_model(model, test_loader, test_targets, threshold, device):
    model.eval()
    test_logits = []
    with torch.no_grad():
        for features, masks, targets in test_loader:
            features, masks = features.to(device), masks.to(device)
            logits = model(features, mask=masks)
            test_logits.extend(logits.cpu().numpy())
            
    test_probs = torch.sigmoid(torch.tensor(test_logits)).numpy()
    test_preds = (test_probs >= threshold).astype(int)
    
    metrics = compute_metrics(test_targets, test_probs, test_preds)
    return metrics

def run_sequence_pipeline():
    set_seed(42)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    train_ds, train_targets, _ = load_data('train')
    val_ds, val_targets, _ = load_data('val')
    test_ds, test_targets, _ = load_data('test')
    
    batch_size = 32
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)
    
    input_dim = 15 # length of FEATURES
    
    # LSTM
    lstm_model = SequenceLSTM(input_dim=input_dim, hidden_dim=64, num_layers=2, dropout=0.2).to(device)
    lstm_model, lstm_thresh = train_model(lstm_model, train_loader, val_loader, val_targets, epochs=20, lr=1e-3, device=device, model_name="LSTM")
    lstm_metrics = evaluate_model(lstm_model, test_loader, test_targets, lstm_thresh, device)
    
    print(f"LSTM Test PR-AUC: {lstm_metrics['PR-AUC']:.4f}")
    
    # Transformer
    tf_model = SequenceTransformer(input_dim=input_dim, d_model=64, nhead=4, num_layers=2, dropout=0.2).to(device)
    tf_model, tf_thresh = train_model(tf_model, train_loader, val_loader, val_targets, epochs=20, lr=1e-3, device=device, model_name="Transformer")
    tf_metrics = evaluate_model(tf_model, test_loader, test_targets, tf_thresh, device)
    
    print(f"Transformer Test PR-AUC: {tf_metrics['PR-AUC']:.4f}")
    
    # Save Models and Registry
    model_dir = 'data/ml/models'
    os.makedirs(model_dir, exist_ok=True)
    
    # Save LSTM
    torch.save(lstm_model.state_dict(), os.path.join(model_dir, 'lstm-sequence-v1.pt'))
    with open(os.path.join(model_dir, 'lstm-sequence-v1_metadata.json'), 'w') as f:
        json.dump({
            "model_id": "lstm-sequence-v1",
            "model_type": "lstm",
            "sequence_length": 20,
            "hyperparameters": {"hidden_dim": 64, "num_layers": 2},
            "test_metrics": lstm_metrics,
            "threshold": float(lstm_thresh),
            "artifact_path": os.path.join(model_dir, 'lstm-sequence-v1.pt')
        }, f, indent=2)
        
    # Save Transformer
    torch.save(tf_model.state_dict(), os.path.join(model_dir, 'transformer-sequence-v1.pt'))
    with open(os.path.join(model_dir, 'transformer-sequence-v1_metadata.json'), 'w') as f:
        json.dump({
            "model_id": "transformer-sequence-v1",
            "model_type": "transformer",
            "sequence_length": 20,
            "hyperparameters": {"d_model": 64, "nhead": 4, "num_layers": 2},
            "test_metrics": tf_metrics,
            "threshold": float(tf_thresh),
            "artifact_path": os.path.join(model_dir, 'transformer-sequence-v1.pt')
        }, f, indent=2)

if __name__ == "__main__":
    run_sequence_pipeline()
