import os
import pandas as pd

def merge_evidence():
    for split in ['train', 'val', 'test']:
        base = pd.read_parquet(f'data/processed/ml/multimodal/{split}_tx_doc.parquet')
        seq = pd.read_parquet(f'data/processed/ml/multimodal/{split}_seq.parquet')
        graph = pd.read_parquet(f'data/processed/ml/multimodal/{split}_graph.parquet')
        
        res = base.merge(seq, on='transaction_id', how='left')
        res['seq_available'] = res['score_seq'].notna().astype(int)
        res['score_seq'] = res['score_seq'].fillna(0.0)
        
        res = res.merge(graph, on='transaction_id', how='left')
        res['graph_available'] = res['score_graph'].notna().astype(int)
        res['score_graph'] = res['score_graph'].fillna(0.0)
        
        res.to_parquet(f'data/processed/ml/multimodal/{split}_evidence.parquet')

if __name__ == '__main__':
    merge_evidence()
