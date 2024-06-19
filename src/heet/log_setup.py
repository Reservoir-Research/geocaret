"""Central module defining global logging settings.

Sets the global logging level, global formatter and the path to
the log file. In case the path does not exist, creates the needed
folder structure.
"""
import logging
import os
import sys
from typing import Tuple, Optional, Union
import errno
from heet.utils import get_package_file, load_yaml

#  Only work with emissions TODO: change global settings for running different
#  software applications, e.g. bathymetry
APP_CONFIG = load_yaml(
    file_name=get_package_file("./config/emissions/general.yaml"))
# Set global logging settings from logging configuration
try:
    logging.getLogger('test').setLevel(APP_CONFIG['logging']['level'])
    LOGGING_LEVEL = APP_CONFIG['logging']['level']
except (ValueError, TypeError):
    LOGGING_LEVEL = logging.DEBUG
# Create logging path
if APP_CONFIG['logging']['log_dir']:
    logging_path = APP_CONFIG['logging']['log_dir']
else:
    logging_path = os.path.join(get_package_file(), 'logs')
# Make logging path folder structure if not present
try:
    os.makedirs(logging_path)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

global_formatter = logging.Formatter(
    '%(asctime)s : %(levelname)s : %(name)s : %(message)s')
global_filehandler = logging.FileHandler(
    os.path.join(logging_path, APP_CONFIG['logging']['log_filename']),
    mode=APP_CONFIG['logging']['mode'])
global_streamhandler = logging.StreamHandler(sys.stdout)

# Stack and exec info for error formatting
STACK_INFO = True  # Stack trace information
EXC_INFO = True  # Exception information


def create_logger(
        logger_name: str,
        formatter: logging.Formatter = global_formatter,
        handlers: Tuple[logging.Handler, ...] = (
            global_filehandler, global_streamhandler),
        logging_level: Optional[Union[str, int]] = None) -> logging.Logger:
    """Create and setup a logger using global settings

    Args:
        logger_name: Name of the logger, usually file name given in
            variable `__name__`

    Returns:
        initialized logging.Logger object
    """
    log = logging.getLogger(logger_name)
    # Get a global logging level
    log.setLevel(LOGGING_LEVEL)
    # Set logging level to the value given in the argument
    if logging_level is not None:
        try:
            log.setLevel(logging_level)
        except (ValueError, TypeError):
            pass
    for handler in handlers:
        handler.setFormatter(formatter)
        log.addHandler(handler)
    return log


if __name__ == '__main__':
    # File entry point to test logging and logger formatting.
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGING_LEVEL)
    logger.addHandler(global_streamhandler)
    logger.addHandler(global_filehandler)
    logger.debug("Sample debug message")
    logger.info("Sample info message")
    logger.error("Sample error message")
    # output sample error message
    try:
        1/0
    except ZeroDivisionError as e:
        logger.error(e, stack_info=STACK_INFO, exc_info=EXC_INFO)
    # output sample exception message
    try:
        1/0
    except ZeroDivisionError as e:
        # stack_info and exc_info are ignored as arguments in logger.exception
        logger.exception(
            "Division by zero exception raised. %s", e,
            stack_info=STACK_INFO,
            exc_info=EXC_INFO)
