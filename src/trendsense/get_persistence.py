from persistence import *

# getting the dataset (only the required columns)
clusters = pd.read_csv('hierarchical_clustered_articles_2.csv')\
    [['l1_cluster_id', 'published']]

# get all unique cluster ids
unique_cluster_ids = clusters['l1_cluster_id'].unique()

# compute half life for each cluster
results = []
for cluster_id in unique_cluster_ids:
    clusters_copy = clusters.copy()
    half_life = get_half_life(clusters_copy, cluster_id, get_visualization=False)
    results.append({'l1_cluster_id': cluster_id, 'half_life': half_life})

# create dataframe
half_life_df = pd.DataFrame(results)

# save to csv
half_life_df.to_csv('half_life.csv', index=False)

print("Half life computation completed and saved to half_life.csv")
