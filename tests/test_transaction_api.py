import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
import os
import json

client = TestClient(app)

def test_transaction_predict_valid():
    # Make sure we have a model file to load, otherwise we expect 503
    payload = {
        "amount": 5000.0,
        "hour": 14,
        "day_of_week": 2,
        "day_of_month": 15,
        "month": 6,
        "is_salary": 0,
        "is_invoice_payment": 1,
        "is_transfer": 0,
        "is_reimbursement": 0,
        "time_since_previous": 86400,
        "rolling_txn_count": 10,
        "rolling_avg_amount": 1000.0,
        "amount_deviation": 4000.0,
        "amount_deviation_ratio": 5.0,
        "unique_counterparty_count": 3
    }
    
    response = client.post("/api/ml/transaction-predict", json=payload)
    
    # If model is not trained yet, it returns 503
    if response.status_code == 503:
        pytest.skip("Model artifact not generated yet")
        
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "probability" in data
    assert "model_id" in data
    assert data["model_id"] == "xgb-transaction-v1"

def test_transaction_predict_invalid_schema():
    # Missing required fields
    payload = {
        "amount": 5000.0,
        "hour": 25 # Invalid hour
    }
    
    response = client.post("/api/ml/transaction-predict", json=payload)
    assert response.status_code == 422 # Validation error
