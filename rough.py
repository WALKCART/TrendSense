from clustering.articles import *
import pandas as pd
from clustering.textGenerator import *
from tqdm import tqdm
warm_up()

clusters = create_article_clusters(
    pd.read_csv('articles.csv'),
    clustering_index_col='clustering_index'
)

# print(*clusters, sep='\n\n')
save_clusters(
    p='clusters.csv',
    clusters=clusters
)

print('saved the clusters in clusters.csv')
