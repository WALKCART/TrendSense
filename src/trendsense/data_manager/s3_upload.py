import os
import boto3
import uuid
import csv
from dotenv import load_dotenv
import state_manager.state_manager as sm
from . import config
from . import buffer_loader
import pandas as pd
from tqdm import tqdm
load_dotenv()


def initialise_temp_log():
    with open(config.TEMP_LOG_CSV, 'w') as fh:
        fh.write("id,s3_key\n")
        print("Successfully created temp_log file")
        fh.close()

def s3_upload():

    s3_client = boto3.client('s3')
    initialise_temp_log()

    df = buffer_loader.load_articles()

    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Uploading to S3"):
        unique_id = str(uuid.uuid4())
        s3_key = "{0}/{1}-{2}-{3}-{4}.json".format(config.S3_PREFIX, row['id'], row['site'], row['section'], unique_id)

        json_payload = row[['id', 'site', 'section', 'title', 'summary', 'link', 'published', 'body']].to_json()

        s3_client.put_object(
            Bucket = config.S3_BUCKET,
            Key = s3_key,
            Body = json_payload
        )

        with open(config.TEMP_LOG_CSV, 'a') as fh:
            fh.write(f"{row['id']},{s3_key}\n")
    
    sm.set("S3_UPLOAD_DONE", "True")
    print("Files successfully uploaded to S3")
