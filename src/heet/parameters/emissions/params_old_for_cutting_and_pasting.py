""" """
import ee
import heet.monitor as mtr
import heet.export
import heet.log_setup
from heet.assets import EmissionAssets

assets = EmissionAssets()

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)

# ==============================================================================
# Populated Profiles
# ==============================================================================


def profile_catchment(catchment_ftc):
    """ """
    # Catchment area
    area_km2 = ee.Number(area(catchment_ftc)).format("%.3f")

    # Mean discharge
    mad_m3_peryr = ee.Algorithms.If(
        ee.Number(t_mar_mm).neq(-999),
        ee.Number(mean_annual_runoff_mm(
            catchment_ftc)).multiply(area(catchment_ftc)).multiply(1000),
        "ND")

    mad_m3_pers = ee.Number(mad_m3_peryr).divide(31557600)

    # Estimated dam height
    catchFeat = catchment_ftc.first()

    water_level = ee.Number(catchFeat.get('t_water_level'))
    dam_height = ee.Number(catchFeat.get('t_dam_height'))
    turbine_efficiency = ee.Number(catchFeat.get('t_turbine_efficiency'))
    power_capacity = ee.Number(catchFeat.get('power_capacity'))
    plant_depth = ee.Number(catchFeat.get('t_plant_depth'))

    # print("[DEBUG] t_water_level", water_level.getInfo())
    # print("[DEBUG] t_dam_height", dam_height.getInfo())
    # print("[DEBUG] t_turbine_efficiency", turbine_efficiency.getInfo())
    # print("[DEBUG] power_capacity", power_capacity.getInfo())
    # print("[DEBUG] t_plant_depth", plant_depth.getInfo())
    # print("[DEBUG] denominator", denominator.getInfo())
    # print("[DEBUG] calc_dam_height", calc_dam_height.getInfo())

    from heet.gis.dams import Dam

    imputed_dam_height = ee.Algorithms.If(
        dam_height.eq(-999),
        Dam.impute_dam_height(
            power_capacity, turbine_efficiency, plant_depth, mad_m3_pers),
        dam_height)

    # print("[DEBUG] imputed_dam_height", imputed_dam_height.getInfo())

    # Impute water level
    imputed_water_level = ee.Number(ee.Algorithms.If(
        water_level.eq(-999),
        imputed_dam_height,
        water_level)).format("%.0f")

    # print("[DEBUG] imputed_water_level", imputed_water_level.getInfo())

    # Imputed water level provence
    # 0 - User input water level
    # 1 - User input dam height
    # 2 - Dam height estimated from power capacity (known turbine efficiency)
    # 3 - Dam height estimated from power capacity (unknown turbine efficiency)

    turbine_efficiency_prov = catchFeat.get('turbine_efficiency_prov')

    imputed_dam_height_prov = ee.Algorithms.If(
        dam_height.eq(-999),
        ee.Number(2).add(turbine_efficiency_prov),
        1
    )

    # Impute water level
    imputed_water_level_prov = ee.Algorithms.If(
        water_level.eq(-999),
        imputed_dam_height_prov,
        0
    )

    c_imputed_water_level_prov = imputed_water_level_prov
    c_imputed_water_level = imputed_water_level





def profile_reservoir(reservoir_ftc) -> ee.FeatureCollection:
    """ """
    # Mean annual global horizontal irradiance (terraclim)
    #  TODO terraclim_mghr underdevelopment (see heet_params_draft)
    # Example use: terraclim_mghr(2000, 2019, reservoir_ftc)
    maghr_kwhperm2perday_alt1 = "UD"
    mghr_all_kwhperm2perday_alt1 = "UD"
    mghr_nov_mar_kwhperm2perday_alt1 = "UD"
    mghr_may_sept_kwhperm2perday_alt1 = "UD"


def batch_delete_shapes(c_dam_ids, output_type) :
    """ """
    file_prefix = heet.export.export_job_specs[output_type]['fileprefix']
    for c_dam_id in c_dam_ids:
        c_dam_id_str = str(c_dam_id)
        targetAssetName = assets.ps_heet_folder + "/" + file_prefix + c_dam_id_str
        try:
            ee.data.deleteAsset(targetAssetName)
        except Exception as error:
            msg = f"Problem deleting intermediate output {targetAssetName}"
            logger.exception(f'{msg}')
            continue


def batch_profile_reservoirs(c_dam_ids):
    """ """
    for c_dam_id in c_dam_ids:
        c_dam_id_str = str(c_dam_id)
        reservoirAssetName = assets.ps_heet_folder + "/" + "r_" + c_dam_id_str
        reservoir_ftc = ee.FeatureCollection(reservoirAssetName)
        try:
            updated_reservoir_ftc = profile_reservoir(reservoir_ftc)
            heet.export.export_ftc(updated_reservoir_ftc, c_dam_id_str, "reservoir_vector_params")
        except Exception as error:
            msg = "Problem updating Reservoir vector with calculated parameters"
            logger.exception(f'{msg}')
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


def batch_profile_catchments(c_dam_ids):
    """ """
    for c_dam_id in c_dam_ids:
        c_dam_id_str = str(c_dam_id)
        catchmentAssetName = assets.ps_heet_folder + "/" + "c_" + c_dam_id_str
        catchment_ftc = ee.FeatureCollection(catchmentAssetName)
        try:
            updated_catchment_ftc = profile_catchment(catchment_ftc)
            heet.export.export_ftc(updated_catchment_ftc, c_dam_id_str, "catchment_vector_params")
        except Exception as error:
            msg = "Problem updating Catchment vector with calculated parameters"
            logger.exception(f'{msg}')
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


def batch_profile_rivers(c_dam_ids):
    """ """
    for c_dam_id in c_dam_ids:
        c_dam_id_str = str(c_dam_id)
        riverAssetName = assets.ps_heet_folder + "/" + "ms_" + c_dam_id_str
        river_ftc = ee.FeatureCollection(riverAssetName)
        try:
            updated_river_ftc = profile_river(river_ftc)
            heet.export.export_ftc(ee.FeatureCollection(updated_river_ftc), c_dam_id_str, "main_river_vector_params")
        except Exception as error:
            msg = "Problem updating River vector with calculated parameters"
            logger.exception(f'{msg}')
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


def batch_profile_nicatchments(c_dam_ids):
    """ """
    for c_dam_id in c_dam_ids:
        c_dam_id_str = str(c_dam_id)
        nicatchmentAssetName = assets.ps_heet_folder + "/" + "n_" + c_dam_id_str
        nicatchment_ftc = ee.FeatureCollection(nicatchmentAssetName)
        try:
            updated_nicatchment_ftc = profile_nicatchment(nicatchment_ftc)
            heet.export.export_ftc(updated_nicatchment_ftc, c_dam_id_str, "ni_catchment_vector_params")
        except Exception as error:
            msg = "Problem updating NI Catchment vector with calculated parameters"
            logger.exception(f'{msg}')
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


if __name__ == "__main__":
    pass
    # Development
    # reservoir_ftc = ee.FeatureCollection("users/KamillaHarding/XHEET/tmp/r_XXXX")
    # reservoir_geom = reservoir_ftc.geometry()
    # reservoir_properties = profile_reservoir(reservoir_ftc)
    # print(reservoir_properties.getInfo())
