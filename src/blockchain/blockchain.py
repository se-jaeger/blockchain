import os
import pickle
import time

import jsonpickle

from src.utils.constants import GENESIS_BLOCK
from src.utils.utils import encode_file_path_properly


class Blockchain(object):

    def __init__(self, path_to_chain: str, json_format: bool = True) -> None:
        """

        Constructor for new ``Blockchain`` object.

        Args:
            path_to_chain (str): Path to chain for restore/ backup purposes.
            json_format (bool): Use JSON format for chain? Otherwise pickle is used.

        """

        super().__init__()

        path_to_chain = encode_file_path_properly(path_to_chain)

        # if local chain exists, load it
        if os.path.isfile(path_to_chain):
            self.chain = self._load_chain(path_to_chain, json_format=json_format)

        else:
            # if no local chain exists, create the genesis block
            genesis_block = GENESIS_BLOCK
            self.chain = [genesis_block]

            # make sure that chain is saved to disc
            self._save_chain(path_to_chain, json_format=json_format)
            self.chain = self._load_chain(path_to_chain, json_format=json_format)



    def _load_chain(self, path_to_chain: str, json_format: bool) -> list:
        """

        Helper method to load chain from disk. Raises an error if no chain is found.

        Args:
            path_to_chain (str): Path to chain file.
            json_format (str): Use JSON format for chain? Otherwise ``pickle`` is used.

        Returns:
            list: Return ``list`` of ``Block`` objects.

        Raises:
            ChainNotFoundError: Will be raised if no local chain could be found.

        """

        path_to_chain = encode_file_path_properly(path_to_chain)

        # handle no existing chain
        if not os.path.isfile(path_to_chain):
            raise ChainNotFoundError("No Blockchain file (.chain) could be found!")

        # deserialize chain from disc depending on serialization format
        if json_format:
            with open(path_to_chain, mode="r") as chain_file:

                # TODO: handle errors: corrupt data, ...
                chain = jsonpickle.decode(chain_file.read())
        else:
            with open(path_to_chain, mode="rb") as chain_file:

                # TODO: handle errors: corrupt data, ...
                chain = pickle.load(chain_file)

        return chain


    def _save_chain(self, path_to_chain: str, json_format: bool) -> None:
        """

        Helper method to save chain to disk. Creates intermediate directories and backups an existing chain file if necessary.

        Args:
            path_to_chain (str): Path to chain file.
            json_format (bool): Use JSON format for chain? Otherwise pickle is used.

        """

        path_to_chain = encode_file_path_properly(path_to_chain)

        # if chain exists, first rename the old one
        if os.path.isfile(path_to_chain):
            filename, file_extension = os.path.splitext(path_to_chain)
            os.rename(path_to_chain, filename + "_" + time.strftime("%d-%m-%Y_%H:%M:%S", time.localtime()) + file_extension)

        # create intermediate directories if necessary
        elif not os.path.isdir(os.path.dirname(path_to_chain)):
            os.makedirs(os.path.dirname(path_to_chain))


        # depending on serialization format serialize chain to disc
        if json_format:
            with open(path_to_chain, "w") as chain_file:
                chain_file.write(jsonpickle.encode(self.chain))
        else:
            with open(path_to_chain, "wb") as chain_file:
                pickle.dump(self.chain, chain_file)


    def new_block(self) -> None:
        pass


    @property
    def chain(self):
        return self._chain


    @chain.setter
    def chain(self, chain):
        self._chain = chain



class ChainNotFoundError(Exception):
    """

    Error if no local chain could be found.

    """