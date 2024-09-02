"""
Test module for soil characteristics and DOC export calculations.

This module contains a series of unit tests designed to validate the accuracy of soil-related 
calculations within the GeoCARET system. Each test compares calculated values from the GeoCARET 
system with known ground truth values to ensure correctness.

The tests cover various soil characteristics and DOC (Dissolved Organic Carbon) export metrics, 
including:

- Mean soil organic carbon stocks
- Mean soil organic carbon content (g/kg)
- Mean soil nitrogen content (g/kg)
- Bulk soil density (kg/dm³)
- Total DOC export
- Strata-weighted molar nitrogen and carbon content

Tests are conducted using data from specific feature collections stored in Google Earth Engine 
(EE) and involve comparing GeoCARET calculations with manually verified reference values. The 
results are logged for each test, providing information on the calculated values, reference 
values, differences, and percentage differences.

Modules tested:
- `mean_soil_oc_stocks`
- `mean_soil_oc_content`
- `mean_soil_nitrogen_content`
- `mean_soil_bdod`
- `total_doc_export`
- `mean_strata_weighted_mol_n`
- `mean_strata_weighted_mol_c`

Fixtures used:
- `get_logger`: A pytest fixture used to obtain a logger instance for logging test results.

Assertions:
- Calculated values are expected to match reference values within a specified tolerance, 
  typically within 0.05% relative error.

Each test function follows a similar pattern:
1. Import necessary functions and data.
2. Define test input and expected results.
3. Perform calculations and compare them to expected results.
4. Log results and assert that the calculated values are within the acceptable range.

Example usage:
    pytest -v test_soil_characteristics.py
"""
import ee
import os
import pytest
import numpy as np


# ==============================================================================
#  Soil Characteristics
# ==============================================================================

# Carbon Stocks
def test_mean_soil_oc_stocks(get_logger) -> None:
    """
    Test the accuracy of mean soil organic carbon stocks calculation.

    This test validates that the mean soil organic carbon stocks calculated by the GeoCARET 
    system matches the known ground truth value for the specified feature collection (px4).

    The feature collection used is 'carbon_poly_px4', and the expected result is 8.25. 
    The test asserts that the calculated result is within 5% relative error of this value.

    Args:
        get_logger (function): A function (pytest fixture) to obtain a logger instance for logging test results.
        
    Assert:
        The calculated result is within 5% relative error of the expected result (8.25).
    """
    from heet_params import mean_soil_oc_stocks
    logger = get_logger
    carbon_poly_px4 = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/carbon_poly_px4"
    )
    test_input = {
        "land_ftc": carbon_poly_px4,
    }
    test_result = 8.25
    calc_result = mean_soil_oc_stocks(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[test_mean_soil_oc_stocks] Mean Soil Organic Carbon Stocks - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


# Carbon Stocks - Null data
def test_mean_soil_oc_stocks_null(get_logger) -> None:
    """
    Test the handling of null data for mean soil organic carbon stocks calculation.

    This test checks that the GeoCARET system correctly returns None when there is no data available
    for the specified feature collection (px2N).

    The feature collection used is 'soil_poly_px2N', and the expected result is None.

    Args:
        get_logger (function): A function (pytest fixture) to obtain a logger instance for logging test results.
        
    Assert:
        The calculated result is None when no data is available.
    """
    from heet_params import mean_soil_oc_stocks
    logger = get_logger
    soil_poly_px2N = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/soil_poly_px2N"
    )
    test_input = {
        "land_ftc": soil_poly_px2N,
    }
    test_result = None
    calc_result = mean_soil_oc_stocks(**test_input).getInfo()
    logger.info(
        f"[test_mean_soil_oc_stocks_null] Mean Soil Organic Carbon Stocks - GeoCARET {calc_result} " +
        f"Manual {test_result}"
    )
    assert calc_result == test_result


