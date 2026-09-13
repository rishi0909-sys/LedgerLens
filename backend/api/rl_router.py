from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
from sb3_contrib import MaskablePPO

router = APIRouter()

class CandidateCase(BaseModel):
    transaction_id: str
    fused_score: float
    cal_tx: float
    cal_doc: float
    cal_seq: float
    cal_graph: float
    conflict_tx_doc: float
    conflict_tx_seq: float
    investigated: bool

class InvestigationRequest(BaseModel):
    candidates: List[CandidateCase]
    remaining_budget: int
    budget_limit: int
    cumulative_discoveries: int

class AgentRecommendation(BaseModel):
    transaction_id: str
    index: int
    confidence: float
    reasoning: str

class InvestigationResponse(BaseModel):
    recommendations: List[AgentRecommendation]
    model_id: str

model = None

@router.on_event("startup")
def load_model():
    global model
    try:
        model = MaskablePPO.load("data/ml/models/rl-investigator-v1.zip", device="cpu")
    except Exception as e:
        print(f"Warning: Could not load RL model: {e}")

@router.post("/api/ml/investigation-next", response_model=InvestigationResponse)
def get_next_investigation(req: InvestigationRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="RL model not loaded")
        
    n_candidates = 20
    features_per_candidate = 8
    
    if len(req.candidates) > n_candidates:
        raise HTTPException(status_code=400, detail=f"Too many candidates. Max {n_candidates}.")
        
    obs = np.zeros((n_candidates, features_per_candidate), dtype=np.float32)
    action_mask = np.zeros(n_candidates, dtype=np.int8)
    
    for i, c in enumerate(req.candidates):
        obs[i] = [
            c.fused_score,
            c.cal_tx,
            c.cal_doc,
            c.cal_seq,
            c.cal_graph,
            c.conflict_tx_doc,
            c.conflict_tx_seq,
            1.0 if c.investigated else 0.0
        ]
        if not c.investigated:
            action_mask[i] = 1
            
    flat_obs = obs.flatten()
    global_state = np.array([
        float(req.remaining_budget) / max(req.budget_limit, 1),
        float(req.cumulative_discoveries)
    ], dtype=np.float32)
    
    final_obs = np.concatenate([flat_obs, global_state])
    
    # We can get action probabilities from the policy
    import torch
    obs_tensor = torch.tensor(final_obs.reshape(1, -1)).to(model.device)
    dist = model.policy.get_distribution(obs_tensor)
    dist.apply_masking(np.array(action_mask).reshape(1, -1))
    probs = dist.distribution.probs.cpu().detach().numpy()[0]
    
    # Get top 3 actions
    top_indices = np.argsort(probs)[::-1]
    top_actions = [i for i in top_indices if action_mask[i] == 1][:3]
    
    if len(top_actions) == 0:
        raise HTTPException(status_code=400, detail="No un-investigated candidates available.")
        
    recommendations = []
    for action in top_actions:
        c = req.candidates[action]
        prob = probs[action]
        
        reasons = []
        if c.fused_score > 0.8:
            reasons.append("High fused anomaly score indicates strong multi-modal risk.")
        elif c.fused_score > 0.6:
            reasons.append("Moderate baseline risk across available modalities.")
            
        if max(c.conflict_tx_doc, c.conflict_tx_seq) > 0.2:
            reasons.append("High conflict between evidence streams suggests active obfuscation.")
        else:
            reasons.append("Evidence streams are in agreement, reducing uncertainty.")
            
        if c.cal_tx > 0.5:
            reasons.append("Significant deviation from expected historical behavior.")
            
        if req.remaining_budget < 2:
            reasons.append("Conservative selection due to low remaining budget.")
            
        if not reasons:
            reasons.append("Selected to explore uncertain policy space.")
            
        summary = f"Recommended case: {c.transaction_id}\nExpected Value (Policy Score): {prob:.2%}\n\nReasoning:\n" + "\n".join(f"• {r}" for r in reasons)
        
        recommendations.append(AgentRecommendation(
            transaction_id=c.transaction_id,
            index=int(action),
            confidence=float(prob),
            reasoning=summary
        ))
            
    return InvestigationResponse(
        recommendations=recommendations,
        model_id="rl-investigator-v1"
    )

import pandas as pd

@router.get("/api/ml/candidate-queue")
def get_candidate_queue():
    # Return the first window from the test set
    try:
        df = pd.read_parquet('data/processed/ml/rl/test_rl.parquet')
        window_id = df['window_id'].unique()[0]
        window_df = df[df['window_id'] == window_id].sort_values('fused_score', ascending=False).head(20).reset_index(drop=True)
        
        candidates = []
        for i, row in window_df.iterrows():
            candidates.append({
                "transaction_id": str(row['transaction_id']),
                "fused_score": float(row['fused_score']),
                "cal_tx": float(row['cal_tx']),
                "cal_doc": float(row['cal_doc']),
                "cal_seq": float(row['cal_seq']),
                "cal_graph": float(row['cal_graph']),
                "conflict_tx_doc": float(row['conflict_tx_doc']),
                "conflict_tx_seq": float(row['conflict_tx_seq']),
                "tx_available": int(row['tx_available']),
                "doc_available": int(row['doc_available']),
                "seq_available": int(row['seq_available']),
                "graph_available": int(row['graph_available']),
                "investigated": False
            })
            
        return {"window_id": window_id, "candidates": candidates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

