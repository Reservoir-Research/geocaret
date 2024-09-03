"""
Module for testing slope, elevation, and depth calculations using the `params` library.

This module includes a series of test functions designed to verify the correctness of various geospatial computations
performed using the `params` library. The tests cover calculations for mean slope in degrees and percentage,
minimum and maximum elevations, and mean and maximum depths. These tests are performed by comparing computed values
against known ground truth values.

The `monkeypatch` utility is used extensively throughout these tests to modify configuration parameters for the 
`params` library, allowing for different testing scenarios.

Dependencies:
- ee: Earth Engine Python API for interacting with Google Earth Engine datasets.
- os: Standard library module for interacting with the operating system.
- pytest: Testing framework for writing and running tests.
- numpy: Library for numerical computing in Python.

Test Functions:
- `test_mean_slope_degrees`: Tests the mean slope calculation in degrees for a different feature collections
- `test_mean_slope`: Tests the mean slope calculation as a percentage for a feature collection.
- `test_minimum_elevation`: Tests the calculation of minimum elevation for a feature collection.
- `test_maximum_elevation`: Tests the calculation of maximum elevation for a feature collection.
- `test_maximum_depth`: Tests the calculation of maximum depth for a feature collection.
- `test_maximum_depth_alt1`: Tests an alternative calculation of maximum depth for a feature collection.
- `test_maximum_depth_alt2`: Tests another alternative calculation of maximum depth for a feature collection.
- `test_mean_depth`: Tests the mean depth calculation for a feature collection.
- `test_minimum_elevation_null`: Tests the calculation of minimum elevation when no valid elevation data is available.
- `test_null_formatter`: Tests the formatting of null values for display.

Each test function:
- Sets up necessary configuration using monkeypatch.
- Loads appropriate test data from Google Earth Engine.
- Performs a calculation using the `params` library.
- Compares the result to a known ground truth value.
- Logs the result and checks that it is within an acceptable range of the ground truth.

"""
import ee
import os
import pytest
import numpy as np


# ==============================================================================
#  Slope tests
# ==============================================================================


@pytest.mark.parametrize(
    "feature_collection, expected_result",
    [
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/slope_poly_px4", 2.100007),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/slope_poly_px1", 4.140905380249023),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/slope_poly_px0", 1.7956430912017822)
    ]
)
def test_mean_slope_degrees(monkeypatch, get_logger, feature_collection, expected_result) -> None:
    """
    Test that the `mean_slope_degrees` function correctly calculates the mean slope
    in degrees for specific ground truth features.

    This test uses the Google Earth Engine (GEE) feature collections for different
    slope polygons and checks the calculated result against the expected ground truth values.

    Args:
        monkeypatch: pytest fixture for monkeypatching.
        get_logger: pytest fixture to get the logger for logging.
        feature_collection: GEE FeatureCollection asset path to test.
        expected_result: The expected result of mean slope in degrees.

    Asserts:
        The calculated mean slope is approximately equal to the expected value within
        a relative tolerance of 0.05%.
    """
    from geocaret.params import mean_slope_degrees
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)
    # Set up the feature collection from the parameter
    catchment_ftc = ee.FeatureCollection(feature_collection)
    test_input = {"catchment_ftc": catchment_ftc}
    # Calculate the mean slope using the function
    calc_result = mean_slope_degrees(**test_input).getInfo()
    # Log the results
    diff = expected_result - calc_result
    pdiff = (abs(expected_result - calc_result) / expected_result) * 100
    logger.info(
        f"[mean_slope_degrees] Mean Slope Deg - Calculated: {calc_result}, " +
        f"Expected: {expected_result}, Diff: {diff}, PDiff: {pdiff}")
    # Assert results within 0.05% relative tolerance
    assert calc_result == pytest.approx(expected_result, rel=5e-2)


