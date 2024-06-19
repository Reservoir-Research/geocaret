""" Define paths and folders for storing data, task monitoring structures
    and calculation options """
import ee
import sys
import os
from datetime import datetime


# ==============================================================================
# Developer Options
# ==============================================================================

# Jensen snap search radius
jensen_search_radius = 1000

# Select upstream basin finding method
upstreamMethod = 3

# Select DEM
# Use hydrologically conditioned DEM for parameter calculations?
paramHydroDEM = False

# Use hydrologically conditioned DEM for reservoir calculations?
resHydroDEM = False

# ==============================================================================
# Export Options
# ==============================================================================

# Export settings for "standard" outputs
exportRawDamPts = False
exportSnappedDamPts = True
exportWatershedCpts = False
exportWatershedDpts = False
exportCatchmentPixels = False
# Catchment vector must be exported for code to function
exportCatchmentVector = True
exportReservoirPixels = False
exportWaterbodies = False
# Reservoir vector must be exported for code to function
exportReservoirVector = True
exportBufferVector = True
# NI catchment vector must be exported for code to function
exportNiCatchmentVector = True
exportSimplifiedReservoir = False
exportSimplifiedReservoirBoundary = False
exportSinkLines = False
exportSourceLines = False
# River vector must be exported for code to function
exportRiver = False
exportMainRiver = True


# ==============================================================================
# Output Folders (EE)
# ==============================================================================

# Define name of the folder for storing temporary files/assets in EE
heet_folder = "XHEET/tmp"
# Define folder names (Must come after ee authentication check)
# Find the list of root folders the user owns in the Earth Engine

if "CI_ROBOT_USER" in os.environ:
    username = "ci-robot"
    root_folder = "projects/ee-future-dams/assets/ci-robot"
else:
    list_of_root_folders = ee.data.getAssetRoots()
    if list_of_root_folders:
        # Retrieve the first root folder if they exist
        username = ee.data.getAssetRoots()[0]["id"].split("/")[-1]
        root_folder = ee.data.getAssetRoots()[0]["id"]
    else:
        sys.exit(
            "Seems like no root folders exist in your Earth Engine \n"
            + "Create a home folder and try again."
        )

# Define names of folders inside the home folder in EE
ps_heet_folder = root_folder + "/" + heet_folder
dams_table_path = ps_heet_folder + "/" + "user_inputs"

# Set in heet_cli
output_drive_folder = ""
output_asset_folder_name = ""
