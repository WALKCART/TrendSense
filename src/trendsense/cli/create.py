import os
from pathlib import Path
import click
from trendsense.clustering.embedding import *
from trendsense.clustering.create_clusters import *
from trendsense.clustering.config import CLUSTERS_OUTPUT_PATH, CLUSTERS_MAP_PATH
from trendsense.data_manager import config
from trendsense.data_manager.fetch import fetch_title_embs


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


@create.command("clusters")
@click.option("-l", "--level", type=click.IntRange(1,4), default=None, help="Run clustering for a specific level only.")
@click.option("--max-level", "-mxl", type=click.IntRange(1,4), default=None, help="Run full hierarchy up to this level.")
@click.option("--output-path", "-o", type=click.Path(path_type=Path), default=None, help="Output directory.")
def create_clusters(level, max_level, output_path):
    """
    Creates clusters
    """
    if level is not None and max_level is not None:
        raise click.UsageError("Use either --level or --max-level, not both.")

    if level is None and max_level is None:
        raise click.UsageError("Either --level or --max-level must be provided.")
    
    if output_path is None:
        output_path = CLUSTERS_OUTPUT_PATH
    output_path.mkdir(parents=True, exist_ok=True)

    # clustering
    if max_level is not None:
        levels = list(range(1, max_level + 1))
    else:
        levels = [level]
    
    title_embs_df = fetch_title_embs()
    # load or initialize cluster map
    if CLUSTERS_MAP_PATH.exists():
        article_cluster_map = pd.read_parquet(CLUSTERS_MAP_PATH)
    else:
        article_cluster_map = title_embs_df[["art_id"]].copy()

    embeddings_l0 = np.vstack(title_embs_df["embedding"].to_list()).astype("float32")

    # normalize embeddings
    norms = np.linalg.norm(embeddings_l0, axis=1, keepdims=True)
    embeddings_l0 = embeddings_l0 / np.clip(norms, 1e-12, None)

    centroids_l1 = None
    centroids_l2 = None
    centroids_l3 = None

    for lvl in levels:

        if lvl == 1:

            click.echo("Running L1 clustering...")

            if "l1_cluster_id" not in article_cluster_map.columns:

                centroids_l1, _ = get_l1_clusters(
                    embeddings_l0,
                    article_cluster_map
                )

        elif lvl == 2:

            click.echo("Running L2 clustering...")

            if "l2_cluster_id" not in article_cluster_map.columns:

                centroids_l1 = np.load(output_path / "l1_centroids.npy")

                valid_l1_ids = sorted(
                    article_cluster_map["l1_cluster_id"]
                    .loc[article_cluster_map["l1_cluster_id"] != -1]
                    .unique()
                )

                centroids_l2, _ = get_l2_clusters(
                    centroids_l1,
                    valid_l1_ids,
                    article_cluster_map
                )

        elif lvl == 3:

            click.echo("Running L3 clustering...")

            if "l3_cluster_id" not in article_cluster_map.columns:

                centroids_l2 = np.load(output_path / "l2_centroids.npy")

                valid_l2_ids = sorted(
                    article_cluster_map["l2_cluster_id"]
                    .loc[article_cluster_map["l2_cluster_id"] != -1]
                    .unique()
                )

                centroids_l3, _ = get_l3_clusters(
                    centroids_l2,
                    valid_l2_ids,
                    article_cluster_map
                )

        elif lvl == 4:

            click.echo("Running L4 clustering...")

            if "l4_cluster_id" not in article_cluster_map.columns:

                centroids_l3 = np.load(output_path / "l3_centroids.npy")

                valid_l3_ids = sorted(
                    article_cluster_map["l3_cluster_id"]
                    .loc[article_cluster_map["l3_cluster_id"] != -1]
                    .unique()
                )

                get_l4_clusters(
                    centroids_l3,
                    valid_l3_ids,
                    article_cluster_map
                )

    # save updated cluster mapping
    article_cluster_map.to_parquet(
        CLUSTERS_MAP_PATH,
        index=False
    )

    click.echo("Clustering complete.")