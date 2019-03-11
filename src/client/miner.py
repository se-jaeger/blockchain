import hashlib
import requests
import jsonpickle

from datetime import timedelta
from multiprocessing import Process, Queue

from src.utils.constants import *
from src.blockchain.data import Data
from src.blockchain.block import Block
from src.client.server import start_server
from src.utils.errors import ChainNotValidError
from src.blockchain.blockchain import Blockchain
from src.utils.utils import encode_IP_port_properly, create_proper_url_string, Job


class Miner(object):

    def __init__(self, path_to_chain: str, json_format: bool, host: str, port: int, difficulty: int, neighbours: list = []) -> None:
        """

        Constructor for new ``Miner`` object.

        Args:
            path_to_chain (str): Path to chain for restore/ backup purposes.
            json_format (bool): Use JSON format for chain? Otherwise pickle is used.
            host (str): IPv4-Address or ``localhost`` of neighbour.
            port (int): Port of neighbour.
            difficulty (int): Amount of trailing 0s for proof of work
            neighbours (list): List of tuples (IP-Address, port) of known neighbours.
        """

        super().__init__()

        if not isinstance(path_to_chain, str):
            raise ValueError("'path_to_chain' has to be of type string!")

        if not isinstance(json_format, bool):
            raise ValueError("'json_format' has to be a boolean value!")


        if not isinstance(host, str):
            raise ValueError("'host' has to be of type string!")

        try:
            encode_IP_port_properly(host, 12345)

        except:
            raise ValueError("'host' is not a valid host string!")


        if not (isinstance(port, int) and not isinstance(port, bool)) or port < 1 or port > 65535:
            raise ValueError("'port' is of wrong type or out of range!")

        if not (isinstance(difficulty, int) and not isinstance(difficulty, bool)) or difficulty < 1:
            raise ValueError("'difficulty' is of wrong type or lower than 1!")


        if not isinstance(neighbours, list):
            raise ValueError("'neighbours' has to be of type list!")

        for index, neighbour in enumerate(neighbours):

            if not isinstance(neighbour, tuple):
                raise ValueError("Elements of 'neighbours' has to be of type tuple!")

            if not isinstance(neighbour[0], str):
                raise ValueError(f"'host' of element at index: {index} of 'neighbours' has to be of type string!")

            try:
                encode_IP_port_properly(neighbour[0], 12345)

            except:
                raise ValueError(f"'host' of element at index: {index} of 'neighbours' is not a valid host string!")

            if not isinstance(neighbour[1], int) or neighbour[1] < 1 or neighbour[1] > 65535:
                raise ValueError(f"'port' of element at index: {index} of 'neighbours' is of wrong type or out of range!")

        self._jobs = []
        self._host = host
        self._port = port
        self._queue = None
        self._neighbours = set()
        self._server_process = None
        self._difficulty = difficulty
        self._not_processed_messages = set()
        self._blockchain = Blockchain(path_to_chain=path_to_chain, json_format=json_format)

        # check if chain is valid
        if not self.is_chain_valid(self.blockchain.chain):

            #TODO: test
            raise ChainNotValidError("Local chain is not valid!")

        for neighbour in neighbours:

            if len(self.neighbours) <= MAX_NEIGHBOURS:
                self.neighbours.add(encode_IP_port_properly(*neighbour))



    def start_mining(self) -> None:
        """
        Starts some background ``Job`` s for the Gossip Protocol, Chain syncing, Data syncing, communication thread as well as the server functionalities as process.
        """

        print("Init async jobs ..")

        update_neighbour_job = Job(interval=timedelta(seconds=GOSSIP_TIME_SECONDS), execute=self.update_neighbours)
        check_for_longest_chain_job = Job(interval=timedelta(seconds=CHAIN_SYNC_TIME_SECONDS), execute=self.check_for_longest_chain)
        fetch_unprocessed_data_job = Job(interval=timedelta(seconds=UNPROCESS_DATA_SYNC_TIME_SECONDS), execute=self.fetch_unprocessed_data)
        communicate_job = Job(interval=timedelta(seconds=0), execute=self.communicate)

        self.queue = Queue()
        self.server_process = Process(target=start_server, args=[self.queue])

        update_neighbour_job.start()
        check_for_longest_chain_job.start()
        fetch_unprocessed_data_job.start()
        communicate_job.start()
        self.server_process.start()

        self.jobs.append(update_neighbour_job)
        self.jobs.append(check_for_longest_chain_job)
        self.jobs.append(fetch_unprocessed_data_job)
        self.jobs.append(communicate_job)

        self.mine()


    def stop_mining(self) -> None:
        """
        Function that gets called when Python was killed. Takes care to shutting down all threads/process and saves the chain to disc.
        """

        print("Start Cleanup!")

        for job in self.jobs:
            job.stop()

        self.server_process.terminate()
        self.server_process.join()

        self.blockchain._save_chain()

        print("Cleanup Done!")


    def communicate(self) -> None:
        """
        Periodical thread to communicate with server process.
        """

        if not self._queue.empty():

            message = self._queue.get_nowait()

            if ADD_KEY in message:

                self.new_message(message[ADD_KEY])

            if SEND_CHAIN_KEY in message:

                message[SEND_CHAIN_KEY].send({
                    'chain': jsonpickle.encode(self.blockchain.chain),
                    'length': len(self.blockchain.chain),
                })

            if SEND_NEIGHBOURS_KEY in message:

                message[SEND_NEIGHBOURS_KEY].send(jsonpickle.encode(self.neighbours))

            if SEND_DATA_KEY in message:

                message[SEND_DATA_KEY].send(jsonpickle.encode(self.unprocessed_data))


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

        print("Data added!")


    def fetch_unprocessed_data(self) -> None:
        """
            Periodical thread to get unprocessed data form neighbours.
            => Broadcasts unprocessed data around the network.
        """

        #print("Fetch unprocessd data ...")

        print(self.unprocessed_data)

        # ask all neighbours for their data queues.
        for neighbour in self.neighbours:

            response = requests.get(create_proper_url_string(neighbour, DATA_ENDPOINT))

            if response.status_code == HTTP_OK:

                data_queue = jsonpickle.decode(response.json())
                self.unprocessed_data.update(data_queue)

            # TODO: else fo HTTP code..


    def is_data_unprocessed(self, data: Data) -> bool:
        """
        Checks if ``data`` is already in local chain.

        Args:
            data (Data): ``Data`` object to check if it exists in the actual chain.

        Returns:
            bool: ``True`` if unprocessed.
        """

        # TODO: speedup with batches:
        # in: list of Data objects to check
        # out: list of Data objects to mine

        for block in self.blockchain.chain:
            if block.data == data:
                return True

        return False


    def update_neighbours(self) -> None:
        """
        Periodical thread to update neighbours if limit is not exceeded.
        """

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

                #TODO: else fo HTTP code..


    def check_for_longest_chain(self) -> None:
        """
        Consensus Algorithm:

            Ask each ``neighbour`` for that ``neighbours``.
            Add all unknown miner to ``neighbours`` set until maximum amount of neighbours is reached.
        """

        #print("Update chain ...")

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

            # TODO: else fo HTTP code..

            # replace local chain with longest valid chain of all neighbours network
            if new_chain:
                self.blockchain.chain = new_chain


    def mine(self) -> None:
        """
        Blocking Mining loop.

        If  ``not_processed_messages`` are available it uses a random message an mines a new block.
        """

        print("start mining")

        while True:

            if len(self.unprocessed_data) > 0:

                print("daten da")
                data = self.unprocessed_data.pop()

                if not self.is_data_unprocessed(data):

                    last_block = self.blockchain.last_block
                    last_proof = last_block.proof
                    previous_hash = self.hash(last_block)

                    # proof of work for new block
                    print("PoW ...")
                    proof = self.proof_of_work(last_proof, self.difficulty)
                    print("PoW - fertig!")
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


    @property
    def server_process(self) -> Process:
        return self._server_process


    @server_process.setter
    def server_process(self, server_process: Process) -> None:
        self._server_process = server_process


    @property
    def queue(self) -> Process:
        return self._queue


    @queue.setter
    def queue(self, queue: Queue) -> None:
        self._queue = queue