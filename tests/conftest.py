"""
conftest.py
"""
import pytest
import heet.log_setup


# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)


if __name__ == "__main__":
    pass
