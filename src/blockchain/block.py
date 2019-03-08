from time import time

from src.blockchain.data import Data


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

        super().__init__()

        if index == 0 and proof == None and previous_hash == None:

            # Genesis Block is ok. For all others check constraints.
            pass

        else:

            if not isinstance(index, int) or index < 0:
                raise ValueError("Index has incorrect type or value!")

            if not isinstance(data, Data):
                raise ValueError("Data is not a object of class 'Data'.")

            if not isinstance(proof, int):
                raise ValueError("Proof has incorrect type!")

            if not isinstance(previous_hash, str) or len(previous_hash) != 64:
                raise ValueError("Previous hash has incorrect type or wrong length!")


        self._index = index
        self._timestamp = time()
        self._data = data
        self._proof = proof
        self._previous_hash = previous_hash


    def __eq__(self, other) -> bool:
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

        block_rep = "Block object with - \n"
        block_rep += "\tindex:\t\t" + str(self.index) + "\n"
        block_rep += "\tdata:\t\t" + str(self.data) + "\n"
        block_rep += "\ttime:\t\t" + str(self.timestamp) + "\n"
        block_rep += "\tproof:\t\t" + str(self.proof) + "\n"
        block_rep += "\tprevious hash:\t" + str(self.previous_hash) + "\n"

        return block_rep


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
    def data(self) -> object:
        return self._data

    @property
    def proof(self) -> int:
        return self._proof

    @property
    def previous_hash(self) -> str:
        return self._previous_hash