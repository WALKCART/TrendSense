from venv import create
import click
from pathlib import Path
from datetime import datetime, timezone
from trendsense.data_manager.s3_upload import articles_s3_upload, title_embs_s3_upload, summary_embs_s3_upload
from trendsense.data_manager.db_upload import articles_db_upload, vec_db_upload


@click.group()
def upload():
    """
    Upload data artifacts to external storage (S3, DBs, etc.)
    """
    pass


@upload.command("s3-articles")
@click.option("--input-path", "-i", type = str, help = "Location of the source file")
def upload_articles_s3(input_path):
    """
    Upload scraped articles to S3 and generate canonical article IDs.
    """
    click.echo("Starting S3 upload for articles...")

    try:
        articles_s3_upload(input_path=input_path)
    except Exception as e:
        click.echo(f"Upload failed: {e}", err=True)
        raise SystemExit(1)

    click.echo("Articles successfully uploaded to S3")


@upload.command("db-articles")
@click.option("--input-path", "-i", type = str, help = "Location of the source file")
def upload_articles_db(input_path):
    """
    Upload scraped articles to ArticlesDB
    """
    click.echo("Starting ArticlesDB upload...")

    try:
        articles_db_upload(input_path=input_path)
    except Exception as e:
        click.echo(f"Upload failed: {e}", err=True)
        raise SystemExit(1)
    
    click.echo("Articles successfully uploaded to ArticlesDB")


@upload.command("s3-title-embs")
@click.option("--input-path", "-i", type=click.Path(exists=True, path_type=Path), default=None, help="Path to title embeddings parquet file (defaults to DataBuffer path)",)
@click.option("--ingested-date", "-d", type=str, default=None, help="Ingested date in YYYY-MM-DD format (defaults to today UTC)",)
def upload_title_embs_s3(input_path, ingested_date):
    """
    Upload title embeddings parquet file to S3.
    """
    # Resolve ingested_date
    if ingested_date:
        ingested_date = datetime.strptime(ingested_date, "%Y-%m-%d").date()
    else:
        ingested_date = datetime.now().date()

    title_embs_s3_upload(
        input_path=input_path,
        ingested_date=ingested_date,
    )

@upload.command("s3-summary-embs")
@click.option("--input-path", "-i", type=click.Path(exists=True, path_type=Path), default=None, help="Path to summary embeddings parquet file (defaults to DataBuffer path)")
@click.option("--ingested-date", "-d", type=str, default=None, help="Ingested date in YYYY-MM-DD format (defaults to today UTC)")
def upload_summary_embs_s3(input_path, ingested_date):
    """
    Upload summary embeddings parquet file to S3.
    """
    # Resolve ingested_date
    if ingested_date:
        ingested_date = datetime.strptime(ingested_date, "%Y-%m-%d").date()
    else:
        ingested_date = datetime.now().date()

    summary_embs_s3_upload(
        input_path=input_path,
        ingested_date=ingested_date,
    )

@upload.command("db-vectors")
@click.option("--created-date", "-d", type=str, default=None, help="Batch creation date in YYYY-MM-DD format (defaults to today UTC)")
def upload_vectors_db(created_date):
    if created_date:
        created_date = datetime.strptime(created_date, "%Y-%m-%d").date()
    else:
        created_date = datetime.now(timezone.utc).date()
    
    vec_db_upload(created_date=created_date)