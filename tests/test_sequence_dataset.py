import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backend.ml.sequence_dataset import TransactionSequenceDataset, FEATURES

def create_dummy_data():
    base_time = datetime(2023, 1, 1)
    data = []
    # 5 transactions for account A
    for i in range(5):
        data.append({
            "transaction_id": f"tx_{i}",
            "timestamp": base_time + timedelta(hours=i),
            "source_account": "A",
            "destination_account": "B",
            "amount": 100 + i,
            "transaction_type": "TRANSFER",
            "is_anomalous": 0
        })
        
    df = pd.DataFrame(data)
    # Mock some features that construct_features would add
    for f in FEATURES:
        if f not in df.columns:
            df[f] = np.random.randn(5)
    
    # We must ensure time_since_previous etc. aren't nan
    df.fillna(0, inplace=True)
    return df

def test_causality_target_modification():
    df = create_dummy_data()
    
    # Generate sequences
    ds1 = TransactionSequenceDataset(df, seq_len=3)
    
    # Check sequence for transaction 2 (which should be tx_0, tx_1)
    # It shouldn't contain tx_2's amount (102)
    tx2_feats, tx2_mask, tx2_target, _ = ds1[2]
    # mask is True, False, False because length is 3, history is 2
    assert tx2_mask.tolist() == [True, False, False]
    # Check that amount for tx2 isn't in history
    amounts = tx2_feats[:, 0].numpy()
    assert 102 not in amounts
    
    # Modify tx_2's amount
    df_mod = df.copy()
    df_mod.loc[df_mod['transaction_id'] == 'tx_2', 'amount'] = 999
    
    ds2 = TransactionSequenceDataset(df_mod, seq_len=3)
    tx2_feats_mod, _, _, _ = ds2[2]
    
    # History should be exactly the same
    np.testing.assert_array_equal(tx2_feats.numpy(), tx2_feats_mod.numpy())

def test_causality_future_modification():
    df = create_dummy_data()
    
    # Modify future transaction (tx_4)
    df_mod = df.copy()
    df_mod.loc[df_mod['transaction_id'] == 'tx_4', 'amount'] = 999
    
    ds1 = TransactionSequenceDataset(df, seq_len=3)
    ds2 = TransactionSequenceDataset(df_mod, seq_len=3)
    
    # Check tx_2's sequence - should be identical
    tx2_feats_1, _, _, _ = ds1[2]
    tx2_feats_2, _, _, _ = ds2[2]
    
    np.testing.assert_array_equal(tx2_feats_1.numpy(), tx2_feats_2.numpy())
    
def test_padding():
    df = create_dummy_data()
    ds = TransactionSequenceDataset(df, seq_len=10)
    
    # tx_0 has NO history
    feats, mask, _, _ = ds[0]
    assert mask.sum() == 10 # all padded
    assert np.all(feats.numpy() == 0)
    
    # tx_4 has 4 historical txs (0, 1, 2, 3)
    feats4, mask4, _, _ = ds[4]
    assert mask4.sum() == 6 # 6 padded, 4 real
    assert mask4.tolist() == [True]*6 + [False]*4
