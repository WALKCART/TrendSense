import os
from dotenv import load_dotenv
from supabase import create_client
from . import config
from . import buffer_loader
import pandas as pd
from tqdm import tqdm
load_dotenv()

def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)


def articles_db_upload():
    supabase = get_supabase_client()

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
            "clustered": False
        }

        supabase.table(config.ARTICLES_DB).upsert(data).execute()

def clusters_db_upload():
    pass

def vector_ref_db_upload():
    pass
