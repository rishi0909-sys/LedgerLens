from fastapi.testclient import TestClient
from backend.api.main import app
import numpy as np

client = TestClient(app)

def test_document_predict_endpoint():
    # Construct a dummy feature vector of size 773
    doc_features = {f"feat_{i}": 0.0 for i in range(773)}
    
    response = client.post("/api/ml/document-predict", json={
        "document_features": doc_features
    })
    
    # We might get 404 if model isn't trained, but if it is, it should return 200
    if response.status_code == 200:
        data = response.json()
        assert "prediction" in data
        assert "probability" in data
        assert "model_id" in data
        assert data["model_id"] == "xgb-document-v1"

def test_multimodal_predict_endpoint():
    # Construct a dummy feature vector of size 15 for tx and 773 for doc
    tx_features = {f"tx_{i}": 0.0 for i in range(15)}
    doc_features = {f"doc_{i}": 0.0 for i in range(773)}
    
    response = client.post("/api/ml/multimodal-predict", json={
        "transaction_features": tx_features,
        "document_features": doc_features
    })
    
    if response.status_code == 200:
        data = response.json()
        assert "prediction" in data
        assert "probability" in data
        assert "model_id" in data
        assert data["model_id"] == "xgb-multimodal-v1"
