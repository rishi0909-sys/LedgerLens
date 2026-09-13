import os
import pandas as pd
import numpy as np
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks
from backend.rl.environment import FinancialInvestigationEnv

def train_rl_agent():
    print("Loading RL data...")
    train_df = pd.read_parquet('data/processed/ml/rl/train_rl.parquet')
    
    # Ensure there are enough windows to train on
    print(f"Train windows: {len(train_df['window_id'].unique())}")
    
    env = FinancialInvestigationEnv(train_df, n_candidates=20, budget=5)
    
    print("Training MaskablePPO...")
    model = MaskablePPO(
        "MlpPolicy",
        env,
        gamma=0.99,
        learning_rate=3e-4,
        n_steps=256,
        batch_size=64,
        ent_coef=0.01,
        seed=42,
        verbose=1
    )
    
    model.learn(total_timesteps=10000)
    
    os.makedirs('data/ml/models', exist_ok=True)
    model.save('data/ml/models/rl-investigator-v1.zip')
    print("Model saved to data/ml/models/rl-investigator-v1.zip")
    
if __name__ == "__main__":
    train_rl_agent()
