from time import time


class Block(object):

    def __init__(self, index: int, data: object, proof: int, previous_hash: str) -> None:
        """

        Constructor for ``Block`` objects.

        Args:
            index (int): If of the new Block.
            data (object): Data that is attached to this block.
            proof (int): The ``proof`` value for this block.
            previous_hash (str): Hash value of previous block in chain.

        """

        super().__init__()

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

        block_rep = "Block object with - "
        block_rep += "index: " + str(self.index)
        block_rep += "\tdata: " + str(self.data)
        block_rep += "\ttime: " + str(self.timestamp)
        block_rep += "\tproof:" + str(self.proof)
        block_rep += "\tprevious hash:" + str(self.previous_hash)

        return block_rep


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