# Private Assets

The HEET tool relies on a number of data sources that are/were unavailable in Google Earth Engine
at the time of development.

These are currently hosted on Kamilla Harding's personal Google Earth Engine account.
Access has been granted to current Future Dam's team. 
License conditions will need to be checked before sharing more widely.

- users/KamillaHarding/XHEET_ASSETS/HydroRIVERS_v10
- users/KamillaHarding/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds-lccs_class
- users/KamillaHarding/XHEET_ASSETS/GHI_NASA_low
- users/KamillaHarding/XHEET_ASSETS/cmp_ro_grdc
- users/KamillaHarding/XHEET_ASSETS/wc2-1_30s_bio_12
- users/KamillaHarding/XHEET_ASSETS/Beck_KG_V1_present_0p0083
- users/KamillaHarding/XHEET_ASSETS/wc2-1_30s_tavg
- users/KamillaHarding/XHEET_ASSETS/OlsenP_kgha1_World*

*Currently (2022-02) to be kept confidential

# Sources

|     Asset                                                          |     Website                                                                                                                                                                                |     Data url                                                                                                                           |
|--------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
|     Beck_KG_V1_present_0p0083.tif                                  |     http://www.gloh2o.org/koppen/                                                                                                                                                          |     https://figshare.com/articles/dataset/Present_and_future_K_ppen-Geiger_climate_classification_maps_at_1-km_resolution/6396959/2    |
|     ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds-lccs_class.nc    |     http://maps.elie.ucl.ac.be/CCI/viewer/download.php                                                                                                                                     |     http://maps.elie.ucl.ac.be/CCI/viewer/download.php                                                                                 |
|     GHI_NASA_low                                                   |     https://geodata.lib.berkeley.edu/catalog/stanford-fd535zg0917           Also:     https://maps.princeton.edu/catalog/stanford-xx487wn6207     https://purl.stanford.edu/fd535zg0917    |     https://geodata.lib.berkeley.edu/catalog/stanford-fd535zg0917     [https://purl.stanford.edu/fd535zg0917]                          |
|     HydroRIVERS_v10.shp                                            |     https://www.hydrosheds.org/page/hydrorivers                                                                                                                                            |     https://www.hydrosheds.org/page/hydrorivers                                                                                        |
|     OCSTHA_M_30cm_250m_ll                                          |     https://www.isric.org/explore/soilgrids/faq-soilgrids-2017                                                                                                                             |     https://files.isric.org/soilgrids/former/2017-03-10/data/                                                                          |
|     cmp_ro_grdc                                            |     https://www.compositerunoff.sr.unh.edu/html/Runoff/index.html                                                                                                                          |     https://www.compositerunoff.sr.unh.edu/html/Runoff/index.html                                                                      |
|     wc2-1_30s_bio_12                                               |     https://www.worldclim.org/data/worldclim21.html#                                                                                                                                       |     https://www.worldclim.org/data/worldclim21.html#                                                                                   |
|     wc2-1_30s_prec                                                 |     https://www.worldclim.org/data/worldclim21.html#                                                                                                                                       |     https://www.worldclim.org/data/worldclim21.html#                                                                                   |
|     wc2-1_30s_tavg                                                 |     https://www.worldclim.org/data/worldclim21.html#                                                                                                                                       |     https://www.worldclim.org/data/worldclim21.html#                                                                                   |

# Preparation/Pre-processing

## Overview

|     Asset                                                                 |     Name                                                                                                    |     Description                                                                                                                                                                                                                                                                                                                              |     Pre-processing Notes                                                                                                                               |
|---------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
|     Beck_KG_V1_present_0p0083.tif                                         |     Köppen-Geiger climate classifications                                                                   |     Global maps of the   Köppen-Geiger climate classification at an unprecedented 1‑km resolution for   the present day (1980–2016)                                                                                                                                                                                                          |     No pre-processing.                                                                                                                                 |
|     ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds-lccs_class.tif          |     Land Cover Maps - v2.0.7     (Year 2010)                                                                |     Global land cover maps   at 300 m spatial resolution [2]; The spatial coverage is latitude -90-90   degrees, longitude -180-180 degrees, and the coordinate system is the   geographic coordinate WGS84 [1].                                                                                                                             |     Data downloaded in netcdf format converted to GeoTiff using example code from:     http://maps.elie.ucl.ac.be/CCI/viewer/download.php#ftp_dwl    |
|     GHI_NASA_low                                                          |     NASA/SSE Irradiance Data 1983-2005.                                                                     |     Solar: Average Monthly and Annual Direct Normal Irradiance Data,   One-Degree Resolution of the World from NASA/SSE, 1983-2005.           This polygon shapefile   represents the 22 year average monthly and annual measurements (kWh/m^2/day)   of global horizontal irradiance (GHI) for the entire world.                            |     No pre-processing.                                                                                                                                 |
|     HydroRIVERS_v10                                                       |     HydroRIVERS v1.0                                                                                        |     HydroRIVERS is a database aiming to   provide the vectorized line network of all global rivers that have a   catchment area of at least 10 km2 or an average river flow of 0.1 cubic   meters per second, or both.                                                                                                                       |     No pre-processing.                                                                                                                                 |
|     OCSTHA_M_30cm_250m_ll.tif                                             |     Soil Grids – Global   Gridded Soil Information (2017)                                                   |     -                                                                                                                                                                                                                                                                                                                                        |     No pre-processing.                                                                                                                                 |
|     cmp_ro_grdc.tif                                                       |     UNH/GRDC Runoff Fields   Data     (composite   monthly runoff fields and annual total runoff fields)    |     Three sets of annual   and monthly climatological (1+12 layers per set)     runoff fields…The sets   are     observed, WBM-simulated, and composite monthly runoff fields.                                                                                                                                                               |     Pre-processing to add Projection information                                                                                       |
|     wc2-1_30s_bio_12                                                      |     WorldClim Historical   Climate data                                                                     |     This is WorldClim version 2.1 climate data for 1970-2000. This version   was released in January 2020.     There are monthly climate data for minimum, mean, and maximum   temperature, precipitation, solar radiation, wind speed, water vapor   pressure, and for total precipitation. There are also 19 “bioclimatic”   variables.    |     No pre-processing                                                                                                                                  |
|     wc2-1_30s_prec                                                        |     -                                                                                                       |     -                                                                                                                                                                                                                                                                                                                                        |     -                                                                                                                                                  |
|     wc2-1_30s_tavg                                                        |     -                                                                                                       |     -                                                                                                                                                                                                                                                                                                                                        |     -                                                                                                                                                  |

[1] https://poles.tpdc.ac.cn/en/data/c205fc4f-4847-4a7d-bb04-7c60f27438ae/
[2] http://maps.elie.ucl.ac.be/CCI/viewer/download.php#ftp_dwl

## Runoff Data
From https://www.compositerunoff.sr.unh.edu/

Projection information (assumed to be EPSG:4326)  added as follows:

```
gdalwarp -t_srs EPSG:4326 -of GTiff -co COMPRESS=LZW -co TILED=YES cmp_ro.tif cmp_ro_grdc.tif
```

## Lancover Data

Netcdf was converted to GeoTiff
```
gdalwarp -of Gtiff -co COMPRESS=LZW -co TILED=YES -ot Byte -te -180.0000000 -90.0000000 180.0000000 90.0000000 -tr 0.002777777777778 0.002777777777778 -t_srs EPSG:4326 NETCDF:ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2.0.7cds.nc:lccs_class ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2.0.7cds.tif
```
