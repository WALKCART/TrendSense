import click

@click.group()
@click.pass_context
def cli(ctx):
    """
    Trense — News scraping, clustering, and trend analysis CLI
    """
    ctx.ensure_object(dict)


# import commands
from trendsense.cli.scrape import scrape
from trendsense.cli.upload import upload

cli.add_command(scrape)
cli.add_command(upload)

if __name__ == "__main__":
    cli()