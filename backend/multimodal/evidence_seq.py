import os
import torch
import pandas as pd

def generate_seq_evidence():
    print("Generating Sequence Evidence...")
    from backend.ml.sequence_models import SequenceLSTM
    for split in ['train', 'val', 'test']:
        seq_data = torch.load(f'data/processed/ml/sequences/{split}_seq.pt', weights_only=False)
        seq_features = seq_data['features']
        input_dim = seq_features.shape[2]
        
        model = SequenceLSTM(input_dim=input_dim, hidden_dim=64, num_layers=2)
        model.load_state_dict(torch.load('data/ml/models/lstm-sequence-v1.pt', weights_only=True))
        model.eval()
        
        with torch.no_grad():
            out = model(torch.tensor(seq_features, dtype=torch.float32), torch.tensor(seq_data['masks'], dtype=torch.bool))
            probs = torch.sigmoid(out).numpy().flatten()
            
        df = pd.DataFrame({'transaction_id': seq_data['metadata'], 'score_seq': probs})
        df.to_parquet(f'data/processed/ml/multimodal/{split}_seq.parquet')

if __name__ == '__main__':
    generate_seq_evidence()
