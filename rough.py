from clustering.embedding import *

sent1 = [
    'This is crazy',
    'You are an idiot',
    'I am so self conscious'
]

sent2 = [
    'This is insane',
    'You are stupid',
    'I am very insecure'
]

# emb1 = get_embedding(sent1)
# emb2 = get_embedding(sent2)
print(get_clustering_inds(sent2+sent1))
