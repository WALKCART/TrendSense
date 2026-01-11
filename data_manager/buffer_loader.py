import numpy as np
import pandas as pd
from . import config


def load_articles():
    '''
        Load articles.csv 
    '''
    return pd.read_csv(config.ARTICLES_CSV)

def load_clusters():
    '''
        Load clusters.csv
    '''
    return pd.read_csv(config.CLUSTERS_CSV)

def load_temp_log():
    '''
        Load temp_log.csv
    '''
    return pd.read_csv(config.TEMP_LOG_CSV)