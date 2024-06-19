""" """
from typing import Dict, Optional
from functools import partial, update_wrapper
import sys
import os
import pathlib
import shutil
import logging
import json
import yaml
import toml

APPLICATION_NAME = "heet"


def get_package_file(*folders: str) -> pathlib.Path:
    """
    Imports package data using importlib functionality. Provides
    different import structure depending on the installed Python
    version.

    Args:
        *folders (str): a number of strings representing folder
            structure in which the packaged data is stored
    """
    # Import the package based on Python's version
    if sys.version_info < (3, 9):
        # importlib.resources either doesn't exist or lacks the files()
        # function, so use the PyPI version:
        import importlib_resources
    else:
        # importlib.resources has files(), so use that:
        import importlib.resources as importlib_resources

    pkg = importlib_resources.files(APPLICATION_NAME)
    # Append folders to package-wide posix path
    return pathlib.Path.joinpath(pkg, '/'.join(folders))


def load_json(file_name: pathlib.Path) -> Dict:
    """Load json file and present the contents in a dictionary."""
    with open(file_name, 'r', encoding='utf-8') as fn:
        json_data = json.load(fn)
    return json_data


def load_yaml(file_name: pathlib.Path) -> Dict:
    """Load yaml file and present the contents in a dictionary.

    Args:
        file_path: path to the .yaml file.
    """
    with open(file_name, 'r', encoding='utf-8') as fn:
        yaml_data = yaml.load(fn, Loader=yaml.FullLoader)
    return yaml_data


def load_toml(file_name: pathlib.Path) -> Dict:
    """Load toml file and present the contents in a dictionary.

    Args:
        file_path: path to the .yaml file.
    """
    toml_data = toml.load(file_name)
    return toml_data


def read_config(
        file_name: pathlib.Path,
        config_type: Optional[str] = None) -> dict:
    """ Reads the config `.yaml` '.toml' or '.json' file with configuration
        data and returns a config dictionary.

    Args:
        file_name: path to the configuration file.
        config_type: type of the configuration file
    """
    load_functions = {
        'yaml': load_yaml,
        'toml': load_toml,
        'json': load_json}
    if config_type is None:
        "Infer config type from file extension"
        config_type = file_name.suffix.replace(".", "")
    try:
        call_function = load_functions[config_type]
        return call_function(file_name=file_name)
    except KeyError:
        return {}


def remove_dir(dir_path: str) -> None:
    shutil.rmtree(dir_path)


class classproperty(property):
    """Class property decorator to make class methods properties in
       Python versions 3.0 - 3.9."""
    def __get__(self, obj, objtype=None):
        return super().__get__(objtype)

    def __set__(self, obj, value):
        super().__set__(type(obj), value)

    def __delete__(self, obj):
        super().__delete__(type(obj))


def wrapped_partial(func, *args, **kwargs):
    """Wraper for `partial` allowing preservation of __name__ and __doc__
    fields in partial functions."""
    partial_func = partial(func, *args, **kwargs)
    update_wrapper(partial_func, func)
    return partial_func


def set_logging_level(logger: logging.Logger, level: str) -> None:
    """Set logging level using string level description."""
    logging_levels = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG,
        "notset": logging.NOTSET}
    try:
        logging_level = logging_levels[level.strip().lower()]
        logger.setLevel(logging_level)
    except KeyError:
        pass


def logging_prefix(module_name: Optional[str]) -> str:
    """Obtain file name and first (parent) folder of a file/module from module
    name to be used as a prefix in logging messages."""
    if module_name:
        directory, file_name = os.path.split(module_name)
        file_name = os.path.splitext(file_name)[0]
        first_folder = os.path.basename(directory)
        logging_prompt = '.'.join([first_folder, file_name])
    else:
        logging_prompt = ""
    return logging_prompt


if __name__ == '__main__':
    from yaml.loader import SafeLoader
    parameters_file = get_package_file('./config/emissions/parameters.yaml')
    print(type(parameters_file))
    print(read_config(parameters_file))
