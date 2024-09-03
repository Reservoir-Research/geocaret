""" Module defining datasets used for catchment and reservoir delineation
    required for calculation of input data for GHG emission calculations """
import ee
# Import asset locations from config
import sys
#sys.path.append("..")
import geocaret.lib as lib


# ==============================================================================
# Datasets (Names of datasets available in the Earth Engine)
# ==============================================================================
# Hydrosheds Flow Accumulation
# This flow accumulation dataset defines the amount of upstream area (in number
# of cells) draining into each cell. The drainage direction layer is used to
# define which cells flow into the target cell. The number of accumulated cells
# is essentially a measure of the upstream catchment area. However, since the
# cell size of the HydroSHEDS data set depends on latitude, the cell
# accumulation value cannot directly be translated into drainage areas in square
# kilometers. Values range from 1 at topographic highs (river sources) to very
# large numbers (on the order of millions of cells) at the mouths of large
# rivers.
# This dataset is at 15 arc-second resolution.
# Lehner, B., Verdin, K., Jarvis, A. (2008): New global hydrography derived
# from spaceborne elevation data. Eos, Transactions, AGU, 89(10): 93-94
FLOWACCUMULATION_NAME = lib.get_public_asset("hydrosheds_flow_acc")
# Hydrosheds Hydrorivers
# Global river network delineation derived from HydroSHEDS data at 15 arc-second
# resolution
# Lehner, B., Grill G. (2013): Global river hydrography and network routing:
# baseline data and new approaches to study the world’s large river systems.
# Hydrological Processes, 27(15): 2171–2186. Data is available at
# www.hydrosheds.org
HYDRORIVERS_NAME = lib.get_private_asset("hydrorivers_v10")
# Hydrosheds Drainage Directions
# This dataset is at 15 arc-second resolution. The datasets available at 15
# arc-seconds are the Hydrologically Conditioned DEM, Drainage (Flow)
# Direction, and Flow Accumulation
# The drainage direction values follow the convention adopted by ESRI's flow
# direction implementation: 1=E, 2=SE, 4=S, 8=SW, 16=W, 32=NW, 64=N, 128=NE
HYDROSHEDS_DD_NAME = lib.get_public_asset("hydrosheds_drainage_dir")
# Hydrosheds Hydrobasins 12
# Global watershed boundaries and sub-basin delineations
# derived from HydroSHEDS data at 15 second resolution
# This dataset provides polygons of nested, hierarchical watersheds, based on
# 15 arc-seconds (approx. 500 m at the equator) resolution raster data.
# The watersheds range from level 1 (coarse) to level 12 (detailed),
# using Pfastetter codes. hybas_12 is at level 12 (detailed)
# Lehner, B., Grill G. (2013): Global river hydrography and network routing:
# baseline data and new approaches to study the world’s large river systems.
# Hydrological Processes, 27(15): 2171–2186. Data is available at
# www.hydrosheds.org
HYDROBASINS12_NAME = lib.get_public_asset("hydrobasins_12")
# WWF HydroSHEDS Basins Level N (n = 1…12)

# ==================================================================
# Drainage Directions
# ==================================================================
def prepare_dd() -> ee.Image:
    """Processes HydroSHEDS Drainage Directions dataset, remap pixel values
    add coordinate and pixel id metadata, returns processed image with
    additional bands"""
    # Retrieve image with selected band(s)
    dd_asset = ee.Image(HYDROSHEDS_DD_NAME).select(["b1"], ["d1"])
    # Remap pixel values
    dd_grid = ee.Image(dd_asset).remap(
        **{
            "from": [1, 2, 4, 8, 16, 32, 64, 128, 0, 255],
            "to": [6, 9, 8, 7, 4, 1, 2, 3, 0, 255],
            "bandName": "d1",
            "defaultValue": 999,
        }
    )
    # Add longitude and latitude (lnglat) to drainage direction img
    proj = dd_grid.select([0]).projection()
    lnglat = ee.Image.pixelLonLat().reproject(proj)
    coords = ee.Image.pixelCoordinates(proj).rename(["gid", "j"])
    # Define expressions to be executed for every field variable
    field_expression_map = {
        "gid": coords.select("gid"),
        "j": coords.select("j"),
    }
    # Bug in EE with renaming means we use gid here (insead of i)
    x_img = ee.Image().expression("gid", field_expression_map)
    y_img = ee.Image().expression("j", field_expression_map)
    # Add pixel id to drainage direction img
    grid_ident = x_img.long().leftShift(32).add(y_img.long()).rename(["grid_id"])
    # Add metadata (bands) with pixel id and longitude and latitude
    dd_grid_coord = dd_grid.addBands(grid_ident).addBands(lnglat)
    return dd_grid_coord


# ==============================================================================
# Data sources
# ==============================================================================
hydrosheds_dict = ee.Dictionary(
        {str(ix+1) : ee.FeatureCollection(
            lib.get_public_asset("hydrosheds") + "v1/Basins/" + f"hybas_{ix+1}") for ix in range(0,12)}
    )

# Hydrosheds Flow Accumulation - b1 band contains flow accumulation data
# between 1 and 2.78651e+07
FLOWACCUMULATION = ee.Image(FLOWACCUMULATION_NAME).select("b1")

# Hydrosheds Hydrorivers
HYDRORIVERS = ee.FeatureCollection(HYDRORIVERS_NAME)

# Hydrosheds Drainage Directions (Image) - b1 band contains drainage direction
# information between 0 and 255.
# 1=E, 2=SE, 4=S, 8=SW, 16=W, 32=NW, 64=N, 128=NE;
# final outlet cells to the ocean are flagged with a value of 0 and cells that
# mark the lowest point of an endorheic basin (inland sink) are flagged with a
# value of 255 (original value of -1)
DRAINAGEDIRECTION = ee.Image(HYDROSHEDS_DD_NAME).select("b1")

# Hydrosheds Hydrobasins at level 12 (FeatureCollection)
# Retrieve collection and add a new field with string representation
# of Pfafstetter code (PFAF_ID)
HYDROBASINS12 = ee.FeatureCollection(HYDROBASINS12_NAME).map(
    lambda feat: feat.set({"SPFAF_ID": ee.Number(feat.get("PFAF_ID")).format("%s")})
)

# Pre-conditioned Hydrosheds Drainage Directions Dataset (Image)
WDRAINAGEDIRECTION = prepare_dd()
