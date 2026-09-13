import torch
import pytest
from backend.ml.sequence_models import SequenceLSTM, SequenceTransformer

def test_lstm_forward():
    batch_size = 4
    seq_len = 20
    input_dim = 15
    
    model = SequenceLSTM(input_dim=input_dim, hidden_dim=32, num_layers=1)
    
    x = torch.randn(batch_size, seq_len, input_dim)
    mask = torch.zeros(batch_size, seq_len, dtype=torch.bool)
    
    # 1. Forward without mask
    out1 = model(x)
    assert out1.shape == (batch_size,)
    
    # 2. Forward with mask
    out2 = model(x, mask=mask)
    assert out2.shape == (batch_size,)
    
    # 3. Forward with partial mask (padding)
    mask[0, :5] = True # First 5 elements of batch 0 are padded
    out3 = model(x, mask=mask)
    assert out3.shape == (batch_size,)

def test_transformer_forward():
    batch_size = 4
    seq_len = 20
    input_dim = 15
    
    model = SequenceTransformer(input_dim=input_dim, d_model=32, nhead=2, num_layers=2)
    
    x = torch.randn(batch_size, seq_len, input_dim)
    mask = torch.zeros(batch_size, seq_len, dtype=torch.bool)
    
    # 1. Forward without mask
    out1 = model(x)
    assert out1.shape == (batch_size,)
    
    # 2. Forward with mask
    out2 = model(x, mask=mask)
    assert out2.shape == (batch_size,)
    
    # 3. Forward with partial mask
    mask[0, :5] = True
    out3 = model(x, mask=mask)
    assert out3.shape == (batch_size,)
    
    # 4. Check masking logic by modifying padded inputs
    # If we change the padded inputs, the output for that batch element should not change (attention ignores it)
    x_mod = x.clone()
    x_mod[0, :5, :] = 999.0
    
    model.eval() # turn off dropout for deterministic output
    with torch.no_grad():
        out_original = model(x, mask=mask)
        out_modified = model(x_mod, mask=mask)
        
    assert torch.allclose(out_original, out_modified, atol=1e-5)
