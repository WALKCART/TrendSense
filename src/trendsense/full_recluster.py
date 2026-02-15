from sentence_transformers import SentenceTransformer
import pandas as pd
import umap
import hdbscan
import os
import numpy as np

# config
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
    df = pd.DataFrame({"label": labels})
    df["embedding"] = list(embeddings)

    df = df[df["label"] != -1]  # remove noise

    if len(df) == 0:
        print(f"No valid clusters found for {filename}")
        return None, None

    grouped = df.groupby("label")["embedding"]

    cluster_ids = sorted(grouped.groups.keys())
    max_cluster_id = max(cluster_ids)

    embedding_dim = embeddings.shape[1]
    centroid_array = np.zeros((max_cluster_id + 1, embedding_dim))

    for cid in cluster_ids:
        cluster_embeddings = np.vstack(grouped.get_group(cid))
        centroid = cluster_embeddings.mean(axis=0)
        centroid /= np.linalg.norm(centroid)
        centroid_array[cid] = centroid

    np.save(filename, centroid_array)

    return centroid_array, cluster_ids

model = SentenceTransformer("all-mpnet-base-v2")

article_dir = "_articles"
article_paths = os.listdir(article_dir)

articles = []
article_bodies = []

for path in article_paths:
    df = pd.read_csv(os.path.join(article_dir, path))
    if "body" not in df.columns:
        continue

    cleaned = df[df["body"].notna()]
    articles.append(cleaned)
    article_bodies.extend(cleaned["body"].astype(str).tolist())

articles = pd.concat(articles, ignore_index=True)

# l0
embeddings_l0 = model.encode(
    article_bodies,
    show_progress_bar=True,
    normalize_embeddings=True
)

# l1
labels_l1 = run_clustering(embeddings_l0)
articles["l1_cluster_id"] = labels_l1

centroids_l1, valid_l1_ids = compute_and_save_centroids(
    embeddings_l0,
    labels_l1,
    "l1_centroids.npy"
)

# l2
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

    articles["l2_cluster_id"] = articles["l1_cluster_id"].map(l1_to_l2)

else:
    articles["l2_cluster_id"] = -1
    centroids_l2 = None


# l3

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

    articles["l3_cluster_id"] = articles["l2_cluster_id"].map(l2_to_l3)

else:
    articles["l3_cluster_id"] = -1
    centroids_l3 = None

# l4
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

    articles["l4_cluster_id"] = articles["l3_cluster_id"].map(l3_to_l4)

else:
    articles["l4_cluster_id"] = -1


articles.to_csv("hierarchical_clustered_articles.csv", index=False)