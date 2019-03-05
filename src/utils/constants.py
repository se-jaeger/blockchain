import hashlib

from src.blockchain.block import Block


GENESIS_BLOCK = Block(index=0, data="This is the very first Block in this chain!", proof=42, previous_hash="no previous hash, because it is the genesis block")
GENESIS_BLOCK_HASH = hashlib.sha256(bytes(GENESIS_BLOCK)).hexdigest()