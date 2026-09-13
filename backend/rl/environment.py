import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class FinancialInvestigationEnv(gym.Env):
    """
    A sequential investigation environment.
    The agent is presented with a queue of up to N suspicious cases.
    It must choose which case to investigate next under a finite budget.
    """
    def __init__(self, df, n_candidates=20, budget=5, max_episodes=None):
        super().__init__()
        self.df = df
        self.n_candidates = n_candidates
        self.budget_limit = budget
        self.max_episodes = max_episodes
        
        # We group cases by chronological window
        self.windows = list(df['window_id'].unique())
        
        self.current_window_idx = 0
        self.current_candidates = None
        self.remaining_budget = 0
        self.investigated = set()
        self.cumulative_discoveries = 0
        
        # Define features per candidate
        # fused_score, cal_tx, cal_doc, cal_seq, cal_graph, 
        # conflict_tx_doc, conflict_tx_seq, investigated_flag
        self.features_per_candidate = 8
        
        # Observation space: 
        # (N candidates * features) + remaining_budget + cumulative_discoveries
        obs_dim = (self.n_candidates * self.features_per_candidate) + 2
        self.observation_space = spaces.Box(low=-1.0, high=10.0, shape=(obs_dim,), dtype=np.float32)
        
        # Action space: Discrete(N)
        self.action_space = spaces.Discrete(self.n_candidates)
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        if self.current_window_idx >= len(self.windows):
            self.current_window_idx = 0
            
        window_id = self.windows[self.current_window_idx]
        window_df = self.df[self.df['window_id'] == window_id].copy()
        
        # Sort by fused_score descending to simulate a suspicious queue
        window_df = window_df.sort_values('fused_score', ascending=False)
        
        # Take up to N candidates
        self.current_candidates = window_df.head(self.n_candidates).reset_index(drop=True)
        
        self.remaining_budget = self.budget_limit
        self.investigated = set()
        self.cumulative_discoveries = 0
        
        self.current_window_idx += 1
        
        return self._get_obs(), self._get_info()
        
    def _get_obs(self):
        obs = np.zeros((self.n_candidates, self.features_per_candidate), dtype=np.float32)
        
        for i in range(len(self.current_candidates)):
            row = self.current_candidates.iloc[i]
            investigated_flag = 1.0 if i in self.investigated else 0.0
            
            # Mask out features if already investigated, or just provide them with the flag
            # Providing them allows the agent to see what it already investigated.
            obs[i] = [
                row['fused_score'],
                row['cal_tx'],
                row['cal_doc'],
                row['cal_seq'],
                row['cal_graph'],
                row['conflict_tx_doc'],
                row['conflict_tx_seq'],
                investigated_flag
            ]
            
        flat_obs = obs.flatten()
        global_state = np.array([
            float(self.remaining_budget) / self.budget_limit,
            float(self.cumulative_discoveries)
        ], dtype=np.float32)
        
        return np.concatenate([flat_obs, global_state])
        
    def _get_info(self):
        # Calculate valid action mask for sb3-contrib MaskablePPO
        valid_actions = np.zeros(self.n_candidates, dtype=np.int8)
        for i in range(len(self.current_candidates)):
            if i not in self.investigated:
                valid_actions[i] = 1
        return {"action_mask": valid_actions}
        
    def step(self, action):
        action = int(action)
        if action >= len(self.current_candidates) or action in self.investigated:
            # Invalid action
            return self._get_obs(), -0.1, False, False, self._get_info()
            
        row = self.current_candidates.iloc[action]
        is_anom = row['is_anomalous'] == 1
        
        self.investigated.add(action)
        self.remaining_budget -= 1
        
        if is_anom:
            reward = 1.0
            self.cumulative_discoveries += 1
        else:
            reward = -0.1
            
        terminated = (self.remaining_budget <= 0) or (len(self.investigated) == len(self.current_candidates))
        
        return self._get_obs(), reward, terminated, False, self._get_info()
        
    def action_masks(self):
        """Used by MaskablePPO to fetch valid actions."""
        return self._get_info()["action_mask"]
