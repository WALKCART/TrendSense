
import pandas as pd
import umap
import hdbscan
import os
import numpy as np
from numpy.typing import NDArray
from typing import Tuple, List, Dict, Optional, cast
from . import config
import re
from collections import Counter
import spacy
from trendsense.data_manager.db_upload import get_supabase_client
from trendsense.clustering.cluster_metrics import get_half_life, get_bursts


# add the function to find the last id of that level and then make ids from that only
# fetch the last serial number
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])


def get_last_cluster_ids() -> Dict:
    """
    Fetch the maximum cluster_id for each level from ClustersDB.
    Returns dict {level: max_cluster_id}
    """
    supabase = get_supabase_client()
    res = (
        supabase.table("ClustersDB")
        .select("cluster_id,level")
        .execute()
    )

    data = res.data or []

    if not data:
        return {1:0,2:0,3:0,4:0}

    df = pd.DataFrame(data)

    last_ids = {}

    for lvl in [1,2,3,4]:
        if lvl not in df["level"].values:
            last_ids[lvl] = 0
        else:
            last_ids[lvl] = df.loc[df["level"] == lvl,"cluster_id"].max()

    return last_ids


def preprocess(text):

    JUNK_WORDS = {
    "reuters", "reuter", "business","standard","say","says","report",
    "million","billion","crore","year","day","week",
    "update","live","latest","news","amp"
    }

    if not isinstance(text, str):
        return []

    text = text.lower()

    # remove wire prefixes
    text = re.sub(r"^(reuters|business standard|ap news)\s*[-:]", "", text)

    # remove punctuation/numbers
    text = re.sub(r"[^a-z\s]", " ", text)

    doc = nlp(text)

    tokens = []

    for token in doc:

        lemma = token.lemma_.strip()

        if token.is_stop:
            continue

        if len(lemma) < 3:
            continue

        if lemma in JUNK_WORDS:
            continue

        tokens.append(lemma)

    # remove duplicates while preserving order
    tokens = list(dict.fromkeys(tokens))

    return tokens


def run_clustering(embeddings, level):
    cfg = config.CLUSTER_CONFIG[level]
    n_samples = embeddings.shape[0]

    # UMAP requires n_components < n_samples
    n_components = min(cfg["UMAP_N_COMPONENTS"], n_samples - 2)
    n_neighbors = min(cfg["UMAP_N_NEIGHBORS"], n_samples - 1)


    # If too few points, skip dimensionality reduction
    if n_samples < 3:
        return np.full(n_samples, -1, dtype=int)

    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        n_components=n_components,
        metric='cosine',
        random_state=config.RANDOM_STATE
    )

    reduced = cast(NDArray[np.float32], reducer.fit_transform(embeddings))

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min(cfg["HDBSCAN_MIN_CLUSTER_SIZE"], n_samples),
        min_samples=min(cfg["HDBSCAN_MIN_SAMPLES"], n_samples),
        metric='euclidean',
        cluster_selection_method='eom',
        cluster_selection_epsilon=0.2
    )

    labels: NDArray[np.int_] = clusterer.fit_predict(reduced)
    return labels


def compute_and_save_centroids(embeddings: NDArray[np.float32], labels: NDArray[np.int_], filename: str) -> Tuple[Optional[NDArray[np.float32]], Optional[List[int]]]:
    """Compute normalized centroids for each non-noise cluster and persist.

    The returned ``centroids`` array will have one row per *valid* cluster in the
    same order as ``cluster_ids``.  This avoids introducing placeholder rows
    for missing ids which would otherwise poison subsequent hierarchical
    clustering steps.

    Args:
        embeddings: np.ndarray of shape (n_samples, dim).
        labels: iterable of cluster labels (may contain -1 for noise).
        filename: path where the centroids array will be saved with ``np.save``.

    Returns:
        Tuple[centroid_array, cluster_ids] or (None, None) when no clusters exist.
    """
    df = pd.DataFrame({"label": labels})
    df["embedding"] = list(embeddings)

    # drop noise points early
    df = df[df["label"] != -1]

    if len(df) == 0:
        print(f"No valid clusters found for {filename}")
        return None, None

    grouped = df.groupby("label")["embedding"]

    cluster_ids: List[int] = sorted(cast(List[int], grouped.groups.keys()))

    embedding_dim = embeddings.shape[1]
    centroids = []

    for cid in cluster_ids:
        cluster_embeddings = np.vstack(cast(List[NDArray[np.float32]], grouped.get_group(cid)))
        centroid = cluster_embeddings.mean(axis=0)
        centroid /= np.linalg.norm(centroid)
        centroids.append(centroid)

    centroid_array: NDArray[np.float32] = np.vstack(centroids)
    np.save(filename, centroid_array)

    return centroid_array, cluster_ids


