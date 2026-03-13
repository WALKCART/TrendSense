import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]
DATA_BUFFER_DIR = BASE_DIR / "DataBuffer"

# Specific File Paths
ARTICLES_CSV = DATA_BUFFER_DIR /"_articles"/"articles.csv"
CLUSTERS_CSV = DATA_BUFFER_DIR / "clusters.csv"
TITLE_EMB_PATH = DATA_BUFFER_DIR /"_vectors"/"title_emb.parquet"
SUMMARY_EMB_PATH = DATA_BUFFER_DIR /"_vectors"/"summary_emb.parquet"
TEMP_ART_LOG_CSV = DATA_BUFFER_DIR /"_ref_logs"/ "art_s3_log.csv"
TEMP_TITLE_VEC_LOG_CSV = DATA_BUFFER_DIR /"_ref_logs"/ "title_vec_log.csv"
TEMP_SUMMARY_VEC_LOG_CSV = DATA_BUFFER_DIR /"_ref_logs"/ "summary_vec_log.csv"
FETCHED_ARTICLES_CSV = DATA_BUFFER_DIR / "fetched_articles.csv"
FETCHED_TITLE_EMBS_FILES = DATA_BUFFER_DIR /"_fetched"/ "fetched_title_embs.parquet"
FETCHED_SUMMARY_EMBS_FILES = DATA_BUFFER_DIR /"_fetched"/ "fetched_summary_embs.parquet"
TEMP_TITLE_EMBS_FILES = DATA_BUFFER_DIR / "temp_title_embs.parquet"
TEMP_SUMMARY_EMBS_FILES = DATA_BUFFER_DIR / "temp_summary_embs.parquet"


# Constants
ARTICLES_DB = "ArticlesDB"
VECTORS_DB = "VectorsDB"
S3_BUCKET = "trendsense"
S3_ARTICLES_PREFIX = "articles"
S3_VECTORS_PREFIX = "vectors"
