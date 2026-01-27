import click
from trendsense.data_manager.s3_upload import articles_s3_upload
from trendsense.data_manager.db_upload import articles_db_upload


@click.group()
def upload():
    """
    Upload data artifacts to external storage (S3, DBs, etc.)
    """
    pass


@upload.command("s3-articles")
def upload_articles_s3():
    """
    Upload scraped articles to S3 and generate canonical article IDs.
    """
    click.echo("Starting S3 upload for articles...")

    try:
        articles_s3_upload()
    except Exception as e:
        click.echo(f"Upload failed: {e}", err=True)
        raise SystemExit(1)

    click.echo("Articles successfully uploaded to S3")


@upload.command("db-articles")
def upload_articles_db():
    """
    Upload scraped articles to ArticlesDB
    """
    click.echo("Starting ArticlesDB upload...")

    try:
        articles_db_upload()
    except Exception as e:
        click.echo(f"Upload failed: {e}", err=True)
        raise SystemExit(1)
    
    click.echo("Articles successfully uploaded to ArticlesDB")