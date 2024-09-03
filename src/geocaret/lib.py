""" """
from typing import Dict
import pathlib
import sys
import toml


APPLICATION_NAME = "geocaret"

def get_package_file(*folders: str) -> pathlib.Path:
    """Imports package data using importlib functionality.

    Args:
        *folders: comma-separated strings representing path to the packaged data
            file.
    Returns:
        A os-indepenent path of the data file.
    """
    # Import the package based on Python's version
    if sys.version_info < (3, 9):
        # importlib.resources either doesn't exist or lacks the files()
        # function, so use the PyPI version:
        import importlib_resources
        pkg = importlib_resources.files(APPLICATION_NAME)
        pkg = pathlib.Path.joinpath(pkg, '/'.join(folders))
        return pkg
    else:
        # importlib.resources has files(), so use that:
        import importlib.resources as importlib_resources
        pkg = importlib_resources.files(APPLICATION_NAME)
        pkg = pkg.joinpath("/".join(folders))
        return pkg


def load_toml(file_path: pathlib.Path) -> Dict:
    """Load toml file"""
    return toml.load(file_path)
    
    
def _get_config():
    asset_config = load_toml(get_package_file("config_files/assets.toml"))
    return asset_config

    
def get_public_asset(asset_name: str) -> str:
    """ """
    public_assets = _get_config().get('public_assets')
    return public_assets[asset_name]


def get_private_asset(asset_name: str) -> str:
    """ """
    private_assets = _get_config().get('private_assets')
    return private_assets[asset_name]
    
    
if __name__ == "__main__":
    ...
