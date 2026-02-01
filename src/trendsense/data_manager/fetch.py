import os
import json
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from . import config
load_dotenv()


def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)


def fetch_article_s3_keys(mode):
    """Fetch the S3 key of articles which havent been clustered or embeded"""
    supabase = get_supabase_client()
    option = {'cluster_opt':'clustered', 'embed_opt':'embedded'}[mode]
    response = (supabase.table(config.ARTICLES_DB)
                    .select("art_id", "s3_key")
                    .eq(option, False)
                    .execute())
    if not response.data:
        return []
    return response.data

def fetch_embedding_s3_keys(mode):
    """Fetch the S3 key of articles which havent been clustered or embeded"""
    supabase = get_supabase_client()
    option = {'cluster_opt':'clustered', 'embed_opt':'embedded'}[mode]
    response = (supabase.table(config.VECTORS_DB)
                    .select("vec_id", "art_id", "title_vec_s3_key", "summary_vec_s3_key")
                    .eq(option, False)
                    .execute())
    if not response.data:
        return []
    return response.data