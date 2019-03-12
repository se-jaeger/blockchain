import click
import signal
import logging
import requests
import jsonpickle

from src.utils.utils import *
from src.utils.constants import *
from src.client.miner import Miner


logger = logging.getLogger()


@click.group()
@click.option('--debug', default=False, is_flag=True)
def cli(debug):
    """
    Entrypoint of CLI implementation.
    """

    # TODO reasonable Config for logging

    if debug:
        logging.basicConfig(level=logging.DEBUG, format=LOGGING_FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)




@cli.group()
def miner():
    """
    Gives the opportunity to use the miner implementation.
    """
    pass


@cli.group()
def get():
    """
    Subcommand to get some information about the actual state.
    """
    pass


@miner.command()
@click.argument("chain_path")
@click.option("--port", default=DEFAULT_PORT, type=int)
@click.option("--host", default=DEFAULT_HOST, type=str)
@click.option("--json", default=DEFAULT_JSON, type=bool)
@click.option("--difficulty", default=DEFAULT_DIFFICULTY, type=int)
@click.option("--neighbours", default=DEFAULT_NEIGHBOURS, type=list)
def start(chain_path: str, json: bool, host: str, port: int, difficulty: int, neighbours: list):

    miner = Miner(path_to_chain=chain_path, json_format=json, host=host, port=port, difficulty=difficulty, neighbours=neighbours)

    try:
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        miner.start_mining()

    except ProgramKilledError:

        logger.error(f"Caught 'ProgramKilledError' -> Shutting down miner.")

        miner.stop_mining()


@cli.command()
@click.argument("message", type=str)
@click.option("--port", default=DEFAULT_PORT, type=int)
@click.option("--host", default=DEFAULT_HOST, type=str)
def add(message, host, port):
    """
    Send a message to known miners.
    """

    response = requests.put(create_URL(host, port, ADD_ENDPOINT), params={MESSAGE_PARAM: message})

    if response.status_code == HTTP_OK:

        json = response.json()

        click.echo(click.style(json["message"], fg="green"))

    else:
        click.echo(click.style("Something went wrong!", fg="red"))


@get.command()
@click.option("--port", default=DEFAULT_PORT, type=int)
@click.option("--host", default=DEFAULT_HOST, type=str)
def chain(host, port):
    """
    Get the actual chain.
    """

    response = requests.get(create_URL(host, port, CHAIN_ENDPOINT))

    if response.status_code == HTTP_OK:

        json = response.json()
        length = json['length']
        chain = jsonpickle.decode(json["chain"])

        click.echo(click.style(f"\nChain with length: {length}\n", fg="green"))
        click.echo(chain)

    else:
        click.echo(click.style("Something went wrong!", fg="red"))


@get.command()
@click.option("--port", default=DEFAULT_PORT, type=int)
@click.option("--host", default=DEFAULT_HOST, type=str)
def neighbours(host, port):
    """
    Get the actual neighbours
    """

    response = requests.get(create_URL(host, port, SEND_NEIGHBOURS_KEY))

    if response.status_code == HTTP_OK:

        json = response.json()
        length = json['length']
        neighbours = jsonpickle.decode(json["neighbours"])

        click.echo(click.style(f"\nActual are {length} neighbours available.\n", fg="green"))
        click.echo(neighbours)

    else:
        click.echo(click.style("Something went wrong!", fg="red"))