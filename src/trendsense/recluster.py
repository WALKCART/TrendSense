from sentence_transformers import SentenceTransformer
from clustering import *
model = SentenceTransformer("all-mpnet-base-v2")
import os
import pandas as pd
from scraper.retrieval import *

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

# articles = pd.concat(articles, ignore_index=True)

# getting the articles 
articles = pd.read_csv('articles_new.csv')

# get the article bodies


cleaned = articles[articles["body"].notna()]
article_bodies.extend(cleaned["body"].astype(str).tolist())


# l0 (embeddings)
embeddings_l0 = model.encode(
    article_bodies,
    show_progress_bar=True,
    normalize_embeddings=True
)

# l1
centroids_l1, valid_l1_ids = get_l1_clusters(embeddings_l0, articles)


# l2
centroids_l2, valid_l2_ids = get_l2_clusters(centroids_l1, valid_l1_ids, articles)


# l3
centroids_l3, valid_l3_ids = get_l3_clusters(centroids_l2, valid_l2_ids, articles)


# l4
centroids_l4, valid_l4_ids = get_l4_clusters(centroids_l3, valid_l3_ids, articles)


articles.to_csv("hierarchical_clustered_articles.csv", index=False)