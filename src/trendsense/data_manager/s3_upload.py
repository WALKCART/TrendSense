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


def initialise_temp_log():
    with open(config.TEMP_LOG_CSV, 'w') as fh:
        fh.write("row_idx,serial_no,article_id,s3_key\n")
        print("Successfully created temp_log file")
        fh.close()


def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
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

def articles_s3_upload():
    s3_client = boto3.client('s3')
    supabase = get_supabase_client()

    initialise_temp_log()

    df = buffer_loader.load_articles()

    next_serial = get_next_serial_no(supabase)

    for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc="Uploading to S3"):
        serial_no = next_serial
        next_serial += 1
        unique_id = str(uuid.uuid4())
        site = row['site']
        section = row['section']
        article_id = f"art-{serial_no}-{site}-{section}-{unique_id}"
        s3_key = f"{config.S3_PREFIX}/{article_id}.json"
        json_payload = row[['title', 'summary', 'body']].to_json()

        s3_client.put_object(
            Bucket = config.S3_BUCKET,
            Key = s3_key,
            Body = json_payload
        )

        with open(config.TEMP_LOG_CSV, 'a') as fh:
            fh.write(f"{idx},{serial_no},{article_id},{s3_key}\n")
    
    print("Articles successfully uploaded to S3")
