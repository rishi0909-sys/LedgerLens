import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv, MessagePassing

class BasicGraphSAGE(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, hidden_channels)
        self.lin = nn.Linear(hidden_channels, out_channels)
        
    def forward(self, x, edge_index, edge_attr=None):
        # Topology only, ignores edge_attr
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.2, training=self.training)
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = self.lin(x).squeeze(-1)
        return x

class EdgeSAGEConv(MessagePassing):
    def __init__(self, in_channels, hidden_channels, edge_channels):
        super().__init__(aggr='mean')
        self.lin_msg = nn.Linear(in_channels + edge_channels, hidden_channels)
        self.lin_update = nn.Linear(in_channels + hidden_channels, hidden_channels)
        
    def forward(self, x, edge_index, edge_attr):
        # propagate calls message() internally
        out = self.propagate(edge_index, x=x, edge_attr=edge_attr)
        out = self.lin_update(torch.cat([x, out], dim=-1))
        return out
        
    def message(self, x_j, edge_attr):
        # x_j is the features of the source nodes
        # edge_attr is the edge features
        msg = torch.cat([x_j, edge_attr], dim=-1)
        return F.relu(self.lin_msg(msg))

class EdgeGraphSAGE(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels, edge_channels):
        super().__init__()
        self.conv1 = EdgeSAGEConv(in_channels, hidden_channels, edge_channels)
        self.conv2 = EdgeSAGEConv(hidden_channels, hidden_channels, edge_channels)
        self.lin = nn.Linear(hidden_channels, out_channels)
        
    def forward(self, x, edge_index, edge_attr):
        x = self.conv1(x, edge_index, edge_attr)
        x = F.relu(x)
        x = F.dropout(x, p=0.2, training=self.training)
        x = self.conv2(x, edge_index, edge_attr)
        x = F.relu(x)
        x = self.lin(x).squeeze(-1)
        return x
