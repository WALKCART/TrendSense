import click
from pathlib import Path
from trendsense.scraper.retrieval import load_sources, get_new
from trendsense.data_manager import config


@click.command()
@click.option(
    "--output",
    "-o",
    default=None,
    help="Optional output filename for scraped articles (CSV).",
)
def scrape(output):
    """
    Scrape new articles from configured sources and store them in a CSV buffer.
    """

    sources = load_sources()

    # default output path
    if output:
        output_path = Path(output)
    else:
        output_path = config.ARTICLES_CSV

    output_path.parent.mkdir(parents=True, exist_ok=True)

    click.echo(f"Scraping articles → {output_path}")

    get_new(
        sources=sources,
        p=str(output_path),
    )

    click.echo("Scraping completed successfully.")