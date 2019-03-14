import os
import logging
import threading

from datetime import timedelta
from urllib.parse import urlparse

from src.utils.errors import ProgramKilledError, PortValueError
from src.utils.constants import DEFAULT_PORT, COLOR_BOLD, COLOR_END, COLOR_GREEN, COLOR_RED


logger = logging.getLogger(__name__)


def encode_file_path_properly(file_path: str) -> str:
    """

    Encode each and every input filepath as absolute pathes.

    Args:
        file_path (str): Path to encode properly

    Returns:
        str: Absolute and properly encoded ``file_path``

    """

    # make sure that '~' in filename is interpreted properly
    file_path = os.path.expanduser(file_path)

    # make sure path is absolute
    file_path = os.path.abspath(file_path)

    return file_path


def split_url_string(host_port: str) -> (str, int):
    """

    Parses the given URL string and returns the IP address/hostname and the port/default port.

    Args:
        host_port (str): Representation of the miner as URL string, e.g.: ``127.0.0.1:12345``, ``miner1:8888``, ``miner``, ``http://localhost``, ...

    Returns:
        (str, int): Tuple of IPv4 Address or hostname string and port number.

    Raises:
        PortValueError: Will be raised if given ``port`` is out of range.
        AddressValueError: Will be raised if given ``address`` is not a valid IPv4 address or "localhost".
    """

    logger.debug(f"Split URL string ... - '{host_port}'")

    # remove leading protocols (http/ https)
    if host_port.startswith("http://"):
        host_port = host_port[len("http://"):]

    elif host_port.startswith("https://"):
        host_port = host_port[len("https://")]

    else:
        logger.debug(f"No leading protocol found: '{host_port}'")


    cleaned_url_string = urlparse(f"http://{host_port}").netloc
    url_split = cleaned_url_string.split(":")

    if(len(url_split) == 1):
        host = url_split[0]
        port = DEFAULT_PORT

    elif(len(url_split) == 2):
        host = url_split[0]
        port = int(url_split[1])

    else:
        logger.warning(f"Split URL string is to long, use index 0 and 1: - '{url_split}'")
        host = url_split[0]
        port = int(url_split[1])

    if port < 1 or port > 65535:
        raise PortValueError("Given port is out of range (1 - 65535).")

    if host == "localhost" or host == "0.0.0.0":
        host = "127.0.0.1"

    logger.debug(f"URL string split. - host: '{host}', port: '{port}")
    return (host, port)


def create_proper_url_string(host_port: (str, int), path: str) -> str:
    """

    Takes the internal representation of neighbours and a endpoint path to create a proper URL string for requests.

    Args:
        host_port (str, int): Internal representation of IP address/hostname and port combination.
        path (str): The endpoint of the API.

    Returns:
        str: Correct URL string for ``address`` and ``path``.
    """

    # remove all leading / (slash)
    while path.startswith("/"):
        path = path[len("/"):]

    return f"http://{host_port[0]}:{host_port[1]}/{path}"


def colorize(text: str, color: str) -> str:

    if color == "bold":
        return f"{COLOR_BOLD}{text}{COLOR_END}"

    elif color == "green":
        return f"{COLOR_GREEN}{text}{COLOR_END}"

    elif color == "red":
        return f"{COLOR_RED}{text}{COLOR_END}"

    else:
        logger.warning(f"Could not find handle for type: '{color}'")
        return text


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