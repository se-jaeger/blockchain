import os
import shutil
import pytest

from src.client.miner import Miner
from src.utils.utils import encode_file_path_properly
from src.utils.constants import GENESIS_BLOCK, GENESIS_BLOCK_HASH


constructor_json_format = [True, False]

path_to_chain = "test_chain/test.chain"
path_to_chain = encode_file_path_properly(path_to_chain)



@pytest.fixture
def clean_chain_file_fixture():

    if os.path.isdir(os.path.dirname(path_to_chain)):
        shutil.rmtree(os.path.dirname(path_to_chain))


@pytest.mark.parametrize("json_format", constructor_json_format)
def test_constructor(json_format, clean_chain_file_fixture):

    miner = Miner(path_to_chain=path_to_chain, json_format=json_format)

    assert isinstance(miner, Miner)
    assert miner.blockchain.chain[0] == GENESIS_BLOCK
    assert miner.blockchain.last_block == GENESIS_BLOCK


@pytest.mark.parametrize("json_format", constructor_json_format)
def test_hash(json_format, clean_chain_file_fixture):

    miner = Miner(path_to_chain=path_to_chain, json_format=json_format)

    assert GENESIS_BLOCK_HASH == miner.hash(GENESIS_BLOCK)

    # only Block objects are hashable by Miner objects
    with pytest.raises(ValueError) as error:

        string_object = "This is a random String object"
        miner.hash(string_object)

    # correct error?
    assert "Only `Block` objects are hashable!" == str(error.value)