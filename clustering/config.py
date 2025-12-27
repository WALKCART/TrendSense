from dataclasses import dataclass
import torch

@dataclass
class clustringConfig:
    device: str = 'cpu'
    model: str = 'all-MiniLM-L6-v2'

device = 'cpu'
if torch.cuda.is_available(): device = 'cuda'
if torch.backends.mps.is_available(): device = 'mps'


bestConfig = clustringConfig(
    device=device
)

cpuConfig = clustringConfig(
    device='cpu'
)

cudaConfig = clustringConfig(
    device='cuda'
)