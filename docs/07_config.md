# Config
Config file heet_config contains a number of user-specified parameters that affect the way that core calculations are carried out. 

Please note that these parameters are not intended for general use and sensible defaults are set by default; we do not recommend that you change these values unless you understand the impact of doing so.

## Jensen Search Radius (jensen_search_radius)

> When snapping the raw dam location to the nearest hydroriver, the jensen_search_radius (m) defines how far from the raw dam location to search for a hydroriver  

* jensen_search_radius defaults to 1000 (m)

## Upstream Basin Finding Method (upstreamMethod)

> upstreamMethod has allowed values 1, 2 or 3

* upstreamMethod 1: Identify basins upstream of snapped dam by tracing basins upstream sequentially. 
* upstreamMethod 2: Identify basins upstream of snapped dam by removing downstream basins. 
* [DEFAULT] upstreamMethod 3: Identify basins upstream of snapped dam by analysis of pfafstetter ids

* upstreamMethod defaults to "3"

## Use of Hydrologically Conditioned DEM (resHydroDEM, paramHydroDEM)

> Choose whether to use the hydrosheds hydrologically conditioned DEM (90m, 3 arc seconds) or SRTM (30m, 1 arc second) for reservoir delineation (resHydroDEM) and parameter calculations (paramHydroDEM)

True indicates that the hydrologically conditioned DEM will be used.

* resHydroDEM defaults to True
* paramHydroDEM defaults to True