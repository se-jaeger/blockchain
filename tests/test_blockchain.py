from src.blockchain.blockchain import *

def test_constructor():
    blockchain = Blockchain()
    assert isinstance(blockchain, Blockchain)