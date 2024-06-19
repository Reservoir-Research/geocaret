# -*- coding: utf-8 -*-
"""Module adding internet connectivity functionality.

Provides `internet_error_handler` - a connectivity decorator for functions and
`ConnectionMonitor` class for monitoring internet connection during execution
of programs requiring sustained connection to the internet.

Typical usage examples:

    Decoration of a function that raises exception, e.g. when internet
    connection is lost. Attempts to execute the decorated function a number
    of times with a delay between each consecutive execution.
    ```
        @internet_error_handler(retries=5, timeout=1, raise_exception=True)
        def lucky_draw():
            import random
            x_rnd = random.uniform(0, 1)
            if x_rnd < 0.5:
                print("Success :)")
                return None
            # If number above 0.5 then it's considered a failure.
            print("Fail :(")
            raise socket.gaierror
        lucky_draw()
    ```

    ConnectionMonitor can be used as a context manager and can run cron
    internet checks at fixed time intervals. Connection status monitoring
    is carried out in a deamon thread.
    ```
    with ConnectionMonitor() as monitor:
        time.sleep(1)
        monitor.start_cron(interval=2, logging=True)
        time.sleep(7)
        monitor.stop_cron(logging=True)
    ```

"""
import time
from typing import Callable, Optional, Tuple, TypeVar
from threading import Thread, Event
import atexit
import socket
import functools
from urllib import request
import urllib3
from transitions import Machine
import heet.log_setup
from heet.exceptions import NoInternetConnectionError

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)

ConnException = TypeVar('ConnException', bound='Exception')


