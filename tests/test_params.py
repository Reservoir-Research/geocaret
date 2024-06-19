""" """
import logging
import ee
import heet.data as dta
import heet.params
from heet.earth_engine import EarthEngine

EarthEngine.init()

#==============================================================================
#  Set up logger
#==============================================================================


# Create new log each run (TODO; better implementation)
with open("tests.log", 'w') as file:
    pass


# Gets or creates a logger
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.DEBUG)

# define file handler and set formatter
file_handler = logging.FileHandler('tests.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)


def test_impute_dam_height():
    """Test that imputed dam height works for a set of test values."""

    test_input = {
        'power_capacity': ee.Number(10),
        'turbine_efficiency': ee.Number(85),
        'plant_depth': ee.Number(0),
        'mad_m3_pers': ee.Number(24),
    }

    test_result = 49.969
    calc_result = heet.params.impute_dam_height(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result) * 100

    logger.info(f'[test_impute_dam_height] Dam Height - HEET {calc_result} ' +
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')

    assert calc_result == test_result

# Terraclimate


# Windspeed
def test_terraclim_windspeed():
    """Test that terraclim windspeed agrees with a manually calculated set of test values."""
    from heet.params import terraclim_monthly_mean

    target_var = 'vs'

    GRID = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_grid_22_01")
    GRID_NULL = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_null_grid_22")
    GRID_PNULL = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_pnull_grid_22")

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.01,
        'target_ftc': GRID
     }

    test_result = 3.80
    calc_result = ee.Number(terraclim_monthly_mean(**test_input)).getInfo()

    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result) * 100

    logger.info(f'[test_terraclim_windspeed] GRID Windspeed - HEET Terraclim {calc_result} ' +
                f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')

    assert abs(test_result - calc_result) < (0.01 * test_result)

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.01,
        'target_ftc': GRID_PNULL
     }

    test_result = 5.19
    calc_result = ee.Number(terraclim_monthly_mean(**test_input)).getInfo()

    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result) * 100

    logger.info(f'[test_terraclim_windspeed] GRID_PNULL Windspeed - HEET Terraclim {calc_result} ' +
                f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')

    assert abs(test_result - calc_result) < (0.01 * test_result)

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.01,
        'target_ftc': GRID_NULL
     }

    test_result = -999
    calc_result = ee.Number(terraclim_monthly_mean(**test_input))

    assert calc_result.getInfo() == test_result


# Soil Moisture
def test_terraclim_soilm_a():
    """Test that terraclim soil moisture agrees with a manually calculated set of test values.
       Annual mean as mean of yearly total.
    """
    from heet.params import terraclim_annual_mean

    target_var = 'soil'

    GRID = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_grid_22_01")
    GRID_NULL = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_null_grid_22")
    GRID_PNULL = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_pnull_grid_22")

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': GRID
     }

    test_result = 535
    calc_result = ee.Number(terraclim_annual_mean(**test_input)).getInfo()

    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result) * 100

    logger.info(f'[test_terraclim_soilm] GRID Soil Moisture - HEET Terraclim {calc_result} ' +
                f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')

    assert abs(test_result - calc_result) < (0.05 * test_result)

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': GRID_PNULL
     }

    test_result = 415
    calc_result = ee.Number(terraclim_annual_mean(**test_input)).getInfo()

    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result) * 100

    logger.info(f'[test_terraclim_soilm] GRID_PNULL Soil Moisture - HEET Terraclim {calc_result} ' +
                f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')

    assert abs(test_result - calc_result) < (0.05 * test_result)

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': GRID_NULL
     }

    test_result = None
    calc_result = ee.Number(terraclim_annual_mean(**test_input))

    assert calc_result.getInfo() == test_result


