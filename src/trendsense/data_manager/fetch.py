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
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
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


def fetch_title_embs():
    """
    Gets the ingestion dates for articles which have been embedded but not clustered
    Based on the ingestion dates fetches the required paraquet files, combines them into one file and stores them in one master file
    """

    supabase = get_supabase_client()
    s3 = boto3.client("s3")

    # fetch the ingestion dates
    resp = (
        supabase
        .table(config.ARTICLES_DB)
        .select("ingested_date")
        .eq("embedded", True)
        .eq("clustered", False)
        .execute()
    )
    if not resp.data:
        print("No articles to cluster.")
        return None
    ingestion_dates = sorted(
        {row["ingested_date"] for row in resp.data}
    )

    # fetch vector embs meta data
    vec_resp = (
        supabase
        .table(config.VECTORS_DB)
        .select("batch_date, title_s3_key")
        .in_("batch_date", ingestion_dates)
        .execute()
    )
    if not vec_resp.data:
        raise RuntimeError("No vector batches found for ingestion dates")
    
    vec_df = pd.DataFrame(vec_resp.data)
    tables = []

    config.TEMP_TITLE_EMBS_DIR.mkdir(parents=True, exist_ok=True)

    for row in vec_resp.data:
        s3_key = row["title_s3_key"]
        local_path = config.TEMP_TITLE_EMBS_DIR / Path(s3_key).name

        if not local_path.exists():
            s3.download_file(
                Bucket=config.S3_BUCKET,
                Key=s3_key,
                Filename=str(local_path),
            )

        table = pq.read_table(local_path)
        tables.append(table)

    if not tables:
        raise RuntimeError("No title embeddings loaded")
    
    combined_table = pa.concat_tables(tables)
    pq.write_table(combined_table, config.FETCHED_TITLE_EMBS_FILES, compression="snappy")

    print(
        f"Fetched title embeddings from {len(ingestion_dates)} batches "
        f"to {config.FETCHED_TITLE_EMBS_FILES}"
    )

    return config.FETCHED_TITLE_EMBS_FILES



def fetch_summary_embs():
    """"""