import shutil
import pytest

from src.blockchain.blockchain import *

constructor_json_format = [True, False]

path_to_chain = "test_chain/test.chain"
path_to_chain = encode_file_path_properly(path_to_chain)



@pytest.fixture
def clean_chain_file_fixture():

    if os.path.isdir(os.path.dirname(path_to_chain)):
        shutil.rmtree(os.path.dirname(path_to_chain))



@pytest.mark.parametrize("json_format", constructor_json_format)
def test_constructor(json_format, clean_chain_file_fixture):

    # test without local chain
    blockchain_without_local_chain = Blockchain(path_to_chain=path_to_chain, json_format=json_format)
    assert isinstance(blockchain_without_local_chain, Blockchain)
    assert blockchain_without_local_chain.chain[0] == GENESIS_BLOCK

    # test with local chain
    blockchain_with_local_chain = Blockchain(path_to_chain=path_to_chain, json_format=json_format)
    assert isinstance(blockchain_with_local_chain, Blockchain)
    assert blockchain_with_local_chain.chain[0] == GENESIS_BLOCK


@pytest.mark.parametrize("json_format", constructor_json_format)
def test_chain_method(json_format, clean_chain_file_fixture):

    blockchain = Blockchain(path_to_chain=path_to_chain, json_format=json_format)
    chain = blockchain.chain
    genesis_block = chain[0]

    assert genesis_block == GENESIS_BLOCK
