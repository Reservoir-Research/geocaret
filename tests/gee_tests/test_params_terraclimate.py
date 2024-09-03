"""
Module: test_params_terraclimate.py

This module contains a series of pytest functions that test the accuracy and reliability of 
various Terraclim data processing functions implemented in the `params` module. The tests 
compare computed values against manually calculated reference values to ensure the correctness of 
the implemented algorithms.

Functions:
- test_terraclim_windspeed
- test_terraclim_soilm_a
- test_terraclim_soilm_b
- test_terraclim_pet
- test_terraclim_pr

- test_terraclim_ro
- test_terraclim_crossref_ro
- test_terraclim_crossref_soil
"""
import ee
import os
import pytest

# =====================
# Terraclimate
# =====================


# Windspeed
@pytest.mark.parametrize(
    "target_ftc, test_result",
    [
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_grid_22_01", 3.80),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_pnull_grid_22", 5.19),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_null_grid_22", None),
    ]
)
def test_terraclim_windspeed(get_logger, target_ftc, test_result) -> None:
    """
    Test that terraclim windspeed values match manually calculated test values.

    This function verifies that the Terraclim windspeed data (variable 'vs') computed for different feature collections
    agree with known reference values or are None when expected.

    Args:
        get_logger (function): A pytest fixture to obtain a logger instance for logging test results.
        target_ftc (str): The feature collection path to be used in the test.
        test_result (float or None): The expected windspeed value or None.

    Asserts:
        - The calculated windspeed is within 1% of the manually calculated value for GRID and GRID_PNULL.
        - The result for GRID_NULL should be None.
    """
    from geocaret.params import terraclim_monthly_mean
    logger = get_logger
    target_var = 'vs'
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.01,      
        'target_ftc': ee.FeatureCollection(target_ftc)
    }
    calc_result = ee.Number(terraclim_monthly_mean(**test_input)).getInfo()
    if test_result == None:
        logger.info(
            f'[test_terraclim_windspeed] {target_ftc} Windspeed - GeoCARET Terraclim {calc_result} ' + 
            f'Expected None')
        assert calc_result == test_result
    else:
        diff = test_result - calc_result
        pdiff = (abs(test_result - calc_result) / test_result) * 100
        logger.info(f'[test_terraclim_windspeed] {target_ftc} Windspeed - GeoCARET Terraclim {calc_result} ' +
                    f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')
        assert abs(test_result - calc_result) < 0.01 * test_result


# Soil Moisture
@pytest.mark.parametrize(
    "target_ftc, test_result",
    [
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_grid_22_01", 535),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_pnull_grid_22", 415),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_null_grid_22", None),
    ]
)
def test_terraclim_soilm_a(get_logger, target_ftc, test_result) -> None:
    """
    Test that terraclim soil moisture values (annual mean as mean of yearly total) match manually calculated test values.

    This function verifies that the Terraclim soil moisture data (variable 'soil') computed for different feature collections
    match known reference values or are None when expected. The test checks both standard and null grid cases.
    Annual mean is calculated from the yearly total.

    Args:
        get_logger (function): A pytest fixture to obtain a logger instance for logging test results.
        target_ftc (str): The feature collection path to be used in the test.
        test_result (float or None): The expected soil moisture value or None.

    Asserts:
        - The calculated soil moisture is within 5% of the manually calculated value for GRID and GRID_PNULL.
        - The result for GRID_NULL should be None.
    """
    from geocaret.params import terraclim_annual_mean
    logger = get_logger
    target_var = 'soil'
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': ee.FeatureCollection(target_ftc)
    }
    calc_result = ee.Number(terraclim_annual_mean(**test_input)).getInfo()
    if test_result == None:
        logger.info(f'[test_terraclim_soilm_a] {target_ftc} Soil Moisture - Expected None, Got {calc_result}')
        assert calc_result == test_result
    else:
        diff = test_result - calc_result
        pdiff = (abs(test_result - calc_result) / test_result) * 100
        logger.info(f'[test_terraclim_soilm_a] {target_ftc} Soil Moisture - GeoCARET Terraclim {calc_result} ' +
                    f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')
        assert abs(test_result - calc_result) < 0.05 * test_result


@pytest.mark.parametrize(
    "target_ftc, test_result",
    [
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_grid_22_01", 45),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_pnull_grid_22", 35),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_null_grid_22", None),
    ]
)
def test_terraclim_soilm_b(get_logger, target_ftc, test_result) -> None:
    """
    Test that terraclim soil moisture values (annual mean as mean of monthly values) match manually calculated test values.

    This function verifies that the Terraclim soil moisture data (variable 'soil') computed for different feature collections
    match known reference values or are None when expected. The test checks both standard and null grid cases.
    Annual mean is calculated as the mean of monthly values.

    Args:
        get_logger (function): A pytest fixture to obtain a logger instance for logging test results.
        target_ftc (str): The feature collection path to be used in the test.
        test_result (float or None): The expected soil moisture value or None.

    Asserts:
        - The calculated soil moisture is within 5% of the manually calculated value for GRID and GRID_PNULL.
        - The result for GRID_NULL should be None.
    """
    from geocaret.params import terraclim_monthly_mean
    logger = get_logger
    target_var = 'soil'
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': ee.FeatureCollection(target_ftc)
    }
    calc_result = ee.Number(terraclim_monthly_mean(**test_input)).getInfo()
    if test_result == None:
        logger.info(f'[test_terraclim_soilm_b] {target_ftc} Soil Moisture - Expected None, Got {calc_result}')
        assert calc_result == test_result
    else:
        diff = test_result - calc_result
        pdiff = (abs(test_result - calc_result) / test_result) * 100
        logger.info(f'[test_terraclim_soilm_b] {target_ftc} Soil Moisture - GeoCARET Terraclim {calc_result} ' +
                    f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')
        assert abs(test_result - calc_result) < 0.05 * test_result

# PET
@pytest.mark.parametrize(
    "target_ftc, test_result",
    [
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_grid_22_01", 611),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_pnull_grid_22", 647),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_null_grid_22", None),
    ]
)
def test_terraclim_pet(get_logger, target_ftc, test_result) -> None:
    """
    Test that terraclim potential evapotranspiration (PET) values match manually calculated test values.

    This function verifies that the Terraclim PET data (variable 'pet') computed for different feature collections
    match known reference values or are None when expected. The test checks both standard and null grid cases.

    Args:
        get_logger (function): A pytest fixture to obtain a logger instance for logging test results.
        target_ftc (str): The feature collection path to be used in the test.
        test_result (float or None): The expected PET value or None.

    Asserts:
        - The calculated PET is within 10% of the manually calculated value for GRID and GRID_PNULL.
        - The result for GRID_NULL should be None.
    """
    from geocaret.params import terraclim_annual_mean
    logger = get_logger
    target_var = 'pet'
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': ee.FeatureCollection(target_ftc)
    }
    calc_result = ee.Number(terraclim_annual_mean(**test_input)).getInfo()
    if test_result == None:
        logger.info(f'[test_terraclim_pet] {target_ftc} PET - Expected None, Got {calc_result}')
        assert calc_result == test_result
    else:
        diff = test_result - calc_result
        pdiff = (abs(test_result - calc_result) / test_result) * 100
        logger.info(
            f'[test_terraclim_pet] {target_ftc} PET - GeoCARET Terraclim {calc_result} ' +
            f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')
        assert abs(test_result - calc_result) < 0.05 * test_result


@pytest.mark.parametrize(
    "target_ftc, test_result",
    [
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_grid_22_01", 902.25),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_pnull_grid_22", 846.355),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_null_grid_22", None),
    ]
)
def test_terraclim_pr(get_logger, target_ftc, test_result) -> None:
    """
    Test that terraclim precipitation (PR) values match manually calculated test values.

    This function verifies that the Terraclim precipitation data (variable 'pr') computed for different feature collections
    match known reference values or are None when expected. The test checks both standard and null grid cases.

    Args:
        get_logger (function): A pytest fixture to obtain a logger instance for logging test results.
        target_ftc (str): The feature collection path to be used in the test.
        test_result (float or None): The expected PR value or None.

    Asserts:
        - The calculated precipitation is within 10% of the manually calculated value for GRID and GRID_PNULL.
        - The result for GRID_NULL should be None.
    """
    from geocaret.params import terraclim_annual_mean
    logger = get_logger
    target_var = 'pr'
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 1.0,
        'target_ftc': ee.FeatureCollection(target_ftc)
    }
    calc_result = ee.Number(terraclim_annual_mean(**test_input)).getInfo()
    
    if test_result == None:
        logger.info(f'[test_terraclim_pr] {target_ftc} PR - Expected None, Got {calc_result}')
        assert calc_result == test_result
    else:
        diff = test_result - calc_result
        pdiff = (abs(test_result - calc_result) / test_result) * 100
        logger.info(f'[test_terraclim_pr] {target_ftc} PR - GeoCARET Terraclim {calc_result} ' +
                    f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')
        assert abs(test_result - calc_result) < 0.05 * test_result

#==============================================================================
# Runoff
#============================================================================== 

@pytest.mark.parametrize(
    "target_ftc, test_result",
    [
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_grid_22_01", 397),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_pnull_grid_22", 311),
        ("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_null_grid_22", None),
    ]
)
def test_terraclim_ro(get_logger, target_ftc, test_result) -> None:
    """
    Test that terraclim runoff (RO) values match manually calculated test values.

    This function verifies that the Terraclim runoff data (variable 'ro') computed for different feature collections
    match known reference values or are None when expected. The test checks both standard and null grid cases.

    Args:
        get_logger (function): A pytest fixture to obtain a logger instance for logging test results.
        target_ftc (str): The feature collection path to be used in the test.
        test_result (float or None): The expected RO value or None.

    Asserts:
        - The calculated runoff is within 10% of the manually calculated value for GRID and GRID_PNULL.
        - The result for GRID_NULL should be None.
    """
    from geocaret.params import terraclim_annual_mean
    logger = get_logger
    target_var = 'ro'
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 1,
        'target_ftc': ee.FeatureCollection(target_ftc)
    }
    calc_result = ee.Number(terraclim_annual_mean(**test_input)).getInfo()
    if test_result == None:
        logger.info(f'[test_terraclim_ro] {target_ftc} RO - Expected None, Got {calc_result}')
        assert calc_result == test_result
    else:
        diff = test_result - calc_result
        pdiff = (abs(test_result - calc_result) / test_result) * 100
        logger.info(f'[test_terraclim_ro] {target_ftc} RO - GeoCARET Terraclim {calc_result} ' +
                    f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')
        assert abs(test_result - calc_result) < 0.05 * test_result


# Runoff (Terraclim) Cross-reference with hydrobasins
def test_terraclim_crossref_ro(get_logger) -> None:
    """Test that terraclim ro is same order of magnitude as hydroAtlas value"""
    """
    Test that terraclim runoff (RO) values are of the same order as the HydroATLAS (manually calculated) test values.

    This function verifies that the Terraclim runoff data (variable 'ro') cross-referenced with manually calculated test values
    match known reference values for different feature collections. The test checks both standard and null grid cases.

    Args:
        get_logger (function): A function to obtain a logger instance for logging test results.

    Asserts:
        - The calculated runoff from cross-referencing is within 10% of the manually calculated value for GRID and GRID_PNULL.
        - The result for GRID_NULL should be None.
    """
    from geocaret.params import terraclim_annual_mean
    import geocaret.data as dta
    logger = get_logger
    target_var = 'ro'
    REFDATA = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_ASSETS/BasinATLAS_v10_lev12") 
    # C1;  4121051890
    target_ftc = dta.HYDROBASINS12.filter(ee.Filter.eq('HYBAS_ID', 4121051890))
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 1,      
        'target_ftc': target_ftc
     }
    test_result =  ee.Feature(REFDATA
        .filter(ee.Filter.eq('HYBAS_ID', 4121051890)).first()
    ).get('run_mm_syr').getInfo()
    calc_result = ee.Number(terraclim_annual_mean(**test_input)).getInfo()
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    rdiff = abs(calc_result/test_result)
    logger.info(f'[test_terraclim_crossref_ro] GeoCARET Terraclim {calc_result} ' + 
                f'HydroAtlas {test_result} Diff {diff} PDiff {pdiff}')      
    assert 0.1 < rdiff < 10


