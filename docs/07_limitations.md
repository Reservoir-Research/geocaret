
## Limitations

Some of the known limitations of this tool are discussed below.

### Relationship between hydrological parameters

The tool outputs a number of hydrological parameters including mean annual runoff (mm/yr), mean annual precipitation (mm/yr) and evapotranspiration (mm/yr).

Please note, that the parameters provided by this tool do not meet the expected constraint:

> [Mean annual runoff = Mean annual precipitation + Mean annual evapotranspiration] X

This constraint is not met as each parameter is obtained from a different GIS data source, each of which differ with respect to temporal resolution and coverage, spatial resolution and modelling methodology.:

| Parameter | Desc                                   | GIS Layer : Band                      | Spatial Resolution (m) | Temporal Resolution | Temporal Coverate |
|-----------|----------------------------------------|---------------------------------------|------------------------|---------------------|-------------------|
| c_map_mm  | Mean annual precipitation (mm/yr)      | WorldClim 2:                          | 927.66                 | Long term mean      | 1970 - 2000       |
| c_map_mm_alt1  | Mean annual precipitation (mm/yr)      | TerraClimate: pr                         |  4638.3                 | Long term mean      | 2000-2019       |
| c_mar_mm  | Mean annual runoff (mm/yr)             | UNH-GRDC Composite Runoff Fields V1.0 | 55659.74               | Long term mean      | < 2000            |
| c_mar_mm_alt1  | Mean annual runoff (mm/yr)             | TerraClimate: ro | 4638.3               | Long term mean      | < 2000            |
| c_mpet_mm | Mean annual evapotranspiration (mm/yr) | TerraClimate: pet                     | 4638.3                 | Long term mean      | 2000-2019         |
| c_mpet_mm_alt1 | Mean annual evapotranspiration (mm/yr) |  Regridded Monthly Terrestrial Water Balance Climatologies (UDEL)                    |   55659.7      |      |         |