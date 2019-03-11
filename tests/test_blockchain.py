import os
import shutil
import pytest

from src.blockchain.data import Data
from src.utils.constants import GENESIS_BLOCK
from src.blockchain.blockchain import Blockchain
from src.utils.utils import encode_file_path_properly



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
    assert blockchain_without_local_chain.last_block == GENESIS_BLOCK

    # test with local chain
    blockchain_with_local_chain = Blockchain(path_to_chain=path_to_chain, json_format=json_format)
    assert isinstance(blockchain_with_local_chain, Blockchain)
    assert blockchain_with_local_chain.chain[0] == GENESIS_BLOCK
    assert blockchain_with_local_chain.last_block == GENESIS_BLOCK


@pytest.mark.parametrize("json_format", constructor_json_format)
def test_add_new_block(json_format, clean_chain_file_fixture):
    blockchain = Blockchain(path_to_chain=path_to_chain, json_format=json_format)

    blockchain.add_new_block(data=Data("second block"), proof=4711, previous_hash="e59be601c9213694f0b72534148199b24d1ed7c1c29c02ba4602e780015a7663")
    blockchain.add_new_block(data=Data("third block"), proof=42, previous_hash="637ae601c9213694f0b72534148199b24d1ed7c1c29c02ba4602e780015a09ab")

    block_0 = blockchain.chain[0]
    block_1 = blockchain.chain[1]
    block_2 = blockchain.chain[2]

    assert block_0 == GENESIS_BLOCK
    assert block_2 == blockchain.last_block

    assert block_0 != block_1
    assert block_0 != block_2
    assert block_1 != block_2



@pytest.mark.parametrize("json_format", constructor_json_format)
def test_chain_method(json_format, clean_chain_file_fixture):

    blockchain = Blockchain(path_to_chain=path_to_chain, json_format=json_format)
    chain = blockchain.chain
    genesis_block = chain[0]

    assert genesis_block == GENESIS_BLOCK

# TODO: Tests for private fuctions..