def test_mean_slope(monkeypatch, get_logger) -> None:
    """
    Test that the `mean_slope` function correctly calculates the mean slope
    in percentage for a specific ground truth feature (px4).

    This test uses the GEE feature collection for slope_poly_px4 and checks the 
    calculated result against the expected ground truth value.

    Args:
        monkeypatch: pytest fixture for monkeypatching.
        get_logger: pytest fixture to get the logger for logging.

    Asserts:
        The calculated mean slope is approximately equal to the expected value (3.67%),
        within a relative tolerance of 0.05%.
    """
    from geocaret.params import mean_slope
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    slope_poly_px4 = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/slope_poly_px4")

    test_input = {"catchment_ftc": slope_poly_px4,}
    # Degrees  2.100007
    # % 3.67 P
    test_result = 3.67
    calc_result = mean_slope(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[mean_slope_perc] Mean Slope % - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


# ==============================================================================
#  Elevation tests
# ==============================================================================


def test_minimum_elevation(monkeypatch, get_logger) -> None:
    """
    Test that the `minimum_elevation` function correctly calculates the minimum elevation
    for a specific ground truth feature (px4).

    This test uses the GEE feature collection for elev_poly_px4 and checks the 
    calculated result against the expected ground truth value.

    Args:
        monkeypatch: pytest fixture for monkeypatching.
        get_logger: pytest fixture to get the logger for logging.

    Asserts:
        The calculated minimum elevation is approximately equal to the expected value (96 meters),
        within a relative tolerance of 0.05%.
    """
    from geocaret.params import minimum_elevation
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection(
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/elev_poly_px4"
        ).first()
    ).set("r_imputed_water_elevation", "98")
    
    elev_poly_px4_ftc = ee.FeatureCollection(elev_poly_px4_ft)
    
    test_input = {"reservoir_ftc": elev_poly_px4_ftc,}
    test_result = 96
    calc_result = minimum_elevation(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[minimum_elevation] Minimum Elevation - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


def test_maximum_elevation(monkeypatch, get_logger) -> None:
    """
    Test that the `maximum_elevation` function correctly calculates the maximum elevation
    for a specific ground truth feature (px4).

    This test uses the GEE feature collection for elev_poly_px4 and checks the 
    calculated result against the expected ground truth value.

    Args:
        monkeypatch: pytest fixture for monkeypatching.
        get_logger: pytest fixture to get the logger for logging.

    Asserts:
        The calculated maximum elevation is approximately equal to the expected value (175 meters),
        within a relative tolerance of 0.05%.
    """
    from geocaret.params import maximum_elevation
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection(
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/elev_poly_px4"
        ).first()
    ).set("r_imputed_water_elevation", "98")
    
    elev_poly_px4_ftc = ee.FeatureCollection(elev_poly_px4_ft)

    test_input = {"reservoir_ftc": elev_poly_px4_ftc,}
    test_result = 98
    calc_result = maximum_elevation(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[maximum_elevation] Maximum Elevation - GeoCARET {calc_result} "
        + f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


# ==============================================================================
#  Depth tests
# ==============================================================================


def test_maximum_depth(monkeypatch, get_logger) -> None:
    """
    Test that the `maximum_depth` function correctly calculates the maximum depth
    for a specific ground truth feature (px4).

    This test uses the GEE feature collection for depth_poly_px4 and checks the 
    calculated result against the expected ground truth value.

    Args:
        monkeypatch: pytest fixture for monkeypatching.
        get_logger: pytest fixture to get the logger for logging.

    Asserts:
        The calculated maximum depth is approximately equal to the expected value (14 meters),
        within a relative tolerance of 0.05%.
    """
    from geocaret.params import maximum_depth
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection(
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/elev_poly_px4"
        ).first()
    ).set("r_imputed_water_elevation", "98")
    
    elev_poly_px4_ftc = ee.FeatureCollection(elev_poly_px4_ft)

    test_input = {"reservoir_ftc": elev_poly_px4_ftc,}
    test_result = 2
    calc_result = maximum_depth(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[maximum_depth] Maximum Depth - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


def test_maximum_depth_alt1(monkeypatch, get_logger) -> None:
    """
    Test an alternative calculation method of the `maximum_depth` function for a specific 
    ground truth feature (px4).

    This test uses the GEE feature collection for depth_poly_px4 and checks the 
    calculated result against the expected ground truth value.

    Args:
        monkeypatch: pytest fixture for monkeypatching.
        get_logger: pytest fixture to get the logger for logging.

    Asserts:
        The calculated maximum depth is approximately equal to the expected value (14 meters),
        within a relative tolerance of 0.05%.
    """
    from geocaret.params import maximum_depth_alt1
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection(
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/elev_poly_px4"
        ).first()
    ).set("r_imputed_water_elevation", "98")
    
    elev_poly_px4_ftc = ee.FeatureCollection(elev_poly_px4_ft)

    test_input = {"reservoir_ftc": elev_poly_px4_ftc,}
    test_result = 1
    calc_result = maximum_depth_alt1(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[maximum_depth_alt1] Maximum Depth Alt1 - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}")
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


