import os
import pickle
import time

from src.blockchain.block import Block
from src.helpers.helpers import encode_file_path_properly


class Blockchain(object):

    def __init__(self, path_to_chain: str) -> None:
        super().__init__()

        path_to_chain = encode_file_path_properly(path_to_chain)

        # if local chain exists, load it
        if os.path.exists(path_to_chain):
            self.chain = self.__load_chain(path_to_chain)

        else:
            # if no local chain exists, create the genesis block
            genesis_block = Block(index=0, data="This is the very first Block in this chain!", proof=100, previous_hash="no previous hash, because it is the genesis block")
            self.chain = [genesis_block]

            # make sure that chain is saved to disc
            self.__save_chain(path_to_chain)
            self.chain = self.__load_chain(path_to_chain)



    def __load_chain(self, path_to_chain: str) -> list:

        #
        if not os.path.isfile(path_to_chain):

            # TODO: error handling for no existing chain
            pass

        with open(path_to_chain, mode="rb") as chain_file:
            # TODO: handle errors: corrupt data, ...
            chain = pickle.load(chain_file)

        return chain


    def __save_chain(self, path_to_chain: str) -> None:

        if os.path.isfile(path_to_chain):

            # if chain exists, rename the old one first
            os.rename(path_to_chain, path_to_chain + "_" + time.strftime("%d-%m-%Y_%H:%M:%S", time.localtime()))

        else:
            if not os.path.isdir(os.path.dirname(path_to_chain)):

                # make directories if it does not exist
                os.makedirs(path_to_chain)

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