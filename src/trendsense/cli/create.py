import os
from pathlib import Path
import click
from trendsense.clustering.embedding import *
from trendsense.data_manager import config


@click.group
def create():
    """
    Create Vector Embeddings, Clusters etc.
    """
    pass

@create.command("embeddings")
@click.option("--title-emb", "-t", is_flag = True, help = "Create Title embeddings")
@click.option("--summary-emb", "-s", is_flag = True, help = "Create Sumary embeddings")
@click.option("--output-path", "-o", type=click.Path(exists=True, path_type=Path), help = "Location of the output DIRECTORY")
def create_embeddings(title_emb, summary_emb, output_path):
    """
    Creates vector embeddings for title and susmmaries and stores them as parquet files
    """
    if not title_emb and not summary_emb:
        raise click.UsageError(
            "Specify at least one embedding type: --title and/or --summary"
        )
    
    get_embedding(output_path=output_path, title_emb=title_emb, summary_emb=summary_emb)