Running the GeoCARET Docker Container
=====================================

Run a GeoCARET analysis
~~~~~~~~~~~~~~~~~~~~~~~

First, copy your input data file to the ``data`` sub-folder and then start the GeoCARET tool by typing the following:

.. code-block:: bash

   $ docker compose run --rm geocaret python heet_cli.py data/input-filename.csv projectname jobname dataset

Where: \* ``data/input-filename.csv`` is the input file. **Note for Windows users:** ensure you use a / and not a  when specifying the path to the data file. \* ``projectname`` is the name of your Earth Engine project \* ``jobname`` is a short 10 character jobname to be used when creating output folders. May only contain the following characters A-Z, a-z, 0-9, -. \* ``dataset`` is the output dataset required: ``standard``, ``extended``, ``diagnostic``, ``diagnostic-catch``, ``diagnostic-res``, ``diagnostic-riv``

See the main GeoCARET documentation, `Preparing Your Input File <docs/03_input_data.md>`__ and `Running The GeoCARET
Script <docs/04_run.md>`__ for full details of input data files and all of the arguments that are passed to the GeoCARET tool.

Google cloud authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If this is the first time you’ve run GeoCARET, you will be asked to
authenticate with Google’s cloud services:

1. You’ll be shown a URL, which you should copy and paste into a web browser. In Windows PowerShell you can hold down the ``Ctrl`` key and click the URL to open it automatically.
2. Follow the instructions to authenticate with Google
3. After authenticating, you’ll be given a token, which you should paste back into the GeoCARET tool command line.
4. Press enter to continue the GeoCARET analysis.

..
.. note::
   Your authentication details will be cached in the ``auth`` sub-folder inside the GeoCARET workspace folder. When you
   subsequently run GeoCARET from this folder, you will not need to reauthenticate.

Once authenticated the GeoCARET analysis will run. This could take several minutes to complete.

Use existing Google cloud credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have previously authenticated with the Google cloud / GEE APIs, you may already have the necessary credentials stored on your computer (e.g. in /home/username/.config, which is the default location on Linux/macOS).

You can use your existing credentials to avoid the need to authenticate when running GeoCARET, by setting the ``GEOCARET_AUTH_PATH`` environment variable:

.. code-block:: bash

   GEOCARET_AUTH_PATH=/home/username/.config docker compose run --rm geocaret python heet_cli.py data/input-filename.csv projectname jobname dataset

Analysis Outputs
~~~~~~~~~~~~~~~~

When the GeoCARET analysis is complete, all output files generated are saved to a sub-folder of your Google Earth Engine project Assets folder, called ``XHEET``:

.. code-block:: bash

   XHEET/<<JOBNAME>>-<<TIMESTAMP>> e.g. XHEET/MYANMAR01-20220130-1450

Calculated properties (output_parameters) are also downloaded to a local results sub-folder, named ``outputs``, as a CSV file
(output_parameters.csv).

Please see the main GeoCARET documentation, `GeoCARET Output data <docs/05A_output_data.md>`__ for full details of the GeoCARET
analysis outputs.
