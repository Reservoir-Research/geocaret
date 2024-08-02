Using the GeoCARET Docker Image
===============================

The GeoCARET Docker image is the simplest way to run GeoCARET. This guide will take you through the required steps:

1. Install Docker Desktop.
2. Pull the GeoCARET Docker image.
3. Use Docker compose to run GeoCARET.

   .. note::
      This documentation assumes that the reader: (1) Understands how to use Google Earth Engine (GEE) and has a properly configured GEE cloud project. See :doc:`additional_steps`. (2) Understands how to use the GeoCARET tool. See :doc:`../input_data` & :doc:`../running_geocaret/running_python_package` for full details. (3) Has a basic familiarity with the shell (macOS or linux) or PowerShell (Windows).

Install Docker Desktop
----------------------

If you already have Docker installed on your computer then skip to the next section, `Pull the GeoCARET Docker image`_.

Installing Docker Desktop
~~~~~~~~~~~~~~~~~~~~~~~~~

Docker Desktop is free and can be installed on Windows, Mac & Linux computers, Please visit https://docs.docker.com/get-docker/ and follow the appropriate instructions for installing Docker Desktop on your computer.

Once installed, make sure Docker Desktop is running, and open a shell prompt (Linux/macOS) or PowerShell (Windows) and typing the following:

.. code-block:: bash

   docker -v

This should return the version number of the installed version of docker. If you see an error message along the lines of ‘Cannot connect to the Docker daemon’ then restart Docker Desktop and try again.

.. _Pulling GeoCARET Docker image:

Pull the GeoCARET Docker image
------------------------------

[**FIXME** this will need to be updated when the GeoCARET image is hosted as a package]

Open a shell prompt (macOS/Linux) or PowerShell (Windows) and type:

.. code-block:: bash

   docker pull ghcr.io/Reservoir-Research/geocaret

Use Docker compose to run GeoCARET
----------------------------------

Prepare your workspace
~~~~~~~~~~~~~~~~~~~~~~

Docker compose is a tool for simplifying the execution of docker containers. We’ll use it to run GeoCARET.

First you’ll need to create a new folder for your GeoCARET workspace, and then inside this you must then create three sub-folders:

-  ``data``, which will hold your input data files.
-  ``outputs``, which will hold the analyses output files
-  ``auth``, which will hold your GEE authentication credentials

For example on linux or macOS, open a shell prompt, or on Windows open PowerShell, and then type:

.. code-block:: bash

   mkdir my_geocaret_work_folder
   cd my_geocaret_work_folder
   mkdir data
   mkdir outputs
   mkdir auth

You’ll also need to download the file `compose.yml <https://github.com/UoMResearchIT/geocaret/blob/geocaret_docker/compose.yml>`__
and save it inside your GeoCARET workspace folder (e.g. ``my_geocaret_work_folder`` in the above example).

   **Important: linux users & directory permissions**

When run on a linux host computer, the GeoCARET docker image will only work if the user ID & group ID (``UID:GID``) of your user account is ``1000:1000``. Otherwise, GeoCARET will not be able to write to the ``auth/`` or ``outputs/`` folders.

If you use linux on a personal laptop, then it is very likely your user account ``UID:GID`` will be ``1000:1000``. 
However, this may not be the case if you log in to a linux server with multiple users. To check your user account, type:

.. code-block:: bash

      id -u  # print user ID (UID)
      id -g  # print group ID (GID)

If your user account has a different UID and/or GID then you should follow the instructions in `Installation <docs/02_install.md>`__ to install the GeoCARET Python script directly.

Test GeoCARET works:
~~~~~~~~~~~~~~~~~~~~

To test everything is working correctly, you should first run the following from inside the GeoCARET workspace folder you just created:

.. code-block:: bash

   cd my_geocaret_work_folder
   docker compose run --rm geocaret

You should see the message *“You must specify a command to run. See README.Docker.md for details.”* and GeoCARET will exit.

Running GeoCARET with ``docker compose``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:doc:`../running_geocaret/running_docker`
