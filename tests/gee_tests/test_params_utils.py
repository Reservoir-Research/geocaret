"""
Module for testing imputed dam height calculations.

This module includes unit tests to verify the accuracy of functions related to 
imputed dam height calculations in the `reservoir` module.
"""
import ee
import os
import pytest


def test_impute_dam_height(get_logger) -> None:
    """
    Test that imputed dam height calculations are accurate for a set of test values.

    This function verifies that the dam height calculated using the `impute_dam_height` function
    from the `reservoir` module matches the expected result. It checks the correctness of the
    imputed height based on predefined input parameters and compares it with a known correct value.

    Args:
        get_logger (function): A function to obtain a logger instance for logging test results.

    Asserts:
        - The calculated dam height should match the expected result exactly.

    Test Details:
        - Test Input:
            - power_capacity: 10 (unit not specified)
            - turbine_efficiency: 85 (percent)
            - plant_depth: 0 (unit not specified)
            - mad_m3_pers: 24 (cubic meters per second)
        - Expected Result: 49.969 (unit not specified)
    """
    from geocaret.reservoir import impute_dam_height
    test_input = {
        'power_capacity': ee.Number(10),
        'turbine_efficiency': ee.Number(85),
        'plant_depth': ee.Number(0),
        'mad_m3_pers': ee.Number(24),
    }
    test_result =  49.969
    calc_result = impute_dam_height(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    logger = get_logger
    logger.info(f'[test_impute_dam_height] Dam Height - GeoCARET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    assert calc_result  == test_result
