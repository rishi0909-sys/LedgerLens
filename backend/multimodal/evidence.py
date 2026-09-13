import os
import torch
import pandas as pd
import xgboost as xgb
import numpy as np

def generate_evidence():
    print("Generating Multimodal Evidence...")
    # Load all transactions to act as the base frame
    data_dir = 'data/processed/ml'
    train_tx = pd.read_parquet(os.path.join(data_dir, 'train.parquet'))
    val_tx = pd.read_parquet(os.path.join(data_dir, 'val.parquet'))
    test_tx = pd.read_parquet(os.path.join(data_dir, 'test.parquet'))
    
    # We will build a unified evidence dataframe for each split
    def build_evidence(split_name, tx_df):
        print(f"Building evidence for {split_name}...")
        df = pd.DataFrame({'transaction_id': tx_df['transaction_id'], 'is_anomalous': tx_df['is_anomalous']})
        
        # 1. Transaction Evidence
        print(" - Transaction Evidence")
        from backend.ml.transaction_anomaly import FEATURES as TX_FEATURES
        tx_model = xgb.XGBClassifier()
        tx_model.load_model('data/ml/models/xgb-transaction-v1.json')
        tx_scores = tx_model.predict_proba(tx_df[TX_FEATURES])[:, 1]
        df['score_tx'] = tx_scores
        df['tx_available'] = 1
        
        # 2. Document Evidence
        print(" - Document Evidence")
        doc_model = xgb.XGBClassifier()
        doc_model.load_model('data/ml/models/xgb-document-v1.json')
        doc_df = pd.read_parquet(os.path.join(data_dir, 'document_features.parquet'))
        # Map by invoice_id
        tx_doc = tx_df[['transaction_id', 'invoice_id']].merge(doc_df, on='invoice_id', how='left')
        
        nlp_cols = [c for c in doc_df.columns if c.startswith('nlp_emb_')]
        struct_cols = ['amount_mismatch', 'vendor_mismatch', 'date_mismatch', 'arithmetic_error']
        cv_cols = ['duplicate_similarity']
        doc_features = nlp_cols + struct_cols + cv_cols
        
        doc_available = tx_doc['invoice_id'].notna() & (tx_doc['invoice_id'] != 0) & (tx_doc['document_id'].notna())
        doc_X = tx_doc[doc_features].fillna(0)
        
        doc_scores = doc_model.predict_proba(doc_X)[:, 1]
        df['score_doc'] = np.where(doc_available, doc_scores, 0.0)
        df['doc_available'] = doc_available.astype(int)
        
        # 3. Sequence Evidence
        print(" - Sequence Evidence")
        # Load the PyTorch LSTM model
        from backend.ml.sequence_models import LSTMFraudDetector
        import torch.nn as nn
        
        # Determine feature dim from sequences
        seq_data = torch.load(f'data/processed/ml/sequences/{split_name}_seq.pt')
        seq_features = seq_data['features']
        input_dim = seq_features.shape[2]
        
        seq_model = LSTMFraudDetector(input_dim=input_dim, hidden_dim=64, num_layers=2)
        seq_model.load_state_dict(torch.load('data/ml/models/lstm-sequence-v1.pt'))
        seq_model.eval()
        
        with torch.no_grad():
            seq_out = seq_model(torch.tensor(seq_features, dtype=torch.float32), torch.tensor(seq_data['masks'], dtype=torch.bool))
            seq_probs = torch.sigmoid(seq_out).numpy().flatten()
            
        seq_map = {txn_id: prob for txn_id, prob in zip(seq_data['metadata'], seq_probs)}
        
        df['score_seq'] = df['transaction_id'].map(seq_map).fillna(0.0)
        df['seq_available'] = df['transaction_id'].isin(seq_map).astype(int)
        
        # 4. Graph Evidence
        print(" - Graph Evidence")
        from backend.ml.graph.graph_models import EdgeFraudSAGE
        # Determine node/edge feature dims from the first snapshot
        graph_snapshots = torch.load(f'data/processed/ml/graph/{split_name}_graphs.pt')
        if len(graph_snapshots) > 0:
            node_dim = graph_snapshots[0].x.shape[1]
            edge_dim = graph_snapshots[0].edge_attr.shape[1]
            
            graph_model = EdgeFraudSAGE(node_in_dim=node_dim, edge_in_dim=edge_dim, hidden_dim=64)
            graph_model.load_state_dict(torch.load('data/ml/models/graphsage-edge-v1.pt'))
            graph_model.eval()
            
            graph_map = {}
            with torch.no_grad():
                for snap in graph_snapshots:
                    out = graph_model(snap.x, snap.edge_index, snap.edge_attr, snap.target_edge_indices)
                    probs = torch.sigmoid(out).numpy().flatten()
                    for txn_id, prob in zip(snap.target_tx_ids, probs):
                        graph_map[txn_id] = prob
                        
            df['score_graph'] = df['transaction_id'].map(graph_map).fillna(0.0)
            df['graph_available'] = df['transaction_id'].isin(graph_map).astype(int)
        else:
            df['score_graph'] = 0.0
            df['graph_available'] = 0
            
        return df

    train_ev = build_evidence('train', train_tx)
    val_ev = build_evidence('val', val_tx)
    test_ev = build_evidence('test', test_tx)
    
    os.makedirs('data/processed/ml/multimodal', exist_ok=True)
    train_ev.to_parquet('data/processed/ml/multimodal/train_evidence.parquet')
    val_ev.to_parquet('data/processed/ml/multimodal/val_evidence.parquet')
    test_ev.to_parquet('data/processed/ml/multimodal/test_evidence.parquet')
    print("Evidence extraction complete.")

if __name__ == "__main__":
    generate_evidence()
