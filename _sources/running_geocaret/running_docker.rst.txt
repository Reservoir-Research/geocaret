Running the GeoCARET Docker Container
=====================================

Run a GeoCARET analysis
~~~~~~~~~~~~~~~~~~~~~~~

First, copy your input data file to the ``data`` sub-folder and then start GeoCARET by typing the following:

.. code-block:: bash

   $ docker compose run --rm geocaret python heet_cli.py [input-file.csv] [projectname] [jobname] [output-option]

where:

* ``[input-file.csv]`` is the path to the user input file.
* ``[projectname]`` is the name of your Google Earth Engine project
* ``[jobname]`` is a short 10 character jobname to be used when creating output folders. May only contain the following characters **A-Z, a-z, 0-9, -**. 
* ``[output-option]`` is the output data option defining the amount of output data: *standard*, *extended*, *diagnostic*, *diagnostic-catch*, *diagnostic-res*, *diagnostic-riv*. - see :doc:`../ghg_emissions/output_data` for details.

Alternatively, you can run the analysis with the input data in one of the files in the ``tests/data`` folder, and assuming your project name is called ``test_project``, job name is called ``job01`` and data is output in the **standard** configuration.

.. code-block:: bash

   $ docker compose run --rm geocaret python heet_cli.py tests/data/dams.csv test_project job01 standard

See :doc:`../ghg_emissions/input_data` and :doc:`running_python_package` to read about input data file specification and about the usage of GeoCARET's command-line interface (CLI) arguments, respectively.

Google Cloud authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. hint::
   Needed when running GeoCARET for the first time only.

If this is the first time you’ve run the GeoCARET tool, you will be asked to authenticate with Google’s cloud services. See :doc:`first_run` for details.

.. note::
   Your authentication details will be cached in the ``auth`` sub-folder inside the GeoCARET workspace folder. When you
   subsequently run GeoCARET from this folder, you will not need to reauthenticate.

Once authenticated the GeoCARET analysis will run. This could take several minutes to complete.

Use existing Google cloud credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have previously authenticated with the Google cloud / GEE APIs, you may already have the necessary credentials stored on your computer (e.g. in /home/username/.config, which is the default location on Linux/macOS).

You can use your existing credentials to avoid the need to authenticate when running GeoCARET, by setting the ``GEOCARET_AUTH_PATH`` environment variable:

.. code-block:: bash

   GEOCARET_AUTH_PATH=/home/[username]/.config docker compose run --rm geocaret python heet_cli.py tests/data/dams.csv test_project job01 standard
   
where [``username``] refers to your user name.

Analysis Outputs
~~~~~~~~~~~~~~~~

When the GeoCARET analysis is complete, all output files generated are saved to a sub-folder of your Google Earth Engine project Assets folder, called ``XHEET``:

.. code-block:: bash

   XHEET/<<JOBNAME>>-<<TIMESTAMP>> e.g. XHEET/JOB01-20220130-1450
   
The timestamp represents the date and time of when the calculations have been started, e.g. the timestamp in the code block above indicated that *JOB01* was started on the 30th of January 2020 at 14:50.

The calculated outputs, i.e. **output_parameters** are downloaded to a local directory in a CSV text format and stored under ``outputs/output_parameters.csv``.

Please see :doc:`../ghg_emissions/output_data` for full details of the GeoCARET analysis outputs.

.. note::
   :doc:`../ghg_emissions/output_data` refers to the outputs created in the process of attaining input data for estimating reservoir greenhouse emissions. This is the primary application of GeoCARET for which GeoCARET been designed at its inception. We are now expending GeoCARET to function more as a generic tool for analysing reservoirs and catchments using geospatial data. Each application will have different input and output data specification. We will document these new features and all the code changes in due time.
