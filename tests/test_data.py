import pytest

from blockchain.blockchain.data import Data
from blockchain.utils.constants import GENESIS_BLOCK_DATA


genesis_data = Data(GENESIS_BLOCK_DATA)


data = Data("dummy data")
same_data = Data("dummy data")


def test_constructor_valid():

    assert isinstance(data, Data)
    assert data.message == "dummy data"
    assert data.id != None
    assert isinstance(data.id, str)
    assert len(data.id) == 32


@pytest.mark.parametrize("input", [123, 47.11, True, ["abc", "asdf"], {"abc", "asdf"}, ("abc", "asdf")])
def test_constructor_invalid(input):

    with pytest.raises(ValueError) as error:

        Data(input)

        assert "Message of Data needs to be of type string!" == str(error.value)


def test__hash__():

    data_hash = data.__hash__()
    genesis_data_hash = genesis_data.__hash__()

    assert data_hash != genesis_data_hash

    # hashing again -> same hash
    assert data_hash == hash(data)
    assert genesis_data_hash == hash(genesis_data)

    # same data -> different hash
    assert hash(data) != hash(same_data)


def test__eq__():

    assert genesis_data == genesis_data
    assert data == data
    assert genesis_data != data