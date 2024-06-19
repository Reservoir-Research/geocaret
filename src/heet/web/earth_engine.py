"""Module for authentication and initialization of Google's Earth Engine."""
from typing import Optional
import sys
from datetime import datetime
import socket
import ee
import google.oauth2
import heet.log_setup
from heet.exceptions import NoInternetConnectionError

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)


class EarthEngineMeta(type):
    """
    Metaclass for the EarthEngine class which allows only one instance of
    the EarthEngine class, i.e. that the EarthEngine class object is only
    initialized once.
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


class EarthEngine(metaclass=EarthEngineMeta):
    """
    EarthEngine class used for initialization of Earth Engine and retrieving
    the running Earth Engine's properties.

    Note: EarthEngine is a singleton class but it is not thread-safe. Modify
    the code if the application is ever switched to multi-threading.
    """

    def __init__(self):
        now = datetime.now()
        self.init_time = now.strftime("%H:%M:%S")
        self._initialized: bool = False

    @staticmethod
    def get_credentials() -> Optional[google.oauth2.credentials.Credentials]:
        """Get users Google API credentials.

        If None then the user is not logged into the user service. In
        particular, Google's Earth Engine has not been initialized."""
        return ee.data._credentials

    @property
    def initialized(self) -> bool:
        return self._initialized

    @classmethod
    def is_authenticated(cls) -> Optional[bool]:
        """Check is the user is authentiated with Google's Earth Engine."""
        try:
            ee.Initialize()
            return True
        except ee.ee_exception.EEException:
            # Trouble finding authentication credentials
            return False
        except socket.gaierror:
            # Internet connection problems
            return None

    def init(self, logging: bool = False) -> None:
        """Initialize the Google Earth Engine library."""
        if not self._initialized:
            try:
                ee.Initialize()
                if logging:
                    logger.info("Earth Engine initialized.")
                self._initialized = True
            except ee.ee_exception.EEException:
                # Trouble finding authentication credentials
                self.authenticate()
                ee.Initialize()
                if logging:
                    logger.info("Earth Engine initialized.")
                self._initialized = True
            except (socket.gaierror, socket.timeout):
                # Internet connection problems
                if logging:
                    logger.exception("Earth Engine could not be initialized.")
        else:
            if logging:
                logger.info("Earth Engine already initialized.")

    def authenticate(self) -> None:
        """Authenticate your access to Google Earth Engine servers and gain
        access to the resources.

        Note: Requires gcloud API installed on the local machine."""
        if self.is_authenticated():
            logger.info("Account already authenticated.")
        else:
            try:
                # Requires Google gcloud
                ee.Authenticate()
            except socket.gaierror as error:
                logger.error(error)
                sys.exit(
                    "Encountered an error authenticating to Google Earth \
                     Engine and will close. see heet.log for details")


if __name__ == '__main__':
    ee.Initialize()
    EarthEngine.get_credentials()
