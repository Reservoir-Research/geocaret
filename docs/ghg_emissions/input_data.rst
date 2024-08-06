Preparing Inputs
================

To run GeoCARET command line interface (CLI), the input parameters for all dams/reservoirs being processed need to be supplied in a **CSV file** and provided as a command-line argument.
For example, if your input file is called ``dams.csv`` and resides inside the ``data`` sub-folder, you could run GeoCARET by typing:

.. code-block:: bash

   > python heet_cli.py data/dams.csv projectname jobname standard 

See :doc:`../running_geocaret/running_python_package` for full details of all the arguments that are passed to GeoCARET CLI. Information about running GeoCARET using an alternative installation with Docker can be found in :doc:`../running_geocaret/running_docker`.

Supported Geographical Region(s)
--------------------------------

Due to limitations imposed by the extent of some GIS layers, the analysis is only possible for dam locations in the latitude range **-60 to +60 decimal degrees (DD)**. Additionally, the analysis of dams at the locations falling within this range, but close to its upper and lower limits will fail if:

-  The HYDROBASINS level 12 subbasin the dam resides in partially lies outside of this range. - see :doc:`gis_assets`, :cite:t:`Lehner2008`.
-  The modelled reservoir extends outside of this range.

Input file specification
------------------------

The User Inputs file, MUST meet the following file specification and constraints:

.. hint::
   Data type **Int** means an integer variable, **Str** is a string, **Bool** is a boolean (1/0) and **Num** is a floating-point numerical variable.

+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
|          name          | title        | description                  | type | required | unique |  min   |  max   |
+========================+==============+==============================+======+==========+========+========+========+
|         ``id``         | Dam          | Dam identifier               | Int  | TRUE     | TRUE   |   1    |        |
|                        | Identifier   |                              |      |          |        |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
|      ``country``       | Country      | The name of the country the  | Str  | TRUE     | FALSE  |        |        |
|                        | Name         | dam is located in. SHOULD be |      |          |        |        |        |
|                        |              | the ISO 3166 official short  |      |          |        |        |        |
|                        |              | name (EN).                   |      |          |        |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
|        ``name``        | Dam Name     | The name of the dam          | Str  | TRUE     | FALSE  |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
|       ``river``        | River        | The name of the river the    | Str  | FALSE    | FALSE  |        |        |
|                        | Name         | dam will be constructed on   |      |          |        |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
|    ``main_basin``      | Main Basin   | The name of main river basin | Str  | FALSE    | FALSE  |        |        |
|                        | Name         | the dam will be located in   |      |          |        |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
|     ``dam_lat``        | Dam          | The latitude of the dam      | Num  | TRUE     | FALSE  |  -60   |  +60   |
|                        | Latitude     | location in decimal degrees  |      |          |        |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
|     ``dam_lon``        | Dam          | The longitude of the dam     | Num  | TRUE     | FALSE  |  -180  |  +180  |
|                        | Longitude    | location in decimal degrees  |      |          |        |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
|     ``dam_height``     | Dam          | The dam height in metres     | Num  | FALSE    | FALSE  |   10   |  300   |
|                        | Height       |                              |      |          |        |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
|     ``fsl_masl``       | Full Supply  | The full supply level of the | Num  | FALSE    | FALSE  |   10   |  300   |
|                        | Level        | reservoir (masl)             |      |          |        |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
|   ``power_capacity``   | Power        | The installed power capacity | Num  | FALSE    | FALSE  |  .001  |  2500  |
|                        | Capacity     | of the dam in MegaWatts      |      |          |        |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
| ``turbine_efficiency`` | Turbine      | The efficiency of the dam's  | Num  | FALSE    | FALSE  |   0    |  100   |
|                        | Efficiency   | turbines, percent            |      |          |        |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
|     ``pland_depth``    | Power        | The depth of the power plant | Num  | FALSE    | FALSE  |   0    |  300   |
|                        | Plant        | below the base of the dam    |      |          |        |        |        |
|                        | Depth        | wall in metres               |      |          |        |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
|  ``year_commissioned`` | Year         | Year Commissioned            | Num  | FALSE    | FALSE  |        |        |
|                        | Commissioned |                              |      |          |        |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+
|  ``future_dam_model``  | Future       | A flag to indicate whether   | Bool | TRUE     | FALSE  |        |        |
|                        | Dam          | the dam should be modelled   |      |          |        |        |        |
|                        | Model        | as a future or existing dam  |      |          |        |        |        |
+------------------------+--------------+------------------------------+------+----------+--------+--------+--------+

