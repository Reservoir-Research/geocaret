""" functions for testing various logging capabilities """
import pytest


def test_dummy(get_logger):
    from lib import get_package_file
    print(get_logger)
    assert True
