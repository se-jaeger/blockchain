import os
import threading

from datetime import timedelta
from ipaddress import ip_address, IPv4Address

from src.utils.errors import ProgramKilledError, PortValueError


def encode_file_path_properly(file_path: str) -> str:
    """

    Encode each and every input filepath as absolute pathes.

    Args:
        file_path (str): Path to encode properly

    Returns:
        str: Absolut and properly encoded ``file_path``

    """

    # make sure that '~' in filename is interpreted properly
    file_path = os.path.expanduser(file_path)

    # make sure path is absolute
    file_path = os.path.abspath(file_path)

    return file_path


def encode_IP_port_properly(ip: str, port: int) -> (IPv4Address, int):
    """

    Validates given IP Address and port.

    Args:
        ip: IP address or ``localhost`` to check for correctness.
        port: Port to validate.

    Returns:
        (IPv4Address, int):

    Raises:
        PortValueError: Will be raised if given ``port`` is out of range.
        AddressValueError: Will be raised if given ``address`` is not a valid IPv4 address or "localhost".
    """

    if ip == "localhost" or ip == "0.0.0.0":
        ip = "127.0.0.1"

    if port < 1 or port > 65535:
        raise PortValueError("Given port is out of range (1 - 65535).")

    return (ip_address(ip), port)


def create_proper_url_string(host_port: (IPv4Address, int), path: str) -> str:
    """

    Args:
        host_port (IPv4Address, int): Internal representation of IP address and port combination.
        path (int): The endpoint of the API.

    Returns:
        str: Correct URL string for ``address`` and ``path``.
    """

    # remove all leading / (slash)
    while path.startswith("/"):
        path = path[len("/"):]

    return f"http://{host_port[0]}:{host_port[1]}/{path}"


def create_URL(address: str, port: int, path: str) -> str:
    """
    Function for convenience to create URL strings.

    Args:
        address: IP address or ``localhost`` to check for correctness.
        port: Port to validate.
        str: Correct URL string for ``address`` and ``path``.

    Returns:
        path (int): The endpoint of the API.
    """

    return create_proper_url_string(encode_IP_port_properly(address, port), path)


def signal_handler(signum, frame):
    """
    Signal handler used to raise special ``ProgramKilledError``.

    Raises:
        ProgramKilledError: To intercept for graceful shutdown.
    """

    raise ProgramKilledError



class Job(threading.Thread):

    def __init__(self, interval: timedelta, execute, *args, **kwargs) -> None:
        """
        Class that represents asynchronous background ``Job``. Runs each ``interval``.

        Args:
            interval (timedelta): The interval when ``execute`` gets executed.
            execute (function): The function to execute.
        """

        super().__init__()

        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs


    def stop(self) -> None:
        """
        Stops the background ``Job``.
        """

        self.stopped.set()
        self.join()


    def run(self) -> None:
        """
        Runs the background ``Job``
        """

        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)