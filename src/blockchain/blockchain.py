import os
import time
import pickle
import logging
import jsonpickle

from src.utils.constants import *
from src.blockchain.data import Data
from src.blockchain.block import Block
from src.utils.errors import ChainNotFoundError
from src.utils.utils import encode_file_path_properly


logger = logging.getLogger(__name__)


class Blockchain(object):

    def __init__(self, path_to_chain: str, json_format: bool, force_new_chain: bool) -> None:
        """

        Constructor for new ``Blockchain`` object.

        Args:
            path_to_chain (str): Path to chain for restore/ backup purposes.
            json_format (bool): Use JSON format for chain? Otherwise pickle is used.
        """

        logger.debug(f"Arguments - path_to_chain: {path_to_chain}, json_format: {json_format}")

        logger.debug("Init parent Class.")
        super().__init__()

        self._path_to_chain = encode_file_path_properly(path_to_chain)
        self._json_format = json_format

        # if local chain exists, load it
        if os.path.isfile(self.path_to_chain) and not force_new_chain:

            logger.debug(f"Load existing chain from disc ...")
            self.load_chain()
            logger.debug(f"Existing chain loaded.")

        else:
            logger.debug(f"Create new chain ...")

            # if no local chain exists, create the genesis block
            self.chain = [GENESIS_BLOCK]
            logger.debug(f"New chain created.")

        logger.info("Created 'Blockchain' object.")
        logger.debug(f"'Blockchain' object created.")


    def load_chain(self) -> None:
        """

        Helper method to load chain from disk. Raises an error if no chain is found.

        Raises:
            ChainNotFoundError: Will be raised if no local chain could be found.

        """

        logger.debug(f"Loading chain from disc ...")

        # handle no existing chain
        if not os.path.isfile(self.path_to_chain):
            raise ChainNotFoundError("No Blockchain file (.chain) could be found!")

        # deserialize chain from disc depending on serialization format
        if self.json_format:
            with open(self.path_to_chain, mode="r") as chain_file:

                logger.debug(f"Decode as JSON - json_format: {self.json_format}")

                # TODO: handle errors: corrupt data, ...
                chain = jsonpickle.decode(chain_file.read())
        else:
            with open(self.path_to_chain, mode="rb") as chain_file:

                logger.debug(f"Decode with pickle - json_format: {self.json_format}")

                # TODO: handle errors: corrupt data, ...
                chain = pickle.load(chain_file)

        logger.debug(f"Chain loaded.")
        self._chain = chain


    def save_chain(self) -> None:
        """

        Helper method to save chain to disk. Creates intermediate directories and backups an existing chain file if necessary.

        """

        logger.debug(f"Saving chain to disc ...")

        # if chain exists, first rename the old one
        if os.path.isfile(self.path_to_chain):

            logger.debug(f"Rename existing chain file.")

            filename, file_extension = os.path.splitext(self.path_to_chain)
            os.rename(self.path_to_chain, filename + "_" + time.strftime("%d-%m-%Y_%H:%M:%S", time.localtime()) + file_extension)

        # create intermediate directories if necessary
        elif not os.path.isdir(os.path.dirname(self.path_to_chain)):

            logger.debug(f"Create intermediate directories.")
            os.makedirs(os.path.dirname(self.path_to_chain))

        hash_file_path = f"{os.path.splitext(self.path_to_chain)[0]}.hash"

        # depending on serialization format serialize chain to disc
        if self.json_format:

            logger.debug(f"Encode as JSON - json_format: {self.json_format}")
            encoded_chain = jsonpickle.encode(self.chain)

            logger.debug(f"Hashing encoded_chain.")
            encoded_chain_hash = hashlib.sha256(encoded_chain.encode()).hexdigest()

            with open(self.path_to_chain, "w") as chain_file:

                logger.debug("Write chain file to disc.")
                chain_file.write(encoded_chain)

            with open(hash_file_path, "w") as chain_hash_file:

                logger.debug("Write chain hash file to disc.")
                chain_hash_file.write(encoded_chain_hash)
        else:

            logger.debug(f"Encode with pickle - json_format: {self.json_format}")
            encoded_chain = pickle.dumps(self.chain)

            logger.debug(f"Hashing encoded_chain.")
            encoded_chain_hash = hashlib.sha256(encoded_chain).hexdigest()

            with open(self.path_to_chain, "wb") as chain_file:

                logger.debug("Write chain file to disc.")
                chain_file.write(encoded_chain)

            with open(hash_file_path, "w") as chain_hash_file:

                logger.debug("Write chain hash file to disc.")
                chain_hash_file.write(encoded_chain_hash)

        logger.debug(f"Chain saved.")


    def add_new_block(self, data: Data, proof: int, previous_hash: str) -> Block:
        """

        Adds a new Block to the existing chain.

        Args:
            data (Data): Data that is attached to this block.
            proof (int): The ``proof`` value for this block.
            previous_hash (str): Hash value of previous block in chain.
        """

        logger.debug(f"Create and add new block ... - data.id: '{data.id}', data.message: '{data.message}', proof: '{proof}'', previous_hash: '{previous_hash}'")

        block = Block(index=len(self.chain), data=data, proof=proof, previous_hash=previous_hash)
        self.chain.append(block)

        logger.debug(f"New block added. - block.index: '{block.index}', block.proof: '{block.proof}', block.previous_hash: '{block.previous_hash}', block.timestamp: '{block.timestamp}', block.data.id: '{block.data.id}', block.data.message: '{block.data.message}'")

        return block


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
        self.save_chain()