def test_terraclim_soilm_b():
    """Test that terraclim soil moisture agrees with a manually calculated set of test values.
       Annual mean as mean of monthly values.
    """
    from heet.params import terraclim_monthly_mean

    target_var = 'soil'

    GRID = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_grid_22_01")
    GRID_NULL = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_null_grid_22")
    GRID_PNULL = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_pnull_grid_22")

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': GRID
     }

    test_result = 45
    calc_result = ee.Number(terraclim_monthly_mean(**test_input)).getInfo()

    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result) * 100

    logger.info(f'[test_terraclim_soilm] GRID Soil Moisture - HEET Terraclim {calc_result} ' +
                f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')

    assert abs(test_result - calc_result) < (0.05 * test_result)

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': GRID_PNULL
     }

    test_result = 35
    calc_result = ee.Number(terraclim_monthly_mean(**test_input)).getInfo()

    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result) * 100

    logger.info(f'[test_terraclim_soilm] GRID_PNULL Soil Moisture - HEET Terraclim {calc_result} ' +
                f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')

    assert abs(test_result - calc_result) < (0.05 * test_result)

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': GRID_NULL
     }

    test_result = -999
    calc_result = ee.Number(terraclim_monthly_mean(**test_input))

    assert calc_result.getInfo() == test_result


# PET
def test_terraclim_pet():
    """Test that terraclim pet agrees with a manually calculated set of test values"""
    from heet.params import terraclim_annual_mean

    target_var = 'pet'

    GRID = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_grid_22_01")
    GRID_NULL = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_null_grid_22")
    GRID_PNULL = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_pnull_grid_22")

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': GRID
     }

    test_result = 611
    calc_result = ee.Number(terraclim_annual_mean(**test_input)).getInfo()

    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result) * 100

    logger.info(f'[test_terraclim_pet] GRID PET - HEET Terraclim {calc_result} ' +
                f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')

    assert abs(test_result - calc_result) < (0.05 * test_result)

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': GRID_PNULL
      }

    test_result = 647
    calc_result = ee.Number(terraclim_annual_mean(**test_input))
    assert abs(test_result - calc_result.getInfo()) < (0.05 * test_result)

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': GRID_NULL
     }

    test_result = None
    calc_result = ee.Number(terraclim_annual_mean(**test_input))

    assert calc_result.getInfo() == test_result

#==============================================================================
# Runoff
#==============================================================================

def test_terraclim_ro():
    """Test that terraclim ro agrees with a manually calculated set of test values"""
    from heet.params import terraclim_annual_mean

    target_var = 'ro'

    GRID = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_grid_22_01")
    GRID_NULL = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_null_grid_22")
    GRID_PNULL = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_pnull_grid_22")

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 1,
        'target_ftc': GRID
     }

    test_result = 397
    calc_result = ee.Number(terraclim_annual_mean(**test_input)).getInfo()

    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result) * 100

    logger.info(f'[test_terraclim_ro] GRID - HEET Terraclim {calc_result}' +
                ' Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')

    assert abs(test_result - calc_result) < (0.05 * test_result)

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 1,
        'target_ftc': GRID_PNULL
     }

    test_result = 311
    calc_result = ee.Number(terraclim_annual_mean(**test_input)).getInfo()

    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result) * 100

    logger.info(f'[test_terraclim_ro] GRID_PNULL - HEET Terraclim {calc_result} ' +
                f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')

    assert abs(test_result - calc_result) < (0.05 * test_result)

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 1,
        'target_ftc': GRID_NULL
     }

    test_result = None
    calc_result = ee.Number(terraclim_annual_mean(**test_input))

    assert calc_result.getInfo() == test_result


# Runoff (Terraclim) Cross-reference with hydrobasins
def test_terraclim_crossref_ro():
    """Test that terraclim ro is same order of magnitude as hydroAtlas value"""
    from heet.params import terraclim_annual_mean

    target_var = 'ro'

    REFDATA = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST_ASSETS/BasinATLAS_v10_lev12")

    # C1;  4121051890
    target_ftc = dta.HYDROBASINS12.filter(
        ee.Filter.eq('HYBAS_ID', 4121051890))

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 1,
        'target_ftc': target_ftc
      }

    test_result = ee.Feature(
        REFDATA.filter(ee.Filter.eq('HYBAS_ID', 4121051890)).first()).get(
        'run_mm_syr').getInfo()

    calc_result = ee.Number(terraclim_annual_mean(**test_input)).getInfo()

    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    rdiff = abs(calc_result/test_result)

    logger.info(f'[test_terraclim_crossref_ro] HEET Terraclim {calc_result} ' +
                f'HydroAtlas {test_result} Diff {diff} PDiff {pdiff}')

    assert 0.1 < rdiff < 10


