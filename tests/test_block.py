from src.blockchain.block import *

def test_constructor():
    block = Block()
    assert isinstance(block, Block)