.. geocaretdocs documentation master file, created by
   sphinx-quickstart on Thu Jul 11 20:16:43 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: _static/images/geocaret-logo.png
   :align: center
   :width: 100 %

|

======================================
Welcome to GeoCARET's documentation
======================================

.. _GeoCARET: https://github.com/Reservoir-Research/geocaret
.. _GEE: https://earthengine.google.com/

**GeoCARET** : Pronounced geokærət as in bʌkət or geokæreɪ as in bʊˈkeɪ.

Version: |version|

GeoCARET_ is a command line Python tool for delineating and analysing catchments and reservoirs.
It relies on Google Earth Engine (`GEE`_) - Google's cloud-based platform developed for planetary-scale environmental analysis. GeoCARET_ uses Google Earth Engine as a backend for performing geometry operations and data processing and as a database of global spatial data in the form of GIS layers. 
GeoCARET_ performs its computations on global spatial datasets available in `GEE`_ and additionally relies on several private assets. 
We have made these assets accessible for analysis by uploading them to a dedicated `GEE`_ asset folder.

.. important::
   The users need to request permission from us to use the dedicated private assets before they can make successful runs with GeoCARET_. 
   Please refer to the :doc:`installation/index` for further instructions.
   To request access to those assets please send email to: `Tomasz Janus - Email 1 <mailto:tomasz.k.janus@gmail.com?subject=%5BGeoCARET%5D%20Request%20Asset%20Access>`__ or `Tomasz Janus - Email 2 <mailto:tjanus.heet@gmail.com?subject=%5BGeoCARET%5D%20Request%20Asset%20Access>`__ with your email address registered with the Google Earth Engine.

.. toctree::
   :maxdepth: 3
   :glob:
   :caption: Contents:

   introduction.rst
   Installation <installation/index.rst>
   algorithms.rst
   Running GeoCARET <running_geocaret/index.rst>
   GHG Model Input Calculations <ghg_emissions/index.rst>
   config.rst
   Python API reference <api/geocaret.rst>
   license.rst
   acknowledgments.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
