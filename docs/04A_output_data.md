# Background

---

When the HEET tool is run, a number of outputs are generated and are saved to several locations.  This document is a guide to the output datasets generated and their location.  

## Run Folder

---

When the HEET tool is run for the first time, a folder XHEET/tmp is created in the top level of your Google Drive assets folder. 

This folder is always used by the currently running HEET job. 

Initially, all output files are written to the XHEET/tmp folder. 

Once the analysis is complete, all output files are copied to Google Drive and to another earth engine assets folder. 

All files are then deleted from XHEET/tmp ready for the next analysis.      

## Output Locations

---

> Results from the HEET tool are saved in three locations: 
> 
> - Google Earth Engine Assets Folder 
> - Google Drive 
> - Local results folder

### Google Earth Engine Assets Folder
All output files generated are saved to a subfolder of Google Earth Engine Assets folder XHEET: 

``XHEET/<<JOBNAME>>-<<TIMESTAMP>> e.g. XHEET/MYANMAR01-20220130-1450``

-	All outputs are native earth engine data structures: feature collections, images or image collections.


### Google Drive
All output files generated are saved to a Google Drive folder: 

``XHEET-<<JOBNAME>>-<<TIMESTAMP>> e.g. XHEET-MYANMAR01-20220130-1450``

- Catchment, Reservoir and River delineations (vectors, feature collections) are exported as shape files.
- Catchment areas and inundated areas (pixels, rasters, images) are exported GeoTiff images.
- Catchment, reservoir and other parameters (feature collections) are exported as csv files. 

Note the following earth engine documentation:

“The Google Drive Folder that the export will reside in. Note: (a) if the folder name exists at any level, the output is written to it, (b) if duplicate folder names exist, output is written to the most recently modified folder, (c) if the folder name does not exist, a new folder will be created at the root, and (d) folder names with separators (e.g. 'path/to/file') are interpreted as literal strings, not system paths. Defaults to Drive root.”

https://developers.google.com/earth-engine/apidocs/export-table-todrive

### Local Results Folder **(calculated parameters only)**

When the analysis is complete, calculated properties (output_parameters) are downloaded to a local results folder as a CSV file (output_parameters.csv). 

``outputs/<<JOBNAME>>-<<TIMESTAMP>> e.g. outputs/MYANMAR01-20220130-1450/output_parameters.csv``

The contents of output_parameters.csv is validated against a set of constraints in ``outputs.resource.yaml`` and ``heet_validate.py``.  Any impossible or improbable calculated 
parameters are flagged in file ``heet_output_report.csv`` 

A subset of the outputs in output_parameters.csv are output as a json file output_parameters.json.

``outputs/<<JOBNAME>>-<<TIMESTAMP>> e.g. outputs/MYANMAR01-20220130-1450/output_parameters.json``

## Guide to Output Files

### Output File Inventory
|      file_prefix         |      title                                   |      description                                                                                                                      |      ee_type                                |      drive_type     |
|--------------------------|----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|---------------------|
|     user_inputs          |     User inputs                              |     User inputs                                                                                                                       |     Feature Collection                      |     CSV             |
|     P_*                  |     Raw dam location                         |     The raw dam location input by the user                                                                                            |     Feature Collection     [Ftc-ft-pt]      |     Shp             |
|     PS_*                 |     Snapped dam location                     |     Dam location snapped to nearest hydroriver                                                      |     Feature Collection     [Ftc-ft-pt]      |     Shp             |
|     WCPTS_               |     Watershed candidate points               |     Watershed search grid.    Hydrobasins 12 subbasin of dam converted to a grid of point locations   (15’ pixel centres).            |     Feature Collection     [Ftc-fts-pts]    |     Shp             |
|     WDPTS_               |     Watershed detected points                |     Points on watershed search grid found by algorithm to belong to   dam catchment.                                                  |     Feature Collection     [Ftc-fts-pts]    |     Shp             |
|     CX_                  |     Catchment pixels                         |     Catchment pixels                                                                                                                  |     Image                                   |     GeoTiff         |
|     C_, c_               |     Catchment boundary                       |     Catchment boundary                                                                                                                |     Feature Collection                      |     Shp             |
|     WBSX_                |     Waterbodies pixels                       |     Waterbodies pixels                                                                                                                |     Image                                   |     GeoTiff         |
|     WBS_                 |     Waterbodies boundaries                   |     Waterbodies boundaries                                                                                                            |     Feature Collection                      |     Shp             |
|     R_, r_               |     Reservoir boundary                       |     Reservoir boundary; boundary of waterbody which intersects the   snapped dam location.                                            |     Feature Collection                      |     Shp             |
|     sr_                  |     Simplified reservoir boundary            |     Simplified reservoir boundary (the outer boundary of the   reservoir ignoring any islands). Used to determine inundated river.    |     Feature Collection                      |     Shp             |
|     S_, s_               |     Inundated river reaches (stream line)    |     Inundated river reaches (stream line)                                                                                             |     Feature Collection                      |     Shp             |
|     MS_, ms_             |     Main indundated river channel            |     Main inundated river channel.                                                                                                     |     Feature Collection                      |     Shp             |
|     N_, n_               |     Non inundated catchment                  |     Non inundated catchment                                                                                                           |     Feature Collection                      |     Shp             |
|     output_parameters    |     Calculated Parameters                    |     Calculated parameters                                                                                                             |     Feature Collection                      |     CSV             |

