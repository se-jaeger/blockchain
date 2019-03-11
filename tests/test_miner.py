import os
import shutil
import pytest

from src.utils.constants import *
from src.client.miner import Miner
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

    miner = Miner(path_to_chain=path_to_chain, json_format=json_format, host=DEFAULT_HOST, port=DEFAULT_PORT, difficulty=DEFAULT_DIFFICULTY, neighbours=[("localhost", 12345)])

    assert isinstance(miner, Miner)
    assert miner.blockchain.chain[0] == GENESIS_BLOCK
    assert miner.blockchain.last_block == GENESIS_BLOCK


@pytest.mark.parametrize("path_to_chain", [123, 47.11, True, ["abc", "asdf"], {"abc", "asdf"}, ("abc", "asdf")])
def test_constructor_invalid_path_to_chain(path_to_chain, clean_chain_file_fixture):

    with pytest.raises(ValueError, match="'path_to_chain' has to be of type string!"):
        Miner(path_to_chain=path_to_chain, json_format=True, host=DEFAULT_HOST, port=DEFAULT_PORT, difficulty=DEFAULT_DIFFICULTY, neighbours=[("localhost", 12345)])


@pytest.mark.parametrize("json_format", [123, 47.11, ["abc", "asdf"], {"abc", "asdf"}, ("abc", "asdf")])
def test_constructor_invalid_json_format(json_format, clean_chain_file_fixture):

    with pytest.raises(ValueError, match="'json_format' has to be a boolean value!"):
        Miner(path_to_chain=path_to_chain, json_format=json_format, host=DEFAULT_HOST, port=DEFAULT_PORT, difficulty=DEFAULT_DIFFICULTY, neighbours=[("localhost", 12345)])


@pytest.mark.parametrize("host", [123, 47.11, True, ["abc", "asdf"], {"abc", "asdf"}, ("abc", "asdf")])
def test_constructor_invalid_host(host, clean_chain_file_fixture):

    with pytest.raises(ValueError, match="'host'"):
        Miner(path_to_chain=path_to_chain, json_format=True, host=host, port=DEFAULT_PORT, difficulty=DEFAULT_DIFFICULTY, neighbours=[("localhost", 12345)])


@pytest.mark.parametrize("port", [-4, 65536, 47.11, True, ["abc", "asdf"], {"abc", "asdf"}, ("abc", "asdf")])
def test_constructor_invalid_port(port, clean_chain_file_fixture):

    with pytest.raises(ValueError, match="'port' is of wrong type or out of range!"):
        Miner(path_to_chain=path_to_chain, json_format=True, host=DEFAULT_HOST, port=port, difficulty=DEFAULT_DIFFICULTY, neighbours=[("localhost", 12345)])


@pytest.mark.parametrize("difficulty", [-1, 0, 47.11, True, ["abc", "asdf"], {"abc", "asdf"}, ("abc", "asdf")])
def test_constructor_invalid_difficulty(difficulty, clean_chain_file_fixture):

    with pytest.raises(ValueError, match="'difficulty' is of wrong type or lower than 1!"):
        Miner(path_to_chain=path_to_chain, json_format=True, host=DEFAULT_HOST, port=DEFAULT_PORT, difficulty=difficulty, neighbours=[("localhost", 12345)])


@pytest.mark.parametrize("neighbours", [65536, 47.11, True, {"abc", "asdf"}, ("abc", "asdf"), [("locaasdflhost", 12345)], [(2, 12345)], [(False, 12345)], [(12.23, 12345)], [("localhost", -1)], [("localhost", 65536)]])
def test_constructor_invalid_neighbours(neighbours, clean_chain_file_fixture):

    with pytest.raises(ValueError, match="'neighbours'"):
        Miner(path_to_chain=path_to_chain, json_format=True, host=DEFAULT_HOST, port=DEFAULT_PORT, difficulty=DEFAULT_DIFFICULTY, neighbours=neighbours)


