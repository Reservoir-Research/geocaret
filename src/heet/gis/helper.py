"""Collection of helper (auxiliary) functions for gis classes.

NOTE: The functions require initialized Earth Engine in order to run.
"""
import sys
import ee
import heet.log_setup
from heet.utils import get_package_file, read_config, set_logging_level
from heet.utils import logging_prefix


# Create a logger and set logging level
logger = heet.log_setup.create_logger(logger_name=__name__)
logger_config: dict = read_config(
    get_package_file('./config/logging_levels.yaml'))
set_logging_level(logger=logger, level=logger_config['gis']['helper'])
MODULE_PREFIX = logging_prefix(sys.modules[__name__].__file__)

# =========================================================
# Auxiliary objects used by different gis modules
# =========================================================


class ExportObject:
    """ """

# =========================================================
# Auxiliary helper functions used in the basins.py module
# =========================================================


def all_odd_or_zero(digit_string: ee.String) -> ee.Number:
    """Check if trailing digits are all odd or zero.
    Returns:
        ee.Number with value 1 if trailing digits are all odd or zero and 0
            dd otherwise.
    """
    odd_matches = ee.String(digit_string).match(r"^\d*[013579]$")
    logger.debug(
        f"[{MODULE_PREFIX}.all_odd_or_zero] - " +
        f"oddMatches: {odd_matches.length().getInfo()}")
    return ee.Number(
        ee.Algorithms.If(odd_matches.length().neq(0), 1, 0))


def get_trail_A(id_A, id_B) -> ee.String:
    """Get trailing digits for pfafstetter id A"""
    id_A = ee.String(id_A)
    id_B = ee.String(id_B)

    def algorithm(current, previous):
        previous = ee.List(previous)
        k = ee.Number(previous.length())
        s_A = ee.String(id_A).slice(0, k)
        r_A = ee.String("^").cat(s_A)
        m_B = ee.Number(ee.String(id_B).match(r_A).length())
        return_value = ee.Algorithms.If(m_B.gt(0), ee.List([k]), ee.List([]))
        return previous.add(return_value)

    start = ee.List([[id_A, id_B]])
    indices_list = ee.List.sequence(0, 11, 1)
    lcs_nested_list = indices_list.iterate(algorithm, start)
    lcs_list = ee.List(lcs_nested_list).flatten()
    # Get last element from lcs_list
    last_elem = ee.Number(ee.List(lcs_list).get(-1))
    trail_A = ee.String(id_A).slice(last_elem, None)
    logger.debug(f"[{MODULE_PREFIX}.get_trail_A] - " +
                 f"lcs_nested_list: {lcs_nested_list}")
    logger.debug(f"[{MODULE_PREFIX}.get_trail_A] - " +
                 f"lcs_list: {lcs_list}")
    logger.debug(f"[{MODULE_PREFIX}.get_trail_A] last_elem: " +
                 f"{last_elem.getInfo()}")
    return trail_A


if __name__ == '__main__':
    """ """
