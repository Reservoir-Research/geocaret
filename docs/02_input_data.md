# Background
To run the HEET tool, the name of an input file (User Inputs file) containing input parameters for each dam  must be supplied as a command line argument: 

```
> python src/heet_cli.py dams.csv myanmar01 standard 

``` 
# Supported Geographical Region(s)
- Analysis is only possible for dam locations in the latitude range -60 to +60 DD. 
- Analysis of dams at locations within range, but close to these upper and lower limits will fail in the following circumstances:
	- The hydrobasins level 12 subbasin the dam resides in partially lies outside of this range.
	- The modelled reservoir extends outside of this range.

# User inputs file specification
The User Inputs file, MUST meet the following file specification and constraints: 
 

|      name                 |      title                |      description                                                                                         |      type      |      required     |      unique     |      min     |      max     |
|---------------------------|---------------------------|----------------------------------------------------------------------------------------------------------|----------------|-------------------|-----------------|--------------|--------------|
|     id                    |     Dam Identifier        |     Dam identifier                                                                                       |     integer    |     TRUE          |     TRUE        |     1        |              |
|     country               |     Country Name          |     The name of the country the dam is located in. SHOULD be the ISO   3166 official short name (EN).    |     string     |     TRUE          |     FALSE       |              |              |
|     name                  |     Dam Name              |     The name of the dam                                                                                  |     string     |     TRUE          |     FALSE       |              |              |
|     river                 |     River Name            |     The name of the river the dam will be constructed on                                                 |     string     |     FALSE         |     FALSE       |              |              |
|     main_basin            |     Main Basin Name       |     The name of main river basin the dam will be located in                                              |     string     |     FALSE         |     FALSE       |              |              |
|     dam_lat               |     Dam Latitude          |     The latitude of the dam location in decimal degrees (DD)                                             |     Num        |     TRUE          |     FALSE       |     -90     |     90      |
|     dam_lon               |     Dam Longitude         |     The longitude of the dam location in decimal degrees (DD)                                            |     Num        |     TRUE          |     FALSE       |    -180          |    180          |
|     dam_height            |     Dam Height            |     The dam height in metres (m)                                                                         |     Num        |     FALSE*        |     FALSE       |     10       |     300      |
|     water_level           |     Water Level           |     The water level of the reservoir relative to the base of the dam   wall in metres (m)                |     Num        |     FALSE*        |     FALSE       |     10       |     300      |
|     power_capacity        |     Power Capacity        |     The installed power capacity of the dam in megawatts (MW)                                            |     Num        |     FALSE*        |     FALSE       |     0.001    |     22500    |
|     turbine_efficiency    |     Turbine Efficiency    |     The efficiency of the dam's turbines, percentage (\%).                                                |     Num        |     FALSE         |     FALSE       |     0        |     100      |
|     plant_depth           |     Power Plant Depth     |     The depth of the power plant below the base of the dam wall in   metres (m)                          |     Num        |     FALSE         |     FALSE       |     0        |     300      |


- File MUST be UTF-8 csv format.
- Columns may be in any order. 
- [*] At least one of dam_height, water_level and power capacity MUST be present. 
- Capitalisation of column names is ignored.  Column names dam_lat, DAM_LAT and dam_Lat are all valid.
- Leading and trailing white are ignored. Column names  ‘dam_lat  ‘ ,  ‘  dam_lat‘,  ‘dam_lat’  are all valid.
- Extra columns may be present, but will be ignored.  

# User inputs file validation

Before the User Input file is uploaded to Google Earth Engine, it is checked for the following problems.  If any issues are detected, the input file will be rejected, the HEET tool will exit and the user is asked to make corrections:

**Duplicate column names**:  duplicate column names are present in the input file. This check is case insensitive and white space insensitive so column names “  dam_lat” and “DAM_LAT” in the same file are regarded as duplicates and are flagged for correction.

**Missing columns**: one or more required columns are missing from the input file.All required columns must be present in the file in addition to one of dam_height, water_level and power capacity.

**Non uniqueness**: one or more columns which should contain unique values, contain one or more duplicate values. All columns where the unique constraint is True must contain unique values.

**Out of range values**:  One or more columns contain out of range values. When a min or max value is specified for a column, a range check is applied to determine whether the supplied values are in range. All values must be within range.

**Mismatched data types**:  One or more columns contains value(s) which do not match the intended data type. All supplied values must match the specified data type of the column they are in e.g. numbers stored as strings e.g. “11,000” are not permitted in numeric or integer fields.

