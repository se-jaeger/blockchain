import click
import signal
import logging
import requests
import jsonpickle

from logging.handlers import RotatingFileHandler

from src.utils.utils import *
from src.utils.constants import *
from src.client.miner import Miner


logger = logging.getLogger()


@click.group()
def cli():
    """
    Entrypoint of CLI implementation.
    """

@cli.group()
def miner():
    """
    Gives the opportunity to use the miner implementation.
    """

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOGGING_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    rotating_file_handler = RotatingFileHandler(MINER_LOG_FILE, maxBytes=MINER_LOG_SIZE, backupCount=3)
    rotating_file_handler.setLevel(logging.DEBUG)
    rotating_file_handler.setFormatter(formatter)

    logger.addHandler(rotating_file_handler)
    logger.addHandler(console_handler)


@cli.group()
def get():
    """
    Subcommand to get some information about the actual state.
    """
    pass


@miner.command()
@click.argument("chain_path")
@click.option("--port", default=DEFAULT_PORT, type=int, help=PORT_HELP)
@click.option("--chain_serialization", default="json", type=click.types.Choice(["json", "pickle"]), help=CHAIN_SERIALIZATION_HELP)
@click.option("--difficulty", default=DEFAULT_DIFFICULTY, type=int, help=DIFFICULTY_HELP)
@click.option("--neighbours", default=DEFAULT_NEIGHBOURS, type=str, help=NEIGHBOURS_HELP)
def start(chain_path: str, chain_serialization: str, port: int, difficulty: int, neighbours: str):
    """
    Starts a local miner.
    """

    if chain_serialization == "json":
        json_format = True

    elif chain_serialization == "pickle":
        json_format = False

    else:
        logger.error(f"--chain_serialization should one of these: 'json' or 'pickle'")
        raise ValueError(f"--chain_serialization should one of these: 'json' or 'pickle'")

    # compile input (localhost:23456,localhost:34567)
    # into proper form (list of tuples): [("localhost", 23456), ("localhost", 34567)]
    neighbours_correct = []

    if neighbours:
        neighbours_list = neighbours.split(",")

        for neighbour_string in neighbours_list:

            host_port_list = neighbour_string.split(":")
            neighbour_tuple = (host_port_list[0], int(host_port_list[1]))

            neighbours_correct.append(neighbour_tuple)


    miner = Miner(path_to_chain=chain_path, json_format=json_format, port=port, difficulty=difficulty, neighbours=neighbours_correct)

    try:
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        miner.start_mining()

    except ProgramKilledError:

        logger.error(f"Caught 'ProgramKilledError' -> Shutting down miner.")

        miner.stop_mining()

        logger.debug("======================================== FINISHED ========================================\n\n\n")


@cli.command()
@click.argument("message", type=str)
@click.option("--port", default=DEFAULT_PORT, type=int, help=PORT_HELP)
@click.option("--host", default=DEFAULT_HOST, type=str, help=HOST_HELP)
def add(message, host, port):
    """
    Send a message to miner at 'host':'port'.
    """

    response = requests.put(create_URL(host, port, ADD_ENDPOINT), params={MESSAGE_PARAM: message})

    if response.status_code == HTTP_OK:

        json = response.json()

        click.echo(click.style(json["message"], fg="green"))

    else:
        click.echo(click.style("Something went wrong!", fg="red"))


@get.command()
@click.option("--port", default=DEFAULT_PORT, type=int, help=PORT_HELP)
@click.option("--host", default=DEFAULT_HOST, type=str, help=HOST_HELP)
def chain(host, port):
    """
    Get the actual chain from miner at 'host':'port'.
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
@click.option("--port", default=DEFAULT_PORT, type=int, help=PORT_HELP)
@click.option("--host", default=DEFAULT_HOST, type=str, help=HOST_HELP)
def neighbours(host, port):
    """
    Get the actual neighbours from miner at 'host':'port'.
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