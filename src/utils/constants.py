import hashlib

from src.blockchain.data import Data
from src.blockchain.block import Block


GENESIS_DATA = Data("This is the workload of the very first Block in this chain!")
GENESIS_BLOCK = Block(index=0, data=GENESIS_DATA, proof=None, previous_hash=None)
GENESIS_BLOCK_HASH = hashlib.sha256(bytes(GENESIS_BLOCK)).hexdigest()

MAX_NEIGHBOURS = 3
DEFAULT_NEIGHBOURS = {"localhost:12345"}

DIFFICULTY_DEFAULT = 5

HOST_DEFAULT = "0.0.0.0"
PORT_DEFAULT = 12345

HTTP_OK = 200
HTTP_BAD = 400
HTTP_NOT_FOUND = 404

DATA_ENDPOINT = "/data"
CHAIN_ENDPOINT = "/chain"
NEIGHBOURS_ENDPOINT = "/neighbours"
ADD_ENDPOINT = "/add"

ADD_KEY = "add"
SEND_CHAIN_KEY = "chain"
SEND_NEIGHBOURS_KEY = "neighbours"
SEND_DATA_KEY = "data"

MESSAGE_PARAM = "message"

GOSSIP_TIME_SECONDS = 5
CHAIN_SYNC_TIME_SECONDS = 5
UNPROCESS_DATA_SYNC_TIME_SECONDS = 5

LOGGING_FORMAT = "[%(asctime)s - %(filename)-15s:%(lineno)-4s - %(levelname)-7s - %(funcName)-25s]: %(message)s"