from clustering.embedding import *

sent1 = pd.Series([
    'I am admire you', #0
    'I am so sad', #1
    'I am so depressed', #1
    'I respect you' #0
])

sent2 = pd.Series([
    0, pd.NA, pd.NA, pd.NA
])

# emb1 = get_embedding(sent1)
# emb2 = get_embedding(sent2)
print(get_clustering_inds(sent1))
