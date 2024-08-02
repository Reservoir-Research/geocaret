Guide to GIS Layers
===================

   The reservoir, catchment and dam characteristics output by this tool
   are extracted and derived from a number of GIS layer data sources

-  The GIS layer data source (layer and variable (band/feature)) for
   each parameter is documented in the output specification file
   99_output_specification.csv

-  Detailed metadata about each GIS layer is provided in the file
   99_gis_layer_metadata.csv. The following metadata are provided:

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
