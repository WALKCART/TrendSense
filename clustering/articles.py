import pandas as pd
from clustering.textGenerator import *
from tqdm import tqdm
from clustering.config import bestConfig

class ArticleCluster:
    '''
    streamlined way to access all articles in a cluster
    - lists the articles
    - gives the cluster a title
    - has the relvancy score
    '''
    def __init__(
            self, 
            subset: pd.DataFrame, # subset of the articles db
            clustering_index_col: str
            ):
        self.articles = subset.reset_index(drop=True)
        self.index = self.articles.loc[0, clustering_index_col]
        self.cluster_title = None

    def get_articles(self):
        return self.articles
    
    def get_cluster_title(self):
        if self.cluster_title is None: 
            summaries = self.articles.summary
            cluster_info =  '\n\n'.join(summaries[~summaries.isna()].to_list())
            title = get_title(cluster_info)
            return title
        else: 
            return self.cluster_title

    def __repr__(self):
        return f'ArticleCluster(index {self.index}: {self.get_cluster_title()})'

def create_article_clusters(
        db: pd.DataFrame,
        clustering_index_col: str
        ):
    clusters = []
    unique = db[clustering_index_col].unique()
    for ind in unique:
        count = (db[clustering_index_col] == ind).sum()
        if count > bestConfig.minimum_articles: clusters.append(ArticleCluster(db[db[clustering_index_col] == ind], clustering_index_col))
    return clusters

def save_clusters(p: str, clusters: list):
    titles = []
    indices = []
    counts = []
    for cluster in tqdm(clusters):
        indices.append(cluster.index)
        titles.append(cluster.get_cluster_title())
        counts.append(cluster.articles.shape[0])
    df = pd.DataFrame({
        'title' : titles, 
        'clustering_index' : indices,
        'article_count' : counts
    })
    df.to_csv(p, index=False)
    print(f'saved as {p}!')

def load_clusters(
        p_clusters:str, 
        p_articles: str,
        clustering_index_col: str, 
        title_col: str
        ):
    clusters = pd.read_csv(p_clusters)
    articles = pd.read_csv(p_articles)

    

