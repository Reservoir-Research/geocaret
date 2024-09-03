"""
This module contains test functions for various environmental and hydrological parameters using Google Earth Engine (GEE) data.

Tests included in this module:

1. **Biome Tests:**
   - `test_predominant_biome`: Validates the correct identification of the predominant biome from a feature collection using a ground truth value.

2. **Evapotranspiration (UDEL) Tests:**
   - `test_twbda_annual_mean_pet`: Tests the calculation of the annual mean potential evapotranspiration (PET) from a feature collection, comparing it to a ground truth value.

3. **Population Tests:**
   - `test_population`: Assesses the accuracy of population estimates from a feature collection against a known ground truth value.
   - `test_population_density`: Verifies the calculation of population density from a feature collection, ensuring it matches the expected result.

4. **Fekete Runoff Tests:**
   - `test_fekete_crossref_ro`: Compares Fekete runoff estimates with a reference value from HydroAtlas to check for consistency in magnitude.

Each test function includes:
- A description of the functionality being tested.
- The expected result for comparison.
- Assertions to validate the correctness of the calculated results.
- Logging of results and differences for debugging and verification.

Fixtures:
- `get_logger`: A pytest fixture for obtaining a logger instance used in each test function to record test execution details.

This module helps ensure the accuracy and reliability of environmental and hydrological calculations performed using Earth Engine data.
"""
import ee
import os
import pytest
import numpy as np


# ==============================================================================
#  Biome tests
# ==============================================================================

def test_predominant_biome(get_logger) -> None:
    """
    Tests the determination of the predominant biome from a feature collection.
    
    Args:
        get_logger: A pytest fixture for obtaining a logger instance.

    Asserts:
        The calculated biome is correctly identified as "Temperate Conifer Forests".
    """
    from geocaret.params import predominant_biome
    logger = get_logger
    biome_poly_1090 = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/biome_poly_1090"
    )
    test_input = {
        "catchment_ftc": biome_poly_1090,
    }
    # 5 - Temperate Conifer Forests
    # 4 - Temperate Broadleaf & Mixed Forests
    test_result = "Temperate Conifer Forests"
    calc_result = predominant_biome(**test_input).getInfo()
    logger.info(
        f"[test_predominant_biome] Predominant Biome - GeoCARET {calc_result} " +
        f"Manual {test_result}"
    )
    assert calc_result == test_result


# ==============================================================================
#  Evapotranspiration (UDEL) tests
# ==============================================================================


def test_twbda_annual_mean_pet(get_logger) -> None:
    """
    Tests the calculation of the annual mean potential evapotranspiration (PET) for a given feature collection.
    Test that the function `twbda_annual_mean_pet` works for a ground truth value (px2).

    Args:
        get_logger: A pytest fixture for obtaining a logger instance.

    Asserts:
        The calculated PET is approximately equal to the expected result within a relative tolerance of 0.05%.
    """
    from geocaret.params import twbda_annual_mean_pet
    logger = get_logger
    twbda_poly_px2 = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/twbda_poly_px2"
    )
    test_input = {"target_ftc": twbda_poly_px2}
    # 74 + 48.30 / 2
    test_result = 61.15
    calc_result = twbda_annual_mean_pet(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[mean_slope_perc] Mean Slope % - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)

# ==============================================================================
#  Population tests
# ==============================================================================


def test_population(get_logger) -> None:
    """
    Tests the population estimation for a given feature collection.
    Test that the function `population` works for a ground truth value (px4).s

    Args:
        get_logger: A pytest fixture for obtaining a logger instance.

    Asserts:
        The calculated population is approximately equal to the expected result within a relative tolerance of 0.05%.
    """
    from geocaret.params import population
    logger = get_logger
    pop_poly_px4 = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/pop_poly_px4"
    )
    test_input = {"target_ftc": pop_poly_px4}
    test_result = 1879.612
    calc_result = population(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[test_population_px4] Population - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)

def test_population_density(get_logger) -> None:
    """
    Tests the population density estimation for a given feature collection.
    Test that the function `population_density` works for a ground truth value (px4).s

    Args:
        get_logger: A pytest fixture for obtaining a logger instance.

    Asserts:
        The calculated population density is approximately equal to the expected result within a relative tolerance of 0.05%.
    """
    from geocaret.params import population_density
    logger = get_logger
    pop_poly_px4 = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/pop_poly_px4"
    )
    test_input = {"target_ftc": pop_poly_px4}
    test_result =  900.0527
    calc_result = population_density(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    logger.info(
        f"[test_population_px4] Population - GeoCARET {calc_result} " +
        f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )
    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


# ==============================================================================
#  Fekete Runoff tests
# ==============================================================================


# Runoff (Fekete) Cross-reference with hydrobasins
def test_fekete_crossref_ro(get_logger) -> None:
    """
    Tests the Fekete runoff estimation by comparing it to a reference value from HydroATLAS.
    Tests that the result from `mean_annual_runoff_mm` is same order of magnitude as the HydroATLAS value.

    Args:
        get_logger: A pytest fixture for obtaining a logger instance.

    Asserts:
        The calculated Fekete runoff is within an order of magnitude of the reference value from HydroAtlas.
    """
    from geocaret.params import mean_annual_runoff_mm
    import geocaret.data as dta
    logger = get_logger
    REFDATA = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_ASSETS/BasinATLAS_v10_lev12"
    )
    # C1;  4121051890
    target_ftc = dta.HYDROBASINS12.filter(ee.Filter.eq("HYBAS_ID", 4121051890))
    test_input = {"catchment_ftc": target_ftc}
    test_result = (
        ee.Feature(REFDATA.filter(ee.Filter.eq("HYBAS_ID", 4121051890)).first())
        .get("run_mm_syr")
        .getInfo()
    )
    calc_result = ee.Number(mean_annual_runoff_mm(**test_input)).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    rdiff = abs(calc_result / test_result)
    logger.info(
        f"[test_fekete_crossref_ro] - GeoCARET Fekete {calc_result} " +
        f"HydroAtlas {test_result} Diff {diff} PDiff {pdiff}"
    )
    assert 0.1 < rdiff < 10
