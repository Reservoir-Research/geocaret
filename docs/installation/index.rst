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

We also provide an alternative, easier installation option, that uses Docker containarization. 
You can find more information in :ref:`What is Docker` and subseqent chapters - :doc:`building_image` and :doc:`using_image`.

.. note::
   Installing GeoCARET_ with Docker requires prior installation of the ``Docker Desktop`` software - see :doc:`building_image` and :doc:`using_image` for details. 

Additional Steps
----------------

Regardless of the installation method, whether as a standalone *Python* package or via a *Docker container*, the users need to create an account on `Google Cloud`_ and set up a project folder before being able to use GeoCARET_. 
The users will also need permission to access private assets that are required for running the computations with GeoCARET_.
These steps are outlined in detail in :doc:`additional_steps`.

.. toctree::
   :maxdepth: 3
   :hidden:
   :caption: Installation Instructions:

   install_package.rst
   using_docker.rst
   building_image.rst
   using_image.rst
   additional_steps.rst
