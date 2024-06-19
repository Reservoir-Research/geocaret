""" """
from typing import Dict
from heet.profiles.profile import Profile
from heet.profiles.profile_output import ProfileOutput

REQUIRED_VARIABLES: Dict[str, str] = {
     "r_area_km2": "NA",
     "r_mean_depth_m": "NA",
     "r_maximum_depth_m": "NA",
     "r_maximum_depth_m_alt1": "NA",
     "r_maximum_depth_m_alt2": "NA",
     "r_volume_m3": "NA",
     "r_mean_temp_1": "NA",
     "r_mean_temp_2": "NA",
     "r_mean_temp_3": "NA",
     "r_mean_temp_4": "NA",
     "r_mean_temp_5": "NA",
     "r_mean_temp_6": "NA",
     "r_mean_temp_7": "NA",
     "r_mean_temp_8": "NA",
     "r_mean_temp_9": "NA",
     "r_mean_temp_10": "NA",
     "r_mean_temp_11": "NA",
     "r_mean_temp_12": "NA",
     "r_mghr_all_kwhperm2perday": "NA",
     "r_mghr_nov_mar_kwhperm2perday": "NA",
     "r_mghr_may_sept_kwhperm2perday": "NA",
     "r_mghr_all_kwhperm2perday_alt1": "NA",
     "r_mghr_nov_mar_kwhperm2perday_alt1": "NA",
     "r_mghr_may_sept_kwhperm2perday_alt1": "NA",
     "r_msoc_kgperm2": "NA",
     "r_landcover_bysoil_0": "NA",
     "r_landcover_bysoil_1": "NA",
     "r_landcover_bysoil_2": "NA",
     "r_landcover_bysoil_3": "NA",
     "r_landcover_bysoil_4": "NA",
     "r_landcover_bysoil_5": "NA",
     "r_landcover_bysoil_6": "NA",
     "r_landcover_bysoil_7": "NA",
     "r_landcover_bysoil_8": "NA",
     "r_landcover_bysoil_9": "NA",
     "r_landcover_bysoil_10": "NA",
     "r_landcover_bysoil_11": "NA",
     "r_landcover_bysoil_12": "NA",
     "r_landcover_bysoil_13": "NA",
     "r_landcover_bysoil_14": "NA",
     "r_landcover_bysoil_15": "NA",
     "r_landcover_bysoil_16": "NA",
     "r_landcover_bysoil_17": "NA",
     "r_landcover_bysoil_18": "NA",
     "r_landcover_bysoil_19": "NA",
     "r_landcover_bysoil_20": "NA",
     "r_landcover_bysoil_21": "NA",
     "r_landcover_bysoil_22": "NA",
     "r_landcover_bysoil_23": "NA",
     "r_landcover_bysoil_24": "NA",
     "r_landcover_bysoil_25": "NA",
     "r_landcover_bysoil_26": "NA",
     "r_mean_annual_windspeed": "NA"}


class ReservoirProfile(Profile):
    """ """

    def populate(self) -> ProfileOutput:
        """ """
