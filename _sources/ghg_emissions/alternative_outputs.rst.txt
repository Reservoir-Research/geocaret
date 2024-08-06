Alternative Parameters and Definitions
======================================

.. _G-Res: https://www.hydropower.org/publications/the-ghg-reservoir-tool-g-res-technical-documentation

Some of GeoCARET’s output parameters can be calculated with more than one methododology, i.e. **alternative implementation**, or from different input data, i.e. **alternative data**. 
What follows, these output parameters have one or more alternative values.
Where such alternative values are available, these names of those additional output parameters are suffixed with the suffix ``_alt`` followed by a number, e.g. ``_alt1``, ``_alt2`` etc. 
Further information about the different parameter variants is provided in the description column in :ref:`output_data_specs`.

The parameters with alternative values are discussed below.

.. note::
   * Some alternative parameter values are currently implemented in the code, but are not output to users as they have been withdrawn. These are designated as **DEPRECATED**. Nevertheless, they may be of interest to future developers.
   * Alternative values are implemented in the code for some parameters, but they are automatically assigned a value of UD (undefined) for the reason being that they are still under development. These paramters are designated as **DEV**. As in the previous point, they may be of interest to future developers.

1. Mean Annual Runoff
---------------------

.. hint::
   Catchment parameter

Three alternative methods are supported:

Default Definition
~~~~~~~~~~~~~~~~~~

By deafault, mean annual runoff, ``c_mar_mm`` [mm/year] is extracted and spatially averaged from the global composite runoff fields provided by `Fekete(2002) <https://www.compositerunoff.sr.unh.edu/>`__.

Alternative Definition 1
~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::
   DEPRECATED

``c_mar_mm_alt1`` is the long term mean annual total runoff (sum of of storm surface runoff, baseflow-groundwater runoff and snow melt) provided in `GLDAS <https://developers.google.com/earth-engine/datasets/catalog/NASA_GLDAS_V021_NOAH_G025_T3H#bands>`__.

This calculation method has been deprecated due to long calculation times due to the dataset's very fine temporal resolution.
The dataset in the form of time series is provided at a 3hr period, what adds to the computational burden during aggregation over many years. 

.. note::
   The data uses calendar, NOT hydrological year.

Alternative Definition 2
~~~~~~~~~~~~~~~~~~~~~~~~

``c_mar_mm_alt2`` is the long term annual mean (2000-2019) of the runoff variable in [mm] provided by `TerraClimate <https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_TERRACLIMATE#citations>`__

.. note::
   The data uses calendar, NOT hydrological year.

2. Maximum Depth
----------------

.. hint::
   Reservoir parameter

Three alternative methods are supported:

Default Definition 1
~~~~~~~~~~~~~~~~~~~~

The default calculation of the maximum depth of the reservoir, ``r_max_depth`` uses the following approach:

.. math:: 
   :nowrap:
   
   \begin{equation}
     Maximum \; Depth = \textrm{Max}(Water \; Surface \; Elevation - Land \; Elevation)
   \end{equation}
   
where:

.. math:: Water \; Surface \; Elevation = Elevation_{dam} + Water \; Level_{reservoir}

The elevation of the reservoir water surface is estimated from either:

(i) full supply level (m.a.s.l) 
(ii) the elevation of the base of the dam + the dam height.

.. hint::
   For some hydroelectric dams, we can back-calculate the dam height from the power equation if e.g. flow and power production are given.

The depth at each point on the reservoir is determined by subtracting the land elevation from the water surface elevation at each pixel.
The maximum depth is then taken as the maximum of theses values.

Alternative Definition 1
~~~~~~~~~~~~~~~~~~~~~~~~

In this alternative implementation (``r_max_depth_alt1``), the deepest location on the reservoir is assumed to be at the dam wall. 

.. note:: 
   This assumption is also made in the calculation of reservoir's 'maximum depth in G-Res_. 
   
The minimum elevation at the dam point location is subtracted from the maximum elevation over the area of the reservoir to provide the maximum depth of the reservoir:

.. math:: 
   Maximum \; Depth = Maximum \; Elevation_{reservoir} - Elevation_{dam}

.. _alternative-definition-2-1:

Alternative Definition 2
~~~~~~~~~~~~~~~~~~~~~~~~

In this alternative implementation (```r_max_depth_alt2``), the deepest location on the reservoir is taken as the difference between the highest and the lowest elevation determined over the area of the reservoir:

.. math:: 
   Maximum \; Depth = Maximum \; Elevation_{reservoir} - Minimum \; Elevation_{reservoir}

This calculation should provide identical results to the default calculation methods, but at the benefit of requiring a simpler Earth Engine calculation method. 

.. hint::
   Developers should consider replacing ``r_max_depth_alt`` with ``r_max_depth_alt2``.

3. Mean Global Horizontal Radiance
----------------------------------

.. hint::
   Reservoir parameter

Two different implementations of mean annual global horizontal radiance are supported:

.. _default-definition-2:

Default Definition
~~~~~~~~~~~~~~~~~~

By default the mean annual global horizontal radiance (``r_mghr_*``) values are extracted from the NASA/SSE Irradiance Data 1983-2005 GIS layer.

Alternative Definition 1
~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::
   DEV

The alternative definition of mean annual global horizontal radiance (``r_mghr_*_alt1``) is calculated as the MGHR [:math:`kWh\;m^{-2}\;d^{-1}`] from the long term annual mean (2000-2019) of downward surface shortwave radiation (srad) [:math:`W/m^{2}`] from TerraClimate. The procedure requires a series of unit conversions.

4. Soil Moisture
----------------

.. hint::
   Catchment parameter

Calculation of soil moisture is done with two alternative methods that use two different data sources.

.. _default-definition-3:

Default Definition
~~~~~~~~~~~~~~~~~~

``c_masm_mm``, i.e. mean annual soil moisture, is calculated as a long term mean (2000-2019) of monthly values from the soil field of TerraClimate *“Soil moisture, derived using a one-dimensional soil water balance model”* [mm/m].

Alternative Definition 1
~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::
   DEPRECATED

This alternative definition (``c_masm_mm_alt1``) calculates the mean annual soil moisture as the long term mean (2016-2021) of monthly values from the ``smp`` field (Soil moisture profile (fraction)) of the NASA-USDA Enhanced SMAP Global Soil Moisture Dataset.

5. Precipitation
----------------

.. hint::
   Catchment parameter

.. _default-definition-4:

Default Definition
~~~~~~~~~~~~~~~~~~

By default, the mean annual precipitation ``c_map_mm`` is calculated from mean monthly WorldClim2 bioclimatic variables.

.. _alternative-definition-1-1:

Alternative Definition 1
~~~~~~~~~~~~~~~~~~~~~~~~

The alternative for the mean annual precipitation (``c_map_mm_alt1``) is calculated as the long term mean (2000-2019) of monthly values from the Precipitation accumulation field of TerraClimate.

6. Evapotranspiration
---------------------

.. hint::
   Catchment parameter

.. _default-definition-5:

Default Definition
~~~~~~~~~~~~~~~~~~

By default, mean annual evapotranspiration ``c_mpet_mm`` is calculated as a long term mean (2000-2019) of monthly values
from Reference evapotranspiration (ASCE Penman-Montieth) field of TerraClimate.

.. _alternative-definition-1-2:

Alternative Definition 1
~~~~~~~~~~~~~~~~~~~~~~~~

This alternative (``c_mpet_mm_alt1``) is calculated from Regridded Monthly Terrestrial Water Balance Climatologies from the University of Delaware http://climate.geog.udel.edu/~climate/html_pages/download_whc150_2.html
