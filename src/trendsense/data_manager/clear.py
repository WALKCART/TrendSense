import os
from dotenv import load_dotenv
from supabase import create_client
from typing import Optional
from . import config
load_dotenv()


def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

def clear_supabase_table(table_name):
    """Clears all rows from the given table."""
    supabase = get_supabase_client()
    if table_name == config.ARTICLES_DB:
        try:
            supabase.table(table_name).delete().not_.is_("art_id", "null").execute()
            return 0
        except Exception as e:
            print(f"Debug Error: {e}")
            return -1
    elif table_name == config.VECTORS_DB:
        try:
            supabase.table(table_name).delete().not_.is_("batch_id", "null").execute()
            return 0
        except Exception as e:
            print(f"Debug Error: {e}")
            return -1
    
def clear_s3(bucket_name: str, prefix: Optional[str]):
    """Implement this"""