""" """
from typing import Tuple, Dict
from heet.profiles.profile import Profile
from heet.profiles.profile_output import ProfileOutput
from heet.parameters.parameters import Parameter
from heet.parameters.emissions.catchment_parameters import (
    MeanSlopePercParameter, MGHRParameter, MeanAnnualRunoffParameter,
    MeanAnnualPrecParameter, PredominantBiomeParameter,
    PredominantClimateParameter, MeanOlsenParameter)


CATCHMENT_PARAMETERS: Tuple[Parameter] = (
    MeanSlopePercParameter, MGHRParameter, MeanAnnualRunoffParameter,
    MeanAnnualPrecParameter, PredominantBiomeParameter,
    PredominantClimateParameter, MeanOlsenParameter
)

# For cross-checking with Kamilla's code
REQUIRED_VARIABLES: Dict[str, str] = {
    "c_area_km2": "NA",
    "c_mean_slope_pc": "NA",
    "c_landcover_0": "NA",
    "c_landcover_1": "NA",
    "c_landcover_2": "NA",
    "c_landcover_3": "NA",
    "c_landcover_4": "NA",
    "c_landcover_5": "NA",
    "c_landcover_6": "NA",
    "c_landcover_7": "NA",
    "c_landcover_8": "NA",
    "c_mar_mm": "NA",
    "c_map_mm": "NA",
    "c_biome": "NONE",
    "c_msoc_kgperm": "NA",
    "c_masm_mm": "NA", # Slow
    "c_masm_mm_alt1": "NA",
    "c_climate_zone": "NA",
    "c_mpet_mm": "NA",
    "c_population": "NA",
    "c_population_density": "NA",
    "c_mar_mm_alt1": "NA", # Very Slow
    "c_mar_mm_alt2": "NA",
    "c_mean_olsen": "NA",
    "c_soil_type": "NONE",
    "c_imputed_water_level": "NA",
    "c_imputed_water_level_prov": "NA"}


class CatchmentProfile(Profile):
    """ """
    VAR_PREFIX = "c_"

    def populate(self) -> ProfileOutput:
        """ """


if __name__ == '__main__':
    catchment_object = []
    catchment_profile = CatchmentProfile(gis_object=catchment_object)
    parameters_1 = [parameter(base_data=catchment_object) for parameter in
                    CATCHMENT_PARAMETERS]
    for parameter in parameters_1:
        catchment_profile.add_parameter(parameter)

    print(catchment_profile.parameter_names)

    prof_out = ProfileOutput.empty(var_value_pairs=REQUIRED_VARIABLES)
    print(prof_out.output)
