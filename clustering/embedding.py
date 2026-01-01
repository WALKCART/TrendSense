from sentence_transformers import SentenceTransformer
import torch
from itertools import combinations
import numpy as np
from clustering.config import bestConfig
import pandas as pd
from tqdm import tqdm

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

def get_clustering_inds(sents: pd.Series, indices: pd.Series = None):
    if indices is None: 
        indices = pd.Series([pd.NA for _ in range(len(sents))])
    assert isinstance(sents, pd.Series), f'sents provided is {type(sents)} not pd.Series!'
    emb = get_embedding(sents)
    ind = 0
    for sent_ind in tqdm(range(len(sents))):
        if indices[sent_ind] is not pd.NA:
            continue
        else:
            unindexed = indices.isna()
            unindexed_count = indices.isna().sum()
            comp = emb[indices.isna(), :] # compared with only unindexed sentences
            sub = emb[[sent_ind], :].repeat(unindexed_count, 0)
            sim = (get_cosine_similarity(sub, comp) > config.thresh)
            mask = unindexed.copy(deep=True)
            mask[unindexed] = sim
            indices[mask] = ind
            if mask.sum() > 0: ind += 1 #increment index only if similar articles found.
    return indices