def get_l1_clusters(embeddings_l0: NDArray[np.float32], articles: pd.DataFrame):
    """Cluster raw article embeddings and attach ``l1_cluster_id`` to ``articles``.

    Returns centroids and corresponding cluster ids for the first level.
    """
    labels_l1 = run_clustering(embeddings_l0, level=1)
    articles["l1_cluster_id"] = labels_l1
    centroids_l1, valid_l1_ids = compute_and_save_centroids(
        embeddings_l0,
        labels_l1,
        f"{config.CLUSTERS_OUTPUT_PATH}/l1_centroids.npy"
    )
    return centroids_l1, valid_l1_ids


def get_l2_clusters(centroids_l1, valid_l1_ids, articles):
    """Cluster level‑1 centroids and assign ``l2_cluster_id`` to ``articles``.

    ``centroids_l1`` is expected to be the array returned by
    :func:`compute_and_save_centroids` for level 1; ``valid_l1_ids`` must be the
    accompanying id list.  The mapping step ensures that noise items remain at
    ``-1``.
    """
    if centroids_l1 is not None and len(centroids_l1) > 2:
        labels_l2 = run_clustering(centroids_l1, level=2)

        centroids_l2, valid_l2_ids = compute_and_save_centroids(
            centroids_l1,
            labels_l2,
            f"{config.CLUSTERS_OUTPUT_PATH}/l2_centroids.npy"
        )

        l1_to_l2 = {
            valid_l1_ids[i]: labels_l2[i]
            for i in range(len(valid_l1_ids))
        }

        articles["l2_cluster_id"] = (
            articles["l1_cluster_id"].map(l1_to_l2)
            .fillna(-1)
            .astype(int)
        )

    else:
        articles["l2_cluster_id"] = -1
        centroids_l2 = None
        valid_l2_ids = None

    return centroids_l2, valid_l2_ids


def get_l3_clusters(centroids_l2, valid_l2_ids, articles):
    """Build a third-level clustering from level‑2 centroids.

    The returned centroids and ids correspond only to non-noise clusters from the
    previous level.  ``articles`` receives a new ``l3_cluster_id`` column; any
    rows that were not part of a valid level‑2 cluster are set to ``-1``.
    """
    if centroids_l2 is not None and len(centroids_l2) > 2:
        labels_l3 = run_clustering(centroids_l2, level=3)

        centroids_l3, valid_l3_ids = compute_and_save_centroids(
            centroids_l2,
            labels_l3,
            f"{config.CLUSTERS_OUTPUT_PATH}/l3_centroids.npy"
        )

        l2_to_l3 = {
            valid_l2_ids[i]: labels_l3[i]
            for i in range(len(valid_l2_ids))
        }

        articles["l3_cluster_id"] = (
            articles["l2_cluster_id"].map(l2_to_l3)
            .fillna(-1)
            .astype(int)
        )

    else:
        articles["l3_cluster_id"] = -1
        centroids_l3 = None
        valid_l3_ids = None

    return centroids_l3, valid_l3_ids


