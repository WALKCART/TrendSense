import os
import io
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
from typing import List, Dict, Any, cast
load_dotenv()


def get_supabase_client():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

    return create_client(url, key)


def fetch_unembedded_articles(page_size: int = 1000) -> pd.DataFrame:
    """
    Fetch articles that have not yet been embedded.

    Returns a DataFrame with columns:
    - art_id
    - title
    - s3_key
    """

    supabase = get_supabase_client()
    rows = []
    offset = 0

    while True:
        response = (
            supabase
            .table(config.ARTICLES_DB)
            .select("art_id, title, s3_key")
            .eq("embedded", False)
            .range(offset, offset + page_size - 1)
            .execute()
        )

        data = response.data or []
        if not data:
            break

        rows.extend(data)
        offset += page_size

    if not rows:
        return pd.DataFrame(columns=["art_id", "title", "s3_key"])

    df = pd.DataFrame(rows)

    df["title"] = df["title"].astype(str).str.strip()
    df["s3_key"] = df["s3_key"].astype(str).str.strip()

    return df


def fetch_summaries(records: Iterable[tuple[str, str]]) -> pd.DataFrame:
    """
    Fetch summaries from S3.

    Parameters
    ----------
    records : iterable of (art_id, s3_key)

    Returns
    -------
    DataFrame with columns:
    - art_id
    - s3_key
    - summary (None if missing)
    """

    s3 = boto3.client("s3")
    BUCKET_NAME = config.S3_BUCKET

    rows = []

    for art_id, s3_key in records:
        summary = None

        if s3_key:
            try:
                obj = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
                body = obj["Body"].read()
                payload = json.loads(body)
                summary = payload.get("summary")

                if not summary or not summary.strip():
                    continue

                rows.append({
                    "art_id": art_id,
                    "s3_key": s3_key,
                    "summary": summary.strip()
                })


            except Exception:
                continue
    return pd.DataFrame(rows)


def fetch_title_embs() -> pd.DataFrame:
    """
    Fetches unclustered article embeddings and buffers their corresponding S3 data.

    The function performs a three-step orchestration:
    1. Identifies articles in 'ArticlesDB' that are embedded but not yet clustered.
    2. Extracts unique ingestion dates from those records to query 'VectrosDB'.
    3. Retrieves S3 keys associated with those dates and loads the embedding 
       objects into the system's databuffer.

    Returns:
        pandas.DataFrame: A combined DataFrame of all fetched embeddings. 
                        Returns an empty DataFrame if no new data is found.
    """

    supabase = get_supabase_client()
    response = supabase.rpc("get_distinct_ingested_dates").execute()
    response = cast(List[Dict[str, Any]], response.data or [])
    ingested_dates = [res['ingested_date'] for res in response]

    if not ingested_dates:
        return pd.DataFrame()
    
    vectors_res = supabase.table(config.VECTORS_DB).select("title_s3_key").in_("batch_date", ingested_dates).execute()
    vectors_data = cast(List[Dict[str, Any]], vectors_res.data or [])
    title_s3_keys = [record['title_s3_key'] for record in vectors_data]

    if not title_s3_keys:
        return pd.DataFrame()
    
    s3_client = boto3.client("s3")
    dfs = []
    for key in title_s3_keys:
        try:
            obj = s3_client.get_object(Bucket=config.S3_BUCKET, Key=key)
            parquet_bytes = obj["Body"].read()

            df = pd.read_parquet(io.BytesIO(parquet_bytes))
            dfs.append(df)
        except ClientError as e:
            print(f"Failed to fetch {key}: {e}")

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)

