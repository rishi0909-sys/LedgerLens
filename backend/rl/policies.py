import numpy as np

class BaseHeuristicPolicy:
    def __init__(self, env):
        self.env = env
        
    def predict(self, obs, action_masks=None):
        raise NotImplementedError

class RandomPolicy(BaseHeuristicPolicy):
    def predict(self, obs, action_masks=None):
        valid_actions = np.where(action_masks == 1)[0]
        if len(valid_actions) == 0:
            return 0, None
        return np.random.choice(valid_actions), None

class HighestRiskPolicy(BaseHeuristicPolicy):
    def predict(self, obs, action_masks=None):
        # fused_score is the first feature in each candidate's vector
        valid_actions = np.where(action_masks == 1)[0]
        if len(valid_actions) == 0:
            return 0, None
            
        best_action = -1
        best_score = -np.inf
        
        for a in valid_actions:
            score = self.env.current_candidates.iloc[a]['fused_score']
            if score > best_score:
                best_score = score
                best_action = a
                
        return best_action, None

class HighestDisagreementPolicy(BaseHeuristicPolicy):
    def predict(self, obs, action_masks=None):
        valid_actions = np.where(action_masks == 1)[0]
        if len(valid_actions) == 0:
            return 0, None
            
        best_action = -1
        best_score = -np.inf
        
        for a in valid_actions:
            row = self.env.current_candidates.iloc[a]
            disagreement = row['conflict_tx_doc'] + row['conflict_tx_seq']
            if disagreement > best_score:
                best_score = disagreement
                best_action = a
                
        return best_action, None

class TransactionRiskPolicy(BaseHeuristicPolicy):
    def predict(self, obs, action_masks=None):
        valid_actions = np.where(action_masks == 1)[0]
        if len(valid_actions) == 0:
            return 0, None
            
        best_action = -1
        best_score = -np.inf
        
        for a in valid_actions:
            score = self.env.current_candidates.iloc[a]['cal_tx']
            if score > best_score:
                best_score = score
                best_action = a
                
        return best_action, None

class OraclePolicy(BaseHeuristicPolicy):
    def predict(self, obs, action_masks=None):
        valid_actions = np.where(action_masks == 1)[0]
        if len(valid_actions) == 0:
            return 0, None
            
        # Prioritize actual anomalies
        for a in valid_actions:
            if self.env.current_candidates.iloc[a]['is_anomalous'] == 1:
                return a, None
                
        # If no anomalies left, pick highest risk
        best_action = valid_actions[0]
        best_score = -np.inf
        for a in valid_actions:
            score = self.env.current_candidates.iloc[a]['fused_score']
            if score > best_score:
                best_score = score
                best_action = a
                
        return best_action, None