Additionally:

-  The file **MUST** be in **UTF-8** ``csv`` format.
-  Columns may be in any order.
-  At least one of ``dam_height``, ``fsl_masl`` and power capacity **MUST** be present.
-  Capitalisation of column names is ignored, i.e. column names ``dam_lat``, ``DAM_LAT`` and ``dam_Lat`` are all valid.
-  Leading and trailing white spaces in column names are ignored.
-  Extra columns with additional variables may be present, but will be ignored.

Future Dams vs Existing Dams
----------------------------

GeoCARET can analyse new proposed sites, a.k.a. *future dams* as well as existing assets, a.k.a. *existing dams*.

By setting the ``future_dam_model`` flag to true/false the user chooses whether to model individual dams as future/existing dams with the following constraints imposed:

Recommendations
~~~~~~~~~~~~~~~

-  Only the dams commissioned after year 2000 can be modelled as future dams, since the digital elevation model **SRTM** was developed in 2000 - see :doc:`gis_assets`.
-  Only the dams commissioned before 2020 can be modelled as existing dams, since the landcover data currently is only available up to year 2020.
-  Dams commissioned between 2001 and 2019 (inclusive) can be modelled either as existing or future dams.

We recommend that existing dams commissioned in or after 2001 are modelled as future dams.

Modelling existing dams
~~~~~~~~~~~~~~~~~~~~~~~

Where dams are modelled as existing dams, the reservoir is delineated using landcover water pixels at a resolution of ~350m.
The version of the landcover data year used for delineating existing reservoirs is chosen as follows.
We select the earliest available dataset created *after* commissioning of the dam.
For example for landcover data sets from years 1992, 2000, 2010 and 2020, a dam commissioned in year 1991 will be delineated using the landcover data from 1992; a dam commissioned in 1992 will be delineated using the data from the year 2000.

Modelling future dams
~~~~~~~~~~~~~~~~~~~~~

Where dams are modelled as future dams, the reservoir is delineated using the function ``delineate_future_reservoir`` which extracts the reservoir by “flooding” the landscape. 
The choice of the digital elevation model (DEM), e.g. DEM type and resolution, can be specified in ``delineator/heet_config.py`` - see :doc:`../config`.

For landcover analysis, we select the first available data *before* commissioning of the dam.
For example for a set of landcover maps availbale from years 1992, 2000, 2010 and 2020, if a dam is commissioned in 1993, the landcover analysis will be conducted using the landcover data from year 1992.
If the landcover data preceding the inundation of the reservoir is not available, we apply the **buffer zone method** following the approach described in `The G-res tool v2.1 Technical
documentation <https://assets-global.website-files.com/5f749e4b9399c80b5e421384/5fa83c07d5f3c691742fd0d8_g-res_technical_document_v2.1.pdf>`__.
We use the landcover data from 1992 as the input to the **buffer zone method** as it is the oldest landcover data available.

User inputs file validation
---------------------------

Before the User Input file is uploaded to Google Earth Engine, it is checked for the potential problems listed below. 
If any issues are detected, the input file will be rejected, the GeoCARET tool will exit and the user will be asked to make corrections:

* **Duplicate column names**: duplicate column names are present in the input file. This check is case insensitive and white space insensitive so column names ``dam_lat`` and ``DAM_LAT`` in the same file are regarded as duplicates and are flagged for correction.

* **Missing columns**: one or more required columns are missing from the input file.All required columns must be present in the file in addition to one of ``dam_height``, ``fsl_masl`` and ``power capacity``.

* **Non uniqueness**: one or more columns which should contain unique values, contain one or more duplicate values. All columns where the unique constraint is True must contain unique values.

* **Out of range values**: One or more columns contain out of range values. When a min or max value is specified for a column, a range check is applied to determine whether the supplied values are in range. All values must be within range.

* **Mismatched data types**: One or more columns contains value(s) which do not match the intended data type. All supplied values must match the specified data type of the column they are in e.g. numbers stored as strings e.g. “11,000” are not permitted in numeric or integer fields.
