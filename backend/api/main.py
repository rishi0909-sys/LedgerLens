from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os
import json
import pandas as pd

from fastapi.middleware.cors import CORSMiddleware
from backend.api.rl_router import router as rl_router

app = FastAPI(title="LedgerLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/ready")
def readiness_check():
    return {"status": "ready"}

app.include_router(rl_router, tags=["RL Investigation Agent"])

# Global variables to hold models
models = {}

class TransactionFeatures(BaseModel):
    amount: float = Field(..., description="Transaction amount")
    hour: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    day_of_month: int = Field(..., ge=1, le=31)
    month: int = Field(..., ge=1, le=12)
    is_salary: int = Field(..., ge=0, le=1)
    is_invoice_payment: int = Field(..., ge=0, le=1)
    is_transfer: int = Field(..., ge=0, le=1)
    is_reimbursement: int = Field(..., ge=0, le=1)
    time_since_previous: float
    rolling_txn_count: float
    rolling_avg_amount: float
    amount_deviation: float
    amount_deviation_ratio: float
    unique_counterparty_count: float

def load_transaction_model():
    import xgboost as xgb
    if "xgb-transaction" in models:
        return models["xgb-transaction"]
        
    model_dir = "data/ml/models"
    metadata_path = os.path.join(model_dir, "xgb-transaction-v1_metadata.json")
    model_path = os.path.join(model_dir, "xgb-transaction-v1.json")
    
    if not os.path.exists(metadata_path) or not os.path.exists(model_path):
        raise HTTPException(status_code=503, detail="Model artifact not found")
        
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
        
    model = xgb.XGBClassifier()
    model.load_model(model_path)
    
    models["xgb-transaction"] = {
        "model": model,
        "metadata": metadata,
        "threshold": metadata["threshold"],
        "model_id": metadata["model_id"]
    }
    return models["xgb-transaction"]

@app.post("/api/ml/transaction-predict")
def predict_transaction(features: TransactionFeatures):
    try:
        model_info = load_transaction_model()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
        
    # Construct feature vector in exactly the expected order
    feature_names = [
        'amount', 'hour', 'day_of_week', 'day_of_month', 'month',
        'is_salary', 'is_invoice_payment', 'is_transfer', 'is_reimbursement',
        'time_since_previous', 'rolling_txn_count', 'rolling_avg_amount', 
        'amount_deviation', 'amount_deviation_ratio', 'unique_counterparty_count'
    ]
    
    feature_dict = features.model_dump()
    row = {k: [feature_dict[k]] for k in feature_names}
    df = pd.DataFrame(row)
    
    prob = float(model_info["model"].predict_proba(df)[0, 1])
    is_anom = prob >= model_info["threshold"]
    
    return {
        "prediction": "ANOMALOUS" if is_anom else "NORMAL",
        "probability": prob,
        "model_id": model_info["model_id"]
    }

class SequenceInput(BaseModel):
    transactions: list[TransactionFeatures] = Field(..., description="Chronological sequence of transactions")

def load_sequence_model():
    if "transformer-sequence" in models:
        return models["transformer-sequence"]
        
    model_dir = "data/ml/models"
    metadata_path = os.path.join(model_dir, "transformer-sequence-v1_metadata.json")
    model_path = os.path.join(model_dir, "transformer-sequence-v1.pt")
    
    if not os.path.exists(metadata_path) or not os.path.exists(model_path):
        raise HTTPException(status_code=503, detail="Sequence model artifact not found")
        
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
        
    from backend.ml.sequence_models import SequenceTransformer
    import torch
    
    model = SequenceTransformer(
        input_dim=15, 
        d_model=metadata["hyperparameters"]["d_model"],
        nhead=metadata["hyperparameters"]["nhead"],
        num_layers=metadata["hyperparameters"]["num_layers"]
    )
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    
    models["transformer-sequence"] = {
        "model": model,
        "metadata": metadata,
        "threshold": metadata["threshold"],
        "model_id": metadata["model_id"]
    }
    return models["transformer-sequence"]

@app.post("/api/ml/sequence-predict")
def predict_sequence(input_data: SequenceInput):
    try:
        model_info = load_sequence_model()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
        
    req_len = model_info["metadata"]["sequence_length"]
    
    # Validation logic
    seq = input_data.transactions
    if len(seq) != req_len:
        raise HTTPException(status_code=422, detail=f"Expected sequence of length {req_len}, got {len(seq)}")
        
    feature_names = [
        'amount', 'hour', 'day_of_week', 'day_of_month', 'month',
        'is_salary', 'is_invoice_payment', 'is_transfer', 'is_reimbursement',
        'time_since_previous', 'rolling_txn_count', 'rolling_avg_amount', 
        'amount_deviation', 'amount_deviation_ratio', 'unique_counterparty_count'
    ]
    
    import torch
    
    # We construct a single batch element of shape [1, req_len, input_dim]
    feat_matrix = []
    for tx in seq:
        d = tx.model_dump()
        feat_matrix.append([d[k] for k in feature_names])
        
    tensor_input = torch.tensor([feat_matrix], dtype=torch.float32)
    # Mask is all False because sequence is full length
    mask = torch.zeros((1, req_len), dtype=torch.bool)
    
    with torch.no_grad():
        logit = model_info["model"](tensor_input, mask=mask)
        prob = float(torch.sigmoid(logit)[0].item())
        
    is_anom = prob >= model_info["threshold"]
    
    return {
        "prediction": "ANOMALOUS" if is_anom else "NORMAL",
        "probability": prob,
        "model_id": model_info["model_id"]
    }
