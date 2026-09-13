import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
import pandas as pd
import numpy as np
import xgboost as xgb
import json

from backend.ml.transaction_features import construct_features

def run():
    print("Loading metadata...")
    with open('data/ml/models/xgb-transaction-v1_metadata.json') as f:
        p2_meta = json.load(f)
    
    print("Loading data...")
    full_df = pd.read_parquet('data/processed/transactions.parquet')
    full_df = construct_features(full_df)
    
    print("Loading model...")
    xgb_model = xgb.XGBClassifier(n_jobs=1)
    xgb_model.load_model('data/ml/models/xgb-transaction-v1.json')
    
    print("Predicting...")
    # Ensure X_hist is float32 to avoid xgb errors
    features = [c for c in full_df.columns if c not in ['transaction_id', 'source_account', 'destination_account', 'timestamp']]
    X_hist = full_df[features].astype(np.float32).values
    probs = xgb_model.predict_proba(X_hist)[:, 1]
    
    print("Saving...")
    np.save('data/processed/ml/phase2_probs.npy', probs)
    print("Done.")
    
if __name__ == "__main__":
    run()
