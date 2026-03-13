from dataclasses import dataclass
from pathlib import Path
import torch


# Runtime Config
@dataclass
class clustringConfig:
    device: str = 'cpu'
    model: str = 'all-MiniLM-L6-v2'
    thresh: float = 0.5
    minimum_articles = 10

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



# Project Paths
BASE_DIR = Path(__file__).resolve().parents[3]
DATA_BUFFER_DIR = BASE_DIR / "DataBuffer"
VECTORS_OUTPUT_PATH = DATA_BUFFER_DIR / "_vectors"
CLUSTERS_OUTPUT_PATH = DATA_BUFFER_DIR / "_clusters"
CLUSTERS_MAP_PATH = DATA_BUFFER_DIR / "_clusters" / "article_cluster_map.parquet"


# Clustering configuration per level

CLUSTER_CONFIG = {
    1: {
        "UMAP_N_NEIGHBORS": 15,
        "UMAP_N_COMPONENTS": 5,
        "HDBSCAN_MIN_CLUSTER_SIZE": 3,
        "HDBSCAN_MIN_SAMPLES": 3,
    },
    2: {
        "UMAP_N_NEIGHBORS": 25,
        "UMAP_N_COMPONENTS": 5,
        "HDBSCAN_MIN_CLUSTER_SIZE": 5,
        "HDBSCAN_MIN_SAMPLES": 4,
    },
    3: {
        "UMAP_N_NEIGHBORS": 35,
        "UMAP_N_COMPONENTS": 5,
        "HDBSCAN_MIN_CLUSTER_SIZE": 8,
        "HDBSCAN_MIN_SAMPLES": 6,
    },
    4: {
        "UMAP_N_NEIGHBORS": 50,
        "UMAP_N_COMPONENTS": 5,
        "HDBSCAN_MIN_CLUSTER_SIZE": 12,
        "HDBSCAN_MIN_SAMPLES": 8,
    }
}

RANDOM_STATE = 42