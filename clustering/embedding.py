from sentence_transformers import SentenceTransformer
import torch
from itertools import combinations
import numpy as np
from clustering.config import bestConfig

config = bestConfig

model = SentenceTransformer(
    model_name_or_path= config.model,
    device=config.device
)

def get_embedding(s: list):
    print('Geting Embeddings:')
    emb = model.encode(s, show_progress_bar=True)
    return emb

def get_cosine_similarity(v1: np.ndarray, 
                          v2: np.ndarray):
    v1 = torch.from_numpy(v1).to(config.device).float()
    v2 = torch.from_numpy(v2).to(config.device).float()
    num = torch.sum(v1 * v2, dim=1)
    den = torch.linalg.norm(v1, dim=1) * torch.linalg.norm(v2, dim=1)
    return (num/den).to('cpu').numpy()

def get_clustering_inds(sents: list):
    pairs = np.array(list(combinations(sents, 2)))
    a = pairs[:, 0]
    b = pairs[:, 1]
    emb1 = get_embedding(a)
    emb2 = get_embedding(b)
    sim = get_cosine_similarity(emb1, emb2)
    ver = sim > config.thresh
    return [x[::-1] for x in enumerate(pairs[ver, :])]
    

