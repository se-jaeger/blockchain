import pytest

from src.blockchain.blockchain import *

constructor_json_format = [True, False]

path_to_chain = "test_chain/test.chain"
path_to_chain = encode_file_path_properly(path_to_chain)


@pytest.mark.parametrize("json_format", constructor_json_format)
def test_constructor(json_format):

    # delete chain if one exists
    if os.path.isfile(path_to_chain):
        os.remove(path_to_chain)

    # test without local chain
    blockchain_without_local_chain = Blockchain(path_to_chain=path_to_chain, json_format=json_format)
    assert isinstance(blockchain_without_local_chain, Blockchain)

    # test with local chain
    blockchain_with_local_chain = Blockchain(path_to_chain=path_to_chain, json_format=json_format)
    assert isinstance(blockchain_with_local_chain, Blockchain)


@pytest.mark.parametrize("json_format", constructor_json_format)
def test_chain_method(json_format):

    # delete chain if one exists
    if os.path.isfile(path_to_chain):
        os.remove(path_to_chain)

    blockchain = Blockchain(path_to_chain=path_to_chain, json_format=json_format)
    chain = blockchain.chain
    genesis_block = chain[0]

    assert genesis_block == GENESIS_BLOCK
