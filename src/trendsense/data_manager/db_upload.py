import os
from dotenv import load_dotenv
from supabase import create_client

import trendsense.clustering.config
from . import config
from . import buffer_loader
import pandas as pd
from tqdm import tqdm
from datetime import datetime, timezone
import pyarrow as pa 
import pyarrow.parquet as pq
from trendsense.clustering.config import bestConfig
load_dotenv()

def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)


def articles_db_upload(input_path):
    supabase = get_supabase_client()

    if input_path:
        articles_df = pd.read_csv(input_path)
    else:
        articles_df = buffer_loader.load_articles()
    log_df = buffer_loader.load_temp_log()
    if articles_df.empty or log_df.empty:
        print("Nothing to upload to ArticlesDB.")
        return
    merged_df = articles_df.merge(
        log_df,
        left_index=True,
        right_on="row_idx",
        how="inner",
    )
    ingested_date = datetime.now().date()
    for _, row in tqdm(merged_df.iterrows(), total=merged_df.shape[0], desc="Syncing to Supabase"):
        data = {
            "art_id":row['article_id'],
            "serial_no": row['serial_no'],
            "site": row['site'],
            "section": row['section'],
            "title": row['title'],
            "link": row['link'],
            "published": row['published'],
            "s3_key": row['s3_key'],
            "embedded": False,
            "clustered": False,
            "ingested_date": ingested_date.isoformat()
        }

        supabase.table(config.ARTICLES_DB).upsert(data).execute()

def chunked(lst, size=200):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def vec_db_upload(created_date):
    """Upload vector embedding meta data to supabase and set embedded flag in articles db to True"""

    supabase = get_supabase_client()

    table = pq.read_table(config.TITLE_EMB_PATH)
    art_ids = table.to_pandas().art_id.tolist()
    if not art_ids:
        raise RuntimeError("No article IDs found in embedding parquet")
    
    title_log = pd.read_csv(config.TEMP_TITLE_VEC_LOG_CSV)
    summary_log = pd.read_csv(config.TEMP_SUMMARY_VEC_LOG_CSV)
    merged_log = title_log.merge(summary_log, on='batch_date')
    if merged_log.empty:
        raise RuntimeError("No batch metadata found in vector temp logs")
    
    rows = []
    for _, row in merged_log.iterrows():
        batch_date_ts = datetime.fromisoformat(row["batch_date"]).replace(tzinfo=timezone.utc).isoformat()
        created_at_ts = datetime.combine(created_date, datetime.min.time(), tzinfo=timezone.utc).isoformat()
        rows.append({
            "id": f"{row['batch_date']}-{bestConfig.model}",  
            "batch_date": batch_date_ts,
            "title_s3_key": row["title_s3_key"],
            "summary_s3_key": row["summary_s3_key"],
            "model_name": bestConfig.model,
            "created_at": created_at_ts,
        })
    supabase.table(config.VECTORS_DB).upsert(rows).execute()

    # update the embedded flag in articles db
    for batch in chunked(art_ids, size=200):
        supabase.table(config.ARTICLES_DB).update({"embedded": True}).in_("art_id", batch).execute()
    print(f"Inserted {len(rows)} vector batch records ")
    print(f"and marked {len(art_ids)} articles as embedded")