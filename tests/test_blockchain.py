from src.blockchain.blockchain import *

def test_constructor():
    blockchain = Blockchain(path_to_chain="dummy_path")
    assert isinstance(blockchain, Blockchain)