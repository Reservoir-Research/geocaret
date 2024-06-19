
import ee
import os

if 'CI_ROBOT_USER' in os.environ:
    print("Running service account authentication")
    gc_service_account = os.environ['GCLOUD_ACCOUNT_EMAIL']
    credentials = ee.ServiceAccountCredentials(gc_service_account, 'service_account_creds.json')
    ee.Initialize(credentials)

else:
    print("Running individual account authentication")
    ee.Initialize()

import pytest
import heet_data as dta
import logging

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
formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)


# Terraclimate

# Windspeed
def test_terraclim_windspeed():
    """Test that terraclim windspeed agrees with a manually calculated set of test values."""
    from heet_params import terraclim_monthly_mean
    
    target_var = 'vs'
    
    GRID = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_grid_22_01") 
    GRID_NULL = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_null_grid_22") 
    GRID_PNULL = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_pnull_grid_22") 
    
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.01,      
        'target_ftc': GRID
     }
       
    test_result =  3.80
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
       
    test_result =  5.19
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
    
    test_result =  None
    calc_result = ee.Number(terraclim_monthly_mean(**test_input))
       
    assert calc_result.getInfo()  == test_result 


# Soil Moisture
def test_terraclim_soilm_a():
    """Test that terraclim soil moisture agrees with a manually calculated set of test values.
       Annual mean as mean of yearly total.
    """
    from heet_params import terraclim_annual_mean
    
    target_var = 'soil'
    
    GRID = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_grid_22_01") 
    GRID_NULL = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_null_grid_22") 
    GRID_PNULL = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_pnull_grid_22") 
    
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,      
        'target_ftc': GRID
     }
       
    test_result =  535
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
       
    test_result =  415
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
    
    test_result =  None
    calc_result = ee.Number(terraclim_annual_mean(**test_input))
       
    assert calc_result.getInfo()  == test_result 

def test_terraclim_soilm_b():
    """Test that terraclim soil moisture agrees with a manually calculated set of test values.
       Annual mean as mean of monthly values.
    """
    from heet_params import terraclim_monthly_mean
    
    target_var = 'soil'
    
    GRID = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_grid_22_01") 
    GRID_NULL = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_null_grid_22") 
    GRID_PNULL = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_pnull_grid_22") 
    
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,      
        'target_ftc': GRID
     }
       
    test_result =  45
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
       
    test_result =  35
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
    
    test_result =  None
    calc_result = ee.Number(terraclim_monthly_mean(**test_input))
       
    assert calc_result.getInfo()  == test_result 

# PET
def test_terraclim_pet():
    """Test that terraclim pet agrees with a manually calculated set of test values"""
    from heet_params import terraclim_annual_mean
    
    target_var = 'pet'
    
    GRID = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_grid_22_01") 
    GRID_NULL = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_null_grid_22") 
    GRID_PNULL = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_pnull_grid_22") 
    
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,      
        'target_ftc': GRID
     }
       
    test_result =  611
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
       
    test_result =  647
    calc_result = ee.Number(terraclim_annual_mean(**test_input))
    assert abs(test_result - calc_result.getInfo()) < (0.05 * test_result)
    
      
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 0.1,
        'target_ftc': GRID_NULL
     }
    
    test_result =  None
    calc_result = ee.Number(terraclim_annual_mean(**test_input))
       
    assert calc_result.getInfo()  == test_result 


def test_terraclim_pr():
    """Test that terraclim pet agrees with a manually calculated set of test values"""
    from heet_params import terraclim_annual_mean
    
    target_var = 'pr'
    
    GRID = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_grid_22_01") 
    GRID_NULL = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_null_grid_22") 
    GRID_PNULL = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_pnull_grid_22") 
    
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 1.0,      
        'target_ftc': GRID
     }
       
    test_result = 902.25
    calc_result = ee.Number(terraclim_annual_mean(**test_input)).getInfo()

    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_terraclim_pet] GRID PR - HEET Terraclim {calc_result} ' + 
                f'Manual Terraclim {test_result} Diff {diff} PDiff {pdiff}')      
    
    assert abs(test_result - calc_result) < (0.05 * test_result)
        
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 1.0,
        'target_ftc': GRID_PNULL
      }
       
    test_result =  846.355
    calc_result = ee.Number(terraclim_annual_mean(**test_input))
    assert abs(test_result - calc_result.getInfo()) < (0.05 * test_result)
    
      
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 1.0,
        'target_ftc': GRID_NULL
     }
    
    test_result =  None
    calc_result = ee.Number(terraclim_annual_mean(**test_input))
       
    assert calc_result.getInfo()  == test_result 

#==============================================================================
# Runoff
#============================================================================== 

def test_terraclim_ro():
    """Test that terraclim ro agrees with a manually calculated set of test values"""
    from heet_params import terraclim_annual_mean
    
    target_var = 'ro'
    
    GRID = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_grid_22_01") 
    GRID_NULL = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_null_grid_22") 
    GRID_PNULL = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/terraclim_pnull_grid_22") 
    
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_var': target_var,
        'scale_factor': 1,      
        'target_ftc': GRID
     }
       
    test_result =  397
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
       
    test_result =  311
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
    
    test_result =  None
    calc_result = ee.Number(terraclim_annual_mean(**test_input))

       
    assert calc_result.getInfo()  == test_result 


# Runoff (Terraclim) Cross-reference with hydrobasins
def test_terraclim_crossref_ro():
    """Test that terraclim ro is same order of magnitude as hydroAtlas value"""
    from heet_params import terraclim_annual_mean
    
    target_var = 'ro'
    
    REFDATA = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_ASSETS/BasinATLAS_v10_lev12") 

    # C1;  4121051890
    target_ftc = (dta.HYDROBASINS12
      .filter(ee.Filter.eq('HYBAS_ID', 4121051890))
    )
    
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
        
    logger.info(f'[test_terraclim_crossref_ro] HEET Terraclim {calc_result} ' + 
                f'HydroAtlas {test_result} Diff {diff} PDiff {pdiff}')      
                
    
    assert 0.1 < rdiff < 10
       
# Soil Moisure (Terraclim) Cross-reference with hydrobasins
def test_terraclim_crossref_soil():
    """Test that terraclim soil moisture is same order of magnitude as hydroAtlas value"""
    from heet_params import terraclim_monthly_mean
    
    target_var = 'soil'
    REFDATA = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_ASSETS/BasinATLAS_v10_lev12") 

    # C1;  4121051890
    target_ftc = (dta.HYDROBASINS12
      .filter(ee.Filter.eq('HYBAS_ID', 4121051890))
    )
    
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
    
    logger.info(f'[test_terraclim_crossref_soil] Soil Moisture - HEET Terraclim' + 
                f'{calc_result} HydroAtlas {test_result} Diff {diff} PDiff {pdiff} Ratio {rdiff}')     

    assert 0.1 < rdiff < 10

