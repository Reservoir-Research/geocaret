""" """
import pathlib
import os
import logging
import pytest
import ee
from lib import get_package_file


@pytest.fixture(scope='session', autouse=True)
def authenticate_google_server():
    """Authenticate to Google server before running any tests."""
    if "CI_ROBOT_USER" in os.environ:
        print("Running service account authentication")
        gc_service_account = os.environ["GCLOUD_ACCOUNT_EMAIL"]
        credentials = ee.ServiceAccountCredentials(
            gc_service_account, "service_account_creds.json"
        )
        ee.Initialize(credentials)
    else:
        print("Running individual account authentication")
        ee.Initialize()


@pytest.fixture
def get_logger() -> logging.RootLogger:
    """Set up logging configuration for tests using logging."""
    # Create a new log each run
    with open("tests.log", 'w') as file:
        pass
    # Get or create a logger
    logger = logging.getLogger()
    # Set log level
    logger.setLevel(logging.DEBUG)
    # Define file handler and set formatter
    file_handler = logging.FileHandler('tests.log')
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    file_handler.setFormatter(formatter)
    # Add file handler to logger
    logger.addHandler(file_handler)
    # Optional: Prevent logging from propagating to the root logger
    logger.propagate = False
    return logger


@pytest.fixture
def root_folder() -> pathlib.Path:
    """ """
    return get_package_file("")