def get_l4_clusters(centroids_l3, valid_l3_ids, articles):
    """Perform a fourth-level clustering based on level‑3 centroids.

    Works similarly to :func:`get_l3_clusters` with the appropriate column
    names and filename.
    """
    if centroids_l3 is not None and len(centroids_l3) > 2:
        labels_l4 = run_clustering(centroids_l3, level=4)

        centroids_l4, valid_l4_ids = compute_and_save_centroids(
            centroids_l3,
            labels_l4,
            f"{config.CLUSTERS_OUTPUT_PATH}/l4_centroids.npy"
        )

        l3_to_l4 = {
            valid_l3_ids[i]: labels_l4[i]
            for i in range(len(valid_l3_ids))
        }

        articles["l4_cluster_id"] = (
            articles["l3_cluster_id"].map(l3_to_l4)
            .fillna(-1)
            .astype(int)
        )

    else:
        articles["l4_cluster_id"] = -1
        centroids_l4 = None
        valid_l4_ids = None

    return centroids_l4, valid_l4_ids


def get_cluster_names(titles):
    token_counts = Counter()
    phrase_counts = Counter()

    for title in titles:

        tokens = preprocess(title)

        if not tokens:
            continue

        token_counts.update(tokens)

        # build bigrams
        bigrams = [" ".join(bg) for bg in zip(tokens, tokens[1:])]
        phrase_counts.update(bigrams)

    # get strongest phrase first
    if phrase_counts:
        phrase, _ = phrase_counts.most_common(1)[0]
        words = phrase.split()
    else:
        words = []

    # add strong single tokens
    for token, _ in token_counts.most_common(5):

        if token not in words:
            words.append(token)

        if len(words) >= 4:
            break

    if not words:
        return "unknown"

    return " ".join(words[:4])


def get_clusters_table(cluster_map_path, output_path):
    if not cluster_map_path:
        cluster_map_path = config.CLUSTERS_MAP_PATH
    if not output_path:
        output_path = config.CLUSTERS_TABLE_PATH

    df = pd.read_parquet(cluster_map_path)

    results = []

    levels = [
        ("l1_cluster_id", "l2_cluster_id", 1),
        ("l2_cluster_id", "l3_cluster_id", 2),
        ("l3_cluster_id", "l4_cluster_id", 3),
        ("l4_cluster_id", None, 4),
    ]

    for cluster_col, parent_col, level in levels:

        if cluster_col not in df.columns:
            continue

        valid = df[df[cluster_col] != -1]

        if valid.empty:
            continue
        
        grouped = valid.groupby(cluster_col)

        for cluster_id, g in grouped:

            parent_cluster = None
            parent_level = None

            if parent_col and parent_col in g.columns:
                parent_vals = g[parent_col].values
                # Filter out noise (-1)
                parent_vals = parent_vals[parent_vals != -1]

                if len(parent_vals) > 0:
                    # All items in a sub-cluster belong to the same parent cluster
                    parent_cluster = int(parent_vals[0])
                    parent_level = level + 1

            # Get cluster name from top titles
            titles = g["title"].dropna().head(50).tolist()
            cluster_name = get_cluster_names(titles)

            # Calculate persistence metrics
            half_life = get_half_life(
                g[["published", cluster_col]]
                .copy()
                .rename(columns={cluster_col: "l1_cluster_id"}),
                cluster_id
            )

            # Calculate burst score
            bursts = get_bursts(
                g[["published"]].copy(),
                cluster_id
            )

            results.append(
                {
                    "cluster_id": int(cluster_id),
                    "level": level,
                    "cluster_name": cluster_name,
                    "parent_cluster_id": parent_cluster,
                    "parent_level": parent_level,
                    "created_date": g["published"].min(),
                    "last_updated": g["published"].max(),
                    "article_count": len(g),
                    "half_life": half_life,
                    "bursts": bursts,
                }
            )

    clusters_df = pd.DataFrame(results)

    clusters_df.sort_values(
        ["level", "cluster_id"],
        inplace=True
    )

    clusters_df.to_csv(output_path, index=False)

    return clusters_df