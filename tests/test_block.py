from src.blockchain.block import *


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