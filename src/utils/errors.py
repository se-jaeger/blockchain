

class PortValueError(ValueError):
    """
     Error if given port is out af valid range (1 - 65535).
    """


class ProgramKilledError(Exception):
    """
    Error if process get killed.
    """


class ChainNotFoundError(Exception):
    """
    Error if no local chain could be found.
    """


class ChainNotValidError(Exception):
    """
    Error if loaded chain is not valid.
    """