# Runoff (Fekete) Cross-reference with hydrobasins
def test_fekete_crossref_ro():
    """Test that fekete ro is same order of magnitude as hydroAtlas value"""
    from heet.params import mean_annual_runoff_mm

    REFDATA = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST_ASSETS/BasinATLAS_v10_lev12")

    # C1;  4121051890
    target_ftc = dta.HYDROBASINS12.filter(ee.Filter.eq('HYBAS_ID', 4121051890))

    test_input = {
        'catchment_ftc': target_ftc
     }

    test_result = ee.Feature(
        REFDATA.filter(ee.Filter.eq('HYBAS_ID', 4121051890)).first()).get(
        'run_mm_syr').getInfo()

    calc_result = ee.Number(mean_annual_runoff_mm(**test_input)).getInfo()

    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    rdiff = abs(calc_result/test_result)

    logger.info(f'[test_fekete_crossref_ro] - HEET Fekete {calc_result} ' +
                f'HydroAtlas {test_result} Diff {diff} PDiff {pdiff}')

    assert 0.1 < rdiff < 10


#==============================================================================
# Soil Moisture
#==============================================================================

# Soil Moisure (Smap) Cross-reference with hydrobasins
def test_smap_crossref_soil():
    """Test that smap soil moisture is same order of magnitude as hydroAtlas value"""
    from heet.params import smap_monthly_mean

    target_var = 'smp'

    REFDATA = ee.FeatureCollection(
        "users/KamillaHarding/XHEET_TEST_ASSETS/BasinATLAS_v10_lev12")

    # C1;  4121051890
    target_ftc = dta.HYDROBASINS12.filter(ee.Filter.eq('HYBAS_ID', 4121051890))

    test_input = {
        'start_yr': 2016,
        'end_yr': 2021,
        'target_var': target_var,
        'target_ftc': target_ftc
      }

    test_result = ee.Number(ee.Feature(REFDATA
      .filter(ee.Filter.eq('HYBAS_ID', 4121051890)).first()
    ).get('swc_pc_syr')).multiply(10).getInfo()

    calc_result = ee.Number(smap_monthly_mean(**test_input)).multiply(1000).getInfo()

    diff = test_result - calc_result

    pdiff = (abs(test_result - calc_result)/test_result)*100
    rdiff = abs(calc_result/test_result)
    logger.info(f'[test_smap_crossref_soil] - HEET SMAP {calc_result}' +
                f' HydroAtlas {test_result} Diff {diff} PDiff {pdiff}')

    assert 0.1 < rdiff < 10


# Soil Moisure (Terraclim) Cross-reference with hydrobasins
def test_terraclim_crossref_soil():
    """Test that terraclim soil moisture is same order of magnitude as hydroAtlas value"""
    from heet.params import terraclim_monthly_mean

    target_var = 'soil'
    REFDATA = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST_ASSETS/BasinATLAS_v10_lev12")

    # C1;  4121051890
    target_ftc = dta.HYDROBASINS12.filter(ee.Filter.eq('HYBAS_ID', 4121051890))

    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': target_ftc
      }

    test_result = ee.Number(ee.Feature(REFDATA
      .filter(ee.Filter.eq('HYBAS_ID', 4121051890)).first()
    ).get('swc_pc_syr')).multiply(10).getInfo()

    calc_result = ee.Number(terraclim_monthly_mean(**test_input)).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result)/test_result)*100
    rdiff = abs(calc_result/test_result)

    logger.info(f'[test_terraclim_crossref_soil] Soil Moisture - HEET Terraclim' +
                f'{calc_result} HydroAtlas {test_result} Diff {diff} PDiff {pdiff} Ratio {rdiff}')

    assert 0.1 < rdiff < 10
