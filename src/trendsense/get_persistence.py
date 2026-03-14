from persistence import *

# getting the dataset (only the required columns)
clusters = pd.read_csv('hierarchical_clustered_articles.csv')\
    [['l1_cluster_id', 'published']]


# choose cluster
cluster_id = clusters['l1_cluster_id'].unique()[0]

half_life = get_half_life(clusters, cluster_id, get_visualization=True)
print(half_life)
