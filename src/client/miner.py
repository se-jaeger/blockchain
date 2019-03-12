import os
import hashlib
import logging
import pickle

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
from src.utils.utils import encode_IP_port_properly, create_proper_url_string, Job, encode_file_path_properly


logger = logging.getLogger(__name__)


class Miner(object):

    def __init__(self, path_to_chain: str, json_format: bool, port: int, difficulty: int, neighbours: list = []) -> None:
        """

        Constructor for new ``Miner`` object.

        Args:
            path_to_chain (str): Path to chain for restore/ backup purposes.
            json_format (bool): Use JSON format for chain? Otherwise pickle is used.
            port (int): Port of neighbour.
            difficulty (int): Amount of trailing 0s for proof of work
            neighbours (list): List of tuples (IP-Address, port) of known neighbours.
        """

        logger.info("Create 'Miner' object ...")
        logger.debug(f"Arguments - path_to_chain: {path_to_chain}, json_format: {json_format}, port: {port}, difficulty: {difficulty}, neighbours: {neighbours}")

        logger.debug("Init parent Class.")
        super().__init__()

        logger.debug(f"Type checks: 'path_to_chain' ...")

        if not isinstance(path_to_chain, str):
            raise ValueError("'path_to_chain' has to be of type string!")

        logger.debug(f"Type checks: 'json_format' ...")

        if not isinstance(json_format, bool):
            raise ValueError("'json_format' has to be a boolean value!")


        logger.debug(f"Type checks: 'port' ...")

        if not (isinstance(port, int) and not isinstance(port, bool)) or port < 1 or port > 65535:
            raise ValueError("'port' is of wrong type or out of range!")

        logger.debug(f"Type checks: 'difficulty' ...")

        if not (isinstance(difficulty, int) and not isinstance(difficulty, bool)) or difficulty < 1:
            raise ValueError("'difficulty' is of wrong type or lower than 1!")


        logger.debug(f"Type checks: 'neighbours' ...")

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

        logger.debug(f"Type checks done: all valid.")

        self._jobs = []
        self._port = port
        self._queue = None
        self._neighbours = set()
        self._server_process = None
        self._difficulty = difficulty
        self._not_processed_messages = set()
        self._blockchain = Blockchain(path_to_chain=encode_file_path_properly(path_to_chain), json_format=json_format)

        logger.debug(f"Check chain ...")

        # check if chain is valid
        if not self.is_chain_valid():

            #TODO: test
            print(self.blockchain.chain)
            raise ChainNotValidError("Local chain is not valid!")

        logger.debug(f"Check chain: valid.")
        logger.debug(f"Create neighbours: ...")

        self_encoded = encode_IP_port_properly("localhost", self.port)

        for neighbour in neighbours:

            if len(self.neighbours) < MAX_NEIGHBOURS:

                neighbour_encoded = encode_IP_port_properly(*neighbour)

                # Do not add own address
                if self_encoded != neighbour_encoded:
                    self.neighbours.add(neighbour_encoded)

        logger.info("Created 'Miner' object.")
        logger.debug(f"'Miner' object created.")



    def start_mining(self) -> None:
        """
        Starts some background ``Job`` s for the Gossip Protocol, Chain syncing, Data syncing, communication thread as well as the server functionalities as process.
        Starts the blocking function ``mine()``.
        """

        logger.info("Configure and start 'Miner' background tasks ...")

        update_neighbour_job = ("Gossip Job", Job(interval=timedelta(seconds=GOSSIP_TIME_SECONDS), execute=self.update_neighbours))
        logger.debug(f"Background thread configured: '{update_neighbour_job[0]}' - interval: {GOSSIP_TIME_SECONDS} seconds.")

        check_for_longest_chain_job = ("Sync Chain Job", Job(interval=timedelta(seconds=CHAIN_SYNC_TIME_SECONDS), execute=self.check_for_longest_chain))
        logger.debug(f"Background thread configured: '{check_for_longest_chain_job[0]}' - interval: {CHAIN_SYNC_TIME_SECONDS} seconds.")

        fetch_unprocessed_data_job = ("Sync Unprocessed Data Job)", Job(interval=timedelta(seconds=UNPROCESSED_DATA_SYNC_TIME_SECONDS), execute=self.fetch_unprocessed_data))
        logger.debug(f"Background thread configured: '{fetch_unprocessed_data_job[0]}' - interval: {UNPROCESSED_DATA_SYNC_TIME_SECONDS} seconds.")

        backup_local_chain_job = ("Backup Local Chain Job", Job(interval=timedelta(seconds=BACKUP_LOCAL_CHAIN_TIME_SECONDS), execute=self.backup_local_chain))
        logger.debug(f"Background thread configured: '{backup_local_chain_job[0]}' - interval: {BACKUP_LOCAL_CHAIN_TIME_SECONDS} seconds.")

        communicate_job = ("Communication Job", Job(interval=timedelta(seconds=0), execute=self.communicate))
        logger.debug(f"Background thread configured: '{communicate_job[0]}'.")

        self._queue = Queue()
        self._server_process = Process(target=start_server, args=[self.queue, self.port])
        logger.debug(f"'Server Process' configured.")

        logger.debug("Start 'Miner' background threads ...")

        update_neighbour_job[1].start()
        logger.debug(f"'{update_neighbour_job[0]}' thread started.")

        check_for_longest_chain_job[1].start()
        logger.debug(f"'{check_for_longest_chain_job[0]}' thread started.")

        fetch_unprocessed_data_job[1].start()
        logger.debug(f"'{fetch_unprocessed_data_job[0]}' thread started.")

        backup_local_chain_job[1].start()
        logger.debug(f"'{backup_local_chain_job[0]}' thread started.")

        communicate_job[1].start()
        logger.debug(f"'{communicate_job[0]}' thread started.")

        self.server_process.start()
        logger.debug(f"'Server Process' started.")

        logger.info("All 'Miner' background tasks started.")

        self.jobs.append(update_neighbour_job)
        self.jobs.append(backup_local_chain_job)
        self.jobs.append(fetch_unprocessed_data_job)
        self.jobs.append(check_for_longest_chain_job)
        self.jobs.append(communicate_job)

        logger.debug("Start mining ...")
        self.mine()


    def stop_mining(self) -> None:
        """
        Function that gets called when Python was killed. Takes care to shutting down all threads/process and saves the chain to disc.
        """

        logger.info("Start shutting down routine.")

        for job_name, job in self.jobs:

            logger.debug(f"Shutting down '{job_name}' ...")
            job.stop()
            logger.debug(f"'{job_name}' Stopped.")

        logger.debug(f"Shutting down 'Server Process' ...")
        self.server_process.terminate()
        self.server_process.join()
        logger.debug(f"'Server Process' Stopped.")

        logger.debug(f"Saving local chain ...")
        self.blockchain.save_chain()
        logger.debug(f"Chain saved.")

        logger.info("Shutting down routine done.")


    def communicate(self) -> None:
        """
        Periodical thread to communicate with server process.
        """

        if not self._queue.empty():

            message = self._queue.get_nowait()
            logger.debug(f"Processing message: '{message[0]}'' ...")

            if ADD_KEY == message[0]:

                logger.debug(f"Found handle for message with key: '{ADD_KEY}'")
                self.new_message(message[1])

            elif SEND_CHAIN_KEY == message[0]:

                logger.debug(f"Found handle for message with key: '{SEND_CHAIN_KEY}'")
                message[1].send({
                    "chain": jsonpickle.encode(self.blockchain.chain),
                    "length": len(self.blockchain.chain),
                })

            elif SEND_NEIGHBOURS_KEY == message[0]:

                logger.debug(f"Found handle for message with key: '{SEND_NEIGHBOURS_KEY}'")
                message[1].send({
                    "neighbours": jsonpickle.encode(self.neighbours),
                    "length": len(self.neighbours),
                })

            elif SEND_DATA_KEY == message[0]:

                logger.debug(f"Found handle for message with key: '{SEND_DATA_KEY}'")
                message[1].send(jsonpickle.encode(self.unprocessed_data))

            else:
                logger.warning(f"Could not find handle for message: '{message[0]}'")


    def proof_of_work(self, last_proof: int, difficulty: int) -> int:
        """
        Simple proof of work:

            Find a number ``p`` that when hashed with the previous ``block``’s solution a hash with ``difficulty`` trailing 0s is produced.

        Args:
            last_proof (int): Solution of the last blocks' proof of work
            difficulty (int): Amount of trailing 0s for a valid proof of work.

        Returns:
            int: Solution for this proof of work quiz.

        Raises:
            ValueError: Will be raised if ``difficulty`` is not a positive integer value.
        """

        logger.debug(f"Do Proof of Work. - last_proof: {last_proof}, difficulty: {difficulty}.")

        if difficulty <= 0:
            raise ValueError("'difficulty' has to be a positive integer value.")

        proof = 0

        while not self.is_proof_of_work_valid(last_proof, proof, difficulty):
            proof += 1

        logger.debug(f"Found Proof of Work - last_proof: {last_proof}, difficulty: {difficulty}.")
        logger.info(f"Found a valid Proof of Work.")

        return proof


    def is_chain_valid(self) -> bool:
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

        Returns:
            bool: ``True`` if ``chain`` is valid, ``False`` otherwise.
        """

        logger.debug(f"Check if chain is valid.")

        previous_block = None

        for index, block in enumerate(self.blockchain.chain):

            # rules for genesis block
            if index == 0:

                # correct genesis block?
                if block.index != 0 or block.previous_hash != None or block.proof != None:

                    logger.debug(f"Genesis Block is not valid: -> What is wrong? index: {block.index != 0}, previous_hash: {block.previous_hash != None}, proof: {block.proof != None}.")

                    # genesis block is not valid! => wrong chain
                    return False

            # rules for any other block
            else:
                previous_hash = Miner.hash(previous_block)

                if block.index != index or block.previous_hash != previous_hash or not self.is_proof_of_work_valid(previous_block.proof, block.proof, self.difficulty) or previous_block.timestamp >= block.timestamp:

                    logger.debug(f"Block with index: {block.index} ist not valid: -> What is wrong? index: {block.index != index}, previous_hash: {block.previous_hash != previous_hash}, PoW valid: {self.is_proof_of_work_valid(previous_block.proof, block.proof, self.difficulty)}, timestamp: {previous_block.timestamp >= block.timestamp}.")

                    # block ist not valid! => wrong chain
                    return False

            previous_block = block

        logger.debug(f"Chain is valid.")
        return True


    def new_message(self, message: str) -> None:
        """
            Adds the new ``message`` to its local cache.

        Args:
            message (str):
        """

        logger.debug(f"Create new unprocessed Data ... - message: '{message}' ...")

        data = Data(message)
        self.unprocessed_data.add(data)

        logger.debug(f"New unprocessed Data created. - message: '{data.message}', id: '{data.id}'")
        logger.info(f"New message added. - message: '{data.message}', id: '{data.id}'")


    def backup_local_chain(self) -> None:
        """
        Periodical thread to backup the local chain to disc.
        """

        logger.debug(f"Backup local chain ... - json_format: {self.blockchain.json_format}")
        hash_file_path = f"{os.path.splitext(self.blockchain.path_to_chain)[0]}.hash"


        def _do_backup(hash_file_path: str, encoded_chain_hash: str):
            """
            Helper function that does the actual backup steps.

            Args:
                hash_file_path (str): String that describes the path to the hash file.
                encoded_chain_hash (str): Hash value of the actual local chain.
            """

            if not os.path.isfile(hash_file_path):

                # if no hash file exists -> create one with actual hash value
                with open(hash_file_path, "w") as hash_file:

                    logger.debug(f"No existing hash file. Write actual hash value.")
                    hash_file.write(encoded_chain_hash)

                    logger.info(f"Backed up chain -> Missing hash file (fixed)")

            else:

                # All as expected: check hash and backup if necessary
                with(open(hash_file_path, "r")) as chain_hash_file:
                    saved_chain_hash = chain_hash_file.read()

                if saved_chain_hash != encoded_chain_hash:

                    logger.debug(f"Hash of chain on disc differ from local chain hash.")
                    logger.debug(f"Backup Chain.")
                    self.blockchain.save_chain()

                    logger.debug(f"Save new hash file.")
                    with(open(hash_file_path, "w")) as chain_hash_file:
                        chain_hash_file.write(encoded_chain_hash)

                    logger.info(f"Backed up chain -> Chain saved.")

                else:
                    logger.info(f"Backed up chain -> No backup needed.")


        if self.blockchain.json_format:

            logger.debug(f"Encode to JSON")
            encoded_chain = jsonpickle.encode(self.blockchain.chain)
            encoded_chain_hash = hashlib.sha256(encoded_chain.encode()).hexdigest()

            _do_backup(hash_file_path, encoded_chain_hash)

        else:
            logger.debug(f"Encode with pickle")
            encoded_chain = pickle.dumps(self.blockchain.chain)
            encoded_chain_hash = hashlib.sha256(encoded_chain).hexdigest()

            _do_backup(hash_file_path, encoded_chain_hash)


    def fetch_unprocessed_data(self) -> None:
        """
            Periodical thread to get unprocessed data form neighbours.
            => Broadcasts unprocessed data around the network.
        """

        logger.debug(f"Syncing unprocessed data ... - neighbours: '{self.neighbours}'")

        old_data = self.unprocessed_data

        # ask all neighbours for their data queues.
        for neighbour in self.neighbours:

            logger.debug(f"Fetch data of neighbour: '{neighbour}'")
            response = requests.get(create_proper_url_string(neighbour, DATA_ENDPOINT))

            if response.status_code == HTTP_OK:

                logger.debug(f"Get data of neighbour: '{neighbour}'")
                data_queue = jsonpickle.decode(response.json())
                self.unprocessed_data.update(data_queue)
                logger.debug(f"Data of neighbour: '{neighbour}' added.")

            else:
                logger.warning(f"Response of neighbour: '{neighbour}' has bad status_code: '{response.status_code}'")

        if old_data == self.unprocessed_data:
            logger.info(f"Synced unprocessed data -> No new data.")
        else:
            logger.info(f"Synced unprocessed data -> New data.")

        logger.debug(f"Syncing unprocessed data done.")


    def is_data_processed(self, data: Data) -> bool:
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

        logger.debug(f"Check if data is not processed ... - data.id: '{data.id}', data.message: '{data.message}'")

        for block in self.blockchain.chain:
            if block.data == data:

                logger.debug(f"Data is not processed: - data.id: '{data.id}', data.message: '{data.message}'")
                return True

        logger.debug(f"Data is already processed: - data.id: '{data.id}', data.message: '{data.message}'")
        return False


    def update_neighbours(self) -> None:
        """
        Periodical thread to update neighbours if limit is not exceeded.
        """

        logger.debug(f"Update neighbours ... - neighbours: '{self.neighbours}'")

        length_old_neighbours = len(self.neighbours)

        # TODO: Delete not accessible neighbours

        if len(self.neighbours) < MAX_NEIGHBOURS:

            logger.debug(f"Maximum amount of neighbours not exceeded. -> update ...")

            self_encoded = encode_IP_port_properly("localhost", self.port)

            # ask all neighbours for their neighbours.
            for neighbour in self.neighbours:

                logger.debug(f"Fetch neighbours of neighbour: '{neighbour}'")
                response = requests.get(create_proper_url_string(neighbour, NEIGHBOURS_ENDPOINT))

                if response.status_code == HTTP_OK:

                    logger.debug(f"Get neighbours of neighbour: '{neighbour}'")
                    new_neighbours = jsonpickle.decode(response.json()["neighbours"])

                    # Add unknown miner to 'neighbours', return when max amount of neighbours is reached
                    for new_neighbour in new_neighbours:

                        neighbour_encoded = encode_IP_port_properly(*new_neighbour)

                        # Do not add own address
                        if self_encoded != neighbour_encoded:
                            logger.debug(f"Add unknown neighbour '{neighbour}' to neighbours.")
                            self.neighbours.add(neighbour_encoded)

                        if len(self.neighbours) >= MAX_NEIGHBOURS:

                            logger.debug(f"Maximum amount of neighbours exceeded -> Stop syncing")
                            logger.info(f"Updated neighbours -> New neighbours added.")
                            return

                else:
                    logger.warning(f"Response of neighbour: '{neighbour}' has bad status_code: '{response.status_code}'")

        if length_old_neighbours < len(self.neighbours):
            logger.info(f"Updated neighbours -> New neighbours added.")
        else:
            logger.info(f"Updated neighbours -> No new neighbours available.")

        logger.debug(f"Update neighbours done.")


    def check_for_longest_chain(self) -> None:
        """
        Consensus Algorithm:

            Ask each ``neighbour`` for that ``neighbours``.
            Add all unknown miner to ``neighbours`` set until maximum amount of neighbours is reached.
        """

        logger.debug(f"Syncing chain ... - neighbours: '{self.neighbours}'")

        new_chain = None
        old_chain = self.blockchain.chain

        # only longest chain is of interest
        max_length = len(self.blockchain.chain)

        for neighbour in self.neighbours:

            logger.debug(f"Fetch chain of neighbour: '{neighbour}'")
            response = requests.get(create_proper_url_string(neighbour, CHAIN_ENDPOINT))

            if response.status_code == HTTP_OK:

                logger.debug(f"Get chain of neighbour: '{neighbour}'")
                length = response.json()['length']
                chain = jsonpickle.decode(response.json()['chain'])

                # chain longer and valid?
                if length > max_length and self.is_chain_valid():

                    logger.debug(f"New chain is longer. - neighbour: '{neighbour}', length of old chain: '{max_length}'', length of chain: '{length}'")
                    max_length = length
                    new_chain = chain

            else:
                logger.warning(f"Response of neighbour: '{neighbour}' has bad status_code: '{response.status_code}'")

            # replace local chain with longest valid chain of all neighbours network
            if new_chain:

                self.blockchain.chain = new_chain
                logger.debug(f"Longer chain added.")

        if old_chain == self.blockchain.chain:
            logger.info(f"Synced chain -> Have already longest chain.")
        else:
            logger.info(f"Synced chain -> New (longer) chain added.")

        logger.debug(f"Syncing chain done.")


    def mine(self) -> None:
        """
        Blocking Mining loop.

        If  ``not_processed_messages`` are available it uses a random message an mines a new block.
        """

        logger.info(f"Start Mining ...")
        logger.debug(f"Start Mining ...")

        while True:

            if len(self.unprocessed_data) > 0:

                data = self.unprocessed_data.pop()
                logger.debug(f"There is local unprocessed data. - data.id: '{data.id}', data.message: '{data.message}'")

                if not self.is_data_processed(data):

                    logger.debug(f"Data is not processed -> mine new block. - data.id: '{data.id}', data.message: '{data.message}'")

                    last_block = self.blockchain.last_block
                    last_proof = last_block.proof
                    previous_hash = self.hash(last_block)

                    # proof of work for new block
                    proof = self.proof_of_work(last_proof, self.difficulty)
                    block = self.blockchain.add_new_block(data=data, proof=proof, previous_hash=previous_hash)

                    logger.debug(f"New Block mined. - block.index: {block.index}, block.proof: {block.proof}, block.previous_hash: {block.previous_hash}, block.timestamp: {block.timestamp}, block.data.id: {block.data.id}, block.data.message: {block.data.message}")
                    logger.info(f"New block mined. - block.index: {block.index}, block.timestamp: {block.timestamp}")


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

        logger.debug(f"Hashing block ... - block.index: {block.index}, block.proof: {block.proof}, block.previous_hash: {block.previous_hash}, block.timestamp: {block.timestamp}, block.data.id: {block.data.id}, block.data.message: {block.data.message}")

        hash_value = hashlib.sha256(bytes(block)).hexdigest()

        logger.debug(f"Hashing block done. - block hash: {hash_value}")
        return hash_value


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
    def port(self) -> int:
        return self._port


    @property
    def jobs(self) -> list:
        return self._jobs


    @property
    def server_process(self) -> Process:
        return self._server_process


    @property
    def queue(self) -> Process:
        return self._queue