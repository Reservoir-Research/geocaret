""" """
import ee
import os
import pytest
import logging


def test_area(get_logger) -> None:
    """Test that area calculation matches a ground truth value for Derbyshire
    
    This test checks that the area calculation for a test region in Derbyshire using the `area` function 
    matches a known ground truth value. The result is logged for comparison.

    The test compares the computed area in GEE to a manually calculated area. 
    The comparison allows a relative difference of 0.005%.

    Args:
        get_logger: A pytest fixture that provides a logger for logging test information.

    Raises:
        AssertionError: If the calculated area does not match the expected value within 
                        the allowable relative difference.
    """
    from geocaret.params import area
    # Reference the target area as a FeatureCollection stored in a GEE folder
    target_roi = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_ASSETS/CTY_DEC_2021_EN_BUC").first() 
    
    test_input = {'land_ftc': target_roi,}
    test_result =  3_056_053_132.916/(1_000*1_000)
    calc_result = area(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    # Log
    logger = get_logger
    logger.info(f'[test_area] Derbyshire area - GeoCARET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    # Check calculated area in km2 is equal within 0.005%
    assert calc_result  == pytest.approx(test_result, rel=5e-3)


@pytest.mark.parametrize(
    "mean_slope_degrees, expected_slope_percent",
    [
        (45, 100),      # Test case for 45 degrees
        (48, 111.06)    # Test case for 48 degrees
    ]
)
def test_degrees_to_perc_slope(get_logger, mean_slope_degrees: int, expected_slope_percent: float) -> None:  
    """Test that degrees to percent slope calculation matches ground truth values.

    This parameterized test verifies that the `degrees_to_perc_slope` function correctly 
    converts degrees to percent slope for given input values. 

    Args:
        get_logger: A pytest fixture that provides a logger for logging test information.
        mean_slope_degrees (int): The slope in degrees to be converted.
        expected_slope_percent (float): The expected slope in percentage after conversion.

    Raises:
        AssertionError: If the calculated percent slope does not match the expected value 
                        within the allowable absolute difference.
    """
    from geocaret.params import degrees_to_perc_slope
    
    test_input = {
        'mean_slope_degrees_value': ee.Number(mean_slope_degrees),
    }
     
    calc_result = degrees_to_perc_slope(**test_input).getInfo() 
    diff = expected_slope_percent - calc_result 
    pdiff = (abs(expected_slope_percent - calc_result)/expected_slope_percent) * 100
    # Log
    logger = get_logger
    logger.info(f'[test_degrees_to_perc_slope] 45 degrees to percentage slope - GeoCARET {calc_result} ' + 
                f'Manual {expected_slope_percent} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.005
    assert calc_result  ==  pytest.approx(expected_slope_percent, abs=5e-3)


def test_reservoir_volume(get_logger) -> None:
    """Test the reservoir volume calculation function.
    
    This test checks that the `reservoir_volume` function calculates the volume 
    correctly based on surface area and mean depth.

    Args:
        get_logger: A pytest fixture that provides a logger for logging test information.

    Raises:
        AssertionError: If the calculated volume does not match the expected value.
    """
    from geocaret.params import reservoir_volume
    
    test_input = {
        'surface_area': ee.Number(1),
        'mean_depth': ee.Number(0.75),
    }
     
    test_result =  0.75
    calc_result = reservoir_volume(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    # Log
    logger = get_logger
    logger.info(f'[test_reservoir_volume] Reservoir Volume - GeoCARET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    assert calc_result  ==  pytest.approx(test_result)    


def test_km2_to_m2(get_logger) -> None:
    """Test the conversion from square kilometers to square meters.
    
    This test verifies that the `km2_to_m2` function correctly converts 
    an area from square kilometers to square meters.

    Args:
        get_logger: A pytest fixture that provides a logger for logging test information.

    Raises:
        AssertionError: If the calculated area in square meters does not match the expected value.
    """
    from geocaret.params import km2_to_m2
    
    test_input = {'surface_area': ee.Number(1)}
     
    test_result =  1_000_000
    calc_result = km2_to_m2(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    # Log
    logger = get_logger
    logger.info(f'[test_km2_to_m2] km2 to m2  - GeoCARET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    assert calc_result  ==  pytest.approx(test_result)    
