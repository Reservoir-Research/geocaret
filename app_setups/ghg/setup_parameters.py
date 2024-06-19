""" Set up collections of parameters to calculate on different feature
collections - catchment, nicatchment, reservoir and river"""
from typing import Any
import ee
import heet.emissions.catchment_parameters as cp
import heet.emissions.reservoir_parameters as rp
import heet.emissions.river_parameters as rrp
from heet.parameters.parameters import RawOutput, FormattedOutputValue


# Define a custom formatter for the windspeed parameter
def mean_annual_windspeed_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.2f")
    not_defined_val = kwargs.get('not_defined', "ND")
    err_val = kwargs.get('err_val', -999)
    return ee.Algorithms.If(
        ee.Number(output).neq(err_val),
        ee.Number(output).format(string_format), not_defined_val)


# Create dummy feature collections
# TO BE REPLACED WITH ACTUAL FEATURE COLLECTIONS!!!
catchment_fc = ee.Feature(ee.Geometry.Point(-62.54, -27.32), {'key': 'val'})
nicatchment_fc = ee.Feature(ee.Geometry.Point(-62.54, -27.32), {'key': 'val'})
reservoir_fc = ee.Feature(ee.Geometry.Point(-62.54, -27.32), {'key': 'val'})
river_fc = ee.Feature(ee.Geometry.Point(-62.54, -27.32), {'key': 'val'})

# TODO- IN PROFILE SETUP MAKE SURE BASED FEATURE COLLECTIONS CAN BE UPDATED
# WITH PARAMETER VALUES FROM PAR VECTORS

# TODO - get selected features too and construct the profile from this data
# features for catchment "c_area_km2",
cpar = [None] * 14
cpar[0] = cp.MeanSlopePercParameter(base_data=catchment_fc)
cpar[1] = cp.LandcoverParameter(base_data=catchment_fc)
cpar[2] = cp.MeanAnnualRunoffParameter(base_data=catchment_fc)
cpar[3] = cp.MeanAnnualPrecParameter(base_data=catchment_fc)
cpar[4] = cp.PredominantBiomeParameter(base_data=catchment_fc)
cpar[5] = cp.MeanSoilOrgCarbonParameter(base_data=catchment_fc)
cpar[6] = cp.TerraClimMonthlyMeanParameter(
    base_data=catchment_fc, name="mean monthly soil moisture",
    variables=["masm_mm"], units=["mm"], start_year=2000, end_year=2019,
    target_var='soil', scale_factor=0.1)  # Slow
cpar[7] = cp.SmapMonthlyMeanParameter(
        base_data=catchment_fc, name="mean annual soil moisture",
        variables=["masm_mm_alt1"], units=["mm"], start_year=2016,
        end_year=2021, target_var='smp')   # Alternative soil moisture
cpar[8] = cp.PredominantClimateParameter(base_data=catchment_fc)
cpar[9] = cp.TerraClimAnnualMeanParameter(
        base_data=catchment_fc,
        name="mean annual potential evapotranspiration",
        variables=["mpet_mm"], units=["mm"], start_year=2000, end_year=2019,
        target_var='pet', scale_factor=0.1)
cpar[10] = cp.PopulationParameter(base_data=catchment_fc)  # Pop. + pop. density
cpar[11] = cp.TerraClimAnnualMeanParameter(
        base_data=catchment_fc, name="mean annual runoff",
        variables=["mar_mm_alt2"], units=["mm"], start_year=2000,
        end_year=2019, target_var='ro', scale_factor=1)
        # Alt Mean annual runnoff (terraclim)
cpar[12] = cp.MeanOlsenParameter(base_data=catchment_fc)
cpar[13] = cp.SoilTypeParameter(base_data=catchment_fc)
# Add extra calculated parameters:
# "c_imputed_water_level": "NA",
# "c_imputed_water_level_prov": "NA"

nicpar = [None]
nicpar[0] = cp.PopulationParameter(base_data=nicatchment_fc)  # Pop. + pop. density
# updated_nicatchment_ftc = (
#     nicatchment_ftc.map(lambda feat: feat.set({
#         "n_population": c_current_population,
#         "n_population_density": c_current_population_density})))

rrpar = [None]
rrpar[0] = rrp.RiverLengthParameter(base_data=river_fc,
                                    variables=["ms_length"])

rpar = [None] * 10
# # Reservoir Area - add those in
# area_km2 = ee.Number(area(reservoir_ftc)).format("%.3f")
# area_m = ee.Number(km2_to_m2(area(reservoir_ftc))).format("%.3f")
rpar[0] = rp.MeanDepthParameter(base_data=reservoir_fc)
rpar[1] = rp.MaxDepthParameter(
    base_data=reservoir_fc, calc_option="default",
    variables=["maximum_depth_m"])
rpar[2] = rp.MaxDepthParameter(
    base_data=reservoir_fc, calc_option="alt1",
    variables=["maximum_depth_m_alt1"])
rpar[3] = rp.MaxDepthParameter(
    base_data=reservoir_fc, calc_option="alt2",
    variables=["maximum_depth_m_alt2"])
# Reservoir volume
# volume_m3 = ee.Number(reservoir_volume(km2_to_m2(area(reservoir_ftc)), mean_depth(reservoir_ftc))).format("%.3f")
rpar[4] = rp.MeanMonthlyTempsParameter(base_data=reservoir_fc) # mean monthly temp
rpar[5] = rp.TerraClimMGHRParameter(base_data=reservoir_fc)
# Mean annual global horizontal irradiance (NASA) 2005
rpar[6] = rp.MGHRParameter(
    base_data=reservoir_fc,
    variables=["mghr_all_alt1", "mghr_nov_mar_alt1", "mghr_may_sept_alt1"])
# Mean soil organic carbon (0-30cm), [kg m-1], Soil Grids
rpar[7] = cp.MeanSoilOrgCarbonParameter(base_data=reservoir_fc)
# Landcover (stratification by soil type needed)
rpar[8] = rp.LandCoverBySoilParameter(base_data=reservoir_fc)
rpar[9] = cp.TerraClimMonthlyMeanParameter(
        base_data=reservoir_fc,
        name="mean annual windspeed",
        variables=["mean_annual_windspeed"],
        units=["mm"], start_year=2000, end_year=2019,
        scale_factor=0.01, target_var='vs',
        formatters=[mean_annual_windspeed_formatter])
