from src.blockchain.block import *
from src.utils.constants import GENESIS_BLOCK


def test_constructor():

    block = Block(index=0, data="dummy data", proof=42, previous_hash="0815")

    assert isinstance(block, Block)

    assert block.index == 0
    assert block.data == "dummy data"
    assert block.proof == 42
    assert block.previous_hash == "0815"


def test_timestamp():

    block1 = Block(index=0, data="dummy data", proof=42, previous_hash="0815")
    block2 = Block(index=0, data="dummy data", proof=42, previous_hash="0815")

    assert block1.timestamp < block2.timestamp


def test_equality():

    another_genesis_block = Block(index=0, data="This is the very first Block in this chain!", proof=42, previous_hash="no previous hash, because it is the genesis block")

    assert GENESIS_BLOCK == GENESIS_BLOCK
    assert another_genesis_block == another_genesis_block
