# Alternative Parameter values

> Some of HEET's output parameters can be calculated using more than one approach e.g. if the parameter is available from more than one data source (**alternative data**) or can be calculated via different routes (**alternative implementation**).

Where alternative values for a parameter are available in the output, they are suffixed with \_alt1, \_alt2 etc and further information about the different parameter variants is provided in the description column of the Output Specification.

Parameters with alternative values are discussed below. Please note:

-   Some alternative parameter values are currently implemented in the code, but are not output to users as they have been withdraw . These are designated DEPRECATED below. These may be of interest to future developers.

-   Some alternative parameter values are currently implemented in the code, but automatically assigned a value of UD (undefined) on output to users as they are still under development. These are designated DEV below. These may be of interest to future developers. These are designated DEV below.

## Mean Annual Runoff (Catchment)

Three alternative methods for calculating the mean annual runoff of the catchment area are supported by the tool:

### Default Definition

The default calculation of mean annual runoff, c_mar_mm ($mm/year$) is extracted and spatially averaged from global composite runoff fields provided by [Fekete(2002)](https://www.compositerunoff.sr.unh.edu/). This is the approach also used by the GRES tool.

### Alternative Definition 1 (DEP)

Alternative definition 1, c_mar_mm_alt1 is the long term annual mean of [GLDAS](https://developers.google.com/earth-engine/datasets/catalog/NASA_GLDAS_V021_NOAH_G025_T3H#bands) mean annual total runoff (sum of of storm surface runoff, baseflow-groundwater runoff and snow melt).

This calculation method has been deprecated due to long calculation times (the dataset is a 3 hr time series and computationally intensive to aggregate over many years). Uses calendar, NOT hydrological year.

### Alternative Definition 2

Alternative definition 2, c_mar_mm_alt2 is the long term annual mean (2000-2019) of [TerraClimate](https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_TERRACLIMATE#citations) runoff variable (mm). Uses calendar, NOT hydrological year.

## Maximum Depth (Reservoir)

Three alternative methods for calculating the maximum reservoir depth are supported by the tool:

### Default Definition 1 

The default calculation of the maximum depth of the reservoir, r_max_depth uses the following approach:

$$Maximum\\;Depth = Max(Water\\;Surface\\;Elevation\\;-\\;Land\\;Elevation)$$

Where:

$$Water\\;Surface\\;Elevation = Elevation_{dam} + Water\\;Level_{res}$$

In this approach, the elevation of the reservoir water surface is estimated from the elevation of the base of the dam and the water level, where water level is measured in m from the dam base and in most cases will be approximated by the dam height.

The depth at each point on the reservoir is determined by subtracting the land elevation from the water surface elevation at each pixel.

The maximum depth is then taken as the maximum of theses values.

### Alternative Definition 1

In this alternative implementation (r_max_depth_alt1), the deepest location on the reservoir is assumed to be at the dam wall. NB: This assumption is made in the GRES calculation of maximum depth. The minimum elevation elevation at the dam point location is subtracted from the maximum elevation over the area of the reservoir to provide the maximum depth of the reservoir:

$$Maximum\\;Depth = Maximum\\;Elevation_{res}-\\;Elevation_{dam}$$

### Alternative Definition 2

In this alternative implementation (r_max_depth_alt2), the deepest location on the reservoir is taken as the difference between the highest and lowest elevation determined over the area of the reservoir:

$$Maximum\\;Depth = Maximum\\;Elevation_{res}-Minimum\\;Elevation_{res}$$

This calculation should provide identical results to the default calculation, but is a simpler Earth Engine calculation. Developers should consider replacing r_max_depth_alt with r_max_depth_alt2.

## Mean Global Horizontal Radiance (Reservoir)

Two different implementations of mean annual global horizontal radiance are supported:

### Default Definition 

The default definition of mean annual global horizontal radiance (r_mghr\_\* variables) extracts the mean GHR for the reservoir directly from the NASA/SSE Irradiance Data 1983-2005 GIS layer.

### Alternative Definition 1  - DEV

The alternative definition of mean annual global horizontal radiance (r_mghr\_\*\_alt1 variables) calculates the MGHR ($kWh\;m^2\;d^{-1}$) from the long term annual mean (2000-2019) of downward surface shortwave radiation (srad, $W/m^{2}$) from TerraClimate via a series of unit conversions.

## Soil moisture (Catchment) 

Two implementations of soil moisture, using two different data sources are supported.

### Default Definition

The default definition (c_masm_mm) calculates mean annual soil moisture as a long term mean (2000-2019) of monthly values from the soil field of TerraClimate "Soil moisture, derived using a one-dimensional soil water balance model" (mm/m).

### Alternative Definition 1 - DEP

This alternative definition (c_masm_mm_alt1) calculates mean annual soil moisture as the long term mean (2016-2021) of monthly values from the smp (Soil moisture profile (fraction)) of the NASA-USDA Enhanced SMAP Global Soil Moisture Dataset.
