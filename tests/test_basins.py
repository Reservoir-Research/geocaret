import pytest
import ee
import os

if 'GCLOUD_SERVICE_KEY' in os.environ:
    print("Running service account authentication")
    gc_service_account = os.environ['GCLOUD_ACCOUNT_EMAIL']
    credentials = ee.ServiceAccountCredentials(gc_service_account, 'service_account_creds.json')
    ee.Initialize(credentials)

else:
    print("Running individual account authentication")
    ee.Initialize()

def test_get_trailA():
  """Check that given two Pfafstetter ids A and B, extracts trailing digits of A"""
  from heet_basins import get_trailA
  
  test_input = {
      'A': ee.String("987654321987"),
      'B': ee.String("987654321900")
  }
 
  test_result = "87"
  
  assert get_trailA(**test_input).getInfo() == test_result
  
  test_input = {
      'A': ee.String("987654321900"),
      'B': ee.String("987654321987")      
  }
 
  test_result = "00"
  
  assert get_trailA(**test_input).getInfo() == test_result  
  

def test_all_odd_or_zero():
    """Check correctly identifies strings containing all odd or zero"""
    from heet_basins import all_odd_or_zero
    
    test_input = {
        'digit_string': ee.String("624"),
    }
       
    test_result = 0    
    assert all_odd_or_zero(**test_input).getInfo() == test_result
    
    
    test_input = {
        'digit_string': ee.String("357"),
    }
       
    test_result = 1
    
    assert all_odd_or_zero(**test_input).getInfo() == test_result
    
    test_input = {
        'digit_string': ee.String(""),
    }
       
    test_result = 0
    
    assert all_odd_or_zero(**test_input).getInfo() == test_result    

    
    
    



