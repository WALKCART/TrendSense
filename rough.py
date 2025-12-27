from clustering.embedding import *

sent1 = [
    'This is crazy',
    'You are an idiot'
]

sent2 = [
    'This is insane',
    'You are stupid'
]

emb1 = get_embedding(sent1)
emb2 = get_embedding(sent2)

print(get_cosine_similarity(emb1, emb2))