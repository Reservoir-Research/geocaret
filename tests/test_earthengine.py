"""Tests for initialization and authentication of the Earth Engine."""
import time
import socket
from pytest_socket import disable_socket
import ee
import urllib3.connection
import pytest
import heet.earth_engine as heet_ee
from heet.web.connectivity import is_connected
from heet.exceptions import NoInternetConnectionError


def test_singleton() -> None:
    """Test if the heet_ee.EarthEngine object is singleton."""
    engine_1 = heet_ee.EarthEngine()
    time.sleep(0.5)
    engine_2 = heet_ee.EarthEngine()
    assert id(engine_1) == id(engine_2)
    assert id(engine_1.init_time) == id(engine_2.init_time)


@pytest.mark.disable_socket
def test_timeout() -> None:
    earth_engine = heet_ee.EarthEngine()
    with pytest.raises(socket.timeout):
        earth_engine.init()

# Test only if internet connection is present
#@pytest.mark.skipif(not is_connected(), reason="Test requires internet connection.")
def test_initialization_status() -> None:
    """Checks whether intialization variable changes status after
    initialization."""
    engine_1 = heet_ee.EarthEngine()
    assert engine_1.initialized is False
    engine_1.init()
    assert engine_1.initialized is True


#@pytest.mark.disable_socket

#@pytest.mark.run_these_please
def test_initialization_status2(disable_external_api_calls) -> None:
    #disable_socket()
    #socket.socket = block_network
    #monkeypatch.setattr(ee, "Initialize", MockEarthEngine.Initialize)
    #monkeypatch.setattr(ee, "Authenticate", MockEarthEngine.Initialize)
    engine_1 = heet_ee.EarthEngine()
    with pytest.raises(NoInternetConnectionError):
        engine_1.init()


def test_initialization_status() -> None:
    """Checks whether intialization variable changes status after
    initialization."""
    engine_1 = heet_ee.EarthEngine()
    engine_1._initialized = False
    assert engine_1.initialized is False
    engine_1.init()
    assert engine_1.initialized is False


class MockEarthEngine():
    """Custom class to mock EarthEngine response."""

    @staticmethod
    def Initialize() -> None:
        print("Mock init")
        pass

    @staticmethod
    def Authenticate() -> None:
        print("Mock authentication")
        pass

# TODO: test authentication and authorization error handling with/without internet access.
