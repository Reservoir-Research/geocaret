import pytest
import ee

ee.Initialize()


# MGHR
def test_terraclim_mghr():
    """Test that terraclim ro for a set of test values."""
    from params import terraclim_mghr
        
    GRID = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_grid_22_01") 
    GRID_NULL = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_null_grid_22") 
    GRID_PNULL = ee.FeatureCollection("users/KamillaHarding/XHEET_TEST/terraclim_pnull_grid_22") 
    
    test_input = {
        'start_yr': 2000,
        'end_yr': 2019,
        'target_ftc': GRID
     }
      
    # Rough value for uk (awaiting better reference data)
    test_result =  2.60
    calc_result = ee.Number(terraclim_mghr(**test_input)[0])
    assert abs(test_result - calc_result.getInfo()) < (0.05 * test_result)

 









