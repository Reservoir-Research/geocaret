Configuration Options
=====================

.. _G-Res: https://www.hydropower.org/publications/the-ghg-reservoir-tool-g-res-technical-documentation
.. _RE-Emission: https://github.com/tomjanus/reemission
.. _Pfaffstetter: https://proceedings.esri.com/library/userconf/proc01/professional/papers/pap1008/p1008.htm
.. _GEE: https://earthengine.google.com/

.. note::
   The following configuration options are related solely to the calculations of inputs to the G-Res_ greenhouse gas emission model and its implementation in our open-source software RE-Emission_ - i.e. the initial and currently the sole utility of GeoCARET. Nevertheless, as we keep re-designing the software and providing new functionalities, configuring new algorithms and functions will be provided to the user as a feature, i.e. the users will be able to add new functionalities and configure them with bespoke configuration settings. Nevertheless, for the time being, the below configuration options are restricted to :doc:`ghg_emissions/index`.

Configuration file ``delineator/heet_config.py`` contains a number of user-specified parameters that affect the way that core calculations are carried out.

.. attention::
   Please note that changing those parameters is not recommended for an average user. Sensible defaults have been set by default and should work well for most cases; we do not recommend that you change these values unless you understand the impact of doing so.

Jensen Search Radius
--------------------

Before we can delineate a reservoir created via construction of a dam, we first need to find a point on the river network on wich the dam is created. This is the point at the base of the dam with the lowest elevation. Often the dam location provided in the input file is not 100% precise for calculation purposes. We need to `move` i.e. snap the original (raw) dam location so that it lies exactly on the river network before we can proceed with reservoir delineation. When snapping the raw dam location to the nearest river, in our case the HydroRivers river network, the ``jensen_search_radius`` (m) defines how far from the raw dam location we should search for a river network.

.. note::
   ``jensen_search_radius`` defaults to 1,000 metres

Upstream Basin Finding Method
-----------------------------

Finding upstream (sub)basins is used in constructing a catchment of a reservoir from within a pool of smaller (sub)basins - see :doc:`algorithms` for details.
We curently support three methods.

-  ``upstreamMethod = 1``: Identify basins upstream of the snapped dam by tracing basins upstream sequentially.

-  ``upstreamMethod = 2``: Identify basins upstream of the snapped dam by removing downstream basins.

-  ``upstreamMethod = 3``: Identify basins upstream of the snapped dam by analysis of Pfaffstetter_ IDs.

.. note::
   By default ``upstreamMethod`` = 3

Use of Digital Elevation Models (DEMs)
--------------------------------------

We currently support two digital elevation models (DEMs): the hydrologically conditioned HydroSHEDS DEM and SRTM DEM for reservoir delineation and calculation of catchment parameters.
The DEM for reservoir delineation is set in parameter ``resHydroDEM`` while the DEM for parameter calculations is set in parameter ``paramHydroDEM``.

.. note::
   A hydrologically conditioned Digital Elevation Model (DEM) is a type of elevation data (most often a raster data) that has been processed to ensure that water flow paths, such as rivers and streams, follow natural drainage patterns without artificial barriers or errors. This conditioning involves modifying the DEM to correct any discrepancies, such as filling in depressions (sinks) or removing obstacles that would disrupt the natural flow of water. The DEM is additionally aligned with the river network (a separate layer of a vector form) such that the river network follows the natural drainage patterns delineated by the DEM.

Setting ``resHydroDEM`` or ``paramHydroDEM`` to ``True`` indicates seletion of the hydrologically conditioned DEM.

The parameter ``hydrodataset`` takes values either “03” or “15” and is used to select the resolution of the hydrologically conditioned DEM (either 3 or 15 Arc seconds). The SRTM DEM is provided at a 30m, (1 Arc second) resolution only.

.. note::
   Default parametrs are:
   
   -  ``resHydroDEM`` defaults to True
   -  ``paramHydroDEM`` defaults to True
   -  ``hydrodataset`` defaults to “03”

Use of dam location for reservoir delineation
---------------------------------------------

Parameter ``delineate_snapped`` is used to choose whether the **raw** or **snapped** (see also `Jensen Search Radius`_) dam location is used for reservoir delineation. ``delineate_snapped`` defaults to True.

Export Options
--------------

Upon finishing calculations the results are located in files on Google Earth Engine (GEE_). The users have an option to export the results to Google Drive automatically after the calculations have finished. The users can also view and analyse the results in the GEE_'s graphical user interface (GUI). See the options below.

-  ``export_to_drive`` is used to choose whether to automatically export results to Google Drive (Defaults to False)
-  ``direct_to_vis`` is used to choose whether the user is directed to a visualiation script on job completion (Defaults to True)

.. note::
   The users can also export the results to Google Drive manually using the ``heet_export_cli.py`` script located in the GeoCARET's' root (main) installation folder.
