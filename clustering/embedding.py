from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from clustering.config import bestConfig

config = bestConfig

model = SentenceTransformer(
    model_name_or_path= config.model,
    device=config.device
)

def get_embedding(s: list):
    emb = model.encode(s)
    return emb

def get_cosine_similarity(v1: np.ndarray, 
                          v2: np.ndarray):
    v1 = torch.from_numpy(v1).to(config.device).float()
    v2 = torch.from_numpy(v2).to(config.device).float()
    num = torch.sum(v1 * v2, dim=1)
    den = torch.linalg.norm(v1, dim=1) * torch.linalg.norm(v2, dim=1)
    return num/den