@pytest.mark.parametrize("json_format", constructor_json_format)
def test_hash(json_format, clean_chain_file_fixture):

    miner = Miner(path_to_chain=path_to_chain, json_format=json_format, host=DEFAULT_HOST, port=DEFAULT_PORT, difficulty=DEFAULT_DIFFICULTY)

    assert GENESIS_BLOCK_HASH == miner.hash(GENESIS_BLOCK)

    # only Block objects are hashable by Miner objects
    with pytest.raises(ValueError) as error:

        string_object = "This is a random String object"
        miner.hash(string_object)

        # correct error?
        assert "Only `Block` objects are hashable!" == str(error.value)


def test_is_proof_of_work_valid():

    last_proof = GENESIS_BLOCK.proof

    assert Miner.is_proof_of_work_valid(last_proof=last_proof, proof=1, difficulty=1)
    assert Miner.is_proof_of_work_valid(last_proof=last_proof, proof=350, difficulty=2)
    assert Miner.is_proof_of_work_valid(last_proof=last_proof, proof=3969, difficulty=3)
    assert Miner.is_proof_of_work_valid(last_proof=last_proof, proof=15558, difficulty=4)

    # difficulty has to be a positive integer value
    with pytest.raises(ValueError) as error:

        Miner.is_proof_of_work_valid(last_proof=last_proof, proof=16, difficulty=0)
        assert "'difficulty' has to be a positive integer value." == str(error.value)

    with pytest.raises(ValueError) as error:

        Miner.is_proof_of_work_valid(last_proof=last_proof, proof=16, difficulty=-1)
        assert "'difficulty' has to be a positive integer value." == str(error.value)


@pytest.mark.parametrize("json_format", constructor_json_format)
def test_proof_of_work(json_format, clean_chain_file_fixture):

    miner = Miner(path_to_chain=path_to_chain, json_format=json_format, host=DEFAULT_HOST, port=DEFAULT_PORT, difficulty=DEFAULT_DIFFICULTY)

    proof_of_work_difficulty_1 = miner.proof_of_work(last_proof=None, difficulty=1)
    proof_of_work_difficulty_2 = miner.proof_of_work(last_proof=None, difficulty=2)
    proof_of_work_difficulty_3 = miner.proof_of_work(last_proof=None, difficulty=3)
    proof_of_work_difficulty_4 = miner.proof_of_work(last_proof=None, difficulty=4)
    proof_of_work_difficulty_5 = miner.proof_of_work(last_proof=None, difficulty=5)

    assert proof_of_work_difficulty_1 == 1
    assert proof_of_work_difficulty_2 == 350
    assert proof_of_work_difficulty_3 == 3969
    assert proof_of_work_difficulty_4 == 15558
    assert proof_of_work_difficulty_5 == 1406000


@pytest.mark.parametrize("json_format", constructor_json_format)
def test_is_chain_valid__valid_chain(json_format, clean_chain_file_fixture):

    miner = Miner(path_to_chain=path_to_chain, json_format=json_format, host=DEFAULT_HOST, port=DEFAULT_PORT, difficulty=DEFAULT_DIFFICULTY)

    genesis_hash = miner.hash(miner.blockchain.last_block)
    miner.blockchain.add_new_block(data=Data("Some test data."), proof=1406000, previous_hash=genesis_hash)

    second_block_hash = miner.hash(miner.blockchain.last_block)
    miner.blockchain.add_new_block(data=Data("Some more test data."), proof=423135, previous_hash=second_block_hash)

    assert miner.is_chain_valid()


@pytest.mark.parametrize("json_format", constructor_json_format)
def test_is_chain_valid__wrong_genesis(json_format, clean_chain_file_fixture):

    miner = Miner(path_to_chain=path_to_chain, json_format=json_format, host=DEFAULT_HOST, port=DEFAULT_PORT, difficulty=DEFAULT_DIFFICULTY)

    genesis_hash = miner.hash(miner.blockchain.last_block)
    miner.blockchain.add_new_block(data=Data("Some test data."), proof=1406000, previous_hash=genesis_hash)

    second_block_hash = miner.hash(miner.blockchain.last_block)
    miner.blockchain.add_new_block(data=Data("Some more test data."), proof=423135, previous_hash=second_block_hash)

    # wrong index, correct previous hash
    miner.blockchain.chain[0]._index = 1
    assert not miner.is_chain_valid()

    # wrong index, wrong previous hash
    miner.blockchain.chain[0]._previous_hash = "e59be601c9213694f0b72534148199b24d1ed7c1c29c02ba4602e780015a7663"
    assert not miner.is_chain_valid()

    # correct index, wrong previous hash
    miner.blockchain.chain[0]._index = 0
    assert not miner.is_chain_valid()


