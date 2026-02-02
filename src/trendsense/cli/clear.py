import click
from trendsense.data_manager.clear import clear_supabase_table

@click.group()
def clear():
    """
    Deletes all the records from external storage (S3, DBs, etc.)
    """
    pass

@clear.command("db-table")
@click.option("--table-name", "-tn", type = str, help = "Supabase table name")
def clear_db(table_name):
    """
    Clears all rows from a specific Supabase database table.
    """
    response = clear_supabase_table(table_name)
    if response == 0:
        click.echo(f"{table_name} successfully cleared!")
    else:
        click.echo(f"Unable to clear {table_name}")
        raise SystemExit(1)