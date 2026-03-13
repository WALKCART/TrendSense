
import pandas as pd
import umap
import hdbscan
import os
import numpy as np

# config:- Add them in the config file and make changes accordingly
UMAP_N_NEIGHBORS = 15
UMAP_N_COMPONENTS = 50
HDBSCAN_MIN_CLUSTER_SIZE = 3
HDBSCAN_MIN_SAMPLES = 10
RANDOM_STATE = 42


def run_clustering(embeddings):
    n_samples = embeddings.shape[0]

    # UMAP requires n_components < n_samples
    n_components = min(UMAP_N_COMPONENTS, n_samples - 2)
    n_neighbors = min(UMAP_N_NEIGHBORS, n_samples - 1)

    # If too few points, skip dimensionality reduction
    if n_samples < 3:
        return np.full(n_samples, -1)

    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        n_components=n_components,
        metric='cosine',
        random_state=RANDOM_STATE
    )

    reduced = reducer.fit_transform(embeddings)

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min(HDBSCAN_MIN_CLUSTER_SIZE, n_samples),
        min_samples=min(HDBSCAN_MIN_SAMPLES, n_samples),
        metric='euclidean',
        cluster_selection_method='eom'
    )

    labels = clusterer.fit_predict(reduced)
    return labels


def compute_and_save_centroids(embeddings, labels, filename):
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

    cluster_ids = sorted(grouped.groups.keys())

    embedding_dim = embeddings.shape[1]
    centroids = []

    for cid in cluster_ids:
        cluster_embeddings = np.vstack(grouped.get_group(cid))
        centroid = cluster_embeddings.mean(axis=0)
        centroid /= np.linalg.norm(centroid)
        centroids.append(centroid)

    centroid_array = np.vstack(centroids)
    np.save(filename, centroid_array)

    return centroid_array, cluster_ids

def get_l1_clusters(embeddings_l0, articles):
    """Cluster raw article embeddings and attach ``l1_cluster_id`` to ``articles``.

    Returns centroids and corresponding cluster ids for the first level.
    """
    labels_l1 = run_clustering(embeddings_l0)
    articles["l1_cluster_id"] = labels_l1
    centroids_l1, valid_l1_ids = compute_and_save_centroids(
        embeddings_l0,
        labels_l1,
        "l1_centroids.npy"
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
        labels_l2 = run_clustering(centroids_l1)

        centroids_l2, valid_l2_ids = compute_and_save_centroids(
            centroids_l1,
            labels_l2,
            "l2_centroids.npy"
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
        labels_l3 = run_clustering(centroids_l2)

        centroids_l3, valid_l3_ids = compute_and_save_centroids(
            centroids_l2,
            labels_l3,
            "l3_centroids.npy"
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
        labels_l4 = run_clustering(centroids_l3)

        centroids_l4, valid_l4_ids = compute_and_save_centroids(
            centroids_l3,
            labels_l4,
            "l4_centroids.npy"
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