### Export Settings and Outputs

|      file_prefix         |      title                                   |      standard     |      extended     |      diagnostic     |      diagnostic-catch     |      diagnostic-res     |      diagnostic-riv     |
|--------------------------|----------------------------------------------|-------------------|-------------------|---------------------|---------------------------|-------------------------|-------------------------|
|     user_inputs          |     User inputs                              |     X             |     X             |     X               |     X                     |     X                   |     X                   |
|     P_*                  |     Raw dam location                         |                   |     X             |     X               |     X                     |     X                   |                         |
|     PS_*                 |     Snapped dam location                     |     X             |     X             |     X               |     X                     |     X                   |     X                   |
|     WCPTS_               |     Watershed candidate points               |                   |                   |     X               |     X                     |                         |                         |
|     WDPTS_               |     Watershed detected points                |                   |                   |     X               |     X                     |                         |                         |
|     CX_                  |     Catchment pixels                         |                   |                   |     X               |     X                     |                         |                         |
|     C_, c_               |     Catchment boundary                       |     X             |     X             |     X               |     X                     |     X                   |     X                   |
|     WBSX_                |     Waterbodies pixels                       |                   |                   |     X               |                           |     X                   |                         |
|     WBS_                 |     Waterbodies boundaries                   |                   |                   |     X               |                           |     X                   |                         |
|     R_, r_               |     Reservoir boundary                       |     X             |     X             |     X               |     X                     |     X                   |     X                   |
|     sr_                  |     Simplified reservoir boundary            |                   |                   |                     |                           |                         |     X                   |
|     S_, s_               |     Inundated river reaches (stream line)    |                   |                   |                     |                           |                         |     X                   |
|     MS_, ms_             |     Main indundated river channel            |     X             |     X             |     X               |     X                     |     X                   |     X                   |
|     N_, n_               |     Non inundated catchment                  |     X             |     X             |     X               |     X                     |     X                   |     X                   |
|     output_parameters    |     Calculated Parameters                    |     X             |     X             |     X               |     X                     |     X                   |     X                   |

### Error Codes

If the analysis of a dam location fails part way through, all output files and parameters calculated up to the point of failure will be saved and exported.  Any parameters that cannot be calculated are assigned a missing value using the codes below.  An error code is assigned to each dam to indicate whether the analysis completed successfully. 

| Code | Definition | 
|------|------------|
| 0 | No Error (complete analysis)| 
| 1 | Analysis failed at snapping dam to hydroriver|
| 2 | Analysis failed at catchment delineation or catchment parameter generation |
| 3 | Analysis failed at reservoir delineation or reservoir parameter generation |
| 4 | Analysis failed at non-inundated catchment delineation or non-inundated catchment  parameter generation  |
| 5 | Analysis failed at river delineation or river parameter generation |

### Missing Data Codes
- Missing numeric/string parameters are assigned a string value of "UD" when parameters are "under development"
- Numeric missing parameters are assigned a string value of "NA" (when delineation has failed)
- String missing parameters are assigned a string value of "NONE" (when delineation has failed)
- Numeric missing parameters are assigned a string value of "ND" (when calculation evaluates to None e.g. if there is missing data in GIS layer)
- String missing parameters are assigned a string value of "NODATA" (when calculation evaluates to None e.g. if there is missing data in GIS layer)

### Provenance Codes
The variable "r_imputed_water_level_prov" is a key variable that is used to indicate how the future water-level of the dam has been derived for the purposes of delineating the reservoir. 

| Code | Definition | 
|------|------------|
| 0    | User inputted water level |
| 1    | User input dam height |
| 2    | Dam height estimated from power capacity (user inputted turbine efficiency) |
| 3    | Dam height estimated from power capacity (assuming turbine efficiency of 85%) |

Plant depth is assumed to be "0" unless a user-specified value is provided.
