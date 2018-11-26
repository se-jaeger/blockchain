from time import time


class Block(object):

    def __init__(self, index: int, data: object, proof: int, previous_hash: str) -> None:
        super().__init__()

        self.__index = index
        self.__timestamp = time()
        self.__data = data
        self.__proof = proof
        self.__previous_hash = previous_hash


    def __eq__(self, other):

        # if all attributes are equal -> block1 = block2
        return self.__dict__ == other.__dict__


    def __repr__(self):

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