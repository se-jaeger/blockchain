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

        Args:
            last_proof (int):
            proof (int):
            difficulty (int):

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