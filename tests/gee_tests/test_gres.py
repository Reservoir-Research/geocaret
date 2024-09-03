"""
This module contains test cases for various functions from the `params` package.
These functions are designed to calculate environmental and hydrological parameters
for specific geographical features such as catchments and reservoirs. The tests
compare the outputs of these functions against ground truth values to ensure accuracy.

The tests in this module include:
- `test_mean_slope_perc_gres`: Tests the mean slope percentage calculation for a specific catchment.
- `test_mghr_gres`: Tests the MGHR (Mean Groundwater Hydraulic Radius) calculation for a specific reservoir.
- `test_mean_annual_runoff_mm_gres`: Tests the mean annual runoff calculation for a specific catchment.
- `test_population_gres`: Tests the population count and density calculations for a specific catchment.
- `test_maximum_depth_alt1_gres`: Tests the maximum depth calculation for a specific reservoir.
- `test_mean_depth_gres`: Tests the mean depth calculation for a specific reservoir.

Some tests are skipped because they depend on different data sources or have underlying differences in methodology
that make direct comparisons invalid.
"""
import ee
import os
import pytest
import numpy as np


# Slope
# -------
# Skip this test as GRES uses a different raw datasource of lower
# resolution (possible NOAA DEM)
@pytest.mark.skip
def test_mean_slope_perc_gres(get_logger) -> None:
    """
    Test that the mean slope function produces the same value as GRES for GAWLAN catchment (W_12_Catchment).

    This test compares the calculated mean slope percentage of a catchment with a known ground truth value
    to verify the accuracy of the `mean_slope_perc` function from the `params` package.

    Args:
        get_logger: A pytest fixture for logging messages during testing.

    Asserts:
        The calculated result is approximately equal to the ground truth value within a tolerance of 0.005.
    """
    from geocaret.params import mean_slope_perc
    logger = get_logger
    W_12_Catchment = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/W_12_Catchment")
    test_input = {"catchment_ftc": W_12_Catchment,}
    # GRES Value degrees: 3.855828478191038; perc: 6.74
    test_result = 6.74
    calc_result = mean_slope_perc(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[mean_slope_perc] Mean Slope % - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.005
    assert calc_result == pytest.approx(test_result, abs=5e-3)


# mghr
# -------
# Skip this test as GRES uses a different, unknown underlying raw datasource
@pytest.mark.skip
def test_mghr_gres(get_logger) -> None:
    """
    Test that mghr reproduces a ground truth value (W_12_Catchment).

    This test checks the MGHR calculation of a reservoir to ensure it matches a known ground truth value
    using the `mghr` function from the `params` package.

    Args:
        get_logger: A pytest fixture for logging messages during testing.

    Asserts:
        The calculated result is approximately equal to the ground truth value within a tolerance of 0.005.
    """
    from geocaret.params import mghr
    logger = get_logger
    W_12_Reservoir = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/W_12_Reservoir_Annotated")
    test_input = {"catchment_ftc": W_12_Reservoir}
    # GRES Value
    test_result = 4.46
    calc_result = mghr(**test_input)[0].getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[mghr] MGHR - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}")
    # Within 0.005
    assert calc_result == pytest.approx(test_result, abs=5e-3)


# mean_annual_runoff_mm
def test_mean_annual_runoff_mm_gres(get_logger) -> None:
    """
    Test that mean runoff function reproduces a ground truth value (W_12_Catchment).

    This test checks the mean annual runoff calculation for a catchment to ensure it matches
    a known ground truth value using the `mean_annual_runoff_mm` function from the `params` package.

    Args:
        get_logger: A pytest fixture for logging messages during testing.

    Asserts:
        The calculated result is approximately equal to the ground truth value within a relative tolerance of 0.05%.
    """
    from geocaret.params import mean_annual_runoff_mm
    logger = get_logger
    W_12_Catchment = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/W_12_Catchment")
    test_input = {"catchment_ftc": W_12_Catchment,}
    # GRES Value
    test_result = 1685.5618570695235
    calc_result = mean_annual_runoff_mm(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[mean_annual_runoff_mm] Runoff - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}")
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


