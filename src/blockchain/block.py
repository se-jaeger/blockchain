from time import time


class Block(object):

    def __init__(self, index: int, data: object, proof: int, previous_hash: str) -> None:
        super().__init__()

        self.__index = index
        self.__timestamp = time()
        self.__data = data
        self.__proof = proof
        self.__previous_hash = previous_hash

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