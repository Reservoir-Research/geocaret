.. _installation-guidelines:

Installation Guidelines
=======================

.. _GeoCARET: https://github.com/Reservoir-Research/geocaret
.. _GEE: https://earthengine.google.com/
.. _Google Cloud: https://cloud.google.com/?hl=en

Installation as a Python Package - Option 1
-------------------------------------------

GeoCARET_ is an application written in Python and has to be installed just like any Python package.
Since GeoCARET_ uses *Google Earth Engine* (GEE_), it requires installation of additional software to facilitate operability with GEE_.
All of the above steps are described in detail in the :doc:`install_package`.

Installation using Docker - Option 2
------------------------------------

We also provide an alternative installation option from a Docker image. 
You can find more information in :ref:`What is Docker` and subseqent chapters - :doc:`building_image` and :doc:`using_image`.

.. note::
   Installing GeoCARET_ with Docker requires prior installation of ``Docker Desktop`` - see :doc:`building_image` and :doc:`using_image` for details. 

Additional Steps
----------------

Regardless of the installation method, the users need to create a Google Account, set up a project in Google Cloud, and request and obtain permissions for reading private assets (GIS layers) required for running some of the computations in GeoCARET_.

These steps are outlined in detail in :doc:`account_setup` and :doc:`access_to_assets`.

.. toctree::
   :maxdepth: 3
   :hidden:
   :caption: Installation Instructions:

   install_package.rst
   using_docker.rst
   building_image.rst
   using_image.rst
   account_setup.rst
   access_to_assets.rst
