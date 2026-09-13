from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
import xgboost as xgb
import numpy as np

from backend.document_ai.reconciliation import reconcile_document_to_ledger
from backend.ml.transaction_anomaly import FEATURES as TX_FEATURES

router = APIRouter()

class ReconcileRequest(BaseModel):
    extracted_fields: dict
    ledger_record: dict

class DocumentPredictRequest(BaseModel):
    document_features: dict

class MultimodalPredictRequest(BaseModel):
    transaction_features: dict
    document_features: dict

# Note: In a real app we'd load the models at startup, but for the assignment this is fine.
DOC_MODEL_PATH = "data/ml/models/xgb-document-v1.json"
MULTIMODAL_MODEL_PATH = "data/ml/models/xgb-multimodal-v1.json"

@router.post("/reconcile")
def reconcile(req: ReconcileRequest):
    result = reconcile_document_to_ledger(req.extracted_fields, req.ledger_record)
    return result

@router.post("/document-predict")
def document_predict(req: DocumentPredictRequest):
    if not os.path.exists(DOC_MODEL_PATH):
        raise HTTPException(status_code=404, detail="Document model not found")
        
    model = xgb.XGBClassifier()
    model.load_model(DOC_MODEL_PATH)
    
    # We would construct the feature vector here, assuming order
    # For now we use the feature count
    probs = model.predict_proba([list(req.document_features.values())])
    pred = "ANOMALOUS" if probs[0][1] > 0.5 else "NORMAL"
    return {"prediction": pred, "probability": float(probs[0][1]), "model_id": "xgb-document-v1"}

@router.post("/multimodal-predict")
def multimodal_predict(req: MultimodalPredictRequest):
    if not os.path.exists(MULTIMODAL_MODEL_PATH):
        raise HTTPException(status_code=404, detail="Multimodal model not found")
        
    model = xgb.XGBClassifier()
    model.load_model(MULTIMODAL_MODEL_PATH)
    
    features = list(req.transaction_features.values()) + list(req.document_features.values())
    
    probs = model.predict_proba([features])
    pred = "ANOMALOUS" if probs[0][1] > 0.5 else "NORMAL"
    
    return {"prediction": pred, "probability": float(probs[0][1]), "model_id": "xgb-multimodal-v1"}
