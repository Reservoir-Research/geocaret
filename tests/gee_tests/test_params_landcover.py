"""
This module contains unit tests for functions related to landcover analysis
in the heet_params module.
"""
import ee
import os
import pytest
import numpy as np


@pytest.mark.parametrize(
    "feature_collection, expected_result, test_description",
    [
        # Single-pixel ground truth example
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_poly_px1", 
        np.array([0, 0, 0, 0, 0, 1, 0, 0, 0]), 
        'Single-pixel ground truth example'),
        # Two-pixel two-category ground truth example
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_poly_px2", 
        np.array([0, 0, 0.5, 0, 0, 0.5, 0, 0, 0]), 
        'Two-pixel two-category ground truth example'),
        # Three-pixel two-category ground truth example
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_poly_px3", 
        np.array([0, 2/3, 0, 0, 0, 1/3, 0, 0, 0]), 
        'Three-pixel two-category ground truth example'),
        # Four-pixel two-category ground truth example
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_poly_px4", 
        np.array([0, 0, 0.25, 0.75, 0, 0, 0, 0, 0]), 
        'Four-pixel two-category ground truth example'),
        # Two-pixel (1, 0.5, 0.5) two-category ground truth example
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_poly_px155", 
        np.array([0, 0, 0.5, 0, 0, 0.5, 0, 0, 0]), 
        'Two-pixel (1, 0.5, 0.5) two-category ground truth example')
    ]
)
def test_landcover(get_logger, feature_collection, expected_result, test_description) -> None:
    """
    Tests that `landcover` works for various ground truth examples.

    Args:
        get_logger: A pytest fixture for obtaining a logger instance.
        feature_collection: GEE FeatureCollection asset path to test.
        expected_result: The expected landcover fractions as a numpy array.
        test_description: A description of the test case for logging.

    Asserts:
        Calculated landcover fractions are approximately equal to the expected test result
        within a small tolerance.
    """
    from heet_params import landcover
    logger = get_logger
    test_input = {
        'land_ftc': ee.FeatureCollection(feature_collection),
        'landcover_analysis_file_str': 'projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds'
    }
    calc_result = landcover(**test_input).getInfo() 
    diff = expected_result - calc_result
    pdiff = (abs(expected_result - calc_result) / expected_result) * 100
    logger.info(
        f'[test_landcover] {test_description} - GeoCARET {calc_result} ' + 
        f'Manual {expected_result} Diff {diff} PDiff {pdiff}'
    )
    assert calc_result == pytest.approx(expected_result)


@pytest.mark.parametrize(
    "feature_collection, expected_result",
    [
        (
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_bysoil_poly_org_px12",
            np.array([
                0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 6/12, 1/12, 4/12, 0, 0, 1/12, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0 
            ])
        ),
        (
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_bysoil_poly_min_px12",
            np.array([
                0, 0, 10/12, 1/12, 1/12, 0, 0, 0, 0,         
                0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0
            ])
        ),
        (
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_bysoil_poly_nodata_px1",
            np.array([
                0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 1, 0,
            ])
        ),
        (
            "projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_bysoil_poly_minorg_px4",
            np.array([
                0, 0, 1/4, 0, 0, 0, 0, 0, 0, 
                0, 0, 3/4, 0, 0, 0, 0, 0, 0, 
                0, 0, 0, 0, 0, 0, 0, 0, 0
            ])
        )
    ]
)
def test_landcover_bysoil(get_logger, feature_collection, expected_result) -> None:
    """
    Tests that landcover stratified by soil `landcover_bysoil` works for different ground truth examples.

    Args:
        get_logger: A pytest fixture for obtaining a logger instance.
        feature_collection: The asset path for the feature collection to test.
        expected_result: The expected result for the test case.

    Asserts:
        Calculated landcover fractions are approximately equal to the test result
        within a small tolerance.
    """
    from heet_params import landcover_bysoil
    logger = get_logger
    landcover_bysoil_poly = ee.FeatureCollection(feature_collection)
    test_input = {
        'land_ftc': landcover_bysoil_poly,
        'landcover_analysis_file_str': 'projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds'
    }
    calc_result = landcover_bysoil(**test_input).getInfo()
    diff = expected_result - calc_result
    pdiff = (abs(expected_result - calc_result)/expected_result) * 100
    logger.info(
        f'[test_landcover_bysoil] Landcover by soil - GeoCARET {calc_result} ' + 
        f'Manual {expected_result} Diff {diff} PDiff {pdiff}'
    )
    assert calc_result == pytest.approx(expected_result)


def test_soc_percent(get_logger, target_ftc = None) -> None:
    """
    Tests the calculation of soil organic carbon percentage (%SOC) for a single ground truth example.

    Args:
        get_logger: A pytest fixture for obtaining a logger instance.
        target_ftc: An optional argument, not used in this test function.

    Asserts:
        The calculated %SOC is approximately equal to the expected result within a relative tolerance of 0.05%.
    """
    from heet_params import soc_percent
    logger = get_logger
    psoc_poly_org_px1 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/psoc_poly_org_px1")
    test_input = {'target_ftc': psoc_poly_org_px1}
    test_result = 20.8
    calc_result = soc_percent(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    logger.info(
        f'[test_soc_percent] %SOC - GeoCARET {calc_result} ' + 
        f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)
    
    
@pytest.mark.parametrize(
    "feature_collection, expected_result",
    [
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/psoc_poly_min_px1", "MINERAL"),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/psoc_poly_org_px1", "ORGANIC")
    ]
)
def test_soil_type(get_logger, feature_collection, expected_result) -> None:
    """
    Tests the identification of soil type (mineral / organic) for two ground truth examples.

    This test uses the Google Earth Engine (GEE) feature collections for different soil polygons 
    and checks the identified soil type against the expected ground truth values.

    Args:
        get_logger: A pytest fixture for obtaining a logger instance.
        feature_collection: GEE FeatureCollection asset path to test.
        expected_result: The expected soil type result.

    Asserts:
        The identified soil type is correctly labeled as expected.
    """
    from heet_params import soil_type
    logger = get_logger
    # Set up the feature collection from the parameter
    target_ftc = ee.FeatureCollection(feature_collection)
    test_input = {'target_ftc': target_ftc}
    # Calculate the soil type using the function
    calc_result = soil_type(**test_input).getInfo()
    # Log the results
    logger.info(
        f'[test_soil_type] %SOC - Calculated: {calc_result}, ' + 
        f'Expected: {expected_result}')

    # Assert that the calculated result matches the expected result
    assert calc_result == expected_result

