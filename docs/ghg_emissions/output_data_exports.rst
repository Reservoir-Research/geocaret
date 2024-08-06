Exporting to Google Drive
=========================

Exporting to Google Drive (GDrive) is controlled by the boolean flag ``export_to_drive`` in the config file ``delineator/heet_config.py``. 

1. Exporting to GDrive automatically
------------------------------------

If ``export_to_drive`` is True, the results will be exported to Google Drive automatically. 

2. Exporting to GDrive later
----------------------------

If ``export_to_drive`` is False, the results will **not** be exported to Google Drive automatically. 
To export the results to Google Drive at a later time, use the utility script ``heet_export_cli.py`` as follows:

.. code-block:: bash

   > python heet_export_cli.py [path-to-results-folder-on-ee] [destination-folder-on-gdrive]
   
.. attention::
   Only a single top-level folder can be specified as the destination folder on GDrive
   
.. hint::
   To read about other configuration options, please refer to :doc:`../config`.

Example usage:

.. code-block:: bash

   > python heet_export_cli.py users/tjanus/XHEET/MYDAMSD22_20230107-2140 XHEET_MYDAMSD22_20230107-2140
   
will export the calculation outputs from the job folder ``MYDAMSD22_20230107-2140`` residing in the users' working folder ``users/tjanus/XHEET`` on Earth Engine and save the data to the folder of the same name in GDrive.

.. note::
   Please note the following `Earth Engine documentation <https://developers.google.com/earth-engine/apidocs/export-table-todrive>`_ describing where in Google Drive the data will be written to. *“The Google Drive Folder that the export will reside in. Note: (a) if the folder name exists at any level, the output is written to it, (b) if duplicate folder names exist, output is written to the most recently modified folder, (c) if the folder name does not exist, a new folder will be created at the root, and (d) folder names with separators (e.g. ‘path/to/file’) are interpreted as literal strings, not system paths. Defaults to Drive root.”*

.. _exports_settings:

Export Settings and Outputs
---------------------------

We provide a setting that is given as an argument in the command-line call - see ``[output-option]`` in the :ref:`syntax` section of :doc:`../running_geocaret/running_python_package` for details.
The output options are provided as columns in the table below: *standard*, *extended*, *diagnostic*, *diagnostic-catch*, *diagnostic-res*, *diagnostic-riv*.
They control the amount of data that is calculated and saved to the Earth Engine folder during the analysis, as illustrated in the table below.

+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``file_prefix``       | title        | st  | ex  | di   | diag   | diag  | diag  |
|                       |              | and | ten | agno | nostic | nosti | nosti |
|                       |              | ard | ded | stic | -catch | c-res | c-riv |
+=======================+==============+=====+=====+======+========+=======+=======+
| ``user_inputs``       | User inputs  | X   | X   | X    | X      | X     | X     |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``P_*``               | Raw dam      |     | X   | X    | X      | X     |       |
|                       | location     |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``PS_*``              | Snapped dam  | X   | X   | X    | X      | X     | X     |
|                       | location     |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``WCPTS_``            | Watershed    |     |     | X    | X      |       |       |
|                       | candidate    |     |     |      |        |       |       |
|                       | points       |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``WDPTS_``            | Watershed    |     |     | X    | X      |       |       |
|                       | detected     |     |     |      |        |       |       |
|                       | points       |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``CX_``               | Catchment    |     |     | X    | X      |       |       |
|                       | pixels       |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``C_``                | Catchment    | X   | X   | X    | X      | X     | X     |
| ``c_``                | boundary     |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``WBSX_``             | Waterbodies  |     |     | X    |        | X     |       |
|                       | pixels       |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``WBS_``              | Waterbodies  |     |     | X    |        | X     |       |
|                       | boundaries   |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``R_``                | Reservoir    | X   | X   | X    | X      | X     | X     |
| ``r_``                | boundary     |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``rbz_``              | Reservoir    | X   | X   | X    | X      | X     | X     |
|                       | buffer zone  |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``sr_``               | Simplified   |     |     |      |        |       | X     |
|                       | reservoir    |     |     |      |        |       |       |
|                       | boundary     |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``S_``                | Inundated    |     |     |      |        |       | X     |
| ``s_``                | river        |     |     |      |        |       |       |
|                       | reaches      |     |     |      |        |       |       |
|                       | (streamline) |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``MS_``               | Main         | X   | X   | X    | X      | X     | X     |
| ``ms_``               | indundated   |     |     |      |        |       |       |
|                       | river        |     |     |      |        |       |       |
|                       | channel      |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``N_``                | Noninundated | X   | X   | X    | X      | X     | X     |
| ``n_``                | catchment    |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+
| ``output_parameters`` | Calculated   | X   | X   | X    | X      | X     | X     |
|                       | Parameters   |     |     |      |        |       |       |
+-----------------------+--------------+-----+-----+------+--------+-------+-------+

