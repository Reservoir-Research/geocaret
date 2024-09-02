"""
This module contains test cases for delineating future reservoirs using the 
`delineate_future_reservoir` function from the `heet_reservoir` package. The tests 
ensure that the function behaves consistently under different input scenarios by 
comparing the geometries of the delineated reservoirs.

The test cases verify that the delineated reservoir areas are equivalent when:
1. Different inputs are provided, such as water elevation, dam height, or power capacity.
2. Configurations are modified using `monkeypatch` to simulate various conditions.
3. The input parameters are mathematically equivalent, leading to similar results.

The following tests are included:
- `test_delineate_future_reservoir_input_we`: Tests equivalence of results when dam height 
  and water elevation are provided, ensuring the delineated area is consistent regardless of 
  the input used.
- `test_delineate_future_reservoir_input_pc`: Tests equivalence of results when dam height 
  and power capacity are provided, ensuring the delineated area is consistent regardless of 
  the input used.
- `test_delineate_future_reservoir_input_dh`: Tests equivalence of results when dam height, 
  water elevation, and power capacity are provided, ensuring the delineated area is consistent 
  regardless of the input used.
"""
import ee
import os
import pytest
import logging


# Delineation of future reservoir
def test_delineate_future_reservoir_input_we(monkeypatch, get_logger) -> None:
    """
    Test that future reservoir delineation produces the same result irrespective 
    of whether dam height or water elevation are supplied (where these are 
    mathematically equivalent).

    The test modifies configuration settings using `monkeypatch` to simulate 
    different scenarios, then compares the geometries of the delineated reservoirs 
    to ensure that the differences are negligible.

    Args:
        monkeypatch: Pytest fixture that allows modifying or simulating modules and attributes.
        get_logger: Pytest fixture for logging messages during testing.

    Asserts:
        The calculated difference in area between two delineated reservoirs is less than 0.001 sq km.
    """
    from heet_reservoir import delineate_future_reservoir
    logger=get_logger
    # Set config parameters
    monkeypatch.setattr("heet_reservoir.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("heet_reservoir.cfg.upstreamMethod", 3)
    monkeypatch.setattr("heet_reservoir.cfg.paramHydroDEM", False)
    monkeypatch.setattr("heet_reservoir.cfg.resHydroDEM", False)
    monkeypatch.setattr("heet_reservoir.cfg.hydrodataset", "03")
    monkeypatch.setattr("heet_reservoir.cfg.delineate_snapped", True)
    catchmentAssetName = "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/C_1201"
    catchment_ftc = ee.FeatureCollection(catchmentAssetName)
    #print(catchment_ftc.getInfo())
    # Input priority:
    # water_elevation > dam_height > power_capacity
    # Generic Function to remove a property from a feature (except id)
    def remove_all_properties(feat):
        ft_property_names = feat.propertyNames()
        target_properties = ft_property_names.filter(ee.Filter.eq("item", "id"))
        return feat.select(target_properties)
    # remove property all catchment properties
    initial_catchment_ftc = catchment_ftc.map(lambda feat: remove_all_properties(feat))
    #print(initial_catchment_ftc.getInfo())
    # Artificial parameters
    # pre-calculated to ensure equivalence
    parameters_dict = {
        "t_fsl_masl": 1495,
        "t_dam_height": 47,
        "t_turbine_efficiency": 85,
        "power_capacity": 16.3349281448784,
        "t_plant_depth": 0,
        "c_mad_m3_pers": "41.68035769706623",
        "raw_lon": 98.580461,
        "raw_lat": 26.051936,
        "ps_lon": 98.58081382992276,
        "ps_lat": 26.051648549730924,
        "turbine_efficiency_prov": 1,}
    # Setup up difference scenarios
    # S1: where dam height is provided and
    # water_elevation and power_capacity are missing
    dam_height_parameters_dict = parameters_dict.copy()
    dam_height_parameters_dict["t_fsl_masl"] = -999
    dam_height_parameters_dict["power_capacity"] = -999
    dh_catchment_ftc = initial_catchment_ftc.map(
        lambda feat: feat.set(dam_height_parameters_dict))
    test_input_dh = {"catchmentVector": dh_catchment_ftc, "c_dam_id_str": "1201"}
    #print(dh_catchment_ftc.getInfo())
    test_dh_reservoir_ft = delineate_future_reservoir(**test_input_dh)
    test_dh_reservoir_geometry = ee.Feature(test_dh_reservoir_ft).geometry()
    # print(test_dh_reservoir_ft.getInfo())
    # S2: where water_elevation is provided and
    # dam height and power_capacity are missing
    we_parameters_dict = parameters_dict.copy()
    we_parameters_dict["t_dam_height"] = -999
    we_parameters_dict["power_capacity"] = -999
    we_catchment_ftc = initial_catchment_ftc.map(
        lambda feat: feat.set(we_parameters_dict))
    test_input_we = {"catchmentVector": we_catchment_ftc, "c_dam_id_str": "1201"}
    test_we_reservoir_ft = delineate_future_reservoir(**test_input_we)
    test_we_reservoir_geometry = ee.Feature(test_we_reservoir_ft).geometry()
    difference_geometry = test_dh_reservoir_geometry.difference(
        **{"right": test_we_reservoir_geometry, "maxError": 1})
    difference_geometry_area = difference_geometry.area().divide(1000 * 1000)
    test_result = 0
    calc_result = ee.Number(difference_geometry_area).getInfo()
    logger.info(
        f"[test_delineate_future_reservoir_input_we] Delineated Area difference {calc_result} " +
        f"Target: {test_result}")
    # Difference is less than 0.001 sq km
    assert calc_result < 0.001


def test_delineate_future_reservoir_input_pc(monkeypatch, get_logger) -> None:
    """
    Test that future reservoir delineation produces the same result irrespective 
    of whether dam height or power capacity are supplied (where these are 
    mathematically equivalent).

    The test modifies configuration settings using `monkeypatch` to simulate 
    different scenarios, then compares the geometries of the delineated reservoirs 
    to ensure that the differences are negligible.

    Args:
        monkeypatch: Pytest fixture that allows modifying or simulating modules and attributes.
        get_logger: Custom logger function for logging messages during testing.

    Asserts:
        The calculated difference in area between two delineated reservoirs is less than 0.001 sq km.
    """
    from heet_reservoir import delineate_future_reservoir
    logger=get_logger
    monkeypatch.setattr("heet_reservoir.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("heet_reservoir.cfg.upstreamMethod", 3)
    monkeypatch.setattr("heet_reservoir.cfg.paramHydroDEM", False)
    monkeypatch.setattr("heet_reservoir.cfg.resHydroDEM", False)
    monkeypatch.setattr("heet_reservoir.cfg.hydrodataset", "03")
    monkeypatch.setattr("heet_reservoir.cfg.delineate_snapped", True)
    catchmentAssetName = "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/C_1201"
    catchment_ftc = ee.FeatureCollection(catchmentAssetName)
    # Input priority:
    # water_elevation > dam_height > power_capacity
    # Generic Function to remove a property from a feature (except id)
    def remove_all_properties(feat):
        ft_property_names = feat.propertyNames()
        target_properties = ft_property_names.filter(ee.Filter.eq("item", "id"))
        return feat.select(target_properties)
    # remove property all catchment properties
    initial_catchment_ftc = catchment_ftc.map(lambda feat: remove_all_properties(feat))
    # Artificial parameters
    # pre-calculated to ensure equivalence
    parameters_dict = {
        "t_fsl_masl": 1495,
        "t_dam_height": 47,
        "t_turbine_efficiency": 85,
        "power_capacity": 16.3349281448784,
        "t_plant_depth": 0,
        "c_mad_m3_pers": "41.68035769706623",
        "raw_lon": 98.580461,
        "raw_lat": 26.051936,
        "ps_lon": 98.58081382992276,
        "ps_lat": 26.051648549730924,
        "turbine_efficiency_prov": 1,}
    # Setup up difference scenarios
    # S1: where dam height is provided and
    # water_elevation and power_capacity are missing
    dam_height_parameters_dict = parameters_dict.copy()
    dam_height_parameters_dict["t_fsl_masl"] = -999
    dam_height_parameters_dict["power_capacity"] = -999
    dh_catchment_ftc = initial_catchment_ftc.map(
        lambda feat: feat.set(dam_height_parameters_dict))
    test_input_dh = {"catchmentVector": dh_catchment_ftc, "c_dam_id_str": "1201"}
    test_dh_reservoir_ft = delineate_future_reservoir(**test_input_dh)
    test_dh_reservoir_geometry = ee.Feature(test_dh_reservoir_ft).geometry()
    # S3: where power_capacity is provided and
    # dam height and water_elevation are missing
    pc_parameters_dict = parameters_dict.copy()
    pc_parameters_dict["t_dam_height"] = -999
    pc_parameters_dict["t_fsl_masl"] = -999
    pc_catchment_ftc = initial_catchment_ftc.map(
        lambda feat: feat.set(pc_parameters_dict))
    test_input_pc = {"catchmentVector": pc_catchment_ftc, "c_dam_id_str": "1201"}
    test_pc_reservoir_ft = delineate_future_reservoir(**test_input_pc)
    test_pc_reservoir_geometry = ee.Feature(test_pc_reservoir_ft).geometry()
    difference_geometry = test_dh_reservoir_geometry.difference(
        **{"right": test_pc_reservoir_geometry, "maxError": 1})
    difference_geometry_area = difference_geometry.area().divide(1000 * 1000)
    test_result = 0
    calc_result = ee.Number(difference_geometry_area).getInfo()
    logger.info(
        f"[test_delineate_future_reservoir_input_pc] Delineated Area difference {calc_result} " +
        f"Target: {test_result}")
    # Difference is less than 0.001 sq km
    assert calc_result < 0.001


def test_delineate_future_reservoir_input_dh(monkeypatch, get_logger) -> None:
    """
    Test that future reservoir delineation produces the same result irrespective 
    of whether dam height, water elevation, or power capacity are supplied (where 
    these are mathematically equivalent).

    The test modifies configuration settings using `monkeypatch` to simulate 
    different scenarios, then compares the geometries of the delineated reservoirs 
    to ensure that the differences are negligible.

    Args:
        monkeypatch: Pytest fixture that allows modifying or simulating modules and attributes.
        get_logger: Custom logger function for logging messages during testing.

    Asserts:
        The calculated difference in area between two delineated reservoirs is less than 0.001 sq km.
    """
    from heet_reservoir import delineate_future_reservoir
    logger=get_logger
    # Set config options explicitly for this test
    monkeypatch.setattr("heet_reservoir.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("heet_reservoir.cfg.upstreamMethod", 3)
    monkeypatch.setattr("heet_reservoir.cfg.paramHydroDEM", False)
    monkeypatch.setattr("heet_reservoir.cfg.resHydroDEM", False)
    monkeypatch.setattr("heet_reservoir.cfg.hydrodataset", "03")
    monkeypatch.setattr("heet_reservoir.cfg.delineate_snapped", True)
    catchmentAssetName = "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/C_1201"
    catchment_ftc = ee.FeatureCollection(catchmentAssetName)
    reservoirAssetName = "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/R_1201"
    reservoir_ftc = ee.FeatureCollection(reservoirAssetName)
    target_reservoir_geometry = ee.Feature(reservoir_ftc.first()).geometry()
    # Input priority:
    # water_elevation > dam_height > power_capacity
    # Generic Function to remove a property from a feature (except id)
    def remove_all_properties(feat):
        ft_property_names = feat.propertyNames()
        target_properties = ft_property_names.filter(ee.Filter.eq("item", "id"))
        return feat.select(target_properties)
    # remove property all catchment properties
    initial_catchment_ftc = catchment_ftc.map(lambda feat: remove_all_properties(feat))
    # Artificial parameters
    # pre-calculated to ensure equivalence
    parameters_dict = {
        "t_fsl_masl": 1495,
        "t_dam_height": 47,
        "t_turbine_efficiency": 85,
        "power_capacity": 16.3349281448784,
        "t_plant_depth": 0,
        "c_mad_m3_pers": "41.68035769706623",
        "raw_lon": 98.580461,
        "raw_lat": 26.051936,
        "ps_lon": 98.58081382992276,
        "ps_lat": 26.051648549730924,
        "turbine_efficiency_prov": 1,
    }
    # Setup up difference scenarios
    # S1: where dam height is provided and
    # water_elevation and power_capacity are missing
    dam_height_parameters_dict = parameters_dict.copy()
    dam_height_parameters_dict["t_fsl_masl"] = -999
    dam_height_parameters_dict["power_capacity"] = -999
    dh_catchment_ftc = initial_catchment_ftc.map(
        lambda feat: feat.set(dam_height_parameters_dict))
    test_input_dh = {"catchmentVector": dh_catchment_ftc, "c_dam_id_str": "1201"}
    test_dh_reservoir_ft = delineate_future_reservoir(**test_input_dh)
    test_dh_reservoir_geometry = ee.Feature(test_dh_reservoir_ft).geometry()
    difference_geometry = test_dh_reservoir_geometry.difference(
        **{"right": target_reservoir_geometry, "maxError": 1})
    difference_geometry_area = difference_geometry.area().divide(1000 * 1000)
    test_result = 0
    calc_result = ee.Number(difference_geometry_area).getInfo()
    logger.info(
        f"[test_delineate_future_reservoir_input_dh] Delineated Area difference {calc_result} " +
        f"Target: {test_result} "
    )
    # Difference is less than 0.001 sq km
    assert calc_result < 0.001
