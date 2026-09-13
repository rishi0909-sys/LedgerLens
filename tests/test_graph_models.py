import torch
from backend.ml.graph.graph_models import BasicGraphSAGE, EdgeGraphSAGE

def test_basic_graphsage():
    in_channels = 7
    hidden_channels = 16
    out_channels = 1
    model = BasicGraphSAGE(in_channels, hidden_channels, out_channels)
    
    # Tiny dataset
    x = torch.randn(5, in_channels)
    edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 3, 4]], dtype=torch.long)
    
    out = model(x, edge_index)
    assert out.shape == (5,)

def test_edge_graphsage():
    in_channels = 7
    hidden_channels = 16
    out_channels = 1
    edge_channels = 2
    model = EdgeGraphSAGE(in_channels, hidden_channels, out_channels, edge_channels)
    
    # Tiny dataset
    x = torch.randn(5, in_channels)
    edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 3, 4]], dtype=torch.long)
    edge_attr = torch.randn(4, edge_channels)
    
    out = model(x, edge_index, edge_attr)
    assert out.shape == (5,)
