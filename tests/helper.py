"""Collection of helper functions required for running some of the unit
    tests.

    Typical usage example:

        if connected(method='requests', timeout=1)):
            print("Connected")
        else:
            print("Disconnected")

        disable_wifi(logging=True)
        enable_wifi(logging=True)
"""
from functools import partial
import subprocess
from sys import platform
import time
import multiprocessing
import urllib.request
import urllib.error
import socket
import http.client as httplib
import requests
import heet.log_setup

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)


def _urllib_connection_check(
        url: str = 'http://google.com',
        timeout: int = 1) -> bool:
    """Checks internet connection using the `urllib` module."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as _:
            pass
        return True
    except urllib.error.URLError:
        return False


def _socket_connection_check(
        host: str = "8.8.8.8",
        port: int = 53,
        timeout: int = 1) -> bool:
    """Checks internet connection using the `socket` module."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(
            socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def _http_connection_check(host: str = "8.8.8.8", timeout: int = 1) -> bool:
    """Checks internet connection using the `httplib` module."""
    conn = httplib.HTTPSConnection(host, timeout=timeout)
    try:
        conn.request("HEAD", "/")
        return True
    except OSError:
        return False
    finally:
        conn.close()


def _requests_connection_check(
        url: str = 'http://google.com',
        timeout: int = 1) -> bool:
    """Checks internet connection using the `requests` module."""
    try:
        _ = requests.head(url=url, timeout=timeout)
        return True
    except requests.ConnectionError:
        pass
    return False


# Check internet connection using a libary of choice
def connected(method: str = 'socket', timeout: int = 1) -> bool:
    """Check internet connection using the urrlib package."""
    _url = 'http://google.com'
    _host = "8.8.8.8"
    _port = 53
    # Create partial functions
    urllib_part = partial(_urllib_connection_check, url=_url)
    socket_part = partial(_socket_connection_check, host=_host, port=_port)
    http_part = partial(_http_connection_check, host=_host)
    requests_part = partial(_requests_connection_check, url=_url)
    # Create an exec dictionary
    exec_map = {
        'urllib': urllib_part,
        'socket': socket_part,
        'http': http_part,
        'requests': requests_part}
    try:
        return exec_map[method](timeout=timeout)
    except KeyError as exc:
        raise KeyError(f"Connection method {method} not defined.") from exc


def _loop_connection_check(
        exit_condition: str,
        check_method='socket',
        timeout=1) -> None:
    """Function for making repeated calls to check internet connection and
    finishing if the desired connection status is achieved.

    WARNING: Do not call this function on its own. It is intended only
    to be called as a thread or a process with appropriate thread/process
    handling."""
    _exit_conditions = {"on": True, "off": False}
    # Be careful, it can be an infinite loop.
    while True:
        if connected(method=check_method, timeout=timeout) is \
                _exit_conditions[exit_condition]:
            return
        continue


def disable_wifi(
        logging: bool = False,
        max_wait: int = 5,
        check_method: str = 'socket') -> None:
    """Turns internet connection OFF using OS call."""
    if logging:
        logger.info("Disabling WiFi connection.")
    if platform in ("linux", "linux2"):
        _ = subprocess.run(["nmcli", "radio", "wifi", "off"], check=True)
    elif platform == "darwin":
        logger.warning("Turning WiFi on/off not supported in MacOS.")
        return
    elif platform == "win32":
        _ = subprocess.run(["netsh", "interface", "set", "interface",
                            "Wi-Fi", "DISABLED"], check=True)
    # Return when internet is disconnected, otherwise wait until the
    # internet disconnection process takes account
    conn_proc = multiprocessing.Process(
        target=_loop_connection_check,
        args=("off", check_method))
    start_time = time.time()
    conn_proc.start()
    while True:
        time_exceeded = bool(time.time() - start_time >= max_wait)
        if not conn_proc.is_alive() or time_exceeded:
            conn_proc.terminate()  # Needed when process does not terminate
            if logging:
                if time_exceeded:
                    logger.error(
                        "WiFi connection couldn't be disabled. Time exceeded.")
                else:
                    logger.info("WiFi connection disabled.")
            return


def enable_wifi(
        logging: bool = False,
        max_wait: int = 10,
        check_method: str = 'socket') -> None:
    """Turns internet connection ON using OS call."""
    if logging:
        logger.info("Enabling WiFi connection.")
    if platform in ("linux", "linux2"):
        _ = subprocess.run(["nmcli", "radio", "wifi", "on"], check=True)
    elif platform == "darwin":
        logger.warning("Turning WiFi on/off not supported in MacOS.")
        return
    elif platform == "win32":
        _ = subprocess.run(["netsh", "interface", "set", "interface",
                            "Wi-Fi", "ENABLED"], check=True)
    # Return when internet is disconnected, otherwise wait until the
    # internet disconnection process takes account
    conn_proc = multiprocessing.Process(
        target=_loop_connection_check,
        args=("on", check_method))
    start_time = time.time()
    conn_proc.start()
    while True:
        time_exceeded = bool(time.time() - start_time >= max_wait)
        if not conn_proc.is_alive() or time_exceeded:
            conn_proc.terminate()  # Needed when process does not terminate
            if logging:
                if time_exceeded:
                    logger.error(
                        "WiFi connection couldn't be enabled. Time exceeded.")
                else:
                    logger.info("WiFi connection enabled.")
            return


if __name__ == '__main__':
    pass
