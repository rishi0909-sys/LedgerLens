import pytest
import pandas as pd
from datetime import datetime, timedelta
from backend.ml.transaction_features import construct_features

@pytest.fixture
def sample_transactions():
    data = [
        {
            "transaction_id": "T1",
            "timestamp": datetime(2023, 1, 1, 10, 0),
            "source_account": "A1",
            "destination_account": "B1",
            "amount": 100.0,
            "transaction_type": "TRANSFER",
            "is_anomaly": False
        },
        {
            "transaction_id": "T2",
            "timestamp": datetime(2023, 1, 1, 11, 0),
            "source_account": "A1",
            "destination_account": "B2",
            "amount": 200.0,
            "transaction_type": "TRANSFER",
            "is_anomaly": False
        },
        {
            "transaction_id": "T3",
            "timestamp": datetime(2023, 1, 1, 12, 0),
            "source_account": "A1",
            "destination_account": "B1",
            "amount": 1000.0,
            "transaction_type": "TRANSFER",
            "is_anomaly": True
        }
    ]
    return pd.DataFrame(data)

def test_causal_exclusion(sample_transactions):
    """
    Test that a transaction's features do not include its own properties
    or future properties.
    """
    df = construct_features(sample_transactions)
    
    # Check T1
    t1 = df[df['transaction_id'] == 'T1'].iloc[0]
    assert t1['time_since_previous'] == 0
    assert t1['rolling_txn_count'] == 0
    assert t1['rolling_avg_amount'] == 0
    assert t1['amount_deviation'] == 100.0
    assert t1['unique_counterparty_count'] == 0
    
    # Check T2 (should only see T1)
    t2 = df[df['transaction_id'] == 'T2'].iloc[0]
    assert t2['time_since_previous'] == 3600  # 1 hour
    assert t2['rolling_txn_count'] == 1
    assert t2['rolling_avg_amount'] == 100.0
    assert t2['amount_deviation'] == 100.0  # (200 - 100)
    assert t2['unique_counterparty_count'] == 1
    
    # Check T3 (should see T1 and T2)
    t3 = df[df['transaction_id'] == 'T3'].iloc[0]
    assert t3['time_since_previous'] == 3600
    assert t3['rolling_txn_count'] == 2
    assert t3['rolling_avg_amount'] == 150.0  # (100 + 200) / 2
    assert t3['amount_deviation'] == 850.0    # 1000 - 150
    assert t3['unique_counterparty_count'] == 2 # B1, B2

def test_chronological_independence(sample_transactions):
    """
    Test that reordering the input DataFrame does not change the calculated features,
    since the function must sort chronologically internally.
    """
    shuffled_df = sample_transactions.sample(frac=1, random_state=42).reset_index(drop=True)
    
    res_ordered = construct_features(sample_transactions)
    res_shuffled = construct_features(shuffled_df)
    
    # Both should be sorted by timestamp ultimately
    pd.testing.assert_frame_equal(res_ordered, res_shuffled)
