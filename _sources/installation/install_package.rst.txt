Installation as a Python Package
================================

.. _GeoCARET: https://github.com/Reservoir-Research/geocaret
.. _git: https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F
.. _Google Cloud: https://cloud.google.com/?hl=en

GeoCARET_ is a command-line tool written in Python. 
This documentation assumes that the reader is comfortable working in the shell (Linux/macOS) or PowerShell (Windows) and has basic experience with git_.
To learn more about Shell, BASH and PowerShell please have a look at this `Medium article <to https://medium.com/@ayogun/shell-vs-bash-vs-powershell-vs-cmd-fa916895aab>`_.
Experience with Python is advantageous but not essential.

To install and run GeoCARET_ on the command line, you will need to

1. Install the correct version of Python, or make sure it is already installed.
2. Setup a virtual environment dedicated to GeoCARET_ (recommended).
3. Install GeoCARET_ and the dependencies, i.e. the packages and the software which GeoCARET_ relies on. This includes Google Cloud CLI application ``Gcloud``.
4. Register to use the Google Earth Engine service and create an associated `Google Cloud`_ Project.
5. Request access to the GeoCARET_ private assets.
6. Run the GeoCARET_ script using the correct command line syntax.

This document provides a guide to steps **1** -- **3**. Steps **4** and **5** are described in :doc:`additional_steps`.
Step **6** is described in :doc:`../running_geocaret/running_python_package`.

1. Installing Python
--------------------

GeoCARET_ requires **Python 3.8 or newer**.

Windows Machines
~~~~~~~~~~~~~~~~

In order to install GeoCARET_ on Windows you need to have **Python 3.8** installed on your machine.
You can install **Python 3.8** by following this link: https://www.python.org/downloads/release/python-3810/
Alternatively, you can use alternative Python distributions: `Anaconda and Miniconda <https://docs.anaconda.com/distro-or-miniconda/>`_.

macOS / Linux
~~~~~~~~~~~~~

Python on Linux/MacOS can be installed in different ways. The most comprehensive list of Python releases is hosted at: https://www.python.org/downloads/. Alternatively, the users can install Python using system package managers such as ``apt`` for Debian-based Linux distributions or ``homebrew`` for MacOS. There are also tools that allow the users to manage Python installations and virtual environments (see `What is a Virtual Environment <https://www.geeksforgeeks.org/python-virtual-environment/>`_) within a single tool, such as e.g. ``pyenv``. Finally, virtual environments can be managed with different tools such as ``venv``, ``virtualenv``, the earlier mentioned ``pyenv``, etc. 
To keep this documentation short, we cannot provide instructions for all those options.
In later steps we will use ``virtualenv`` but please know that alternative methods are available.
Instead, we let the user choose the method they're most comfortable with and consult relevant documentation(s) when needed.

Terminal
^^^^^^^^

Installing GeoCARET_, and Python packages in general, usually requires writing installation commands within a command line interpreter. On macOS and Linux, the users can use the built-in terminal. On Windows, the users can opt for the built-in CommandPrompt (CMD) or PowerShell, or install Git Bash on Windows (https://gitforwindows.org/). Alternatively, on all platforms, if `Anaconda and Miniconda <https://docs.anaconda.com/distro-or-miniconda/>`_ has been installed, the users can take advantage of command-line interpreters shipped with those Anaconda and Miniconda distributions.

2. Setting up a virtual environment
-----------------------------------

.. note::
   It is not mandatory to install a virtual environment specifically for GeoCARET. Users can install GeoCARET in any existing virtual environment or even in the system Python installation. However, this approach is not recommended, as it can lead to package conflicts that might disrupt other Python-dependent software on the system. Therefore, it is advisable to use virtual environments tailored to specific applications. This practice isolates Python interpreters and package dependencies, preventing conflicts and ensuring stable operation.

Windows Machines
~~~~~~~~~~~~~~~~

-  Download the GeoCARET_ tool code from GitHub and unzip the code into a folder called `GeoCARET` (alternatively you can clone the repository if you use git_).
-  Open Anaconda Prompt (search for “Anaconda Prompt” in Windows start menu) OR Open Anaconda Powershell Prompt (search for “Anaconda Prompt” in Windows start menu) our other Shell tool on your operating system.
-  Using the command prompt, navigate to the GeoCARET tool folder
-  Install ``virtualenv`` - one of the available tools for creating virtual environments:

.. code-block:: bash

   > pip install virtualenv

-  Create a new virtual environment:
-  First, check the location of you Python 3.8 installation with ``py --list-paths`` in CMD or PowerShell or with ``where python``, if you're using Git BASH. Put this installation path (wrapped in double quotes) after the ``--python`` flag, see below

.. code-block:: bash

   > virtualenv --python=[installation_path] geocaretenv
   
e.g.

.. code-block:: bash

   > virtualenv --python="C:\Users\username\AppData\Local\Programs\Python\Python38\python.exe" geocaretenv

macOS / Linux
~~~~~~~~~~~~~

-  Download the GeoCARET_ tool code from GitHub and unzip the code into a folder called `GeoCARET`
-  Open the Terminal
-  Using the command prompt, navigate to the GeoCARET folder
-  Install ``virtualenv``  - one of the available tools for creating virtual environments:

.. code-block:: bash

   > pip install virtualenv

-  Create a new virtual environment:
-  First, check the location of Python using ``which -a python`` and then find all available Python version with ``ls``, e.g. ``ls /usr/bin/python*``.

.. attention::
   Remember to use the asterisk (*)
   
- Look for the path that matches the Python installation that you intend to be using within the virtual environment, in case you have several Python installations on your system, e.g. ``/usr/bin/python3.8``.
- Create the virtual environment

.. code-block:: bash

   > virtualenv --python="/usr/bin/python3.8" geocaretenv
   
3. Installing GeoCARET and its dependencies
-------------------------------------------

Windows Machines
~~~~~~~~~~~~~~~~

CMD/PowerShell
^^^^^^^^^^^^^^

-  Navigate to the GeoCARET installation folder
-  Activate the virtual environment:

.. code-block:: bash

   > .\geocaretenv\Scripts\activate

-  Install required libraries

.. code-block:: bash

   pip install -r requirements.txt

-  Deactivate the virtual environment

.. code-block:: bash

   deactivate

Git BASH
^^^^^^^^

-  Navigate to the GeoCARET installation folder

-  Activate the virtual environment:

.. code-block:: bash

   > source geocaretenv/Scripts/activate

-  Install required libraries

.. code-block:: bash

   pip install -r requirements.txt

-  Deactivate the virtual environment

.. code-block:: bash

   deactivate

macOS / LINUX
~~~~~~~~~~~~~

-  Navigate to the GeoCARET installation folder

-  Activate the virtual environment:

.. code-block:: bash

   > source geocaretenv/bin/activate

-  Install required libraries

.. code-block:: bash

   pip install -r requirements.txt

-  Deactivate the virtual environment

.. code-block:: bash

   deactivate

Gcloud command line tool (CLI) installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tool requires the ``gcloud`` command line tool. A working Gcloud installation is required on all operating systems. Download and install gcloud for your operating system here: - https://cloud.google.com/sdk/docs/install

Final Steps (4 & 5)
-------------------

To complete the installation, you need to set up a Google Cloud project and request access to some Private Assets. The instructions on how to do this can be found in :doc:`additional_steps`.





