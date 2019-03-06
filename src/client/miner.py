import hashlib

from src.blockchain.block import Block
from src.blockchain.blockchain import Blockchain


class Miner(object):

    def __init__(self, path_to_chain: str, json_format: bool = True) -> None:
        """

        Constructor for new ``Miner`` object.

        Args:
            path_to_chain (str): Path to chain for restore/ backup purposes.
            json_format (bool): Use JSON format for chain? Otherwise pickle is used.
        """

        super().__init__()

        self._blockchain = Blockchain(path_to_chain=path_to_chain, json_format=json_format)


    def proof_of_work(self, last_proof: int, difficulty: int = 5) -> int:
        """
        Simple proof of work:

            Find a number ``p`` that when hashed with the previous `block``’s solution a hash with ``difficulty`` trailing 0s is produced.

        Args:
            last_proof (int): Solution of the last blocks' proof of work
            difficulty (int): Amount of trailing 0s for a valid proof of work.

        Returns:
            int: Solution for this proof of work quiz.

        Raises:
            ValueError: Will be raised if ``difficulty`` is not a positive integer value.
        """

        if difficulty <= 0:
            raise ValueError("'difficulty' has to be a positive integer value.")

        proof = 0

        while not self.is_proof_of_work_valid(last_proof, proof, difficulty):
            proof += 1

        return proof


    def is_chain_valid(self, chain: list) -> bool:
        """

        Checks if the given ``chain`` satisfies the following rules:
            1. The first (genesis) block:
                - ``index`` = 0
                - ``previous_hash`` = None
                - ``proof`` = None

            2. each and every following block:
                - ``index``: step size 1 and monotonically increasing (1, 2, 3, 4, ...)
                - ``previous_hash``: SHA-256 of the string representation of the preceding block
                - ``proof``: has to be valid -> see: :meth:`~Miner.is_proof_of_work_valid`
                - ``timestamp``: higher than the timestamp of of preceding block

        Args:
            chain (list): list of ``Block`` objects forming a blockchain.

        Returns:
            bool: ``True`` if ``chain`` is valid, ``False`` otherwise.
        """

        previous_block = None

        for index, block in enumerate(chain):

            # rules for genesis block
            if index == 0:

                # correct genesis block?
                if block.index != 0 or block.previous_hash != None or block.proof != None:

                    # genesis block is not valid! => wrong chain
                    return False

            # rules for any other block
            else:
                previous_hash = Miner.hash(previous_block)

                # TODO: add difficulty - maybe for constructing miner object?
                if block.index != index or block.previous_hash != previous_hash or not self.is_proof_of_work_valid(previous_block.proof, block.proof) or previous_block.timestamp >= block.timestamp:

                    # block ist not valid! => wrong chain
                    return False

            previous_block = block

        return True


    @staticmethod
    def hash(block: Block) -> str:
        """

        Hash a ``Block`` object with SHA-256.

        Args:
            block (Block): Object of class ``Block`` to hash.

        Returns:
            str: Hex representation of ``block`` hash.

        Raises:
            ValueError: Will be raised if no ``Block`` object is passed.
        """

        if not isinstance(block, Block):
            raise ValueError("Only `Block` objects are hashable!")

        return hashlib.sha256(bytes(block)).hexdigest()


    @staticmethod
    def is_proof_of_work_valid(last_proof: int, proof: int, difficulty: int = 5) -> bool:
        """

        Checks if the proof of work was correct.
        The hash value of ``last_proof`` concatenated with ``proof`` has to be ``difficulty`` trailing 0s.

        Args:
            last_proof (int): Value of the ``proof`` of the preceding block.
            proof (int): ``proof`` of the actual block.
            difficulty (int): Amount of trailing 0s.

        Returns:
            bool: ``True`` if proof of work is correct, ``False`` otherwise.

        Raises:
            ValueError: Will be raised if ``difficulty`` is not a positive integer value.
        """

        if difficulty <= 0:
            raise ValueError("'difficulty' has to be a positive integer value.")

        guess = "{}{}".format(last_proof, proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        # hash ends with `difficulty` trailing 0?
        return guess_hash[-difficulty:] == "0" * difficulty


    @property
    def blockchain(self):
        return self._blockchain


    @blockchain.setter
    def blockchain(self, blockchain: Blockchain):
        self._blockchain = blockchain