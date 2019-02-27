import click



@click.group()
def cli():
    """
        Entrypoint of CLI implementation.
    """
    pass

@cli.command()
@click.argument("chain_path")
def start(chain_path: str):
    pass


@cli.command()
def stop():
    pass
