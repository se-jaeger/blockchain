import os
import pickle
import time

import jsonpickle

from src.blockchain.block import Block
from src.utils.utils import encode_file_path_properly


class Blockchain(object):

    def __init__(self, path_to_chain: str, json_format: bool = True) -> None:
        super().__init__()

        path_to_chain = encode_file_path_properly(path_to_chain)

        # if local chain exists, load it
        if os.path.isfile(path_to_chain):
            self.chain = self.__load_chain(path_to_chain, json_format=json_format)

        else:
            # if no local chain exists, create the genesis block
            genesis_block = Block(index=0, data="This is the very first Block in this chain!", proof=100, previous_hash="no previous hash, because it is the genesis block")
            self.chain = [genesis_block]

            # make sure that chain is saved to disc
            self.__save_chain(path_to_chain, json_format=json_format)
            self.chain = self.__load_chain(path_to_chain, json_format=json_format)



    def __load_chain(self, path_to_chain: str, json_format: bool) -> list:

        path_to_chain = encode_file_path_properly(path_to_chain)

        # handle no existing chain
        if not os.path.isfile(path_to_chain):

            # TODO: error handling for no existing chain
            pass

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


    def __save_chain(self, path_to_chain: str, json_format: bool) -> None:

        path_to_chain = encode_file_path_properly(path_to_chain)

        # if chain exists, rename the old one first
        if os.path.isfile(path_to_chain):
            os.rename(path_to_chain, path_to_chain + "_" + time.strftime("%d-%m-%Y_%H:%M:%S", time.localtime()))

        else:

            # make directories if it does not exist
            if not os.path.isdir(os.path.dirname(path_to_chain)):
                os.makedirs(os.path.dirname(path_to_chain))

        # serialize chain to disc depending on serialization format
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
        return self.__chain


    @chain.setter
    def chain(self, chain):
        self.__chain = chain