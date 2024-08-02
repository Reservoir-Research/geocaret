Preparing Your Input File
=========================

Background
----------

To run the GeoCARET tool, the name of an input file (User Inputs file)
containing input parameters for each dam must be supplied as a command
line argument. For example, if your inputs file is called ``dams.csv`` and
is inside the ``data`` sub-folder, you could run the GeoCARET tool by
typing:

::

   > python heet_cli.py data/dams.csv projectname myanmar01 standard 

See `Running The GeoCARET Script <04_run.md>`__ for full details of all
the arguments that are passed to the GeoCARET tool.

Supported Geographical Region(s)
--------------------------------

-  Analysis is only possible for dam locations in the latitude range -60
   to +60 DD.
-  Analysis of dams at locations within range, but close to these upper
   and lower limits will fail in the following circumstances:

   -  The hydrobasins level 12 subbasin the dam resides in partially
      lies outside of this range.
   -  The modelled reservoir extends outside of this range.

User inputs file specification
------------------------------

The User Inputs file, MUST meet the following file specification and
constraints:

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
|                        | Capacity     | of the dam in megawatts      |      |          |        |        |        |
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

-  File **MUST** be **UTF-8** ``csv`` format.
-  Columns may be in any order.
-  [*] At least one of ``dam_height``, ``fsl_masl`` and power capacity **MUST** be present.
-  Capitalisation of column names is ignored. Column names dam_lat, DAM_LAT and dam_Lat are all valid.
-  Leading and trailing white are ignored. Column names ``dam_lat`` , ``dam_lat``, ``dam_lat`` are all valid.
-  Extra columns may be present, but will be ignored.

Future Dams vs Existing Dams
----------------------------

By setting the future_dam_model flag to true/false the user chooses whether to model individual dams as future/existing dams with the following constraints imposed:

-  Only dams commissioned after 2000 can be modelled as future dams (SRTM data year was 2000)
-  Only dams commissioned before 2020 can be modelled as existing dams (landcover data currently only available up to 2020).
-  Dams commissioned 2001-2019 inclusive can be modelled as existing or future dams

We recommend that existing dams commissioned on or after 2001 are modelled as future dams

Where dams are modelled as existing dams, the reservoir is delineated
using landcover water pixels at a resolution of ~350m.The landcover data
year to use for delineation is chosen as follows: first available data
*after* commissioning of dam from years 1992, 2000, 2010 and 2020 e.g. a
dam commissioned in 1991 will be delineated using 1992 data; a dam
commissioned in 1992 will be delineated using 2000 data;

Where dams are modelled as future dams, the reservoir is delineated using function delineate_future_reservoir which extracts the reservoir by “flooding” the landscape. 
Some choices about the underlying DEM to use for delineation and it’s resolution can be specified in delineator/heet_config.

For landcover analysis, the first available data *before* commissioning
of dam is used from years 1992, 2000, 2010 and 2020 e.g. for a dam
commissioned in 1993, landcover analysis will be conducted using 1992
data; Where landcover data preceding the inundation of the reservoir is
not available, a buffer zone method following the approach applied to
the 1992 data following the approach of the The GHG Reservoir Tool see
`The G-res tool v2.1 Technical
documentation <https://assets-global.website-files.com/5f749e4b9399c80b5e421384/5fa83c07d5f3c691742fd0d8_g-res_technical_document_v2.1.pdf>`__.

User inputs file validation
---------------------------

Before the User Input file is uploaded to Google Earth Engine, it is
checked for the following problems. If any issues are detected, the
input file will be rejected, the GeoCARET tool will exit and the user is
asked to make corrections:

**Duplicate column names**: duplicate column names are present in the
input file. This check is case insensitive and white space insensitive
so column names “ dam_lat” and “DAM_LAT” in the same file are regarded
as duplicates and are flagged for correction.

**Missing columns**: one or more required columns are missing from the
input file.All required columns must be present in the file in addition
to one of dam_height, fsl_masl and power capacity.

**Non uniqueness**: one or more columns which should contain unique
values, contain one or more duplicate values. All columns where the
unique constraint is True must contain unique values.

**Out of range values**: One or more columns contain out of range
values. When a min or max value is specified for a column, a range check
is applied to determine whether the supplied values are in range. All
values must be within range.

**Mismatched data types**: One or more columns contains value(s) which
do not match the intended data type. All supplied values must match the
specified data type of the column they are in e.g. numbers stored as
strings e.g. “11,000” are not permitted in numeric or integer fields.
