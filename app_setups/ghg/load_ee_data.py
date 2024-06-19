"""Load ee data from urls"""
import heet.gis.data as gis_data
from heet.utils import get_package_file, read_config

data_sources = read_config(get_package_file('./config/emissions/data.yaml'))

if __name__ == '__main__':
    # Instantiate the EE data objects
    hydrorivers = gis_data.HydroRiversData.from_config(config=data_sources)
    flow_accumulation = gis_data.FlowAccumulationData.from_config(
        config=data_sources)
    drainage_dir = gis_data.DrainageDirectionData.from_config(
        config=data_sources)
    hydrobasins_l12 = gis_data.HydroBasinsData.from_config(
        config=data_sources, level=12)

    HYDRORIVERS = hydrorivers.data
    FLOWACCUMULATION = flow_accumulation.band('b1')
    DRAINAGEDIRECTION = drainage_dir.band('b1')
    WDRAINAGEDIRECTION = drainage_dir.precondition()
    HYDROBASINS12 = hydrobasins_l12.data

    # Repetition here: hydrosheds-dict loads all hydrobasin data but above only
    # level 12 is used. Either initialize hydrosheds_dict and remove HYDROBASINS12
    # or only initialize the data that is required to limit the memory usage.
    hydrosheds_dict = gis_data.HydroShedsData.from_config(
        config=data_sources).data
