import os
from pathlib import Path
import config
import pandas as pd


articles_df = pd.read_csv(config.ARTICLES_CSV)
log_df = pd.read_csv(config.TEMP_LOG_CSV)
merged_df = pd.merge(articles_df, log_df, on='id')
    