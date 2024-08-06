GIS Assets
==========

Calculations in GeoCARET rely on access to various GIS assets (layer) which are used for reservoir and catchment delineations and calculating reservoir and catchment characteristics, such as population density, surface runoff, mean monthly temperatures, etc.

The abbreviated table of GIS assets with data URLs in Google Earth Engine (GEE), Web links to the data and its documentations, and literature references, is provided below.

.. note::
   **[home-folder]** in the *GEE Data URL* column refers to the location of private assets that we have uploaded to GEE and which would not have been accessible in GEE otherwise. The **[home-folder]** variable is **projects/ee-future-dams**.

Access to Private Assets
------------------------

.. important::
   The users need to request permission from us to use those private assets before they can make successful runs with GeoCARET. 
   Please refer to the :doc:`../installation/index` for further instructions.
   To request access to those assets please send email to: `Tomasz Janus - Email 1 <mailto:tomasz.k.janus@gmail.com?subject=%5BGeoCARET%5D%20Request%20Asset%20Access>`__ or `Tomasz Janus - Email 2 <mailto:tjanus.heet@gmail.com?subject=%5BGeoCARET%5D%20Request%20Asset%20Access>`__ with your email address registered with the Google Earth Engine.


Asset Table
-----------

.. csv-table:: GIS Assets used for calculation of GHG emission model inputs
   :file: gis_assets.csv
   :delim: ,
   
GIS Assets with Metadata
------------------------

A fuller datasets of GIS assets containing additional metadata can be downloaded in a CSV file format by clicking on the icon below.

.. image:: ../_static/images/spreadsheet-2127832_640.png
   :width: 100
   :alt: Spreadsheet file icon
   :target: ../_static/files/gis_layer_metadata.csv

-  The information about which GIS layer data source (layer and variable (band/feature)) is used for calculating each output parameter, is documented in :ref:`output_data_specs`.


The legend to the metadata fields is provided below.

+---------------------------+------------------------------------------+
| metadata_field            | description                              |
+===========================+==========================================+
| gis_layer_title           | GIS layer title                          |
+---------------------------+------------------------------------------+
| gis_layer_location        | GIS layer storage location on Google     |
|                           | Earth Engine                             |
+---------------------------+------------------------------------------+
| ee_url                    | URL of GIS Layer Entry in Google Earth   |
|                           | Engine                                   |
+---------------------------+------------------------------------------+
| ee_asset_type             | Google Earth Engine asset type           |
+---------------------------+------------------------------------------+
| ee_asset_vars             | Band/feature used from Google Earth      |
|                           | Engine asset                             |
+---------------------------+------------------------------------------+
| tool_data_usage           | Description of how the GIS layer is      |
|                           | utilised by this tool                    |
+---------------------------+------------------------------------------+
| tool_data_year            | Which years of data are utilised from    |
|                           | the GIS layer                            |
+---------------------------+------------------------------------------+
| temporal_resolution       | Temporal resolution of the data          |
|                           | e.g. daily, monthly, yearly values etc   |
+---------------------------+------------------------------------------+
| temporal_coverage         | Temporal coverage of the GIS layer       |
+---------------------------+------------------------------------------+
| dataset_provider          | Dataset provider                         |
+---------------------------+------------------------------------------+
| dataset_provider_link     | Dataset provider url                     |
+---------------------------+------------------------------------------+
| pixel_resolution          | Pixel Resolution                         |
+---------------------------+------------------------------------------+
| terms_of_use              | Terms of Use                             |
+---------------------------+------------------------------------------+
| citations                 | Citations                                |
+---------------------------+------------------------------------------+
| paper_url                 | Link to relevant publication             |
+---------------------------+------------------------------------------+
| notes                     | Additional notes                         |
+---------------------------+------------------------------------------+


Private Assets
--------------

.. _code: http://maps.elie.ucl.ac.be/CCI/viewer/download.php#ftp_dwl

