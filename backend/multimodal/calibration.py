import pandas as pd
import numpy as np
import pickle
import os
from sklearn.calibration import IsotonicRegression

def calibrate_scores():
    print("Calibrating Modality Scores...")
    data_dir = 'data/processed/ml/multimodal'
    train_ev = pd.read_parquet(os.path.join(data_dir, 'train_evidence.parquet'))
    val_ev = pd.read_parquet(os.path.join(data_dir, 'val_evidence.parquet'))
    test_ev = pd.read_parquet(os.path.join(data_dir, 'test_evidence.parquet'))
    
    calibrators = {}
    
    # We calibrate each modality separately on the validation set to avoid overfitting
    # and to ensure scores act like probabilities
    
    for modality in ['tx', 'doc', 'seq', 'graph']:
        score_col = f'score_{modality}'
        avail_col = f'{modality}_available'
        
        # Only fit calibrator where data is available
        mask = val_ev[avail_col] == 1
        if mask.sum() > 10:  # Need enough points
            ir = IsotonicRegression(out_of_bounds='clip')
            ir.fit(val_ev.loc[mask, score_col], val_ev.loc[mask, 'is_anomalous'])
            calibrators[modality] = ir
            
            # Apply calibration to all sets
            train_ev[f'cal_{modality}'] = np.where(
                train_ev[avail_col] == 1,
                ir.predict(train_ev[score_col]),
                0.0
            )
            val_ev[f'cal_{modality}'] = np.where(
                val_ev[avail_col] == 1,
                ir.predict(val_ev[score_col]),
                0.0
            )
            test_ev[f'cal_{modality}'] = np.where(
                test_ev[avail_col] == 1,
                ir.predict(test_ev[score_col]),
                0.0
            )
        else:
            # Fallback if extremely sparse (like documents in validation)
            print(f"Warning: {modality} too sparse in validation. Passing raw scores.")
            calibrators[modality] = "passthrough"
            train_ev[f'cal_{modality}'] = train_ev[score_col]
            val_ev[f'cal_{modality}'] = val_ev[score_col]
            test_ev[f'cal_{modality}'] = test_ev[score_col]
            
    # Save calibrators
    os.makedirs('data/ml/models', exist_ok=True)
    with open('data/ml/models/calibrators-v1.pkl', 'wb') as f:
        pickle.dump(calibrators, f)
        
    train_ev.to_parquet(os.path.join(data_dir, 'train_calibrated.parquet'))
    val_ev.to_parquet(os.path.join(data_dir, 'val_calibrated.parquet'))
    test_ev.to_parquet(os.path.join(data_dir, 'test_calibrated.parquet'))
    print("Calibration complete.")

if __name__ == "__main__":
    calibrate_scores()