def internet_error_handler(
        retries: int = 5,
        aux_exceptions: Tuple[ConnException, ...] = (),
        timeout: Optional[int] = None,
        raise_exception: bool = False) -> Callable:
    """
    Wrapper function for handling socket connection errors when internet
    connection is interrupted.

    Attempts to call a function several times until the function executes.
    If the function call is unsuccessful, it either raises exception or
    exits without any action.

    Args:
        retries (int): Number of attempts before final function call is made.
        aux_errors: Tuple of additional errors to be handled.
        timeout (int): Number of second between consecutive attempts.
        raise_exception (bool): Defines whether interruption of internet
            connection raises an exception or just an error message.
    Raises:
        NoInternetConnectionError: a custom exception raised when internet
            connection is absent.
    """
    _socket_exceptions: tuple = (socket.timeout, socket.gaierror)
    _http_exceptions: tuple = (request.http.client.RemoteDisconnected,
                               urllib3.exceptions.NewConnectionError)
    _generic_exceptions: tuple = (TypeError,)
    _exceptions: tuple = tuple(set(
        _socket_exceptions +
        _http_exceptions +
        _generic_exceptions +
        aux_exceptions))

    def decorator_internet_error_handler(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper_socket_error(*args, **kwargs) -> Optional[Callable]:
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except _exceptions as exc:
                    attempts += 1
                    if attempts == retries:
                        if raise_exception:
                            raise NoInternetConnectionError(exc) from exc
                    if timeout is not None:
                        time.sleep(timeout)
                else:
                    break
        return wrapper_socket_error
    return decorator_internet_error_handler


class ConnectionMonitorMeta(type):
    """
    Metaclass for the ConnectionMonitor class which allows only one instance of
    the ConnectionMonitor class, i.e. that the ConnectionMonitor class object
    is only initialized once. (Singleton pattern)
    """

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class ConnectionMonitor(metaclass=ConnectionMonitorMeta):
    """
    Class for monitoring internet connectivity during computations requiring
    maintaining internet connection.

    Attributes:
        host (str): 8.8.8.8 (google-public-dns-a.google.com) IP the connection
            that is being monitored.
        timeout (int): how many seconds to wait beore connetion status
            is returned.
        port (int): Port that is listened to (53/tcp DNS Service)
        cron_interval (int): Number of seconds between consecutive connection
            checks.
    """
    # Set up states and transitions for the transitions poackae
    states = ['initial', 'connected', 'disconnected']
    transitions = [
        {'trigger': 'is_on',
         'source': 'initial',
         'dest': 'connected',
         'after': 'greet_connected'},
        {'trigger': 'is_off',
         'source': 'initial',
         'dest': 'disconnected',
         'after': 'greet_disconnected'},
        {'trigger': 'is_off',
         'source': 'connected',
         'dest': 'disconnected',
         'after': 'disconnect'},
        {'trigger': 'is_off',
         'source': 'disconnected',
         'dest': None},
        {'trigger': 'is_on',
         'source': 'disconnected',
         'dest': 'connected',
         'after': 'reconnect'},
        {'trigger': 'is_on',
         'source': 'connected',
         'dest': None}]

    def __init__(
            self,
            host: str = "8.8.8.8",
            timeout: int = 1,
            port: int = 53,
            cron_interval: int = 2):
        self.host = host
        self.timeout = timeout
        self.port = port
        self.cron_interval = cron_interval
        # Start with the initial (first) state
        self.state: str = self.states[0]
        # Start a default cron thread with time interval of 1 second.
        self._cron_thread = Thread(
            target=self.connection_checking, daemon=True)
        self._stop_event: Event = Event()
        # Initialize the state machine
        self._machine = Machine(
            model=self, states=self.states, transitions=self.transitions,
            initial=self.state, send_event=False,
            auto_transitions=False)
        # Check connection and update connection status variables
        self.connection_check()

    def __enter__(self):
        """Handling event when context manager is started."""
        self.start_cron()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Handling event when context manager is closed."""
        self.stop_cron()

    @staticmethod
    def is_connected(host: str = "8.8.8.8", port: int = 53,
                     timeout: int = 1, logging: bool = False) -> bool:
        """Check if internet connection is alive and external IP address is
        reachable.
        Args:
            host: (string) 8.8.8.8 (google-public-dns-a.google.com)
            port: (integer) (53/tcp DNS Service).
            timeout: (float) timeout in seconds.
            logging: (bool) Flag setting logging on/off
        Returns:
            True if external IP address is reachable and False if external IP
                address is unreachable.
        """
        socket.setdefaulttimeout(timeout)
        # Check if socket can be created
        try:
            socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            logger.error(msg)
            if logging:
                logger.warning("Could not open socket.")
            return False
        # Check connection
        try:
            socket1.connect((host, port))
        except OSError as msg:
            if logging:
                logger.error(msg.strerror)
            return False
        finally:
            socket1.close()
        return True

    def connection_check(self) -> None:
        """Check if the computer is connected to internet."""
        connected = self.is_connected()
        if connected:
            self.is_on()
        else:
            self.is_off()

    def connection_checking(self) -> None:
        """Run internet connection checking at fixed intervals.
        To be run only as a deamon thread."""
        while not self._stop_event.is_set():
            self.connection_check()
            time.sleep(self.cron_interval)

    @staticmethod
    def reconnect() -> None:
        """Code executed after state change from disconnected to connected."""
        logger.info("Internet connection reestablised.")

    @staticmethod
    def disconnect() -> None:
        """Code executed after state change from connected to diconnected."""
        logger.info("Internet connection lost.")

    @staticmethod
    def greet_connected() -> None:
        """Code executed upon initialization to connected state."""
        logger.info("Internet connection present.")

    @staticmethod
    def greet_disconnected() -> None:
        """Code executed when internet connection absent upon initializtion."""
        logger.info("Internet connection absent.")

    def start_cron(self, logging: bool = False) -> None:
        """Starts monitoring internet connection at fixed intervals.
        Uses a deamon thread.

        Args:
            logging (bool): Turns logging of transition updates on/off.
        """
        if self._cron_thread.is_alive():
            if logging:
                logger.info("Internet connection monitor running already.")
        else:
            self._cron_thread = Thread(
                target=self.connection_checking,
                daemon=True, name="Internet monitor.")
            self._cron_thread.start()
            # register the at exit
            atexit.register(self.stop_cron)
            if logging:
                logger.info("Internet connection monitor started.")

    def stop_cron(self, logging: bool = False) -> None:
        """Stops the cron internet monitor.
        Args:
            logging (bool): Turns logging of transition updates on/off."""
        if self._cron_thread.is_alive():
            self._stop_event.set()
            self._cron_thread.join()
            self._stop_event.clear()
            if logging:
                logger.info("Internet connection monitor stopped.")
        else:
            if logging:
                logger.info("Internet connection monitor not running already.")

    def is_cron_running(self) -> bool:
        return self._cron_thread.is_alive()


if __name__ == '__main__':
    pass
