from uuid import uuid4


class Data(object):

    def __init__(self, message: str) -> None:
        """
        Constructor for ``Data`` container class.

            Constraints:
                - ``message`` has to be a string.

        Args:
            message (str): The message to store in this ``Data`` container.

        Raises:
            ValueError: Gets raised if ``message`` is not a string.
        """

        super().__init__()

        if not isinstance(message, str):
            raise ValueError("Message of Data needs to be of type string!")

        self._id = str(uuid4()).replace("-", "")
        self._message = message


    def __hash__(self):
        """
        Needed to use ``Set``s of ``Data`` objects.
        """
        return hash(self.id)


    def __repr__(self) -> str:

        data_rep = "Data object with - \n"
        data_rep += "\t\t\t\tid:\t" + str(self.id) + "\n"
        data_rep += "\t\t\t\tmessage:" + str(self.message)

        return data_rep


    def __eq__(self, other) -> bool:

        if not isinstance(other, Data):
            return False

        return self.id == other.id


    @property
    def id(self) -> str:
        return self._id


    @property
    def message(self) -> str:
        return self._message