import os
import pandas as pd
import numpy as np
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks
from backend.rl.environment import FinancialInvestigationEnv
from backend.rl.policies import RandomPolicy, HighestRiskPolicy, HighestDisagreementPolicy, TransactionRiskPolicy, OraclePolicy

def evaluate_policy(env, policy_obj, is_sb3=False):
    discoveries = []
    
    for _ in range(len(env.windows)):
        obs, info = env.reset()
        done = False
        window_discoveries = 0
        
        while not done:
            action_masks = info.get("action_mask", np.ones(env.n_candidates))
            
            if is_sb3:
                action, _ = policy_obj.predict(obs, action_masks=action_masks, deterministic=True)
            else:
                action, _ = policy_obj.predict(obs, action_masks=action_masks)
                
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            if reward > 0:
                window_discoveries += 1
                
        discoveries.append(window_discoveries)
        
    return np.mean(discoveries), np.sum(discoveries)

def run_evaluation():
    print("Loading test set...")
    test_df = pd.read_parquet('data/processed/ml/rl/test_rl.parquet')
    
    budgets = [5, 10, 20]
    results = []
    
    try:
        model = MaskablePPO.load('data/ml/models/rl-investigator-v1.zip')
    except Exception as e:
        print(f"Failed to load PPO model: {e}")
        model = None

    for b in budgets:
        print(f"\nEvaluating at Budget K={b}")
        env = FinancialInvestigationEnv(test_df, n_candidates=20, budget=b)
        
        policies = {
            'Random': RandomPolicy(env),
            'Transaction Risk': TransactionRiskPolicy(env),
            'Highest Risk': HighestRiskPolicy(env),
            'Highest Disagreement': HighestDisagreementPolicy(env),
            'Oracle': OraclePolicy(env)
        }
        
        for name, policy in policies.items():
            mean_disc, sum_disc = evaluate_policy(env, policy, is_sb3=False)
            print(f"{name}: {sum_disc} total anomalies discovered (avg {mean_disc:.2f}/window)")
            results.append({'Policy': name, 'Budget': b, 'Anomalies': sum_disc})
            
        if model is not None:
            mean_disc, sum_disc = evaluate_policy(env, model, is_sb3=True)
            print(f"RL PPO: {sum_disc} total anomalies discovered (avg {mean_disc:.2f}/window)")
            results.append({'Policy': 'RL PPO', 'Budget': b, 'Anomalies': sum_disc})
            
    res_df = pd.DataFrame(results)
    os.makedirs('data/ml/rl', exist_ok=True)
    res_df.to_parquet('data/ml/rl/policy_comparison.parquet')
    
if __name__ == "__main__":
    run_evaluation()
