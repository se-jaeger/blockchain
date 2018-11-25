import os



class Blockchain(object):

    def __init__(self, path_to_chain: str) -> None:
        super().__init__()

        # if local chain exists, load it
        if os.path.exists(os.path.expanduser(path_to_chain)):
            self.__chain = self.__load_chain(path_to_chain)

        else:
            # Create the genesis block
            pass



    def __load_chain(self, path_to_chain: str) -> list:
        pass

    def __save_chain(self, path_to_chain: str) -> None:
        pass

    def new_block(self) -> None:
        pass