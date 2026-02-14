from sentence_transformers import SentenceTransformer
import pandas as pd
import umap
import hdbscan
import os 

model = SentenceTransformer("all-mpnet-base-v2")

# getting placeholder articles
article_dir = '_articles'
article_paths = os.listdir(article_dir)
articles = []
article_bodies = []

for path in article_paths:
    df = pd.read_csv(os.path.join(article_dir, path))
    
    # Ensure body exists
    if 'body' not in df.columns:
        continue
    
    # Drop NaNs
    cleaned = df[df['body'].notna()]
    articles.append(cleaned)
    
    # Convert everything explicitly to string
    # cleaned['body'] = cleaned.astype(str)
    article_bodies.extend(cleaned['body'].tolist())
articles = pd.concat(articles, ignore_index=True, axis=0)

# embedding
embeddings = model.encode(article_bodies, 
                          show_progress_bar=True,
                          normalize_embeddings=True)

# dimensionality reduction
reducer = umap.UMAP(
    n_neighbors=15,
    n_components=50,
    metric='cosine',
    random_state=42
)

reduced_embeddings = reducer.fit_transform(embeddings)

# clustering
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=15, # hyper param for L0, L1, L2, L3
    min_samples=10,
    metric='euclidean',  ## since we are using UMAP, we can use euclidean distance for clustering
    cluster_selection_method='eom'
)

labels = clusterer.fit_predict(reduced_embeddings).tolist()
assert isinstance(labels, list), "labels isn\'t a list"

# create a dataframe to hold the results
articles['cluster_index'] = pd.Series(labels)
articles.to_csv('reclustered_articles.csv', index=False)