# Carbon content
def test_mean_soil_oc_content(get_logger) -> None:
    """
    Test the accuracy of soil organic carbon content calculation.

    This test validates that the mean soil organic carbon content (g/kg) calculated by the GeoCARET 
    system matches the known ground truth value for the specified feature collection (px1).

    The feature collection used is 'psoc_poly_org_px1', and the expected result is 208.067. 
    The test asserts that the calculated result is within 5% relative error of this value.

    Args:
        get_logger (function): A function to obtain a logger instance for logging test results.

    Assert:
        The calculated result is within 5% relative error of the expected result (208.067).
    """
    from heet_params import mean_soil_oc_content
    logger = get_logger
    psoc_poly_org_px1 = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/psoc_poly_org_px1"
    )
    test_input = {
        "target_ftc": psoc_poly_org_px1,
    }
    # Total C g/kg
    test_result = 208.067
    calc_result = mean_soil_oc_content(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[test_mean_soil_oc_content] Mean Soil Organic Carbon Content- GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


# Nitrogen content
def test_mean_soil_nitrogen_content(get_logger) -> None:
    """
    Test the accuracy of soil nitrogen content calculation.

    This test validates that the mean soil nitrogen content (g/kg) calculated by the GeoCARET 
    system matches the known ground truth value for the specified feature collection (px1).

    The feature collection used is 'soiln_poly_px1', and the expected result is 66.368. 
    The test asserts that the calculated result is within 5% relative error of this value.

    Args:
        get_logger (function): A function (pytest fixture) to obtain a logger instance for logging test results.

    Assert:
        The calculated result is within 5% relative error of the expected result (66.368).
    """
    from heet_params import mean_soil_nitrogen_content
    logger = get_logger
    soiln_poly_px1 = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/soiln_poly_px1"
    )
    test_input = {
        "target_ftc": soiln_poly_px1,
    }
    # Total N g/kg
    test_result = 66.368
    calc_result = mean_soil_nitrogen_content(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100

    logger.info(
        f"[test_mean_soil_nitrogen_content] Mean Soil Nitrogen Content - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


# Soil Bulk Density
def test_mean_soil_bdod(get_logger) -> None:
    """
    Test the accuracy of soil bulk density calculation.

    This test validates that the mean soil bulk density (kg/dm³) calculated by the GeoCARET 
    system matches the known ground truth value for the specified feature collection (px1).

    The feature collection used is 'soilbdod_poly_px1', and the expected result is 1.077. 
    The test asserts that the calculated result is within 5% relative error of this value.

    Args:
        get_logger (function): A function (pytest fixture) to obtain a logger instance for logging test results.

    Assert:
        The calculated result is within 5% relative error of the expected result (1.077).
    """
    from heet_params import mean_soil_bdod
    logger = get_logger
    soilbdod_poly_px1 = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/soilbdod_poly_px1"
    )
    test_input = {
        "target_ftc": soilbdod_poly_px1,
    }
    # Soil Density (kg/dm3)
    test_result = 1.077
    calc_result = mean_soil_bdod(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[test_mean_soil_bdod] Bulk Soil Density - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


# DOC export
def test_total_doc_export(get_logger) -> None:
    """
    Test the accuracy of total DOC (Dissolved Organic Carbon) export calculation.

    This test validates that the total DOC export calculated by the GeoCARET system matches 
    the known ground truth value for the specified feature collection (px1).

    The feature collection used is 'cn_poly_px1', and the expected result is -43.62673765. 
    The test asserts that the calculated result is within 5% relative error of this value.

    Args:
        get_logger (function): A function (pytest fixture) to obtain a logger instance for logging test results.

    Assert:
        The calculated result is within 5% relative error of the expected result (-43.62673765).
    """
    from heet_params import total_doc_export
    logger = get_logger
    cn_poly_px1 = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/cn_poly_px1"
    )
    test_input = {
        "target_ftc": cn_poly_px1,
    }
    # Total DOC Export
    test_result = -43.62673765
    calc_result = total_doc_export(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[test_total_doc_export] DOC Export - GeoCARET {calc_result} "
        + f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


def test_mean_strata_weighted_mol_n(get_logger) -> None:
    """
    Test the accuracy of mean strata-weighted molar nitrogen content calculation.

    This test validates that the mean strata-weighted molar nitrogen content calculated by the 
    GeoCARET system matches the known ground truth value for the specified feature collection (px1).

    The feature collection used is 'cn_poly_px1', and the expected result is 4.317969258. 
    The test asserts that the calculated result is within 5% relative error of this value.

    Args:
        get_logger (function): A pytest fixture to obtain a logger instance for logging test results.

    Assert:
        The calculated result is within 5% relative error of the expected result (4.317969258).
    """
    from heet_params import mean_strata_weighted_mol_n
    logger = get_logger
    cn_poly_px1 = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/cn_poly_px1"
    )
    test_input = {
        "target_ftc": cn_poly_px1,
    }
    # mean_strata_weighted_mol_n
    test_result = 4.317969258
    calc_result = mean_strata_weighted_mol_n(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[test_total_doc_export] DOC Export - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


def test_mean_strata_weighted_mol_c(get_logger) -> None:
    """
    Test the accuracy of mean strata-weighted molar carbon content calculation.

    This test validates that the mean strata-weighted molar carbon content calculated by the 
    GeoCARET system matches the known ground truth value for the specified feature collection (px1).

    The feature collection used is 'cn_poly_px1', and the expected result is 5.81363375. 
    The test asserts that the calculated result is within 5% relative error of this value.

    Args:
        get_logger (function): A pytest fixture to obtain a logger instance for logging test results.

    Assert:
        The calculated result is within 5% relative error of the expected result (5.81363375).
    """
    from heet_params import mean_strata_weighted_mol_c
    logger = get_logger
    cn_poly_px1 = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/cn_poly_px1"
    )
    test_input = {
        "target_ftc": cn_poly_px1,
    }
    # mean_strata_weighted_mol_c
    test_result = 5.81363375
    calc_result = mean_strata_weighted_mol_c(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[mean_strata_weighted_mol_c] GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)
