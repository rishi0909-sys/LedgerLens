from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import numpy as np
import pickle
import xgboost as xgb
import os

router = APIRouter()

# Schemas
class EvidencePredictRequest(BaseModel):
    transaction_features: dict
    # We allow caller to provide raw document text/image if available, 
    # but for simplicity in API, we can accept raw features or pre-extracted doc features.
    document_features: dict | None = None
    # For graph and sequence, they are contextual and typically retrieved from DB internally 
    # given a transaction ID. For this test, we accept them as provided context.
    sequence_features: list[float] | None = None
    graph_node_features: list[float] | None = None

class EvidenceExplanation(BaseModel):
    modality: str
    contribution: float
    reason: str

class EvidenceResponse(BaseModel):
    risk_score: float
    decision: str
    evidence: list[EvidenceExplanation]
    model_id: str

# Loading Models Lazily
MODELS = {}

def load_models():
    if "tx" not in MODELS:
        tx_model = xgb.XGBClassifier()
        tx_model.load_model('data/ml/models/xgb-transaction-v1.json')
        MODELS["tx"] = tx_model
        
        doc_model = xgb.XGBClassifier()
        if os.path.exists('data/ml/models/xgb-document-v1.json'):
            doc_model.load_model('data/ml/models/xgb-document-v1.json')
        MODELS["doc"] = doc_model
        
        # In a real app we'd load seq/graph models here as well.
        
        with open('data/ml/models/calibrators-v1.pkl', 'rb') as f:
            MODELS["calibrators"] = pickle.load(f)
            
        xgb_fusion = xgb.XGBClassifier()
        xgb_fusion.load_model('data/ml/models/fusion-xgb-v1.json')
        MODELS["fusion"] = xgb_fusion

@router.post("/evidence-fusion-predict", response_model=EvidenceResponse)
def evidence_fusion_predict(req: EvidencePredictRequest):
    load_models()
    
    # 1. Generate Modality Evidence
    # Transaction
    tx_features = list(req.transaction_features.values())
    raw_tx_score = MODELS["tx"].predict_proba([tx_features])[0][1]
    
    # Document
    if req.document_features:
        doc_features = list(req.document_features.values())
        raw_doc_score = MODELS["doc"].predict_proba([doc_features])[0][1]
        doc_avail = 1
    else:
        raw_doc_score = 0.0
        doc_avail = 0
        
    # Sequence / Graph (mocked inference for API simplicity unless provided)
    raw_seq_score = 0.0
    seq_avail = 0
    raw_graph_score = 0.0
    graph_avail = 0
    
    # 2. Calibrate
    calibrators = MODELS["calibrators"]
    
    def cal(score, mod):
        if calibrators[mod] == "passthrough":
            return score
        return calibrators[mod].predict([score])[0]
        
    cal_tx = cal(raw_tx_score, "tx")
    cal_doc = cal(raw_doc_score, "doc") if doc_avail else 0.0
    cal_seq = cal(raw_seq_score, "seq") if seq_avail else 0.0
    cal_graph = cal(raw_graph_score, "graph") if graph_avail else 0.0
    
    # 3. Fuse
    conflict_tx_doc = abs(cal_tx - cal_doc) if doc_avail else 0.0
    conflict_tx_seq = abs(cal_tx - cal_seq) if seq_avail else 0.0
    
    fusion_features = [
        cal_tx, 1,
        cal_doc, doc_avail,
        cal_seq, seq_avail,
        cal_graph, graph_avail,
        conflict_tx_doc,
        conflict_tx_seq
    ]
    
    final_score = MODELS["fusion"].predict_proba([fusion_features])[0][1]
    
    # 4. Explain
    explanations = []
    explanations.append(EvidenceExplanation(
        modality="transaction",
        contribution=cal_tx,
        reason=f"Structured transaction profile indicates {'high' if cal_tx > 0.5 else 'low'} risk."
    ))
    
    if doc_avail:
        explanations.append(EvidenceExplanation(
            modality="document",
            contribution=cal_doc,
            reason=f"Document reconciliation and NLP indicates {'high' if cal_doc > 0.5 else 'low'} risk."
        ))
        
    if conflict_tx_doc > 0.5:
        explanations.append(EvidenceExplanation(
            modality="fusion_conflict",
            contribution=conflict_tx_doc,
            reason="High conflict between transaction and document evidence."
        ))
    
    return EvidenceResponse(
        risk_score=float(final_score),
        decision="ANOMALOUS" if final_score > 0.5 else "NORMAL",
        evidence=explanations,
        model_id="fusion-xgb-v1"
    )
