from src.blockchain.blockchain import *

def test_constructor():
    blockchain = Blockchain(path_to_chain="test_chain/test.chain")
    assert isinstance(blockchain, Blockchain)