import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_BUFFER_DIR = BASE_DIR / "DataBuffer"

# Specific File Paths
ARTICLES_CSV = DATA_BUFFER_DIR / "articles.csv"
CLUSTERS_CSV = DATA_BUFFER_DIR / "clusters.csv"
TEMP_LOG_CSV = DATA_BUFFER_DIR / "temp_log.csv"

# Constants
ARTICLES_DB = "ArticlesDB"
S3_BUCKET = "trendsense"
S3_PREFIX = "article-content"

# Flags
S3_UPLOAD_DONE = False
ARTICLESDB_UPLOAD_DONE = False