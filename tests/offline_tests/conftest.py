""" """
import pytest
import logging


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
