import pytest

from src.blockchain.data import Data
from src.blockchain.block import Block
from src.utils.constants import GENESIS_BLOCK


data = Data("dummy data")
same_data = Data("dummy data")
dummy_prev_hash = "e59be601c9213694f0b72534148199b24d1ed7c1c29c02ba4602e780015a7663"
another_genesis_block = Block(index=0, data=GENESIS_BLOCK.data, proof=None, previous_hash=None)


def test_constructor():

    block = Block(index=0, data=data, proof=42, previous_hash=dummy_prev_hash)

    assert isinstance(block, Block)

    assert block.index == 0
    assert block.data == data
    assert block.proof == 42
    assert block.previous_hash == dummy_prev_hash


@pytest.mark.parametrize("index", [-1, "asdf", 47.11, [123, 33], {123, 33}, (123, 33)])
def test_constructor_wrong_index(index):


    with pytest.raises(ValueError) as error:

        Block(index=index, data=data, proof=42, previous_hash=dummy_prev_hash)

        assert "Index has incorrect type or value!" == str(error.value)


@pytest.mark.parametrize("data", [-1, "asdf", 47.11, [123, 33], {123, 33}, (123, 33)])
def test_constructor_wrong_data(data):
    with pytest.raises(ValueError) as error:
        Block(index=0, data=data, proof=42, previous_hash=dummy_prev_hash)

        assert "Data is not a object of class 'Data'." == str(error.value)


@pytest.mark.parametrize("proof", ["asdf", 47.11, [123, 33], {123, 33}, (123, 33)])
def test_constructor_wrong_index(proof):
    with pytest.raises(ValueError) as error:
        Block(index=0, data=data, proof=proof, previous_hash=dummy_prev_hash)

        assert "Proof has incorrect type!" == str(error.value)


@pytest.mark.parametrize("previous_hash", [8127 , "asdf", 47.11, [123, 33], {123, 33}, (123, 33)])
def test_constructor_wrong_index(previous_hash):
    with pytest.raises(ValueError) as error:
        Block(index=0, data=data, proof=42, previous_hash=previous_hash)

        assert "Previous hash has incorrect type or wrong length!" == str(error.value)


def test_timestamp():

    block1 = Block(index=0, data=data, proof=42, previous_hash=dummy_prev_hash)
    block2 = Block(index=0, data=data, proof=42, previous_hash=dummy_prev_hash)

    assert block1.timestamp < block2.timestamp


def test_equality():

    assert GENESIS_BLOCK == GENESIS_BLOCK
    assert another_genesis_block == another_genesis_block
    assert GENESIS_BLOCK != another_genesis_block


def test_negative_equality():

    assert GENESIS_BLOCK != another_genesis_block

    string_object = "This is a random String object"

    assert GENESIS_BLOCK != string_object
    assert string_object != another_genesis_block