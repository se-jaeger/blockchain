import logging

from time import time

from src.utils.utils import colorize
from src.blockchain.data import Data


logger = logging.getLogger(__name__)


class Block(object):

    def __init__(self, index: int, data: Data, proof: int, previous_hash: str) -> None:
        """

        Constructor for ``Block`` objects.
            Constraints:
                - ``index`` has to be int and positiv
                - ``data`` has to be a object of class ``Data``
                - ``proof`` has to be int
                - ``prevoius_hash`` has to be string and of length 64 (64 hex digits hash).

        Args:
            index (int): If of the new Block.
            data (Data): Data that is attached to this block.
            proof (int): The ``proof`` value for this block.
            previous_hash (str): Hash value of previous block in chain.

        """

        logger.debug(f"Arguments - index: {index}, data.id: {data.id if isinstance(data, Data) else None}, data.message: {data.message if isinstance(data, Data) else None}, proof: {proof}, previous_hash: {previous_hash}")

        logger.debug("Init parent Class.")
        super().__init__()

        if index == 0 and proof == None and previous_hash == None:

            logger.debug("Genesis Block -> no type checks ...")

            # Genesis Block is ok. For all others check constraints.
            pass

        else:

            logger.debug(f"Type checks: 'index' ...")

            if not isinstance(index, int) or index < 0:
                raise ValueError("Index has incorrect type or value!")

            logger.debug(f"Type checks: 'data' ...")

            if not isinstance(data, Data):
                raise ValueError("Data is not a object of class 'Data'.")

            logger.debug(f"Type checks: 'proof' ...")

            if not isinstance(proof, int):
                raise ValueError("Proof has incorrect type!")

            logger.debug(f"Type checks: 'previous_hash' ...")

            if not isinstance(previous_hash, str) or len(previous_hash) != 64:
                raise ValueError("Previous hash has incorrect type or wrong length!")

        logger.debug(f"Type checks done: all valid.")

        self._index = index
        self._timestamp = time()
        self._data = data
        self._proof = proof
        self._previous_hash = previous_hash

        logger.info("Created 'Block' object.")
        logger.debug(f"'Block' object created.")


    def __eq__(self, other: object) -> bool:
        """

        Method for comparing two ``Block`` objects.

        Args:
            other (Block): ``Block`` object to compare with ``self``.

        Returns:
            bool: ``True`` if blocks are equal. ``False`` otherwise.

        """

        if not isinstance(other, Block):
            return False

        # if all attributes are equal => block1 = block2
        return self.__dict__ == other.__dict__


    def __repr__(self) -> str:
        """

        String representation of ``Block`` object.

        Returns:
            str: String representation of ``Block`` object.

        """

        block_representation =  f"\n| {'=' * 80}\n"
        block_representation += f"| {colorize('index', 'bold')}: \t {str(self.index)} \n"
        block_representation += f"| {colorize('time', 'bold')}: \t {str(self.timestamp)} \n"
        block_representation += f"| {colorize('proof', 'bold')}: \t {str(self.proof)} \n"
        block_representation += f"| {colorize('prev. hash', 'bold')}: \t {str(self.previous_hash)} \n"
        block_representation += f"{str(self.data)}\n"
        block_representation += f"| {'=' * 80}\n"

        return block_representation


    def __bytes__(self) -> bytes:
        """

        Uses the encoded string representation of this ``Block`` object as ``bytes`` representation.

        Returns:
            bytes: ``byte`` representation of ``Block`` object.
        """
        return self.__repr__().encode("utf-8")


    @property
    def index(self) -> int:
        return self._index

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def data(self) -> Data:
        return self._data

    @property
    def proof(self) -> int:
        return self._proof

    @property
    def previous_hash(self) -> str:
        return self._previous_hash