Limitations
===========

Some of the known limitations of this tool are discussed below.

Relationship between hydrological parameters
--------------------------------------------

The tool outputs a number of hydrological parameters including mean annual runoff (mm/yr), mean annual precipitation (mm/yr) and
evapotranspiration (mm/yr).

Please note, that the parameters provided by this tool do not meet the expected constraint:

   [Mean annual runoff = Mean annual precipitation + Mean annual
   evapotranspiration] X

This constraint is not met as each parameter is obtained from a different GIS data source, each of which differ with respect to temporal resolution and coverage, spatial resolution and modelling methodology.:

+--------------------+-----------------+-----------------+----------+--------+-------+
| Parameter          | Description     | GIS Layer :     | Spatial  | Te     | Tem   |
|                    |                 | Band            | Re       | mporal | poral |
|                    |                 |                 | solution | Reso   | Cov   |
|                    |                 |                 | (m)      | lution | erate |
|                    |                 |                 |          |        |       |
+====================+=================+=================+==========+========+=======+
| ``c_map_mm``       | Mean annual     | WorldClim 2:    | 927.66   | Long   | 1970  |
|                    | precipitation   |                 |          | term   | -     |
|                    | (mm/yr)         |                 |          | mean   | 2000  |
+--------------------+-----------------+-----------------+----------+--------+-------+
| ``c_map_mm_alt1``  | Mean annual     | TerraClimate:   | 4638.3   | Long   | 2000  |
|                    | precipitation   | pr              |          | term   | -2019 |
|                    | (mm/yr)         |                 |          | mean   |       |
+--------------------+-----------------+-----------------+----------+--------+-------+
| ``c_mar_mm``       | Mean annual     | UNH-GRDC        | 55659.74 | Long   | <     |
|                    | runoff (mm/yr)  | Composite       |          | term   | 2000  |
|                    |                 | Runoff Fields   |          | mean   |       |
|                    |                 | V1.0            |          |        |       |
+--------------------+-----------------+-----------------+----------+--------+-------+
| ``c_mar_mm_alt1``  | Mean annual     | TerraClimate:   | 4638.3   | Long   | <     |
|                    | runoff (mm/yr)  | ro              |          | term   | 2000  |
|                    |                 |                 |          | mean   |       |
+--------------------+-----------------+-----------------+----------+--------+-------+
| ``c_mpet_mm``      | Mean annual     | TerraClimate:   | 4638.3   | Long   | 2000  |
|                    | eva             | pet             |          | term   | -2019 |
|                    | potranspiration |                 |          | mean   |       |
|                    | (mm/yr)         |                 |          |        |       |
|                    |                 |                 |          |        |       |
+--------------------+-----------------+-----------------+----------+--------+-------+
| ``c_mpet_mm_alt1`` | Mean annual     | Regridded       | 55659.7  |        |       |
|                    | eva             | Monthly         |          |        |       |
|                    | potranspiration | Terrestrial     |          |        |       |
|                    | (mm/yr)         | Water Balance   |          |        |       |
|                    |                 | Climatologies   |          |        |       |
|                    |                 | (UDEL)          |          |        |       |
+--------------------+-----------------+-----------------+----------+--------+-------+
