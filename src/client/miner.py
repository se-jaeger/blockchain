from src.blockchain.block import Block


class Miner(object):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def hash(block: Block) -> str:
        pass