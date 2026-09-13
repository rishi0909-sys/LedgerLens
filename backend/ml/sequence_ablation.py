import os
import json
import torch
from backend.ml.sequence_dataset import build_sequence_data
from backend.ml.sequence_training import run_sequence_pipeline, load_data, train_model, evaluate_model
from backend.ml.sequence_models import SequenceLSTM, SequenceTransformer
from torch.utils.data import DataLoader

def run_ablation():
    lengths = [1, 10, 20]
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    input_dim = 15
    batch_size = 32
    
    results = {}
    
    for L in lengths:
        print(f"\n--- Running Ablation for L={L} ---")
        
        # 1. Build data
        build_sequence_data(
            'data/processed/transactions.parquet',
            'data/processed/ground_truth.json',
            'data/processed/ml/sequences',
            seq_len=L
        )
        
        # 2. Load data
        train_ds, train_targets, _ = load_data('train')
        val_ds, val_targets, _ = load_data('val')
        test_ds, test_targets, _ = load_data('test')
        
        train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
        test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)
        
        # 3. Train LSTM
        torch.manual_seed(42)
        lstm = SequenceLSTM(input_dim=input_dim, hidden_dim=64, num_layers=2, dropout=0.2).to(device)
        lstm, lstm_thresh = train_model(lstm, train_loader, val_loader, val_targets, epochs=20, lr=1e-3, device=device, model_name=f"LSTM L={L}")
        lstm_metrics = evaluate_model(lstm, test_loader, test_targets, lstm_thresh, device)
        
        # 4. Train Transformer
        torch.manual_seed(42)
        tf = SequenceTransformer(input_dim=input_dim, d_model=64, nhead=4, num_layers=2, dropout=0.2).to(device)
        tf, tf_thresh = train_model(tf, train_loader, val_loader, val_targets, epochs=20, lr=1e-3, device=device, model_name=f"Transformer L={L}")
        tf_metrics = evaluate_model(tf, test_loader, test_targets, tf_thresh, device)
        
        results[f"L={L}"] = {
            "LSTM_PR_AUC": lstm_metrics["PR-AUC"],
            "Transformer_PR_AUC": tf_metrics["PR-AUC"]
        }
        
    print("\n--- Ablation Results ---")
    print(json.dumps(results, indent=2))
    
    with open('data/ml/sequence_ablation_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_ablation()