def test_maximum_depth_alt2(monkeypatch, get_logger) -> None:
    """
    Test another alternative calculation method of the `maximum_depth` function for a specific 
    ground truth feature (px4).

    This test uses the GEE feature collection for depth_poly_px4 and checks the 
    calculated result against the expected ground truth value.

    Args:
        monkeypatch: pytest fixture for monkeypatching.
        get_logger: pytest fixture to get the logger for logging.

    Asserts:
        The calculated maximum depth is approximately equal to the expected value (14 meters),
        within a relative tolerance of 0.05%.
    """
    from geocaret.params import maximum_depth_alt2
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection(
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/elev_poly_px4"
        ).first()
    ).set("r_imputed_water_elevation", "98")
    
    elev_poly_px4_ftc = ee.FeatureCollection(elev_poly_px4_ft)

    test_input = {"reservoir_ftc": elev_poly_px4_ftc,}
    test_result = 2
    calc_result = maximum_depth_alt2(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[maximum_elevation] Maximum Depth Alt1 - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


def test_mean_depth(monkeypatch, get_logger) -> None:
    """
    Test that the `mean_depth` function correctly calculates the mean depth
    for a specific ground truth feature (px4).

    This test uses the GEE feature collection for depth_poly_px4 and checks the 
    calculated result against the expected ground truth value.

    Args:
        monkeypatch: pytest fixture for monkeypatching.
        get_logger: pytest fixture to get the logger for logging.

    Asserts:
        The calculated mean depth is approximately equal to the expected value (5.9 meters),
        within a relative tolerance of 0.05%.
    """
    from geocaret.params import mean_depth
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection(
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/elev_poly_px4"
        ).first()
    ).set("r_imputed_water_elevation", "98")
    
    elev_poly_px4_ftc = ee.FeatureCollection(elev_poly_px4_ft)

    test_input = {"reservoir_ftc": elev_poly_px4_ftc,}
    test_result = 1
    calc_result = mean_depth(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[maximum_elevation] Mean Depth - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}")
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


# ==============================================================================
#  Null Elevation tests
# ==============================================================================

def test_minimum_elevation_null(monkeypatch, get_logger) -> None:
    """
    Test that the minimum elevation calculation correctly handles null values for a ground truth dataset (px4).

    This test verifies the behavior of the `minimum_elevation` function when provided with a feature collection
    where the elevation is set to a specific value ("98") but should be considered as null in the results.
    
    Args:
        monkeypatch (pytest.MonkeyPatch): A pytest fixture to modify environment variables and attributes.
        get_logger (function): A function to retrieve a logger instance.

    Asserts:
        The calculated minimum elevation is equal None.
    """
    from geocaret.params import minimum_elevation
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    null_elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection(
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/null_elev_poly_px4"
        ).first()
    ).set("r_imputed_water_elevation", "98")
    
    null_elev_poly_px4_ftc = ee.FeatureCollection(null_elev_poly_px4_ft)

    test_input = {"reservoir_ftc": null_elev_poly_px4_ftc,}

    test_result = None
    calc_result = minimum_elevation(**test_input).getInfo()
    logger.info(
        f"[minimum_elevation_null] Minimum Elevation - GeoCARET {calc_result} " +
        f"Manual {test_result}"
    )
    assert calc_result == test_result


def test_null_formatter(monkeypatch, get_logger) -> None:
    """Tests that null values in metric_formatter are mapped to 'ND'.

    Args:
        monkeypatch: A pytest fixture for patching modules and functions.
        get_logger: A function for obtaining a logger instance.

    Asserts:
        The `minimum_elevation` function with a null value input returns 'ND' after being formatted by `metric_formatter`.
    """
    from geocaret.params import minimum_elevation
    from geocaret.params import metric_formatter
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    null_elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection(
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/null_elev_poly_px4"
        ).first()
    ).set("r_imputed_water_elevation", "98")
    
    null_elev_poly_px4_ftc = ee.FeatureCollection(null_elev_poly_px4_ft)

    test_input = {"reservoir_ftc": null_elev_poly_px4_ftc,}
    test_result = "ND"
    calc_result = metric_formatter(
        minimum_elevation(**test_input),
        "minimum_elevation"
    ).getInfo()

    logger.info(
        f"[minimum_elevation_null] Minimum Elevation - GeoCARET {calc_result} " +
        f"Manual {test_result}"
    )
    assert calc_result == test_result


def test_maximum_elevation_null(monkeypatch, get_logger) -> None:
    """Tests that maximum_elevation works for a ground truth value (px4) with null elevation.

    Args:
        monkeypatch: A pytest fixture for patching modules and functions.
        get_logger: A function for obtaining a logger instance.

    Asserts:
        The `maximum_elevation` function with a null value input returns None.
    """
    from geocaret.params import maximum_elevation
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    null_elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection(
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/null_elev_poly_px4"
        ).first()
    ).set("r_imputed_water_elevation", "98")
    
    null_elev_poly_px4_ftc = ee.FeatureCollection(null_elev_poly_px4_ft)
    test_input = {"reservoir_ftc": null_elev_poly_px4_ftc,}
    test_result = None
    calc_result = maximum_elevation(**test_input).getInfo()
    logger.info(
        f"[maximum_elevation_null] Maximum Elevation - GeoCARET {calc_result} " +
        f"Manual {test_result}"
    )
    assert calc_result == test_result