GeoCARET relies on a number of data sources that were unavailable in Google Earth Engine catalog at the time of development.
These assets are hosted on our Google Earth Engine account at ``projects/ee-future-dams/XHEET_ASSETS``. 
In order to use GeoCARET the users need to obtain privileges to access (read) the asset files individually -see `Access to Private Assets`_.
Please check :doc:`../installation/install_package` for more details`.

Locations of Private Assets
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
   The data below duplicates the data provided in `Asset Table`_ and `GIS Assets with Metadata`_. We have kept it in the documentation for now because we have not had time to check that there are no discrepancies between the two sources of the same data.

1. ``projects/ee-future-dams/XHEET_ASSETS/HydroRIVERS_v10`` - shp file.
2. ``projects/ee-future-dams/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-[Year]-v2-0-7cds`` [#]_ - nc file
3. ``projects/ee-future-dams/XHEET_ASSETS/GHI_NASA_low``
4. ``projects/ee-future-dams/XHEET_ASSETS/cmp_ro_grdc`` - TiFF file
5. ``projects/ee-future-dams/XHEET_ASSETS/wc2-1_30s_bio_12``
6. ``projects/ee-future-dams/XHEET_ASSETS/Beck_KG_V1_present_0p0083``- TiFF file.
7. ``projects/ee-future-dams/XHEET_ASSETS/wc2-1_30s_tavg``
8. ``projects/ee-future-dams/XHEET_ASSETS/OlsenP_kgha1_World`` [#]_
9. ``projects/ee-future-dams/XHEET_ASSETS/Eo150_clim_xyz_updated``
10. ``projects/ee-future-dams/XHEET_ASSETS/wc2-1_30s_prec``
11. ``projects/ee-future-dams/XHEET_ASSETS/C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.nc`` - nc file

.. rubric:: Footnotes

.. [#] Currently used year is 2010, i.e. "Year" equals 2010
.. [#] Currently we're using tha data from years (2022-02).


Asset Sources
*************

.. _weblink1: http://www.gloh2o.org/koppen/
.. _dataurl1: https://figshare.com/articles/dataset/Present_and_future_K_ppen-Geiger_climate_classification_maps_at_1-km_resolution/6396959/2
.. _weblink2: http://maps.elie.ucl.ac.be/CCI/viewer/download.php
.. _dataurl2: https://cds.climate.copernicus.eu/cdsapp#!/dataset/satellite-land-cover?tab=form
.. _weblink3: http://maps.elie.ucl.ac.be/CCI/viewer/download.php
.. _dataurl3: https://cds.climate.copernicus.eu/cdsapp#!/dataset/satellite-land-cover?tab=form
.. _weblink4: https://geodata.lib.berkeley.edu/catalog/stanford-fd535zg0917
.. _weblink4b: https://maps.princeton.edu/catalog/stanford-xx487wn6207
.. _weblink4c: https://purl.stanford.edu/fd535zg0917
.. _dataurl4: https://geodata.lib.berkeley.edu/catalog/stanford-fd535zg0917
.. _dataurl4b: https://purl.stanford.edu/fd535zg0917
.. _weblink5: https://www.hydrosheds.org/page/hydrorivers
.. _dataurl5: https://www.hydrosheds.org/page/hydrorivers
.. _weblink6: https://www.compositerunoff.sr.unh.edu/html/Runoff/index.html
.. _dataurl6: https://www.compositerunoff.sr.unh.edu/html/Runoff/index.html
.. _weblink7: https://www.worldclim.org/data/worldclim21.html#
.. _dataurl7: https://www.worldclim.org/data/worldclim21.html#
.. _weblink8: http://climate.geog.udel.edu/~climate/html_pages/download_whc150_2.html
.. _dataurl8: http://climate.geog.udel.edu/~climate/html_pages/download_whc150_2.html

+---------+----------------+-----------------------+
| Asset   | Website        | Data url              |
+=========+================+=======================+
| **6**   | `weblink1`_    | `dataurl1`_           |
+---------+----------------+-----------------------+
| **2**   | `weblink2`_    | `dataurl2`_           |
+---------+----------------+-----------------------+
| **11**  | `weblink3`_    | `dataurl3`_           |
+---------+----------------+-----------------------+
| **3**   | `weblink4`_,   | `dataurl4`_           |
|         | `weblink4b`_,  | `dataurl4b`_          |
|         | `weblink4c`_   |                       |
+---------+----------------+-----------------------+
| **1**   | `weblink5`_    | `dataurl5`_           |
+---------+----------------+-----------------------+
| **4**   | `weblink6`_    | `dataurl6`_           |
+---------+----------------+-----------------------+
| **5**   | `weblink7`_    | `dataurl7`_           |
+---------+----------------+-----------------------+
| **10**  | `weblink7`_    | `dataurl7`_           |
+---------+----------------+-----------------------+
| **7**   | `weblink7`_    | `dataurl7`_           |
+---------+----------------+-----------------------+
| **9**   | `weblink8`_    | `dataurl8`_           |
+---------+----------------+-----------------------+

Preparation/Pre-processing
~~~~~~~~~~~~~~~~~~~~~~~~~~

Some of the assets had to be pre-processed before uploading them to GEE, such that their file formats and data conform to GEE's specifications. These pre-processing steps are listed below.

+--------+-----------------+----------------------------------+----------------+
| Asset  | Name            | Description                      | Pre-processing |
|        |                 |                                  | Notes          |
+========+=================+==================================+================+
| **6**  | Köppen-Geiger   | Global maps of the Köppen-Geiger | No             |
|        | climate         | climate classification at an     | pre-processing |
|        | classifications | unprecedented 1‑km resolution    |                |
|        |                 | for the present day (1980–2016)  |                |
+--------+-----------------+----------------------------------+----------------+
| **2**, | Land Cover      | Global land cover maps at 300 m  | Data           |
| **11** | Maps - v2.0.7   | spatial resolution [2]_; The     | downloaded in  |
|        | (1992, 2000,    | spatial coverage is latitude     | netcdf format  |
|        | 2010), 2.1.1    | -90-90 degrees, longitude        | converted to   |
|        | (2020)          | -180-180 degrees, and the        | GeoTiff using  |
|        |                 | coordinate system is the         | example        |
|        |                 | geographic coordinate WGS84 [1]_ | `code`_        |
+--------+-----------------+----------------------------------+----------------+
| **3**  | NASA/SSE        | Solar: Average Monthly and       | No             |
|        | Irradiance      | Annual Direct Normal Irradiance  | pre-processing |
|        | Data            | Data, One-Degree Resolution of   |                |
|        | 1983-2005       | the World from NASA/SSE,         |                |
|        |                 | 1983-2005. This polygon          |                |
|        |                 | shapefile represents the 22 year |                |
|        |                 | average monthly and annual       |                |
|        |                 | measurements (kWh/m$^2$/day) of  |                |
|        |                 | global horizontal irradiance     |                |
|        |                 | (GHI) for the entire world.      |                |
+--------+-----------------+----------------------------------+----------------+
| **1**  | HydroRIVERS     | HydroRIVERS is a database aiming | No             |
|        | v1.0            | to provide the vectorized line   | pre-processing |
|        |                 | network of all global rivers     |                |
|        |                 | that have a catchment area of at |                |
|        |                 | least 10 km$^2$ or an average    |                |
|        |                 | river flow of 0.1 cubic meters   |                |
|        |                 | per second, or both.             |                |
+--------+-----------------+----------------------------------+----------------+
| **4**  | UNH/GRDC Runoff | Three sets of annual and monthly | Pre-processing |
|        | Fields Data     | climatological (1+12 layers per  | to add         |
|        | (composite      | set) runoff fields…The sets are  | Projection     |
|        | monthly runoff  | observed, WBM-simulated, and     | information    |
|        | fields and      | composite monthly runoff fields. |                |
|        | annual total    |                                  |                |
|        | runoff fields)  |                                  |                |
+--------+-----------------+----------------------------------+----------------+
| **5**  | WorldClim       | This is WorldClim version 2.1    | No             |
|        | Historical      | climate data for 1970-2000. This | pre-processing |
|        | Climate         | version was released in January  |                |
|        | data            | 2020. There are monthly climate  |                |
|        |                 | data for minimum, mean, and      |                |
|        |                 | maximum temperature,             |                |
|        |                 | precipitation, solar radiation,  |                |
|        |                 | wind speed, water vapor          |                |
|        |                 | pressure, and for total          |                |
|        |                 | precipitation. There are also 19 |                |
|        |                 | “bioclimatic” variables.         |                |
+--------+-----------------+----------------------------------+----------------+
| **10** | -               | -                                | -              |
+--------+-----------------+----------------------------------+----------------+
| **7**  | -               | -                                | -              |
+--------+-----------------+----------------------------------+----------------+
| **9**  | Regridded       | -                                | Convert XYZ    |
|        | Monthly         |                                  | to tiff; Add   |
|        | Terrestial      |                                  | projection;    |
|        | Water           |                                  | derive annual  |
|        | Balance         |                                  | total          |
|        | Climatologies   |                                  | evapo          |
|        |                 |                                  | transpiration  |
|        |                 |                                  | from monthly   |
|        |                 |                                  | values         |
+--------+-----------------+----------------------------------+----------------+

.. rubric:: Footnotes

.. [1] https://poles.tpdc.ac.cn/en/data/c205fc4f-4847-4a7d-bb04-7c60f27438ae/
.. [2] http://maps.elie.ucl.ac.be/CCI/viewer/download.php#ftp_dwl

Literature
----------

|

.. bibliography:: ../_static/references.bib
