import click
from pathlib import Path
from datetime import date, timedelta, datetime, time
from trendsense.scraper.retrieval import load_sources, get_new
from trendsense.data_manager import config


@click.command()
@click.option("--output", "-o", type = click.Path(), default=None, 
              help="Optional output filename for scraped articles (CSV)."
)
@click.option("--end-dt", "-edt", type = click.DateTime(formats=["%Y-%m-%d"]), default=None, 
              help="The END date of the search (Default: today)."
)
@click.option("--end-time", "-et", type = click.DateTime(formats=["%H:%M:%S", "%H:%M"]),
              default=None, help="The END time (HH:MM:SS). Defaults to end of day."
)
@click.option("--start-dt", "-sdt", type=click.DateTime(formats=["%Y-%m-%d"]), 
              help="An absolute START date (Overwrites lookback)."
)
@click.option("--start-time", "-st", type = click.DateTime(formats=["%H:%M:%S", "%H:%M"]), default=None,
              help="The START time (HH:MM:SS). Defaults to 00:00:00."
)
@click.option("--lookback", "-l", type = int, default=None, 
              help="How many days to look back from the END date."
)
def scrape(output, end_dt, end_time, start_dt, start_time, lookback):
    """
    Scrape new articles from configured sources and store them in a CSV buffer.
    """

    sources = load_sources()

    # output path
    if output:
        output_path = Path(output)
    else:
        output_path = config.ARTICLES_CSV

    output_path.parent.mkdir(parents=True, exist_ok=True)

    end_dt = end_dt.date() if end_dt else date.today()
    end_time = end_time.time() if end_time else time(23, 59, 59)
    end_date_time = datetime.combine(end_dt, end_time)

    if start_dt:
        start_dt = start_dt.date()
        start_time = start_time.time() if start_time else time(0, 0, 0)
        start_date_time = datetime.combine(start_dt, start_time)
    elif lookback is not None:
        start_date_time = end_date_time - timedelta(days=lookback)
    else:
        start_date_time = None  

    click.echo(f"Scraping articles → {output_path}")

    get_new(
        sources=sources,
        p=str(output_path),
        start_dt=start_date_time,
        end_dt=end_date_time
    )

    click.echo("Scraping completed successfully.")