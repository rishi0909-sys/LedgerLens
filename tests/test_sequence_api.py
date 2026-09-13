import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_sequence_predict_valid():
    # Construct sequence of 20 elements
    seq = []
    for _ in range(20):
        seq.append({
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
        })
        
    payload = {"transactions": seq}
    
    response = client.post("/api/ml/sequence-predict", json=payload)
    if response.status_code == 503:
        pytest.skip("Sequence model artifact not generated yet")
        
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "probability" in data
    assert "model_id" in data
    assert "lstm" in data["model_id"] or "transformer" in data["model_id"]

def test_sequence_predict_invalid_length():
    seq = [{"amount": 100.0}] * 5 # Only 5 elements, incomplete schema
    payload = {"transactions": seq}
    
    response = client.post("/api/ml/sequence-predict", json=payload)
    assert response.status_code == 422 # Validation error
