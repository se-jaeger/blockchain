import hashlib

from src.blockchain.block import Block
from src.blockchain.blockchain import Blockchain



class Miner(object):

    def __init__(self, path_to_chain: str, json_format: bool = True) -> None:
        """

        Constructor for new ``Miner`` object.

        Args:
            path_to_chain (str): Path to chain for restore/ backup purposes.
            json_format (bool): Use JSON format for chain? Otherwise pickle is used.
        """

        super().__init__()

        self._blockchain = Blockchain(path_to_chain=path_to_chain, json_format=json_format)


    @staticmethod
    def hash(block: Block) -> str:
        """

        Hash a ``Block`` object with SHA-256.

        Args:
            block (Block):

        Returns:
            str: Hex representation of ``block`` hash.
        """

        if not isinstance(block, Block):
            raise ValueError("Only `Block` objects are hashable!")

        return hashlib.sha256(bytes(block)).hexdigest()


    @property
    def blockchain(self):
        return self._blockchain


    @blockchain.setter
    def blockchain(self, blockchain: Blockchain):
        self._blockchain = blockchain