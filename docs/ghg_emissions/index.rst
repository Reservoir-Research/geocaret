.. _ghg-model-input-calcs:

============================
GHG Model Input Calculations
============================

.. _GeoCARET: https://github.com/Reservoir-Research/geocaret
.. _ReEmission: https://github.com/tomjanus/reemission

This part of the documentation outlines the application of GeoCARET_ to calculating reservoir and catchment parameters required for the subsequent estimation of reservoir greenhouse gas emissions in our open-source software ReEmission_. 
This is the initial intended application for GeoCARET_ - see :ref:`Origins`. 
However, we are now redesigning GeoCARET_ into a more generic tool and a framework for reservoir- and catchment-scale analysis that can be configured by users into performing user-defined computations - see :ref:`Vision`.

.. attention::
   What follows, the next chapters descibe the content related **solely** to running GeoCARET for its initial intended purpose, i.e. calculating inputs to greenhouse gas (GHG) emission model.

Sections
========

This (sub) documentation is built around the four main subjects listed below:

* Input data specification.
* The GIS layers (assets) required for the calculations. This includes the public assets available on GEE and the private assets uploaded by the users.
* Output data specification and alternative outputs.
* Limitations imposed by the input data, the GIS assets, and the algorithms.

|

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   Preparing Input Data <input_data.rst>
   gis_assets.rst
   output_data.rst
   output_data_exports.rst
   alternative_outputs.rst
   koppen_codes.rst
   limitations.rst
