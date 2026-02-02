import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import torch
from itertools import combinations
import numpy as np
from trendsense.clustering.config import bestConfig
import pandas as pd
from tqdm import tqdm
import umap
from sklearn.cluster import HDBSCAN
from trendsense.clustering.config import bestConfig
import pyarrow as pa
import pyarrow.parquet as pq
from trendsense.data_manager.fetch import get_supabase_client
import trendsense.data_manager


config = bestConfig

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(
            model_name_or_path=config.model,
            device=config.device
        )
    return _model

def get_embedding(input_path: Path, output_path: Path, title_emb: bool = False, summary_emb: bool = False):
    """Creates embeddings for selected fields and stores them in parquet file """

    if not title_emb and not summary_emb:
        raise ValueError("At least one of title or summary must be True")
    
    print('Creating Embeddings:')
    articles_df = pd.read_csv(input_path)
    output_path.mkdir(parents=True, exist_ok=True)

    if title_emb:
        _embed_and_write(
            df=articles_df,
            column="title",
            output_file=output_path / "title_emb.parquet",
        )
    if summary_emb:
        _embed_and_write(
            df=articles_df,
            column="summary",
            output_file=output_path / "summary_emb.parquet",
        )
    

def _embed_and_write(df, column: str, output_file: Path):
    """
    Embed a given text column for selected article IDs
    and write embeddings to a Parquet file.
    """
    supabase = get_supabase_client()
    response = (
        supabase
        .table(trendsense.data_manager.config.ARTICLES_DB)
        .select("art_id, title, link, site, section, published")
        .eq("embedded", False)
        .execute()
    )
    
    if not response.data:
        print("No eligible articles found in Supabase. Skipping.")
        return

    db_df = pd.DataFrame(response.data)
    def norm_str(s):
        return s.astype(str).str.strip().str.lower()
    def norm_date(s):
        return pd.to_datetime(s, errors="coerce").dt.date

    join_cols = ["link", "site", "section", "title", "published"]
    for col in join_cols:
        df[col] = norm_str(df[col])
        db_df[col] = norm_str(db_df[col])
    df["published"] = norm_date(df["published"])
    db_df["published"] = norm_date(db_df["published"])
    merged = df.merge(
        db_df,
        on=join_cols,
        how="inner",
        validate="one_to_one"
    )

    if len(merged) != len(df):
        raise RuntimeError(
            f"CSV-Supabase mismatch: CSV={len(df)}, merged={len(merged)}"
        )
    
    valid = merged[
        merged[column].notna()
        & merged[column].astype(str).str.strip().ne("")
    ]

    if valid.empty:
        print(f"No valid {column} texts found. Skipping.")
        return

    texts = valid[column].astype(str).tolist()
    art_ids = valid["art_id"].tolist()

    print(f"Embedding {len(texts)} {column} texts...")

    model = get_model()

    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.asarray(embeddings, dtype="float32")

    table = pa.table({
        "art_id": art_ids,
        "embedding": list(embeddings)
    })

    pq.write_table(table, output_file, compression="snappy")


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

def get_clustering_inds_hdb(sents: pd.Series, min_cluster_size: int = 10):
    # Experimenting with HDBSCAN
    assert isinstance(sents, pd.Series), f'sents provided is {type(sents)} not pd.Series!'
    embeddings = get_embedding(sents.to_list())
    print('Reducing Dimensions with UMAP...')
    reducer = umap.UMAP(
        n_neighbors=10,      
        n_components=5,      
        min_dist=0.0,        
        metric='cosine',     
        random_state=42
    )
    reduced_embeddings = reducer.fit_transform(embeddings)

    print('Clustering with HDBSCAN...')
    clusterer = HDBSCAN(
        min_cluster_size=config.minimum_articles,  
        min_samples=3,
        metric='euclidean',                 
        cluster_selection_method='eom',    
        cluster_selection_epsilon=0.35, 
    )
    
    cluster_labels = clusterer.fit_predict(reduced_embeddings)

    indices = pd.Series(cluster_labels, index=sents.index)
    
    return indices

