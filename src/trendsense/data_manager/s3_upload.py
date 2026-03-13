import os
import boto3
import uuid
from supabase import create_client
from dotenv import load_dotenv
from . import config
from . import buffer_loader
import pandas as pd
from tqdm import tqdm
load_dotenv()


def _clean_str(s):
    return (
        str(s)
        .lower()
        .strip()
        .replace(" ", "_")
        .replace("/", "_")
    )

def initialise_temp_log(mode: str):
    if mode == 'articles':
        with open(config.TEMP_ART_LOG_CSV, 'w') as fh:
            fh.write("row_idx,serial_no,article_id,s3_key\n")
            print("Successfully created temp_log file")
            fh.close()
    elif mode == 'title_vectors':
        with open(config.TEMP_TITLE_VEC_LOG_CSV, 'w') as fh:
            fh.write("batch_date,title_s3_key\n")
            print("Successfully created temp_log file")
            fh.close()
    elif mode == 'summary_vectors':
        with open(config.TEMP_SUMMARY_VEC_LOG_CSV, 'w') as fh:
            fh.write("batch_date,summary_s3_key\n")
            print("Successfully created temp_log file")
            fh.close()


def get_supabase_client():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    return create_client(url, key)


def get_next_serial_no(supabase) -> int:
    res = (
        supabase
        .table(config.ARTICLES_DB)
        .select("serial_no")
        .order("serial_no", desc=True)
        .limit(1)
        .execute()
    )

    if not res.data:
        return 0  # 0-indexed

    return res.data[0]["serial_no"] + 1


def articles_s3_upload(input_path):
    s3_client = boto3.client('s3')
    supabase = get_supabase_client()

    initialise_temp_log('articles')
    if input_path:
        df = pd.read_csv(input_path)
    else:
        df = buffer_loader.load_articles()

    next_serial = get_next_serial_no(supabase)

    for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc="Uploading to S3", mininterval=1):
        serial_no = next_serial
        next_serial += 1
        unique_id = str(uuid.uuid4().hex)
        site = _clean_str(row['site'])
        section = _clean_str(row['section'])
        article_id = f"art-{serial_no}-{site}-{section}-{unique_id}"
        s3_key = f"{config.S3_ARTICLES_PREFIX}/{article_id}.json"
        json_payload = row[['title', 'summary', 'body']].to_json()

        try:
            s3_client.put_object(
                Bucket = config.S3_BUCKET,
                Key = s3_key,
                Body = json_payload,
                ContentType="application/json"
            )

            with open(config.TEMP_ART_LOG_CSV, 'a') as fh:
                fh.write(f"{idx},{serial_no},{article_id},{s3_key}\n")
        except Exception as e:
            print(f"Failed to upload article {article_id}: {e}")
            continue
        
    print("Articles successfully uploaded to S3")

def title_embs_s3_upload(input_path, ingested_date):
    """Upload title embeddings parquet file to S3"""

    s3_client = boto3.client('s3')

    initialise_temp_log('title_vectors')
    if input_path:
        title_path = input_path
    else:
        title_path = config.TITLE_EMB_PATH
    if not title_path.exists():
        raise FileNotFoundError(f"Parquet file not found: {title_path}")

    batch_date = ingested_date.isoformat()
    s3_key = f"{config.S3_VECTORS_PREFIX}/{batch_date}/title_embs.parquet"

    # Upload file directly (NO open())
    s3_client.upload_file(
        Filename=str(title_path),
        Bucket=config.S3_BUCKET,
        Key=s3_key,
    )
    with open(config.TEMP_TITLE_VEC_LOG_CSV, 'a') as fh:
        fh.write(f"{batch_date},{s3_key}\n")

    print(f"Uploaded title embeddings to s3://{config.S3_BUCKET}/{s3_key}")


def summary_embs_s3_upload(input_path, ingested_date):
    """Upload title embeddings parquet file to S3"""

    s3_client = boto3.client('s3')

    initialise_temp_log('summary_vectors')
    if input_path:
        summary_path = input_path
    else:
        summary_path = config.SUMMARY_EMB_PATH
    if not summary_path.exists():
        raise FileNotFoundError(f"Parquet file not found: {summary_path}")

    batch_date = ingested_date.isoformat()
    s3_key = f"{config.S3_VECTORS_PREFIX}/{batch_date}/summary_embs.parquet"

    # Upload file directly (NO open())
    s3_client.upload_file(
        Filename=str(summary_path),
        Bucket=config.S3_BUCKET,
        Key=s3_key,
    )
    with open(config.TEMP_SUMMARY_VEC_LOG_CSV, 'a') as fh:
        fh.write(f"{batch_date},{s3_key}\n")

    print(f"Uploaded title embeddings to s3://{config.S3_BUCKET}/{s3_key}")
