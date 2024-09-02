"""
This module contains a test case for delineating the main river using the 
`delineate_river` function from the `heet_river` package. The test ensures that 
the function runs without errors when applied to a known dam and produces the 
expected results.

The test case included:
- `test_rwo_delineate_river`: Tests that the delineation of the main river runs 
  successfully for a specified dam without raising any errors.
"""
import ee
import os
import pytest
import logging


# Delineation of main river
def test_rwo_delineate_river(get_logger) -> None:
    """
    Test that delineation of the main river runs without error for a known dam.

    This test checks the `delineate_river` function from the `heet_river` package 
    to ensure it executes successfully without raising any errors when provided 
    with valid input data for a known dam.

    Args:
        get_logger: A pytest fixture for logging messages during testing.

    Asserts:
        The function runs without raising a `MyError` exception. If an exception is 
        raised, the test fails and logs an error message.
    """
    from heet_river import delineate_river
    catchmentAssetName = "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/C_1201"
    catchment_ftc = ee.FeatureCollection(catchmentAssetName)
    reservoirAssetName = "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/R_1201"
    res_ftc = ee.FeatureCollection(reservoirAssetName)
    snappedAssetName = "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/PS_1201"
    damFeat = ee.FeatureCollection(snappedAssetName)
    try:
        mainRiverVector, riverVector = delineate_river(damFeat, res_ftc, "1201")
        msg = "delineate_river completed without explicit error(s)"
    except MyError:
        msg = "delineate_river failed with error(s)"
        pytest.fail("delineate_river failed with error(s)")
    logger = get_logger
    logger.info(f"[test_rwo_delineate_river] " + f"{msg}")
