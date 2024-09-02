""" """
import ee
import os
import pytest


# ==============================================================================
# Soil Moisture
# ==============================================================================

# Soil Moisure (Smap) Cross-reference with hydrobasins
def test_smap_crossref_soil(get_logger) -> None:
    """
    Test that SMAP soil moisture values are within the same order of magnitude as HydroAtlas reference values.

    This function validates the accuracy of soil moisture data derived from SMAP (Soil Moisture Active Passive) 
    by comparing it against a known reference value from HydroAtlas. The test checks if the calculated soil 
    moisture is consistent with the reference value within an acceptable range of magnitude.

    Args:
        get_logger: A pytest fixture for obtaining a logger instance.

    Asserts:
        The ratio of the calculated soil moisture value to the reference value should be between 0.1 and 10, 
        ensuring that the values are within the same order of magnitude.
    """
    from heet_params import smap_monthly_mean
    import heet_data as dta
    target_var = "smp"
    REFDATA = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_ASSETS/BasinATLAS_v10_lev12"
    )
    # C1;  4121051890
    target_ftc = dta.HYDROBASINS12.filter(ee.Filter.eq("HYBAS_ID", 4121051890))
    test_input = {
        "start_yr": 2016,
        "end_yr": 2021,
        "target_var": target_var,
        "target_ftc": target_ftc,
    }
    test_result = (
        ee.Number(
            ee.Feature(
                REFDATA.filter(ee.Filter.eq("HYBAS_ID", 4121051890)).first()
            ).get("swc_pc_syr")
        )
        .multiply(10)
        .getInfo()
    )
    calc_result = ee.Number(smap_monthly_mean(**test_input)).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100
    rdiff = abs(calc_result / test_result)
    logger = get_logger
    logger.info(
        f"[test_smap_crossref_soil] - GeoCARET SMAP {calc_result}"
        + f" HydroAtlas {test_result} Diff {diff} PDiff {pdiff}"
    )
    assert 0.1 < rdiff < 10
