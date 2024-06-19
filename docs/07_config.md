# Configuration Options
Config file delineator/heet_config contains a number of user-specified parameters that affect the way that core calculations are carried out. 

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

## Use of Hydrologically Conditioned DEM (resHydroDEM, paramHydroDEM, hydrodataset)

> Choose whether to use the hydrosheds hydrologically conditioned DEM or SRTM (30m, 1 arc second) for reservoir delineation (resHydroDEM) and parameter calculations (paramHydroDEM)

True indicates that the hydrologically conditioned DEM will be used.

Parameter hydrodataset can take values "03" or "15" and is used to select the 
resolution of hydrologically conditioned DEM (3 or 15 Arc seconds)

* resHydroDEM defaults to True
* paramHydroDEM defaults to True
* hydrodataset defaults to "03"

## Use snapped or raw dam location for reservoir delineation
Parameter delineate_snapped is used to choose whether the raw or snapper
dam location is used for reservoir delineation:

* delineate_snapped defaults to True

# Export Options
* export_to_drive is used to choose whether to automatically export results to Google Drive (Defaults to False)
* direct_to_vis is used to choose whether the user is directed to a visualiation script on job completion (Defaults to True)