import click
import signal

from src.utils.utils import *
from src.client.miner import Miner



@click.group()
def cli():
    """
    Entrypoint of CLI implementation.
    """

    pass


@cli.group()
def miner():
    """
    Gives the opportunity to use the miner implementation.
    """
    pass


@miner.command()
@click.argument("chain_path")
@click.option("--json", default=True, type=bool)
@click.option("--port", default=12345, type=int)
@click.option("--difficulty", default=5, type=int)
@click.option("--host", default= "127.0.0.1", type=str)
def start(chain_path: str, json: bool, host: str, port: int, difficulty: int):

    miner = Miner(path_to_chain=chain_path, json_format=json, host=host, port=port, difficulty=difficulty)

    try:
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        miner.start_mining()

    except ProgramKilledError:

        # TODO cleanup...
        print("Program killed: running cleanup code")

        for job in miner.jobs:
            job.stop()


@cli.command()
@click.argument("message", type=str)
@click.option("--host", default= "127.0.0.1", type=str)
@click.option("--port", default=12345, type=int)
def add(message, host, port):
    """
    Send a message to known miners.
    """

    # TODO: send given message  to local miner ...

    pass


@cli.command()
def asdf():
    miner = Miner("/Users/sjaeger/Desktop/asdf/test.chain", neighbours=[("localhost", 12345)], json_format=True, host="127.0.0.1", port=12345, difficulty=5)

    print(miner.check_for_longest_chain())
    print(miner.blockchain.chain)
