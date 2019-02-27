from time import time


class Block(object):

    def __init__(self, index: int, data: object, proof: int, previous_hash: str) -> None:
        """

        Constructor for `Block` objects.

        Args:
            index: `index` of new Block.
            data: `data` that is attached to this block.
            proof: The `proof` value for this block.
            previous_hash: Hash value of previous block in chain.

        """
        super().__init__()

        self.__index = index
        self.__timestamp = time()
        self.__data = data
        self.__proof = proof
        self.__previous_hash = previous_hash


    def __eq__(self, other) -> bool:
        """

        Method for comparing two `Block` objects.

        Args:
            other: `Block` object to compare with `self`.

        Returns:
            object: `True` if blocks are equal. `False` otherwise.

        """
        # if all attributes are equal => block1 = block2
        #TODO: test for: other is no Block object..
        return self.__dict__ == other.__dict__


    def __repr__(self) -> str:
        """

        String representation of `Block` object.

        Returns:
            object: String representation of `Block` object.

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
        return self.__index

    @property
    def timestamp(self) -> float:
        return self.__timestamp

    @property
    def data(self) -> object:
        return self.__data

    @property
    def proof(self) -> int:
        return self.__proof

    @property
    def previous_hash(self) -> str:
        return self.__previous_hash