# Soil Moisure (Terraclim) Cross-reference with hydrobasins
def test_terraclim_crossref_soil(get_logger) -> None:
    """
    Test that Terraclim soil moisture values are in the same order of magnitude as hydroATLAS values.

    This function cross-references Terraclim soil moisture data with reference values from HydroATLAS.
    It checks if the soil moisture values for a specific hydrobasin from Terraclim are within a reasonable 
    order of magnitude compared to manually provided reference values. 

    Args:
        get_logger (function): A pytest fixture to obtain a logger instance for logging test results.

    Asserts:
        The ratio of the calculated Terraclim soil moisture value to the reference HydroAtlas value
        should be within the range of 0.1 to 10, indicating they are of the same order of magnitude.
    """
    from geocaret.params import terraclim_monthly_mean
    import geocaret.data as dta
    logger = get_logger
    target_var = 'soil'
    REFDATA = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_ASSETS/BasinATLAS_v10_lev12") 
    # C1;  4121051890
    target_ftc = dta.HYDROBASINS12.filter(ee.Filter.eq('HYBAS_ID', 4121051890))
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,      
        'target_ftc': target_ftc
    }
    test_result =  ee.Number(ee.Feature(REFDATA
      .filter(ee.Filter.eq('HYBAS_ID', 4121051890)).first()
    ).get('swc_pc_syr')).multiply(10).getInfo()
    calc_result = ee.Number(terraclim_monthly_mean(**test_input)).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result)*100
    rdiff = abs(calc_result/test_result)
    logger.info(
        f'[test_terraclim_crossref_soil] Soil Moisture - GeoCARET Terraclim' + 
        f'{calc_result} HydroAtlas {test_result} Diff {diff} PDiff {pdiff} Ratio {rdiff}')     
    assert 0.1 < rdiff < 10

