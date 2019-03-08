import os
import time
import pickle
import jsonpickle

from src.blockchain.data import Data
from src.blockchain.block import Block
from src.utils.constants import GENESIS_BLOCK
from src.utils.utils import encode_file_path_properly


class Blockchain(object):

    def __init__(self, path_to_chain: str, json_format: bool) -> None:
        """

        Constructor for new ``Blockchain`` object.

        Args:
            path_to_chain (str): Path to chain for restore/ backup purposes.
            json_format (bool): Use JSON format for chain? Otherwise pickle is used.
        """

        super().__init__()

        self._path_to_chain = encode_file_path_properly(path_to_chain)
        self._json_format = json_format

        # if local chain exists, load it
        if os.path.isfile(self.path_to_chain):
            self.chain = self._load_chain()

        else:
            # if no local chain exists, create the genesis block
            self.chain = [GENESIS_BLOCK]

            # make sure that chain is saved to disc
            self._save_chain()
            self.chain = self._load_chain()


    def _load_chain(self) -> list:
        """

        Helper method to load chain from disk. Raises an error if no chain is found.

        Returns:
            list: Return ``list`` of ``Block`` objects.

        Raises:
            ChainNotFoundError: Will be raised if no local chain could be found.

        """

        path_to_chain = encode_file_path_properly(self.path_to_chain)

        # handle no existing chain
        if not os.path.isfile(path_to_chain):
            raise ChainNotFoundError("No Blockchain file (.chain) could be found!")

        # deserialize chain from disc depending on serialization format
        if self.json_format:
            with open(path_to_chain, mode="r") as chain_file:

                # TODO: handle errors: corrupt data, ...
                chain = jsonpickle.decode(chain_file.read())
        else:
            with open(path_to_chain, mode="rb") as chain_file:

                # TODO: handle errors: corrupt data, ...
                chain = pickle.load(chain_file)

        return chain


    def _save_chain(self) -> None:
        """

        Helper method to save chain to disk. Creates intermediate directories and backups an existing chain file if necessary.

        """

        path_to_chain = encode_file_path_properly(self.path_to_chain)

        # if chain exists, first rename the old one
        if os.path.isfile(path_to_chain):
            filename, file_extension = os.path.splitext(path_to_chain)
            os.rename(path_to_chain, filename + "_" + time.strftime("%d-%m-%Y_%H:%M:%S", time.localtime()) + file_extension)

        # create intermediate directories if necessary
        elif not os.path.isdir(os.path.dirname(path_to_chain)):
            os.makedirs(os.path.dirname(path_to_chain))

        # depending on serialization format serialize chain to disc
        if self.json_format:
            with open(path_to_chain, "w") as chain_file:
                chain_file.write(jsonpickle.encode(self.chain))
        else:
            with open(path_to_chain, "wb") as chain_file:
                pickle.dump(self.chain, chain_file)


    def add_new_block(self, data: Data, proof: int, previous_hash: str) -> None:
        """

        Adds a new Block to the existing chain.

        Args:
            data (Data): Data that is attached to this block.
            proof (int): The ``proof`` value for this block.
            previous_hash (str): Hash value of previous block in chain.
        """

        block = Block(index=len(self.chain), data=data, proof=proof, previous_hash=previous_hash)
        self.chain.append(block)

        #TODO: good idea? -> hack to save actual chain..
        self._save_chain()


    def __repr__(self) -> str:
        # TODO: print blockckain
        pass


    @property
    def last_block(self) -> Block:
        return self.chain[-1]


    @property
    def path_to_chain(self) -> str:
        return self._path_to_chain


    @property
    def json_format(self) -> bool:
        return self._json_format


    @property
    def chain(self) -> list:
        return self._chain


    @chain.setter
    def chain(self, chain: list) -> None:
        self._chain = chain



class ChainNotFoundError(Exception):
    """

    Error if no local chain could be found.

    """