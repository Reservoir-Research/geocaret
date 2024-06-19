import ee
import os

if "CI_ROBOT_USER" in os.environ:
    print("Running service account authentication")
    gc_service_account = os.environ["GCLOUD_ACCOUNT_EMAIL"]
    credentials = ee.ServiceAccountCredentials(
        gc_service_account, "service_account_creds.json"
    )
    ee.Initialize(credentials)

else:
    print("Running individual account authentication")
    ee.Initialize()

import pytest
import heet_data as dta
import logging

# ==============================================================================
#  Set up logger
# ==============================================================================


# Create new log each run (TODO; better implementation)
with open("tests.log", "w") as file:
    pass


# Gets or creates a logger
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.DEBUG)

# define file handler and set formatter
file_handler = logging.FileHandler("tests.log")
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)

# Delineation of future reservoir
def test_delineate_future_reservoir_input_we(monkeypatch):
    """Test that future reservoir delineation produces the same result
    irrespective of whether dam height or water elevation or
    supplied (where these are mathematically equivalent)
    """
    from heet_reservoir import delineate_future_reservoir

    # Set config parameters
    monkeypatch.setattr("heet_reservoir.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("heet_reservoir.cfg.upstreamMethod", 3)
    monkeypatch.setattr("heet_reservoir.cfg.paramHydroDEM", False)
    monkeypatch.setattr("heet_reservoir.cfg.resHydroDEM", False)
    monkeypatch.setattr("heet_reservoir.cfg.hydrodataset", "03")
    monkeypatch.setattr("heet_reservoir.cfg.delineate_snapped", True)

    catchmentAssetName = "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/C_1201"
    catchment_ftc = ee.FeatureCollection(catchmentAssetName)
    print(catchment_ftc.getInfo())

    # Input priority:
    # water_elevation > dam_height > power_capacity

    # Generic Function to remove a property from a feature (except id)
    def remove_all_properties(feat):
        ft_property_names = feat.propertyNames()
        target_properties = ft_property_names.filter(ee.Filter.eq("item", "id"))
        return feat.select(target_properties)

    # remove property all catchment properties
    initial_catchment_ftc = catchment_ftc.map(lambda feat: remove_all_properties(feat))
    print(initial_catchment_ftc.getInfo())

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
        lambda feat: feat.set(dam_height_parameters_dict)
    )

    test_input_dh = {"catchmentVector": dh_catchment_ftc, "c_dam_id_str": "1201"}
    print(dh_catchment_ftc.getInfo())

    test_dh_reservoir_ft = delineate_future_reservoir(**test_input_dh)
    test_dh_reservoir_geometry = ee.Feature(test_dh_reservoir_ft).geometry()
    # print(test_dh_reservoir_ft.getInfo())

    # S2: where water_elevation is provided and
    # dam height and power_capacity are missing
    we_parameters_dict = parameters_dict.copy()
    we_parameters_dict["t_dam_height"] = -999
    we_parameters_dict["power_capacity"] = -999

    we_catchment_ftc = initial_catchment_ftc.map(
        lambda feat: feat.set(we_parameters_dict)
    )

    test_input_we = {"catchmentVector": we_catchment_ftc, "c_dam_id_str": "1201"}

    test_we_reservoir_ft = delineate_future_reservoir(**test_input_we)
    test_we_reservoir_geometry = ee.Feature(test_we_reservoir_ft).geometry()

    difference_geometry = test_dh_reservoir_geometry.difference(
        **{"right": test_we_reservoir_geometry, "maxError": 1}
    )

    difference_geometry_area = difference_geometry.area().divide(1000 * 1000)

    test_result = 0
    calc_result = ee.Number(difference_geometry_area).getInfo()

    logger.info(
        f"[test_delineate_future_reservoir_input_we] Delineated Area difference {calc_result} "
        + f"Target: {test_result}"
    )

    # Difference is less than 0.001 sq km
    assert calc_result < 0.001


def test_delineate_future_reservoir_input_pc(monkeypatch):
    """Test that future reservoir delineation produces the same result
    irrespective of whether dam height or power capacity are
    supplied (where these are mathematically equivalent)
    """
    from heet_reservoir import delineate_future_reservoir

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
        "turbine_efficiency_prov": 1,
    }
    # Setup up difference scenarios

    # S1: where dam height is provided and
    # water_elevation and power_capacity are missing
    dam_height_parameters_dict = parameters_dict.copy()
    dam_height_parameters_dict["t_fsl_masl"] = -999
    dam_height_parameters_dict["power_capacity"] = -999

    dh_catchment_ftc = initial_catchment_ftc.map(
        lambda feat: feat.set(dam_height_parameters_dict)
    )

    test_input_dh = {"catchmentVector": dh_catchment_ftc, "c_dam_id_str": "1201"}

    test_dh_reservoir_ft = delineate_future_reservoir(**test_input_dh)
    test_dh_reservoir_geometry = ee.Feature(test_dh_reservoir_ft).geometry()

    # S3: where power_capacity is provided and
    # dam height and water_elevation are missing
    pc_parameters_dict = parameters_dict.copy()
    pc_parameters_dict["t_dam_height"] = -999
    pc_parameters_dict["t_fsl_masl"] = -999

    pc_catchment_ftc = initial_catchment_ftc.map(
        lambda feat: feat.set(pc_parameters_dict)
    )

    test_input_pc = {"catchmentVector": pc_catchment_ftc, "c_dam_id_str": "1201"}
    test_pc_reservoir_ft = delineate_future_reservoir(**test_input_pc)
    test_pc_reservoir_geometry = ee.Feature(test_pc_reservoir_ft).geometry()

    difference_geometry = test_dh_reservoir_geometry.difference(
        **{"right": test_pc_reservoir_geometry, "maxError": 1}
    )
    difference_geometry_area = difference_geometry.area().divide(1000 * 1000)

    test_result = 0
    calc_result = ee.Number(difference_geometry_area).getInfo()

    logger.info(
        f"[test_delineate_future_reservoir_input_pc] Delineated Area difference {calc_result} "
        + f"Target: {test_result}"
    )

    # Difference is less than 0.001 sq km
    assert calc_result < 0.001


def test_delineate_future_reservoir_input_dh(monkeypatch):
    """Test that future reservoir delineation produces the same result
    irrespective of whether dam height, water elevation or
    power capacity are supplied (where these are mathematically equivalent)
    """
    from heet_reservoir import delineate_future_reservoir

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
        lambda feat: feat.set(dam_height_parameters_dict)
    )

    test_input_dh = {"catchmentVector": dh_catchment_ftc, "c_dam_id_str": "1201"}

    test_dh_reservoir_ft = delineate_future_reservoir(**test_input_dh)
    test_dh_reservoir_geometry = ee.Feature(test_dh_reservoir_ft).geometry()

    difference_geometry = test_dh_reservoir_geometry.difference(
        **{"right": target_reservoir_geometry, "maxError": 1}
    )
    difference_geometry_area = difference_geometry.area().divide(1000 * 1000)

    test_result = 0
    calc_result = ee.Number(difference_geometry_area).getInfo()

    logger.info(
        f"[test_delineate_future_reservoir_input_dh] Delineated Area difference {calc_result} "
        + f"Target: {test_result} "
    )

    # Difference is less than 0.001 sq km
    assert calc_result < 0.001
