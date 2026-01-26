import os
import csv
from dotenv import load_dotenv
from supabase import create_client
from . import config
from . import buffer_loader
from . import buffer_cleaner
import state_manager.state_manager as sm
import pandas as pd
from tqdm import tqdm
load_dotenv()

def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

def articlesdb_upload():
    if not sm.get("S3_UPLOAD_DONE"):
        return ("Upload files to S3 before updating ArticlesDB", -1)
    supabase = get_supabase_client()

    try:
        articles_df = buffer_loader.load_articles()
        log_df = buffer_loader.load_temp_log()
        merged_df = pd.merge(articles_df, log_df, on='id')

    except FileNotFoundError as e:
        return ("Error: Could not find either aritcles.csv or temp_log.csv", -2)

    for index, row in tqdm(merged_df.iterrows(), total=merged_df.shape[0], desc="Syncing to Supabase"):
        data = {
            "id": str(row['id']),
            "site": row['site'],
            "section": row['section'],
            "title": row['title'],
            "link": row['link'],
            "published": row['published'],
            "s3_key": row['s3_key']
        }

        try:
            supabase.table(config.ARTICLES_DB).upsert(data).execute()
        except Exception as e:
            return f"\nError inserting ID {row['id']}: {e}"
    
    return ("Files Successfully Uploaded to ArticlesDB", 0)

