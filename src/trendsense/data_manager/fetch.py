import os
import json
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from . import config
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from typing import Iterable
load_dotenv()


def get_supabase_client():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

    return create_client(url, key)


def fetch_title_embs():
    """
    Fetches unclustered article embeddings and buffers their corresponding S3 data.

    The function performs a three-step orchestration:
    1. Identifies articles in 'ArticlesDB' that are embedded but not yet clustered.
    2. Extracts unique ingestion dates from those records to query 'VectrosDB'.
    3. Retrieves S3 keys associated with those dates and loads the embedding 
       objects into the system's databuffer.

    Returns:
        None
    
    Raises:
        PostgrestException: If there is an error querying the Supabase tables.
        S3Error: If the retrieval of embedding files from S3 fails.
    """