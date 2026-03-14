import pandas as pd
from trendsense.clustering.create_clusters import get_clusters_table

df = get_clusters_table(None, None)
print(df.head())