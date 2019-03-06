import hashlib

from src.blockchain.block import Block


GENESIS_BLOCK = Block(index=0, data="This is the very first Block in this chain!", proof=None, previous_hash=None)
GENESIS_BLOCK_HASH = hashlib.sha256(bytes(GENESIS_BLOCK)).hexdigest()