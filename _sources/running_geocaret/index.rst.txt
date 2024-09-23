.. _running-geocaret:

Running GeoCARET
================

.. _GeoCARET: https://github.com/Reservoir-Research/geocaret
.. _RE-Emission: https://github.com/tomjanus/reemission
.. _GEE: https://earthengine.google.com/
.. _Google Cloud: https://cloud.google.com/?hl=en

GeoCARET_ can be run as a **Python package** (standard) or from a **Docker image** (optional - see :doc:`../installation/using_docker` for a short description of what Docker is) depending on the chosen installation option - see :doc:`../installation/index`.  

Running GeoCARET_ requires a valid input file. To find out about the input file specification, please refer to :doc:`../ghg_emissions/input_data`.

.. attention::

   Currently, GeoCARET serves a single purpose: sourcing input data for GHG emission estimation using our software, RE-Emission_. Consequently, GeoCARET has a single run command and relies on an input data file formatted specifically for this single application. We are in the process of refactoring and reformulating GeoCARET into a more versatile and generic tool for reservoir and catchment analysis. This expansion means GeoCARET will support more analysis options, offer additional run commands, and allow users to create their own input files and specifications.
   
For detailed instructions how to run GeoCARET as a Python package and/or from a Docker image, navigate to  :doc:`running_python_package` and :doc:`running_docker`, respectively. When you run GeoCARET for the first time, you will need to authenticate your Earth Engine account with OAuth2. This requires an additional manual step of copying and pasting an authorization code. For more information, navigate to :doc:`first_run`. During this initial run, login credentials will stored as a file and subsequent logins will be done automatically. 

.. toctree::
   :maxdepth: 3
   :hidden:
   :caption: Running GeoCARET:

   first_run.rst
   running_python_package.rst
   running_docker.rst
