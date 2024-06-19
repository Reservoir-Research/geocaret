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


#==============================================================================
# Soil Moisture
#============================================================================== 

# Soil Moisure (Smap) Cross-reference with hydrobasins
def test_smap_crossref_soil():
    """Test that smap soil moisture is same order of magnitude as hydroAtlas value"""
    from heet_params import smap_monthly_mean
    
    target_var = 'smp'
    
    REFDATA = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_ASSETS/BasinATLAS_v10_lev12") 

    # C1;  4121051890
    target_ftc = (dta.HYDROBASINS12
      .filter(ee.Filter.eq('HYBAS_ID', 4121051890))
    )
    
    test_input = {
        'start_yr': 2016,
        'end_yr': 2021,
        'target_var': target_var, 
        'target_ftc': target_ftc
      }
       
    test_result =  ee.Number(ee.Feature(REFDATA
      .filter(ee.Filter.eq('HYBAS_ID', 4121051890)).first()
    ).get('swc_pc_syr')).multiply(10).getInfo()
    
    calc_result = ee.Number(smap_monthly_mean(**test_input)).multiply(1000).getInfo()
    
    diff = test_result - calc_result 

    pdiff = (abs(test_result - calc_result)/test_result)*100
    rdiff = abs(calc_result/test_result)
    logger.info(f'[test_smap_crossref_soil] - HEET SMAP {calc_result}' + 
                f' HydroAtlas {test_result} Diff {diff} PDiff {pdiff}')      
                        
    assert 0.1 < rdiff < 10