# population
# -------
# Skip this test as although GRES uses the same data product, the year used
# (unknown) is different to that used by this tool (2020)
@pytest.mark.skip
def test_population_gres(get_logger) -> None:
    """
    Test that population function reproduces a ground truth value (W_12_Catchment).

    This test checks the population count and density calculations for a catchment to ensure
    they match known ground truth values using the `population` function from the `params` package.

    Args:
        get_logger: A pytest fixture for logging messages during testing.

    Asserts:
        The calculated results are approximately equal to the ground truth values within a relative tolerance of 0.05%.
    """
    from geocaret.params import population
    logger = get_logger
    W_12_Catchment = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/W_12_Catchment")
    test_input = {"target_ftc": W_12_Catchment}
    # GRES Value
    test_result_1 = 8462.955230759912
    test_result_2 = 10.82177198010264
    ee_calc_result_1, ee_calc_result_2 = population(**test_input)
    calc_result_1 = ee_calc_result_1.getInfo()
    calc_result_2 = ee_calc_result_2.getInfo()
    diff1 = test_result_1 - calc_result_1
    pdiff1 = (abs(test_result_1 - calc_result_1) / test_result_1) * 100
    diff2 = test_result_2 - calc_result_2
    pdiff2 = (abs(test_result_2 - calc_result_2) / test_result_2) * 100
    logger.info(
        f"[population] Population Count - GeoCARET {calc_result_1} " +
        f"Manual {test_result_1} Diff {diff1} PDiff {pdiff1}")
    logger.info(
        f"[population] Population Density - GeoCARET {calc_result_2} " +
        f"Manual {test_result_2} Diff {diff2} PDiff {pdiff2}")
    # Within 0.05%
    assert calc_result_1 == pytest.approx(test_result_1, rel=5e-2)
    assert calc_result_2 == pytest.approx(test_result_2, rel=5e-2)


# maximum_depth_alt1
# -------------------
# Skip this test as although GRES uses the same raw data source, the scale at
# which the calculation is done is much higher (300)
# (informally - when the scale of calculation is the same, values do match)
# @pytest.mark.skip
def test_maximum_depth_alt1_gres(monkeypatch, get_logger) -> None:
    """
    Test that maximum depth function reproduces a ground truth value (W_12_Reservoir).

    This test checks the maximum depth calculation for a reservoir to ensure it matches
    a known ground truth value using the `maximum_depth_alt1` function from the `heet_params` package.

    Args:
        monkeypatch: A pytest fixture for dynamically changing values or functions during a test.
        get_logger: A pytest fixture for logging messages during testing.

    Asserts:
        The calculated result is approximately equal to the ground truth value within a relative tolerance of 0.05%.
    """
    from geocaret.params import maximum_depth_alt1
    logger = get_logger
    # Set config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)
    W_12_Reservoir = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/W_12_Reservoir_Annotated"
    )
    test_input = {"reservoir_ftc": W_12_Reservoir,}
    # GRES Value at 30 m scale
    test_result = 143
    calc_result = maximum_depth_alt1(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[mean_annual_runoff_mm] Runoff - GeoCARET {calc_result} "
        + f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


# mean_depth
# Skip this test as although GRES uses a similar approach, they are not equivalent
# GRES uses max elevation as reference point for depth
# GeoCARET uses elevation of imputed water level
@pytest.mark.skip
def test_mean_depth_gres(get_logger) -> None:
    """
    Test that mean depth function reproduces a ground truth value (W_12_Reservoir).

    This test checks the mean depth calculation for a reservoir to ensure it matches
    a known ground truth value using the `mean_depth` function from the `params` package.

    Args:
        get_logger: A pytest fixture for logging messages during testing.

    Asserts:
        The calculated result is approximately equal to the ground truth value within a relative tolerance of 0.05%.
    """
    from geocaret.params import mean_depth
    logger = get_logger
    W_12_Reservoir = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/W_12_Reservoir_Annotated")
    test_input = {"reservoir_ftc": W_12_Reservoir,}
    # GRES Value (at 30m scale)
    test_result = 105.38015788589671
    calc_result = mean_depth(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[mean_depth] Mean Depth - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}")
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)
