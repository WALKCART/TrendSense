import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]
DATA_BUFFER_DIR = BASE_DIR / "DataBuffer"

# Specific File Paths
ARTICLES_CSV = DATA_BUFFER_DIR / "articles.csv"
CLUSTERS_CSV = DATA_BUFFER_DIR / "clusters.csv"
TEMP_LOG_CSV = DATA_BUFFER_DIR / "temp_art_s3_log.csv"

# Constants
ARTICLES_DB = "ArticlesDB"
S3_BUCKET = "trendsense"
S3_PREFIX = "article-content"