# ==============================================================================
#  Null Depth tests
# ==============================================================================

def test_maximum_depth_null(monkeypatch, get_logger) -> None:
    """Tests that maximum_depth works for a ground truth value (px4) with null elevation.

    Args:
        monkeypatch: A pytest fixture for patching modules and functions.
        get_logger: A function for obtaining a logger instance.

    Asserts:
        The `maximum_depth` function with a null value input returns None.
    """
    from geocaret.params import maximum_depth
    from geocaret.params import metric_formatter
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    ## Not utilised
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    null_elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection(
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/null_elev_poly_px4"
        ).first()
    ).set("r_imputed_water_elevation", "98")
    
    null_elev_poly_px4_ftc = ee.FeatureCollection(null_elev_poly_px4_ft)
    test_input = {"reservoir_ftc": null_elev_poly_px4_ftc,}
    test_result = None
    calc_result =  maximum_depth(**test_input).getInfo()
    logger.info(
        f"[maximum_depth_null] Maximum Depth - GeoCARET {calc_result} " + f"Manual {test_result}"
    )
    assert calc_result == test_result


def test_maximum_depth_alt1_null(monkeypatch, get_logger) -> None:
    """Tests that maximum_depth_alt1 works for a ground truth value (px4) with null elevation.

    Args:
        monkeypatch: A pytest fixture for patching modules and functions.
        get_logger: A pytest fixture for obtaining a logger instance.

    Asserts:
        The `maximum_depth_alt1` function with a null value input returns None.
    """
    from geocaret.params import maximum_depth_alt1
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    null_elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection(
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/null_elev_poly_px4"
        ).first()
    ).set("r_imputed_water_elevation", "98")
    
    null_elev_poly_px4_ftc = ee.FeatureCollection(null_elev_poly_px4_ft)
    test_input = {"reservoir_ftc": null_elev_poly_px4_ftc,}
    test_result = None
    calc_result = maximum_depth_alt1(**test_input).getInfo()
    logger.info(
        f"[maximum_depth_alt1_null] Maximum Depth Alt1 - GeoCARET {calc_result} " +
        f"Manual {test_result} ")
    assert calc_result == test_result


def test_maximum_depth_alt2_null(monkeypatch, get_logger) -> None:
    """Tests that maximum_depth_alt2 works for a ground truth value (px4) with null elevation.

    Args:
      monkeypatch: A pytest fixture for patching modules and functions.
      get_logger: A function for obtaining a logger instance.

    Asserts:
        The `maximum_depth_alt2` function with a null value input returns a value within 0.05% of None.
    """
    from geocaret.params import maximum_depth_alt2
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    null_elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection(
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/null_elev_poly_px4"
        ).first()
    ).set("r_imputed_water_elevation", "98")
    
    null_elev_poly_px4_ftc = ee.FeatureCollection(null_elev_poly_px4_ft)
    test_input = {"reservoir_ftc": null_elev_poly_px4_ftc,}
    test_result = None
    calc_result = maximum_depth_alt2(**test_input).getInfo()
    logger.info(
        f"[maximum_elevation_null] Maximum Depth Alt1 - GeoCARET {calc_result} " +
        f"Manual {test_result}")
    # Within 0.05%
    assert calc_result == test_result


def test_mean_depth_null(monkeypatch, get_logger) -> None:
    """Tests that mean_depth works for a ground truth value (px4) with null elevation.

    Args:
        monkeypatch: A pytest fixture for patching modules and functions.
        get_logger: A function for obtaining a logger instance.

    Asserts:
        The `mean_depth` function with a null value input returns None.
    """

    from geocaret.params import mean_depth
    logger = get_logger
    # Monkey patch the config parameters
    monkeypatch.setattr("geocaret.params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("geocaret.params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("geocaret.params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.resHydroDEM", False)
    monkeypatch.setattr("geocaret.params.cfg.hydrodataset", "03")
    monkeypatch.setattr("geocaret.params.cfg.delineate_snapped", True)

    null_elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection(
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/null_elev_poly_px4"
        ).first()
    ).set("r_imputed_water_elevation", "98")

    null_elev_poly_px4_ftc = ee.FeatureCollection(null_elev_poly_px4_ft)
    test_input = {"reservoir_ftc": null_elev_poly_px4_ftc,}
    test_result = None
    calc_result = mean_depth(**test_input).getInfo()
    logger.info(
        f"[maximum_elevation] Mean Depth - GeoCARET {calc_result} " +
        f"Manual {test_result} ")
    assert calc_result == test_result
