from datetime import timedelta

import hashlib
import requests
import jsonpickle
import multiprocessing

from src.utils.constants import *
from src.blockchain.data import Data
from src.blockchain.block import Block
from src.client.server import start_server
from src.blockchain.blockchain import Blockchain
from src.utils.utils import encode_IP_port_properly, create_proper_url_string, Job


class Miner(object):

    def __init__(self, path_to_chain: str, json_format: bool, host: str, port: int, difficulty: int, neighbours: list = []) -> None:
        """

        Constructor for new ``Miner`` object.

        Args:
            path_to_chain (str): Path to chain for restore/ backup purposes.
            json_format (bool): Use JSON format for chain? Otherwise pickle is used.
            host (str):
            port (int):
            difficulty (int): Amount of trailing 0s for proof of work
            neighbours (list): List of tuples (IP-Address, port) of known neighbours.
        """

        super().__init__()

        # TODO: type checks -> raise error..

        self._jobs = []
        self._host = host
        self._port = port
        self._neighbours = set()
        self._difficulty = difficulty
        self._not_processed_messages = set()
        self._blockchain = Blockchain(path_to_chain=path_to_chain, json_format=json_format)

        for neighbour in neighbours:

            if len(self.neighbours) <= MAX_NEIGHBOURS:
                self.neighbours.add(encode_IP_port_properly(*neighbour))



    def start_mining(self) -> None:
        """
        Starts some background ``Job``s for the Gossip Protocol, Chain syncing, Data syncing as well as the server functionalities.
        """

        print("Init async jobs ..")


        a = Job(interval=timedelta(seconds=GOSSIP_TIME_SECONDS), execute=self.update_neighbours)
        b = Job(interval=timedelta(seconds=CHAIN_SYNC_TIME_SECONDS), execute=self.check_for_longest_chain)
        c = Job(interval=timedelta(seconds=UNPROCESS_DATA_SYNC_TIME_SECONDS), execute=self.fetch_unprocessed_data)

        multiprocessing.Process(target=start_server, args=[self]).start()

        a.start()
        b.start()
        c.start()

        self.jobs.append(a)
        self.jobs.append(b)
        self.jobs.append(c)


        # TODO .
        print("Start async jobs ..")


        print("Start Mining...")

        self.mine()


    def proof_of_work(self, last_proof: int, difficulty: int) -> int:
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

                if block.index != index or block.previous_hash != previous_hash or not self.is_proof_of_work_valid(previous_block.proof, block.proof, self.difficulty) or previous_block.timestamp >= block.timestamp:

                    # block ist not valid! => wrong chain
                    return False

            previous_block = block

        return True


    def new_message(self, message: str) -> None:
        """
            Adds the new ``message`` to its local cache.

        Args:
            message (str):
        """
        data = Data(message)

        self.unprocessed_data.add(data)


    def fetch_unprocessed_data(self) -> None:
        """
            Periodical process to broadcast
        """

        print("Fetch unprocessd data ...")

        # ask all neighbours for their data queues.
        for neighbour in self.neighbours:

            response = requests.get(create_proper_url_string(neighbour, DATA_ENDPOINT))
            data_queue = jsonpickle.decode(response.json())

            self.unprocessed_data.update(data_queue)


    def is_data_unprocessed(self, data: Data) -> bool:

        # TODO: speedup with batches:
        # in: list of Data objects to check
        # out: list of Data objects to mine

        for block in self.blockchain.chain:
            if block.data == data:
                return True

        return False


    def full_chain(self) -> None:
        pass

        # TODO: maybe good idea to return pretty printed chain


    def update_neighbours(self) -> None:

        print("update neighbours ...")

        # TODO: Delete not accessible neighbours

        if len(self.neighbours) < MAX_NEIGHBOURS:

            # ask all neighbours for their neighbours.
            for neighbour in self.neighbours:

                response = requests.get(create_proper_url_string(neighbour, NEIGHBOURS_ENDPOINT))

                if response.status_code == HTTP_OK:

                    new_neighbours = jsonpickle.decode(response.json())

                    # Add unknown miner to 'neighbours', return when max amount of neighbours is reached
                    for new_neighbour in new_neighbours:

                        self.neighbours.add(new_neighbour)

                        if len(self.neighbours) >= MAX_NEIGHBOURS:
                            return


    def check_for_longest_chain(self) -> None:
        """
        Consensus Algorithm:

            Ask each ``neighbour`` for that ``neighbours``.
            Add all unknown miner to ``neighbours`` set until maximum amount of neighbours is reached.
        """

        print("Update chain ...")

        new_chain = None

        # only longest chain is of interest
        max_length = len(self.blockchain.chain)

        for neighbour in self.neighbours:

            response = requests.get(create_proper_url_string(neighbour, CHAIN_ENDPOINT))

            if response.status_code == HTTP_OK:

                length = response.json()['length']
                chain = jsonpickle.decode(response.json()['chain'])

                # chain longer and valid?
                if length > max_length and self.is_chain_valid(chain):

                    max_length = length
                    new_chain = chain

            # replace local chain with longest valid chain of all neighbours network
            if new_chain:
                self.blockchain.chain = new_chain


    def mine(self) -> None:
        """
        Blocking Mining loop.

        If  ``not_processed_messages`` are available it uses a random message an mines a new block.
        """

        while True:

            if len(self.unprocessed_data) > 0:

                data = self.unprocessed_data.pop()

                if not self.is_data_unprocessed(data):

                    last_block = self.blockchain.last_block
                    last_proof = last_block.proof
                    previous_hash = self.hash(last_block)

                    # proof of work for new block
                    proof = self.proof_of_work(last_proof, self.difficulty)

                    self.blockchain.add_new_block(data=data, proof=proof, previous_hash=previous_hash)


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
    def is_proof_of_work_valid(last_proof: int, proof: int, difficulty: int) -> bool:
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
    def blockchain(self) -> Blockchain:
        return self._blockchain


    @property
    def difficulty(self) -> int:
        return self._difficulty


    @property
    def unprocessed_data(self) -> set:
        return self._not_processed_messages


    @unprocessed_data.setter
    def unprocessed_data(self, not_processed_messages: set) -> None:
        self._not_processed_messages = not_processed_messages


    @property
    def neighbours(self) -> set:
        return self._neighbours


    @property
    def host(self) -> str:
        return self._host


    @property
    def port(self) -> int:
        return self._port


    @property
    def jobs(self) -> list:
        return self._jobs


    # @jobs.setter
    # def jobs(self, jobs: list) -> None:
    #     self._jobs = jobs