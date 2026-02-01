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
from trendsense.cli.clear import clear
from trendsense.cli.create import create

cli.add_command(scrape)
cli.add_command(upload)
cli.add_command(clear)
cli.add_command(create)

if __name__ == "__main__":
    cli()