@pytest.mark.parametrize("json_format", constructor_json_format)
def test_is_chain_valid__wrong_block_1(json_format, clean_chain_file_fixture):

    miner = Miner(path_to_chain=path_to_chain, json_format=json_format, host=DEFAULT_HOST, port=DEFAULT_PORT, difficulty=DEFAULT_DIFFICULTY)

    genesis_hash = miner.hash(miner.blockchain.last_block)
    miner.blockchain.add_new_block(data=Data("Some test data."), proof=1406000, previous_hash=genesis_hash)

    second_block_hash = miner.hash(miner.blockchain.last_block)
    miner.blockchain.add_new_block(data=Data("Some more test data."), proof=423135, previous_hash=second_block_hash)

    # wrong index, correct previous hash, correct proof of work, correct timestamp
    miner.blockchain.chain[1]._index = 42
    assert not miner.is_chain_valid()

    # wrong index, wrong previous hash, correct proof of work, correct timestamp
    miner.blockchain.chain[1]._previous_hash = None
    assert not miner.is_chain_valid()

    # wrong index, wrong previous hash, wrong proof of work, correct timestamp
    miner.blockchain.chain[1]._proof = 1234876423876
    assert not miner.is_chain_valid()

    # wrong index, wrong previous hash, wrong proof of work, wrong timestamp
    miner.blockchain.chain[1]._timestamp = miner.blockchain.chain[0].timestamp
    assert not miner.is_chain_valid()

    # correct index, wrong previous hash, wrong proof of work, wrong timestamp
    miner.blockchain.chain[1]._index = 1
    assert not miner.is_chain_valid()

    # correct index, correct previous hash, wrong proof of work, wrong timestamp
    miner.blockchain.chain[1]._previous_hash = genesis_hash
    assert not miner.is_chain_valid()

    # correct index, correct previous hash, correct proof of work, wrong timestamp
    miner.blockchain.chain[1]._proof = 1406000
    assert not miner.is_chain_valid()


@pytest.mark.parametrize("json_format", constructor_json_format)
def test_is_chain_valid__wrong_block_2(json_format, clean_chain_file_fixture):

    miner = Miner(path_to_chain=path_to_chain, json_format=json_format, host=DEFAULT_HOST, port=DEFAULT_PORT, difficulty=DEFAULT_DIFFICULTY)

    genesis_hash = miner.hash(miner.blockchain.last_block)
    miner.blockchain.add_new_block(data=Data("Some test data."), proof=1406000, previous_hash=genesis_hash)

    second_block_hash = miner.hash(miner.blockchain.last_block)
    miner.blockchain.add_new_block(data=Data("Some more test data."), proof=423135, previous_hash=second_block_hash)

    # wrong index, correct previous hash, correct proof of work, correct timestamp
    miner.blockchain.chain[2]._index = 42
    assert not miner.is_chain_valid()

    # wrong index, wrong previous hash, correct proof of work, correct timestamp
    miner.blockchain.chain[2]._previous_hash = None
    assert not miner.is_chain_valid()

    # wrong index, wrong previous hash, wrong proof of work, correct timestamp
    miner.blockchain.chain[2]._proof = 1234876423876
    assert not miner.is_chain_valid()

    # wrong index, wrong previous hash, wrong proof of work, wrong timestamp
    miner.blockchain.chain[2]._timestamp = miner.blockchain.chain[0].timestamp
    assert not miner.is_chain_valid()

    # correct index, wrong previous hash, wrong proof of work, wrong timestamp
    miner.blockchain.chain[2]._index = 2
    assert not miner.is_chain_valid()

    # correct index, correct previous hash, wrong proof of work, wrong timestamp
    miner.blockchain.chain[2]._previous_hash = second_block_hash
    assert not miner.is_chain_valid()

    # correct index, correct previous hash, correct proof of work, wrong timestamp
    miner.blockchain.chain[2]._proof = 423135
    assert not miner.is_chain_valid()
