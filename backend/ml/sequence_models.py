import torch
import torch.nn as nn
import math

class SequenceLSTM(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 64, num_layers: int = 1, dropout: float = 0.1):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim, 1)

    def forward(self, x, mask=None):
        # x shape: [batch_size, seq_len, input_dim]
        # mask shape: [batch_size, seq_len], where True means padded
        
        if mask is not None:
            # We want to use packed sequence to ignore padding properly
            lengths = (~mask).sum(dim=1).cpu()
            
            # If all lengths are 0 (shouldn't happen in our data generation but just in case)
            lengths = torch.clamp(lengths, min=1)
            
            packed_x = nn.utils.rnn.pack_padded_sequence(x, lengths, batch_first=True, enforce_sorted=False)
            packed_out, (hn, cn) = self.lstm(packed_x)
            
            # hn shape: [num_layers, batch, hidden_dim]
            # take the top layer's hidden state
            last_hidden = hn[-1]
        else:
            out, (hn, cn) = self.lstm(x)
            last_hidden = hn[-1]
            
        last_hidden = self.dropout(last_hidden)
        logits = self.fc(last_hidden).squeeze(1)
        return logits

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(1, max_len, d_model)
        pe[0, :, 0::2] = torch.sin(position * div_term)
        pe[0, :, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        # x shape: [batch_size, seq_len, embedding_dim]
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)

class SequenceTransformer(nn.Module):
    def __init__(
        self, 
        input_dim: int, 
        d_model: int = 64, 
        nhead: int = 4, 
        num_layers: int = 2, 
        dim_feedforward: int = 128,
        dropout: float = 0.1
    ):
        super().__init__()
        self.input_projection = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        self.fc = nn.Linear(d_model, 1)

    def forward(self, x, mask=None):
        # x shape: [batch, seq_len, input_dim]
        # mask shape: [batch, seq_len] - True indicates padding
        
        x = self.input_projection(x)
        x = self.pos_encoder(x)
        
        # In PyTorch TransformerEncoder, src_key_padding_mask has True for padded positions
        out = self.transformer(x, src_key_padding_mask=mask)
        
        # Masked Pooling
        if mask is not None:
            # We want to mean-pool over the valid positions
            # out shape: [batch, seq_len, d_model]
            valid_mask = ~mask  # [batch, seq_len], True means valid
            valid_mask = valid_mask.unsqueeze(-1).float()  # [batch, seq_len, 1]
            
            sum_out = (out * valid_mask).sum(dim=1)  # [batch, d_model]
            lengths = valid_mask.sum(dim=1)  # [batch, 1]
            lengths = torch.clamp(lengths, min=1.0)
            
            pooled = sum_out / lengths
        else:
            pooled = out.mean(dim=1)
            
        logits = self.fc(pooled).squeeze(1)
        
        # If a sequence was completely padded, Transformer might output NaNs
        logits = torch.nan_to_num(logits, nan=-10.0)
        
        return logits
